"""Tests for the LLM prompting layer and its integration into the pipeline."""

import json

import numpy as np
import pytest

from slack_question_analyzer.group_labeler import GroupLabeler
from slack_question_analyzer.analyzer import QuestionAnalyzer


@pytest.fixture(autouse=True)
def isolated_llm_cache(tmp_path, monkeypatch):
    """Keep each test's LLM result cache in its own temp directory."""
    monkeypatch.setenv('LLM_CACHE_DIR', str(tmp_path / 'llm_cache'))


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def chat_response(content):
    """Shape of an Ollama /api/chat response."""
    return FakeResponse({'message': {'role': 'assistant', 'content': content}})


def patch_chat(monkeypatch, replies, captured=None):
    """Make requests.post return the given reply contents in order."""
    replies = list(replies)

    def fake_post(url, json=None, timeout=None):
        if captured is not None:
            captured.append({'url': url, 'body': json})
        return chat_response(replies.pop(0))

    monkeypatch.setattr('slack_question_analyzer.group_labeler.requests.post', fake_post)


# ---- Output parsing & validation ----

def test_parse_json_tolerates_prose():
    assert GroupLabeler._parse_json('Sure! {"topic": "VPN Access", "summary": "x"} ok')['topic'] == 'VPN Access'
    assert GroupLabeler._parse_json('not json') is None


def test_validate_label_rejects_generic_topics():
    assert GroupLabeler._validate_label({'topic': 'General Questions', 'summary': 's'}) is not None
    assert GroupLabeler._validate_label({'topic': 'Help', 'summary': 's'}) is not None
    assert GroupLabeler._validate_label({'topic': '', 'summary': 's'}) is not None
    assert GroupLabeler._validate_label({'topic': 'Antivirus Scanning', 'summary': ''}) is not None
    assert GroupLabeler._validate_label({'topic': 'Antivirus Scanning', 'summary': 's'}) is None


# ---- label_group ----

def test_label_group_uses_chat_with_schema_and_few_shot(monkeypatch):
    captured = []
    patch_chat(monkeypatch,
               ['{"topic": "Password Reset", "summary": "How to reset passwords."}'],
               captured)

    label = GroupLabeler('ollama').label_group(
        ['How do I reset my password?'], keywords=['password', 'reset'])

    assert label == {'topic': 'Password Reset', 'summary': 'How to reset passwords.'}
    body = captured[0]['body']
    assert captured[0]['url'].endswith('/api/chat')
    assert body['format']['type'] == 'object'  # full JSON schema, not just "json"
    assert body['options']['temperature'] == 0
    assert body['keep_alive'] == '10m'
    user_msg = body['messages'][1]['content']
    assert 'Example:' in user_msg                 # few-shot examples present
    assert 'Keywords: password, reset' in user_msg
    assert 'Never use vague topics' in body['messages'][0]['content']


def test_extraction_prompt_has_few_shot_and_long_excerpts(monkeypatch):
    captured = []
    patch_chat(monkeypatch, [json.dumps({'questions': []})], captured)
    long_message = 'x' * 500 + ' how do I fix this?'
    GroupLabeler('ollama').extract_questions([long_message])

    user_msg = captured[0]['body']['messages'][1]['content']
    assert 'Example messages:' in user_msg          # few-shot present
    assert 'bulk-disable' in user_msg               # the worked example
    assert 'x' * 500 in user_msg                    # 600-char excerpts, not 300
    assert captured[0]['body']['options']['num_predict'] == 800


def test_domain_context_injected_into_prompts(monkeypatch):
    monkeypatch.setenv('DOMAIN_CONTEXT', 'a webMethods MFT support channel')
    captured = []
    patch_chat(monkeypatch,
               ['{"topic": "Virus Scanning", "summary": "s"}'], captured)
    GroupLabeler('ollama').label_group(['How do I scan files?'])

    system = captured[0]['body']['messages'][0]['content']
    assert 'webMethods MFT support channel' in system


def test_label_group_retries_generic_topic_with_feedback(monkeypatch):
    captured = []
    patch_chat(monkeypatch,
               ['{"topic": "General Questions", "summary": "stuff"}',
                '{"topic": "Webhook Configuration", "summary": "How to configure webhooks."}'],
               captured)

    label = GroupLabeler('ollama').label_group(['How do I configure the webhook?'])

    assert label['topic'] == 'Webhook Configuration'
    assert len(captured) == 2
    # Retry conversation includes the bad answer and corrective feedback
    retry_messages = captured[1]['body']['messages']
    assert retry_messages[2]['role'] == 'assistant'
    assert 'too generic' in retry_messages[3]['content']


def test_label_group_returns_none_when_retry_also_fails(monkeypatch):
    patch_chat(monkeypatch, ['{"topic": "Help", "summary": "x"}',
                             '{"topic": "Misc", "summary": "x"}'])
    assert GroupLabeler('ollama').label_group(['Anything?']) is None


def test_label_results_are_cached_on_disk(monkeypatch):
    """Identical prompts are served from the cache, even across instances."""
    captured = []
    patch_chat(monkeypatch,
               ['{"topic": "Password Reset", "summary": "How to reset passwords."}'],
               captured)

    first = GroupLabeler('ollama').label_group(['How do I reset my password?'])
    # A brand-new instance with the same prompt must not hit the model again
    second = GroupLabeler('ollama').label_group(['How do I reset my password?'])

    assert first == second
    assert len(captured) == 1  # one real chat call total


def test_label_group_returns_none_on_connection_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise ConnectionError('refused')

    monkeypatch.setattr('slack_question_analyzer.group_labeler.requests.post', boom)
    assert GroupLabeler('ollama').label_group(['Anything?']) is None


# ---- Other capabilities ----

def test_verify_same_topic(monkeypatch):
    captured = []
    patch_chat(monkeypatch, ['{"same_topic": true}'], captured)
    result = GroupLabeler('ollama').verify_same_topic(
        ['How do I reset my password?'], ['Password reset steps?'])
    assert result is True
    assert 'Group A:' in captured[0]['body']['messages'][1]['content']

    patch_chat(monkeypatch, ['{"same_topic": false}'])
    assert GroupLabeler('ollama').verify_same_topic(['a?'], ['b?']) is False

    # Different questions (a fresh prompt) so the cached verdict above isn't reused
    patch_chat(monkeypatch, ['{"same_topic": "maybe"}'])
    assert GroupLabeler('ollama').verify_same_topic(['c?'], ['d?']) is None


def test_summarize_analysis(monkeypatch):
    patch_chat(monkeypatch, ['{"summary": "Antivirus scanning dominates with 12 questions."}'])
    groups = [{'topic': 'Antivirus Scanning', 'count': 12,
               'representative_question': 'How do I configure scanning?'}]
    summary = GroupLabeler('ollama').summarize_analysis(groups, 30)
    assert 'Antivirus' in summary


def test_detect_questions_filters_invalid_indices(monkeypatch):
    patch_chat(monkeypatch, [json.dumps({'questions': [
        {'index': 0, 'question': 'How do I fix the webhook?'},
        {'index': 99, 'question': 'out of range'},
        {'index': 1, 'question': ''},
    ]})])
    found = GroupLabeler('ollama').detect_questions(
        ["can't get the webhook to work, stuck all day", 'deploy went fine'])
    assert found == [{'index': 0, 'question': 'How do I fix the webhook?'}]


def test_is_answered(monkeypatch):
    patch_chat(monkeypatch, ['{"answered": true}'])
    assert GroupLabeler('ollama').is_answered('How do I reset?', ['Go to settings > reset.']) is True

    patch_chat(monkeypatch, ['{"answered": false}'])
    assert GroupLabeler('ollama').is_answered('How do I reset?', ['Let me check.']) is False


def test_available_checks_model_is_pulled(monkeypatch):
    monkeypatch.setattr('slack_question_analyzer.group_labeler.requests.get',
                        lambda *a, **k: FakeResponse({'models': [{'name': 'llama3.2:latest'}]}))
    labeler = GroupLabeler('ollama')
    labeler.model = 'llama3.2'
    assert labeler.available() is True

    other = GroupLabeler('ollama')
    other.model = 'mistral'
    assert other.available() is False


def test_available_false_when_ollama_unreachable(monkeypatch):
    import requests as requests_module

    def refuse(*args, **kwargs):
        raise requests_module.ConnectionError('refused')

    monkeypatch.setattr('slack_question_analyzer.group_labeler.requests.get', refuse)
    assert GroupLabeler('ollama').available() is False


# ---- Pipeline integration ----

SAMPLE_CONTENT = (
    "2024-01-05\nHow do I reset my password?\n"
    "-----------------------------------------------------------\n"
    "2024-01-08\nHow can I get my password changed?\n"
    "-----------------------------------------------------------\n"
    "2024-01-09\nWhat is the deploy schedule for production releases?\n"
)

VECTORS = {
    'how do i reset my password?': [1.0, 0.0, 0.0],
    'how can i get my password changed?': [0.99, 0.05, 0.0],
    'what is the deploy schedule for production releases?': [0.0, 1.0, 0.0],
}


def make_analyzer(monkeypatch, vectors=VECTORS, **kwargs):
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.85')
    analyzer = QuestionAnalyzer(provider='ollama', use_disk_cache=False, **kwargs)
    monkeypatch.setattr(analyzer.similarity_analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: np.array([vectors[t] for t in texts]))
    return analyzer


def stub_llm(monkeypatch, analyzer, **methods):
    monkeypatch.setattr(analyzer.labeler, 'available', lambda: True)
    # Default: LLM-first extraction "fails" so the regex fallback runs,
    # keeping older tests' question sets unchanged
    methods.setdefault('extract_questions', lambda texts, thorough=False: None)
    for name, fn in methods.items():
        monkeypatch.setattr(analyzer.labeler, name, fn)


def test_llm_labels_and_summary_applied(monkeypatch):
    analyzer = make_analyzer(monkeypatch, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: {'topic': 'Password Reset',
                                                       'summary': 'People ask how to reset passwords.'},
             verify_same_topic=lambda a, b: None,
             detect_questions=lambda texts: [],
             summarize_analysis=lambda groups, total: 'Password resets dominate.')

    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    group = results['groups'][0]
    assert group['topic'] == 'Password Reset'
    assert group['summary'] == 'People ask how to reset passwords.'
    assert results['executive_summary'] == 'Password resets dominate.'


def test_keyword_fallback_when_labels_disabled(monkeypatch):
    analyzer = make_analyzer(monkeypatch, label_groups=False)
    assert analyzer.labeler is None

    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    group = results['groups'][0]
    assert group['topic']  # keyword-derived
    assert 'password' in group['topic'].lower()
    assert group['summary'] is None
    assert results['executive_summary'] is None


def test_keyword_fallback_when_llm_fails(monkeypatch):
    analyzer = make_analyzer(monkeypatch, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: None,
             verify_same_topic=lambda a, b: None,
             detect_questions=lambda texts: [],
             summarize_analysis=lambda groups, total: None)

    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    assert results['groups'][0]['topic']  # fell back to keywords, not missing


def test_llm_detection_adds_missed_questions(monkeypatch):
    monkeypatch.setenv('LLM_EXTRACTION', 'on')  # regex-first + missed-pass mode
    content = (
        "2024-01-05\nHow do I reset my password?\n"
        "-----------------------------------------------------------\n"
        "2024-01-06\nstuck all day, the webhook just times out on every call\n"
    )
    vectors = {
        'how do i reset my password?': [1.0, 0.0],
        'how do i fix webhook timeouts?': [0.0, 1.0],
    }
    analyzer = make_analyzer(monkeypatch, vectors=vectors, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: None,
             verify_same_topic=lambda a, b: None,
             detect_questions=lambda texts: [{'index': 0, 'question': 'How do I fix webhook timeouts?'}],
             summarize_analysis=lambda groups, total: None)

    results = analyzer.analyze_slack_content(content)
    assert results['total_questions'] == 2
    texts = [q['text'] for q in results['ungrouped_questions']]
    assert 'How do I fix webhook timeouts?' in texts


def test_full_llm_extraction_mode(monkeypatch):
    """LLM_EXTRACTION=full: the LLM extracts and cleans every question."""
    monkeypatch.setenv('LLM_EXTRACTION', 'full')
    content = (
        "2024-01-05\nHi Team, Can I check if the agent comes pre-installed?\n"
        "-----------------------------------------------------------\n"
        "2024-01-06\nThe deploy finished fine.\n"
    )
    vectors = {'does the metering agent come pre-installed?': [1.0, 0.0]}
    analyzer = make_analyzer(monkeypatch, vectors=vectors, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: None,
             verify_same_topic=lambda a, b: None,
             extract_questions=lambda texts, thorough=False: [
                 {'index': 0, 'question': 'Does the Metering Agent come pre-installed?'}
             ] if 'pre-installed' in texts[0] else [],
             summarize_analysis=lambda groups, total: None)

    results = analyzer.analyze_slack_content(content)
    assert results['total_questions'] == 1
    question = results['ungrouped_questions'][0]
    assert question['text'] == 'Does the Metering Agent come pre-installed?'
    assert question['llm_extracted'] is True


def test_full_extraction_falls_back_to_regex_on_llm_failure(monkeypatch):
    monkeypatch.setenv('LLM_EXTRACTION', 'full')
    analyzer = make_analyzer(monkeypatch, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: None,
             verify_same_topic=lambda a, b: None,
             extract_questions=lambda texts, thorough=False: None,  # LLM call failed
             summarize_analysis=lambda groups, total: None)

    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    assert results['total_questions'] == 3  # regex fallback kept everything


def test_auto_mode_defaults_to_llm_extraction_for_small_transcripts(monkeypatch):
    """Without any LLM_EXTRACTION setting, small transcripts get LLM-first."""
    monkeypatch.delenv('LLM_EXTRACTION', raising=False)
    vectors = {'does the agent come pre-installed?': [1.0, 0.0]}
    analyzer = make_analyzer(monkeypatch, vectors=vectors, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: None,
             verify_same_topic=lambda a, b: None,
             extract_questions=lambda texts, thorough=False: [
                 {'index': 0, 'question': 'Does the agent come pre-installed?'}],
             summarize_analysis=lambda groups, total: None)

    results = analyzer.analyze_slack_content(
        "2024-01-05\nHi Team, can I check if the agent comes pre-installed?\n")
    assert results['total_questions'] == 1
    assert results['ungrouped_questions'][0]['llm_extracted'] is True


def test_answer_detection_counts_resolved_threads(monkeypatch):
    content = json.dumps([
        {'text': 'How do I reset my password?', 'ts': '1704412800.0'},
        {'text': 'Go to settings > security > reset.', 'ts': '1704412900.0',
         'thread_ts': '1704412800.0'},
        {'text': 'What is the deploy schedule for production releases?', 'ts': '1704499200.0'},
    ])
    vectors = {
        'how do i reset my password?': [1.0, 0.0],
        'what is the deploy schedule for production releases?': [0.0, 1.0],
    }
    analyzer = make_analyzer(monkeypatch, vectors=vectors, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: None,
             verify_same_topic=lambda a, b: None,
             detect_questions=lambda texts: [],
             is_answered=lambda question, replies: True,
             summarize_analysis=lambda groups, total: None)

    results = analyzer.analyze_slack_content(content)
    assert results['answered_questions'] == 1


# ---- Group audit (outlier eviction) ----

def test_audit_group_returns_zero_based_outliers(monkeypatch):
    labeler = GroupLabeler(provider='ollama')
    patch_chat(monkeypatch, [json.dumps({'outliers': [1]})])
    assert labeler.audit_group(['How do I install the metering agent?',
                                'How do I set up monitoring alerts?']) == [0]


def test_audit_group_clean_and_uncertain(monkeypatch):
    labeler = GroupLabeler(provider='ollama')
    patch_chat(monkeypatch, [json.dumps({'outliers': []})])
    assert labeler.audit_group(['a?', 'b?']) == []

    def boom(*a, **k):
        raise RuntimeError('ollama down')
    monkeypatch.setattr('slack_question_analyzer.group_labeler.requests.post', boom)
    # different questions: the cached verdict for ('a?', 'b?') must not apply
    assert labeler.audit_group(['c?', 'd?']) is None


def test_audit_group_rejects_evict_everything_verdict(monkeypatch):
    """'All questions are outliers' is not a meaningful audit."""
    labeler = GroupLabeler(provider='ollama')
    patch_chat(monkeypatch, [json.dumps({'outliers': [1, 2]})])
    assert labeler.audit_group(['a?', 'b?']) is None


def test_audit_group_ignores_out_of_range_indices(monkeypatch):
    labeler = GroupLabeler(provider='ollama')
    patch_chat(monkeypatch, [json.dumps({'outliers': [2, 9, 0]})])
    assert labeler.audit_group(['a?', 'b?', 'c?']) == [1]


# ---- Timeout & warm-up ----

def test_llm_timeout_configurable(monkeypatch):
    monkeypatch.setenv('LLM_TIMEOUT', '300')
    assert GroupLabeler(provider='ollama').timeout == 300
    monkeypatch.delenv('LLM_TIMEOUT')
    assert GroupLabeler(provider='ollama').timeout == 180


def test_warm_up_loads_model_without_generating(monkeypatch):
    labeler = GroupLabeler(provider='ollama')
    captured = []
    patch_chat(monkeypatch, ['ignored'], captured)
    labeler.warm_up()
    assert captured[0]['body']['messages'] == []
    assert captured[0]['body']['model'] == labeler.model


def test_warm_up_swallows_connection_errors(monkeypatch):
    import requests as _requests
    labeler = GroupLabeler(provider='ollama')

    def boom(*a, **k):
        raise _requests.ConnectionError('no ollama')
    monkeypatch.setattr('slack_question_analyzer.group_labeler.requests.post', boom)
    labeler.warm_up()  # must not raise


# ---- Fast/quality model split ----

def tags_response(monkeypatch, names):
    monkeypatch.setattr(
        'slack_question_analyzer.group_labeler.requests.get',
        lambda *a, **k: FakeResponse({'models': [{'name': n} for n in names]}))


def test_fast_model_split_when_both_downloaded(monkeypatch):
    monkeypatch.setenv('OLLAMA_GENERATION_MODEL', 'llama3.1:8b')
    tags_response(monkeypatch, ['llama3.1:8b', 'llama3.2:latest'])
    labeler = GroupLabeler(provider='ollama')
    assert labeler.available() is True
    assert labeler.model == 'llama3.1:8b'        # judgment calls
    assert labeler.fast_model == 'llama3.2'      # token-heavy extraction


def test_no_split_when_small_model_missing(monkeypatch):
    monkeypatch.setenv('OLLAMA_GENERATION_MODEL', 'llama3.1:8b')
    tags_response(monkeypatch, ['llama3.1:8b'])
    labeler = GroupLabeler(provider='ollama')
    assert labeler.available() is True
    assert labeler.fast_model == 'llama3.1:8b'


def test_fast_model_env_override(monkeypatch):
    monkeypatch.setenv('OLLAMA_GENERATION_MODEL', 'llama3.1:8b')
    monkeypatch.setenv('OLLAMA_FAST_MODEL', 'qwen2.5:3b')
    tags_response(monkeypatch, ['llama3.1:8b', 'llama3.2:latest', 'qwen2.5:3b'])
    labeler = GroupLabeler(provider='ollama')
    labeler.available()
    assert labeler.fast_model == 'qwen2.5:3b'


def test_extraction_uses_fast_model(monkeypatch):
    monkeypatch.setenv('OLLAMA_GENERATION_MODEL', 'llama3.1:8b')
    labeler = GroupLabeler(provider='ollama')
    labeler.fast_model = 'llama3.2'
    captured = []
    patch_chat(monkeypatch, [json.dumps({'questions': []})], captured)
    assert labeler.extract_questions(['How do I reset my password?']) == []
    assert captured[0]['body']['model'] == 'llama3.2'


def test_judgment_calls_use_quality_model(monkeypatch):
    monkeypatch.setenv('OLLAMA_GENERATION_MODEL', 'llama3.1:8b')
    labeler = GroupLabeler(provider='ollama')
    labeler.fast_model = 'llama3.2'
    captured = []
    patch_chat(monkeypatch, [json.dumps({'outliers': []})], captured)
    labeler.audit_group(['a?', 'b?'])
    assert captured[0]['body']['model'] == 'llama3.1:8b'


def test_warm_up_loads_both_models_when_split(monkeypatch):
    monkeypatch.setenv('OLLAMA_GENERATION_MODEL', 'llama3.1:8b')
    tags_response(monkeypatch, ['llama3.1:8b', 'llama3.2:latest'])

    class InlineThread:
        def __init__(self, target=None, args=(), daemon=None):
            self._target, self._args = target, args
        def start(self):
            self._target(*self._args)

    monkeypatch.setattr('slack_question_analyzer.group_labeler.threading.Thread',
                        InlineThread)
    labeler = GroupLabeler(provider='ollama')
    captured = []
    patch_chat(monkeypatch, ['x', 'y'], captured)
    labeler.warm_up()
    loaded = [c['body']['model'] for c in captured]
    assert loaded == ['llama3.2', 'llama3.1:8b']  # fast first, quality after
    assert all(c['body']['messages'] == [] for c in captured)


# ---- Extraction safety net ----

def test_safety_net_recovers_batch_the_fast_model_skipped(monkeypatch):
    """A fast model wrongly answering 'no questions here' must not silently
    lose a conversation: the quality model gets a second look."""
    monkeypatch.setenv('LLM_EXTRACTION', 'full')
    vectors = {'how do i configure iwhi monitoring?': [1.0, 0.0]}
    analyzer = make_analyzer(monkeypatch, vectors=vectors, label_groups=True)

    def extract(texts, thorough=False):
        if thorough:
            return [{'index': 0, 'question': 'How do I configure IWHI monitoring?'}]
        return []  # fast model: "no questions here" (wrong)

    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: None,
             verify_same_topic=lambda a, b: None,
             extract_questions=extract,
             summarize_analysis=lambda groups, total: None)

    results = analyzer.analyze_slack_content(
        "2024-01-05\nHow do I configure IWHI monitoring?\n")
    assert results['total_questions'] == 1
    assert results['ungrouped_questions'][0]['text'] == 'How do I configure IWHI monitoring?'


def test_safety_net_falls_back_to_regex_when_both_models_skip(monkeypatch):
    monkeypatch.setenv('LLM_EXTRACTION', 'full')
    vectors = {'how do i configure iwhi monitoring?': [1.0, 0.0]}
    analyzer = make_analyzer(monkeypatch, vectors=vectors, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             label_group=lambda texts, keywords=None: None,
             verify_same_topic=lambda a, b: None,
             extract_questions=lambda texts, thorough=False: [],
             summarize_analysis=lambda groups, total: None)

    results = analyzer.analyze_slack_content(
        "2024-01-05\nHow do I configure IWHI monitoring?\n")
    assert results['total_questions'] == 1  # regex version kept


# ---- Theme funnel ----

def test_assign_themes_maps_one_based_indices(monkeypatch):
    labeler = GroupLabeler(provider='ollama')
    patch_chat(monkeypatch, [json.dumps({'themes': [
        {'name': 'Security', 'items': [1, 3]},
        {'name': 'Transfers', 'items': [2]},
        {'name': 'Bogus', 'items': [99]},
    ]})])
    assigned = labeler.assign_themes(['Azure tokens', 'REST transfer triggers',
                                      'Certificate vault'])
    assert assigned == ['Security', 'Transfers', 'Security']


def test_assign_themes_returns_none_on_failure(monkeypatch):
    labeler = GroupLabeler(provider='ollama')

    def boom(*a, **k):
        raise RuntimeError('down')
    monkeypatch.setattr('slack_question_analyzer.group_labeler.requests.post', boom)
    assert labeler.assign_themes(['a', 'b']) is None


def test_analyzer_assigns_themes_to_groups_and_uniques(monkeypatch):
    analyzer = make_analyzer(monkeypatch, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             assign_themes=lambda items: ['Security', 'Security', 'Monitoring',
                                          'Monitoring', 'Security'])
    groups = [{'topic': 'Azure Tokens', 'count': 3, 'representative_question': 'x'},
              {'topic': 'Cert Vault', 'count': 2, 'representative_question': 'y'}]
    uniques = [{'text': 'IWHI monitoring examples?'},
               {'text': 'Metering agent pre-installed?'},
               {'text': 'Password reset?'}]

    themes = analyzer._assign_themes(groups, uniques)
    assert themes == [{'name': 'Security', 'count': 6},
                      {'name': 'Monitoring', 'count': 2}]
    assert groups[0]['theme'] == 'Security'
    assert uniques[0]['theme'] == 'Monitoring'


def test_themes_skipped_for_tiny_corpora(monkeypatch):
    analyzer = make_analyzer(monkeypatch, label_groups=True)
    stub_llm(monkeypatch, analyzer,
             assign_themes=lambda items: ['A', 'B'])
    assert analyzer._assign_themes(
        [{'topic': 'T', 'count': 2, 'representative_question': 'x'}],
        [{'text': 'q?'}]) is None
