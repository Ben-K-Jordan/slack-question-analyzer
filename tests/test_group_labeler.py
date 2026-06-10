"""Tests for the LLM prompting layer and its integration into the pipeline."""

import json

import numpy as np

from src.group_labeler import GroupLabeler
from src.analyzer import QuestionAnalyzer


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

    monkeypatch.setattr('src.group_labeler.requests.post', fake_post)


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


def test_label_group_returns_none_on_connection_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise ConnectionError('refused')

    monkeypatch.setattr('src.group_labeler.requests.post', boom)
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

    patch_chat(monkeypatch, ['{"same_topic": "maybe"}'])
    assert GroupLabeler('ollama').verify_same_topic(['a?'], ['b?']) is None


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
    monkeypatch.setattr('src.group_labeler.requests.get',
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

    monkeypatch.setattr('src.group_labeler.requests.get', refuse)
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
