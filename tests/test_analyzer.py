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
