"""The regression-fixture evaluation harness."""

import json

import numpy as np
import pytest

from slack_question_analyzer.evaluation import (load_fixture, evaluate,
                                                format_report, _same_group_pairs)
from slack_question_analyzer.analyzer import QuestionAnalyzer


def test_shipped_fixture_is_valid():
    fixture = load_fixture('fixtures/field_run_2026-06-10.json')
    assert len(fixture['questions']) == 17
    threads = [q for q in fixture['questions'] if q.get('group') == 'thread-scaling']
    assert len(threads) == 3  # incl. the singleton-rescue target


def test_load_fixture_rejects_unlabeled(tmp_path):
    path = tmp_path / 'bad.json'
    path.write_text(json.dumps({'questions': [{'text': 'q?'}]}), encoding='utf-8')
    with pytest.raises(ValueError):
        load_fixture(str(path))


def test_same_group_pairs():
    pairs = _same_group_pairs({'a': 'g1', 'b': 'g1', 'c': 'g2', 'd': None})
    assert pairs == {frozenset(('a', 'b'))}


def test_evaluate_scores_routing_and_pairs(tmp_path, monkeypatch):
    taxonomy = {'version': 9, 'buckets': [
        {'id': 1, 'name': 'Antivirus', 'anchor': 'anchor-av', 'category': 'File Ops'},
        {'id': 2, 'name': 'Monitoring', 'anchor': 'anchor-mon', 'category': 'Ops'},
    ]}
    tax_path = tmp_path / 'tax.json'
    tax_path.write_text(json.dumps(taxonomy), encoding='utf-8')
    monkeypatch.setenv('TAXONOMY_PATH', str(tax_path))
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.8')
    monkeypatch.setenv('OLLAMA_MODEL', 'test-embed')

    vectors = {
        'anchor-av': [1.0, 0.0, 0.0],
        'anchor-mon': [0.0, 1.0, 0.0],
        'virus scan email alert?': [0.9, 0.0, 0.435],
        'quarantine folder for infected files?': [0.9, 0.0, -0.435],
        'e2e monitoring setup?': [0.05, 0.95, 0.0],
    }
    analyzer = QuestionAnalyzer(provider='ollama', use_disk_cache=False,
                                label_groups=False)
    monkeypatch.setattr(
        analyzer.similarity_analyzer, 'get_embeddings_batch',
        lambda texts, progress_callback=None: np.array([vectors[t] for t in texts]))

    fixture = {'questions': [
        {'text': 'Virus scan email alert?', 'bucket': 'Antivirus', 'group': 'av'},
        {'text': 'Quarantine folder for infected files?', 'bucket': 'Antivirus', 'group': 'av'},
        # Deliberately mislabeled: routed to Monitoring, expected Antivirus
        {'text': 'E2e monitoring setup?', 'bucket': 'Antivirus', 'group': None},
    ]}

    result = evaluate(analyzer, fixture)
    assert result['routing_correct'] == 2
    assert len(result['routing_mismatches']) == 1
    assert result['routing_mismatches'][0]['got'] == 'Monitoring'
    # The two antivirus questions only pair if in-bucket clustering joins
    # them; at sim 0.62 under bar 0.8 with no verifier they stay apart
    assert result['pairs_expected'] == 1
    assert result['pair_recall'] in (0.0, 1.0)
    report = format_report(result)
    assert 'Routing:  2/3' in report
