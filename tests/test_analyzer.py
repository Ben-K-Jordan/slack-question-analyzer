"""End-to-end tests for the QuestionAnalyzer pipeline with a fake provider."""

import csv
import json

import numpy as np
import pytest

from slack_question_analyzer.analyzer import QuestionAnalyzer

SAMPLE_CONTENT = (
    "2024-01-05\n"
    "How do I reset my password?\n"
    "-----------------------------------------------------------\n"
    "2024-01-08\n"
    "How can I reset my password?\n"
    "-----------------------------------------------------------\n"
    "2024-01-09\n"
    "What is the deploy schedule for production releases?\n"
)


@pytest.fixture
def analyzer(monkeypatch):
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.85')
    monkeypatch.setenv('GROUP_LABELS', 'off')  # keyword topics only; no LLM in tests
    analyzer = QuestionAnalyzer(provider='ollama', use_disk_cache=False)

    # Deterministic fake embeddings: password questions overlap, deploy doesn't
    vectors = {
        'how do i reset my password?': [1.0, 0.0, 0.0],
        'how can i reset my password?': [0.99, 0.05, 0.0],
        'what is the deploy schedule for production releases?': [0.0, 1.0, 0.0],
    }

    def fake_batch(texts, progress_callback=None):
        return np.array([vectors[t] for t in texts])

    monkeypatch.setattr(analyzer.similarity_analyzer, 'get_embeddings_batch', fake_batch)
    return analyzer


def test_full_pipeline(analyzer):
    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)

    assert results['total_questions'] == 3
    assert results['total_groups'] == 1
    assert len(results['ungrouped_questions']) == 1

    group = results['groups'][0]
    assert group['count'] == 2
    assert 'password' in group['keywords']
    assert group['topic']  # keyword-derived fallback label
    assert group['date_range'] == {'first_asked': '2024-01-05', 'last_asked': '2024-01-08'}
    assert results['metadata']['provider'] == 'ollama'


def test_threshold_suggestion_when_nothing_groups(monkeypatch):
    """With a too-strict threshold, results carry stats and a suggestion."""
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.95')
    monkeypatch.setenv('GROUP_LABELS', 'off')
    analyzer = QuestionAnalyzer(provider='ollama', use_disk_cache=False)

    vectors = {
        'how do i reset my password?': [1.0, 0.0, 0.0],
        'how can i reset my password?': [0.9, np.sqrt(1 - 0.81), 0.0],  # sim 0.9 < 0.95
        'what is the deploy schedule for production releases?': [0.0, 0.0, 1.0],
    }
    monkeypatch.setattr(analyzer.similarity_analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: np.array([vectors[t] for t in texts]))

    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    assert results['total_groups'] == 0

    stats = results['metadata']['similarity_stats']
    assert stats['max'] == 0.9
    suggestion = QuestionAnalyzer.suggested_threshold(results)
    assert suggestion == 0.88  # just below the best pair


def test_no_threshold_suggestion_when_groups_exist(analyzer):
    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    assert results['total_groups'] == 1
    assert QuestionAnalyzer.suggested_threshold(results) is None


def test_analyze_contents_merges_multiple_files(analyzer):
    """Messages from several files (e.g. a zipped export) form one corpus."""
    file1 = json.dumps([{'text': 'How do I reset my password?', 'ts': '1704412800.0'}])
    file2 = json.dumps([{'text': 'How can I reset my password?', 'ts': '1704672000.0'}])

    results = analyzer.analyze_contents([file1, file2])
    assert results['total_questions'] == 2
    assert results['total_groups'] == 1  # grouped across file boundaries
    assert results['groups'][0]['count'] == 2


def test_empty_content(analyzer):
    results = analyzer.analyze_slack_content("")
    assert results['total_questions'] == 0
    assert results['groups'] == []
    assert results['ungrouped_questions'] == []


def test_json_export(analyzer, tmp_path):
    output_file = tmp_path / 'results.json'
    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    analyzer.save_results(results, str(output_file))

    saved = json.loads(output_file.read_text(encoding='utf-8'))
    assert saved['total_questions'] == 3


def test_csv_export(analyzer, tmp_path):
    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    output_file = tmp_path / 'results.csv'
    analyzer.export_csv(results, str(output_file))

    with open(output_file, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))

    assert rows[0][0] == 'group_rank'
    # 2 grouped questions + 1 ungrouped + header
    assert len(rows) == 4


def test_markdown_export(analyzer, tmp_path):
    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    output_file = tmp_path / 'results.md'
    analyzer.export_markdown(results, str(output_file))

    report = output_file.read_text(encoding='utf-8')
    assert '# Question Analysis Report' in report
    assert 'asked 2 times' in report
    assert 'Unique Questions (1)' in report


def test_keywords_contrast_against_corpus(analyzer):
    """Words common to the whole corpus ('customer') characterize nothing;
    group-specific words ('antivirus') must win. Fillers are stopworded."""
    def q(text):
        return {'text': text, 'normalized_text': text.lower()}

    group = [q('Customer just needs antivirus scanning enabled?'),
             q('Customer asks how antivirus quarantine works?')]
    rest = [q('Customer just needs the transfer scheduled?'),
            q('Customer just needs webhook retries configured?')]
    corpus = group + rest

    keywords = analyzer._extract_keywords(
        group, analyzer._corpus_doc_freq(corpus), len(corpus))
    assert keywords[0] == 'antivirus'
    assert 'just' not in keywords and 'needs' not in keywords
    assert keywords[1] != 'customer'  # corpus-wide word can't outrank specifics


def test_same_message_rephrasings_collapse(analyzer):
    """Field regression: the extractor rewrote ONE complaint from two angles
    ('what is the error' / 'why does it fail'), inflating the question count.
    Same message + moderate content-word overlap = one ask. Distinct
    multi-questions from one message share few words and must survive."""
    def q(text, source):
        return {'text': text, 'normalized_text': text.lower(),
                'original_message': source}

    questions = [
        q('What is the antivirus scanning error when copying to Target System?', 'm1'),
        q('Why does the Copy Task to Target System fail due to an antivirus scanning error?', 'm1'),
        q('Can we trigger transfers via REST instead of the scheduler?', 'm2'),
        q('Is there a way to bulk-disable actions?', 'm2'),
        # Same text as the m1 question but a DIFFERENT message: a real repeat
        q('What is the antivirus scanning error when copying to Target System?', 'm3'),
    ]
    kept = analyzer._collapse_same_message_rephrasings(questions)
    texts = [k['text'] for k in kept]
    assert len(kept) == 4
    assert 'Why does the Copy Task to Target System fail due to an antivirus scanning error?' not in texts
    assert texts.count('What is the antivirus scanning error when copying to Target System?') == 2


def test_date_collision_phantom_dropped(analyzer):
    """Invariant: identical text on two dates is illegal unless each copy's
    own source contains it. The backfilled phantom dies; the genuine copy
    and genuine cross-date repeats survive."""
    def q(text, date, source):
        return {'text': text, 'normalized_text': text.lower(), 'date': date,
                'original_message': source}

    custom = 'Can we get a custom error that the script can return?'
    metering = 'How can users check their own transaction statistics?'
    questions = [
        q(custom, 'June 2, 2026', custom),            # genuine: source contains it
        q(custom, 'May 30, 2026', metering),          # phantom: source is a metering msg
        q(metering, 'May 30, 2026', metering),        # genuine
        # genuine cross-date repeat: both sources contain the text
        q('How do I reset my password?', 'June 1, 2026', 'How do I reset my password?'),
        q('How do I reset my password?', 'June 3, 2026', 'How do I reset my password?'),
    ]
    kept = analyzer._enforce_date_integrity(questions)
    dates_for_custom = [k['date'] for k in kept if k['text'] == custom]
    assert dates_for_custom == ['June 2, 2026']  # phantom May 30 copy dropped
    assert sum(1 for k in kept if 'password' in k['text']) == 2  # repeats kept

def test_same_source_rephrases_never_count_as_recurrence(analyzer):
    """Fixture-2 round 4: same-message rephrases that slipped past
    consolidation clustered into a phantom 'asked 2x'. Invariant: within a
    group, one occurrence per source message — unless the texts are
    identical (distinct short messages can share the same text)."""
    phantom = {'count': 2, 'questions': [
        {'text': 'How can I normalize file encoding during transfers?',
         'normalized_text': 'how can i normalize file encoding during transfers?',
         'original_message': 'm4'},
        {'text': 'What is the right way to handle encoding?',
         'normalized_text': 'what is the right way to handle encoding?',
         'original_message': 'm4'},
    ]}
    genuine = {'count': 2, 'questions': [
        {'text': 'How do I reset my password?',
         'normalized_text': 'how do i reset my password?',
         'original_message': 'How do I reset my password?'},
        {'text': 'How do I reset my password?',
         'normalized_text': 'how do i reset my password?',
         'original_message': 'How do I reset my password?'},
    ]}
    cross_message = {'count': 2, 'questions': [
        {'text': 'Limit concurrent transfers per node?',
         'normalized_text': 'limit concurrent transfers per node?',
         'original_message': 'm10'},
        {'text': 'Cap how many transfers run at once per node?',
         'normalized_text': 'cap how many transfers run at once per node?',
         'original_message': 'm11'},
    ]}
    analyzer._collapse_same_source_occurrences([phantom, genuine, cross_message])
    assert phantom['count'] == 1        # rephrase phantom collapsed
    assert genuine['count'] == 2        # identical-text repeats untouched
    assert cross_message['count'] == 2  # genuine recurrence untouched

def test_render_integrity_repairs_unprovable_groups(analyzer):
    """Exit invariant: a group may only render a count it can prove with
    rows. Empty rows are stripped, and a 2x that can't show two distinct
    sources (or identical text throughout) is demoted to singletons."""
    empty_row = {'count': 2, 'representative_question': 'r', 'avg_similarity': 0.9,
                 'questions': [
                     {'text': 'Real question?', 'normalized_text': 'real question?',
                      'original_message': 'm1'},
                     {'text': '', 'normalized_text': '', 'original_message': 'm2'}]}
    phantom = {'count': 2, 'representative_question': 'p', 'avg_similarity': 0.9,
               'questions': [
                   {'text': 'Rewrite one?', 'normalized_text': 'rewrite one?',
                    'original_message': 'm4'},
                   {'text': 'Rewrite two?', 'normalized_text': 'rewrite two?',
                    'original_message': 'm4'}]}
    genuine = {'count': 2, 'representative_question': 'g', 'avg_similarity': 0.9,
               'questions': [
                   {'text': 'Same q?', 'normalized_text': 'same q?',
                    'original_message': 'a'},
                   {'text': 'Same q reworded?', 'normalized_text': 'same q reworded?',
                    'original_message': 'b'}]}
    out = analyzer._enforce_render_integrity([empty_row, phantom, genuine])

    counts = sorted(g['count'] for g in out)
    assert counts == [1, 1, 1, 2]            # phantom demoted to 2 singletons
    assert all(q['text'] for g in out for q in g['questions'])  # no empty rows
    two = next(g for g in out if g['count'] == 2)
    assert two['representative_question'] == 'g'  # only the provable 2x survives


def test_dropped_questions_provenance_in_results(analyzer):
    """Nothing is silently consumed: removed questions become records."""
    content = (
        "2024-01-05\nHow do I reset my password?\n"
        "-----------------------------------------------------------\n"
        "2024-01-09\nWhat is the deploy schedule for production releases?\n"
    )
    results = analyzer.analyze_slack_content(content)
    assert 'dropped_questions' in results
    assert results['dropped_questions'] == []  # nothing dropped on clean input
