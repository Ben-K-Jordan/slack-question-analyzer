"""End-to-end tests for the QuestionAnalyzer pipeline with a fake provider."""

import csv
import json

import numpy as np
import pytest

from src.analyzer import QuestionAnalyzer

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
    assert group['date_range'] == {'first_asked': '2024-01-05', 'last_asked': '2024-01-08'}
    assert results['metadata']['provider'] == 'ollama'


def test_empty_content(analyzer):
    results = analyzer.analyze_slack_content("")
    assert results['total_questions'] == 0
    assert results['groups'] == []
    assert results['ungrouped_questions'] == []


def test_json_export(analyzer, tmp_path):
    input_file = tmp_path / 'input.txt'
    input_file.write_text(SAMPLE_CONTENT, encoding='utf-8')
    output_file = tmp_path / 'results.json'

    analyzer.analyze_from_file(str(input_file), str(output_file))

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
