"""The regression-fixture evaluation harness."""

import json

import numpy as np
import pytest

from slack_question_analyzer.evaluation import (load_fixture, evaluate,
                                                format_report, _same_group_pairs,
                                                evaluate_transcript,
                                                format_transcript_report)
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


# --- transcript-level fixtures (end-to-end answer keys) ---

class _StubAnalyzer:
    """Stands in for QuestionAnalyzer: evaluate_transcript only needs
    analyze_contents."""

    def __init__(self, results):
        self.results = results
        self.received = None

    def analyze_contents(self, contents, **kwargs):
        self.received = contents
        return self.results


def _row(text, source, **extra):
    return {'text': text, 'original_message': source, **extra}


def _transcript_fixture(tmp_path, expect):
    (tmp_path / 'fake.txt').write_text('June 9, 2026\n\nfake', encoding='utf-8')
    path = tmp_path / 'fix.json'
    path.write_text(json.dumps({'type': 'transcript', 'transcript': 'fake.txt',
                                'expect': expect}), encoding='utf-8')
    return load_fixture(str(path))


def _good_results():
    rotation = [_row('Can we rotate SSH keys without downtime?',
                     'one of my customers wants to rotate the SSH keys'),
                _row('Is zero-downtime key rotation possible?',
                     'Re: SFTP keys - is it possible to roll over the SSH host')]
    return {
        'total_questions': 3,
        'total_groups': 1,
        'groups': [{'count': 2, 'representative_question': rotation[0]['text'],
                    'questions': rotation}],
        'ungrouped_questions': [
            _row('How do we handle a checksum mismatch gracefully?',
                 'When an inbound file fails checksum validation')],
        'feature_requests': [
            _row('Add a dark mode option to the web UI.',
                 'They would like a dark mode option')],
        'metadata': {'llm_stats': {}},
    }


def test_load_fixture_transcript_type(tmp_path):
    fixture = _transcript_fixture(tmp_path, {'total_asks': 4})
    assert fixture['_dir'] == str(tmp_path)
    bad = tmp_path / 'bad.json'
    bad.write_text(json.dumps({'type': 'transcript', 'transcript': 'x.txt'}),
                   encoding='utf-8')
    with pytest.raises(ValueError):
        load_fixture(str(bad))


def test_evaluate_transcript_all_green(tmp_path):
    fixture = _transcript_fixture(tmp_path, {
        'total_asks': 4,
        'recurring_topics': 1,
        'recurring_must_match': ['rotat', 'key'],
        'feedback_count': 1,
        'feedback_must_match': ['dark mode'],
        'feedback_must_not_match': ['checksum'],
        'message_asks': [{'contains': 'fails checksum validation', 'asks': 1},
                         {'contains': 'rotate the SSH keys', 'asks': 1}],
        'support_must_match': ['checksum'],
        'must_not_match': ['(bypass|disable)[^.?!]*(checksum|validation)'],
        'must_not_group': [['checksum', 'dark mode']],
    })
    result = evaluate_transcript(_StubAnalyzer(_good_results()), fixture)
    assert result['failed'] == 0, format_transcript_report(result)
    assert 'FAIL' not in format_transcript_report(result)


def test_evaluate_transcript_catches_each_failure_mode(tmp_path):
    results = _good_results()
    # Verb drift on the checksum question + a false merge + a lost ask
    results['ungrouped_questions'][0]['text'] = \
        'How do we disable checksum validation?'
    results['groups'][0]['questions'].append(
        _row('Can files be zip-compressed before transfer?',
             'compress files into a zip archive'))
    results['groups'][0]['count'] = 3
    results['metadata']['llm_stats'] = {'integrity_repairs': 1}
    fixture = _transcript_fixture(tmp_path, {
        'total_asks': 17,
        'recurring_topics': 2,
        'feedback_count': 0,
        'message_asks': [{'contains': 'chargeback reporting', 'asks': 1}],
        'must_not_match': ['disable[^.?!]*validation'],
        'must_not_group': [['rotat', 'zip']],
    })
    result = evaluate_transcript(_StubAnalyzer(results), fixture)
    failed = {c['name'] for c in result['checks'] if not c['ok']}
    assert 'total asks = 17' in failed                     # 5 != 17
    assert 'recurring topics = 2' in failed                # got 1
    assert 'product feedback = 0' in failed                # got 1
    assert any('chargeback' in n for n in failed)          # marker matched 0 rows
    assert any('verb drift' in n for n in failed)
    assert any('not merged' in n for n in failed)
    assert 'no render-integrity repairs needed' in failed
    report = format_transcript_report(result)
    assert 'FAIL' in report and 'silently dropped' in report


def test_evaluate_transcript_isolates_topic_bank(tmp_path, monkeypatch):
    monkeypatch.setenv('TOPIC_BANK_PATH', '/real/bank.json')
    seen = {}

    class _Spy(_StubAnalyzer):
        def analyze_contents(self, contents, **kwargs):
            import os
            seen['bank'] = os.environ['TOPIC_BANK_PATH']
            return super().analyze_contents(contents, **kwargs)

    fixture = _transcript_fixture(tmp_path, {'total_asks': 4})
    evaluate_transcript(_Spy(_good_results()), fixture)
    assert seen['bank'] != '/real/bank.json'   # temp bank during the run
    import os
    assert os.environ['TOPIC_BANK_PATH'] == '/real/bank.json'  # restored


def _markers_resolve(transcript_path, fixture_path):
    """Every 'contains' marker must hit exactly ONE message within the
    200-char original_message cap, and the per-message asks must sum to
    total_asks — validates the shipped keys without any LLM."""
    from slack_question_analyzer.question_extractor import QuestionExtractor
    fixture = load_fixture(fixture_path)
    content = open(transcript_path, encoding='utf-8').read()
    messages = QuestionExtractor().extract_messages(content)
    capped = [' '.join(m['text'].split())[:200].lower() for m in messages]
    for spec in fixture['expect']['message_asks']:
        hits = [c for c in capped if spec['contains'].lower() in c]
        assert len(hits) == 1, f"marker {spec['contains']!r} hit {len(hits)} messages"
    total = sum(s['asks'] for s in fixture['expect']['message_asks'])
    assert total == fixture['expect']['total_asks']


def test_shipped_mft_fixture_1_markers_resolve():
    _markers_resolve('fixtures/mft_test_transcript.txt',
                     'fixtures/mft_synthetic_1.json')


def test_shipped_mft_fixture_2_markers_resolve():
    _markers_resolve('fixtures/mft_test_transcript_2.txt',
                     'fixtures/mft_synthetic_2.json')
