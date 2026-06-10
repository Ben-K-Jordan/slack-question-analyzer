"""Tests for the learned topic bank."""

import numpy as np

from slack_question_analyzer.topic_bank import TopicBank
from slack_question_analyzer.analyzer import QuestionAnalyzer


def make_group(topic='Password Reset', count=3):
    return {
        'topic': topic,
        'summary': 'People ask how to reset passwords.',
        'representative_question': 'How do I reset my password?',
        'keywords': ['password', 'reset'],
        'count': count,
    }


def test_record_and_match_roundtrip(tmp_path):
    path = tmp_path / 'bank.json'
    bank = TopicBank(path=str(path))
    bank.record(make_group(), [1.0, 0.0])
    bank.save()

    reloaded = TopicBank(path=str(path))
    hit = reloaded.match([0.95, 0.31], threshold=0.85)  # ~0.95 similarity
    assert hit is not None
    assert hit['topic'] == 'Password Reset'

    assert reloaded.match([0.0, 1.0], threshold=0.85) is None  # orthogonal


def test_matched_entries_accumulate_history(tmp_path):
    bank = TopicBank(path=str(tmp_path / 'bank.json'))
    entry = bank.record(make_group(count=3), [1.0, 0.0])
    updated = bank.record(make_group(topic='ignored new name', count=2),
                          [1.0, 0.0], matched=entry)

    assert updated is entry
    assert entry['topic'] == 'Password Reset'  # established name kept
    assert entry['question_count'] == 5
    assert entry['analysis_count'] == 2


def test_dimension_mismatch_entries_are_skipped(tmp_path):
    """Old entries from a different embedding model can't poison matches."""
    bank = TopicBank(path=str(tmp_path / 'bank.json'))
    bank.record(make_group(), [1.0, 0.0, 0.0])  # 3-dim entry
    assert bank.match([1.0, 0.0], threshold=0.5) is None  # 2-dim query


def test_disabled_bank_is_inert(tmp_path):
    path = tmp_path / 'bank.json'
    bank = TopicBank(path=str(path), enabled=False)
    assert bank.record(make_group(), [1.0, 0.0]) is None
    bank.save()
    assert not path.exists()


# ---- Pipeline integration: labels stay stable across analyses ----

SAMPLE_CONTENT = (
    "2024-01-05\nHow do I reset my password?\n"
    "-----------------------------------------------------------\n"
    "2024-01-08\nHow can I reset my password?\n"
)

VECTORS = {
    'how do i reset my password?': [1.0, 0.0],
    'how can i reset my password?': [0.99, np.sqrt(1 - 0.99 ** 2)],
}


def make_analyzer(monkeypatch):
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.85')
    monkeypatch.setenv('OLLAMA_MODEL', 'test-embed')  # no embed prefix
    monkeypatch.setenv('LLM_EXTRACTION', 'off')
    analyzer = QuestionAnalyzer(provider='ollama', use_disk_cache=False,
                                label_groups=True)

    def fake_batch(texts, progress_callback=None):
        # Populate the in-memory cache so group centroids can be computed
        for t in texts:
            analyzer.similarity_analyzer.embeddings_cache.set(t, VECTORS[t])
        return np.array([VECTORS[t] for t in texts])

    monkeypatch.setattr(analyzer.similarity_analyzer, 'get_embeddings_batch', fake_batch)
    monkeypatch.setattr(analyzer.labeler, 'available', lambda: True)
    monkeypatch.setattr(analyzer.labeler, 'verify_same_topic', lambda a, b: None)
    monkeypatch.setattr(analyzer.labeler, 'summarize_analysis', lambda g, t: None)
    return analyzer


def test_bank_keeps_topic_names_stable_across_analyses(monkeypatch):
    # First analysis: the LLM names the group; the bank learns it
    first = make_analyzer(monkeypatch)
    monkeypatch.setattr(first.labeler, 'label_group',
                        lambda texts, keywords=None: {'topic': 'Password Reset',
                                                      'summary': 'Resets.'})
    results1 = first.analyze_slack_content(SAMPLE_CONTENT)
    assert results1['groups'][0]['topic'] == 'Password Reset'
    assert results1['groups'][0]['seen_in_analyses'] == 1

    # Second analysis (fresh instance): the bank labels it — the LLM must
    # not be asked again, and the name must be identical
    second = make_analyzer(monkeypatch)

    def never(texts, keywords=None):
        raise AssertionError('bank should have labeled this group')

    monkeypatch.setattr(second.labeler, 'label_group', never)
    results2 = second.analyze_slack_content(SAMPLE_CONTENT)
    group = results2['groups'][0]
    assert group['topic'] == 'Password Reset'
    assert group['seen_in_analyses'] == 2


def test_bank_off_disables_learning(monkeypatch):
    monkeypatch.setenv('TOPIC_BANK', 'off')
    analyzer = make_analyzer(monkeypatch)
    monkeypatch.setattr(analyzer.labeler, 'label_group',
                        lambda texts, keywords=None: {'topic': 'Password Reset',
                                                      'summary': 'Resets.'})
    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    assert 'seen_in_analyses' not in results['groups'][0]
