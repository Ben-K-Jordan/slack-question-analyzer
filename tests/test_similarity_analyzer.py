"""Tests for similarity grouping and the embedding cache."""

import numpy as np
import pytest

from slack_question_analyzer.similarity_analyzer import SimilarityAnalyzer, EmbeddingCache, EmbeddingError


def make_analyzer(monkeypatch, threshold='0.85'):
    monkeypatch.setenv('SIMILARITY_THRESHOLD', threshold)
    # A model without a task prefix, so fakes can match on raw text
    monkeypatch.setenv('OLLAMA_MODEL', 'test-embed')
    return SimilarityAnalyzer(provider='ollama', use_disk_cache=False)


def question(text):
    return {'text': text, 'normalized_text': text.lower(), 'date': 'Unknown',
            'original_message': text}


def test_groups_similar_questions(monkeypatch):
    analyzer = make_analyzer(monkeypatch)

    # Two near-identical vectors and one orthogonal one
    fake_embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.99, 0.05, 0.0],
        [0.0, 1.0, 0.0],
    ])
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake_embeddings)

    questions = [question('How do I reset my password?'),
                 question('How can I reset my password?'),
                 question('What is the deploy schedule?')]
    groups = analyzer.group_similar_questions(questions)

    assert len(groups) == 2
    assert groups[0]['count'] == 2
    assert groups[1]['count'] == 1
    assert 0.0 <= groups[0]['avg_similarity'] <= 1.0


def test_empty_input_returns_no_groups(monkeypatch):
    analyzer = make_analyzer(monkeypatch)
    assert analyzer.group_similar_questions([]) == []


def test_invalid_threshold_rejected(monkeypatch):
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '1.5')
    with pytest.raises(ValueError):
        SimilarityAnalyzer(provider='ollama', use_disk_cache=False)

    monkeypatch.setenv('SIMILARITY_THRESHOLD', 'abc')
    with pytest.raises(ValueError):
        SimilarityAnalyzer(provider='ollama', use_disk_cache=False)


def test_invalid_provider_rejected(monkeypatch):
    with pytest.raises(ValueError):
        SimilarityAnalyzer(provider='something-else')


def test_batch_raises_when_provider_fails(monkeypatch):
    analyzer = make_analyzer(monkeypatch)
    analyzer.MAX_RETRIES = 1

    def boom(text):
        raise EmbeddingError('connection refused')

    monkeypatch.setattr(analyzer, '_ollama_embedding', boom)
    with pytest.raises(EmbeddingError):
        analyzer.get_embeddings_batch(['some question'])


def test_batch_uses_cache_and_dedupes(monkeypatch):
    analyzer = make_analyzer(monkeypatch)
    calls = []

    def fake_embedding(text):
        calls.append(text)
        return [1.0, 0.0]

    monkeypatch.setattr(analyzer, '_ollama_embedding', fake_embedding)
    result = analyzer.get_embeddings_batch(['a', 'a', 'b'])

    assert sorted(calls) == ['a', 'b']  # 'a' embedded once despite appearing twice
    assert result.shape == (3, 2)

    # Second run should be fully served from cache
    calls.clear()
    analyzer.get_embeddings_batch(['a', 'b'])
    assert calls == []


def test_exact_duplicates_need_no_embeddings(monkeypatch):
    """Identical questions are grouped with zero AI calls."""
    analyzer = make_analyzer(monkeypatch)
    calls = []
    monkeypatch.setattr(analyzer, '_ollama_embedding',
                        lambda text: calls.append(text) or [1.0, 0.0])

    questions = [question('How do I reset my password?') for _ in range(3)]
    groups = analyzer.group_similar_questions(questions)

    assert calls == []  # no embeddings fetched at all
    assert len(groups) == 1
    assert groups[0]['count'] == 3
    assert groups[0]['avg_similarity'] == 1.0


def test_duplicates_embed_once_per_distinct_question(monkeypatch):
    analyzer = make_analyzer(monkeypatch)
    vectors = {'how do i reset my password?': [1.0, 0.0],
               'what is the deploy schedule?': [0.0, 1.0]}
    calls = []

    def fake_embedding(text):
        calls.append(text)
        return vectors[text]

    monkeypatch.setattr(analyzer, '_ollama_embedding', fake_embedding)

    questions = [question('How do I reset my password?'),
                 question('How do I reset my password?'),
                 question('What is the deploy schedule?')]
    groups = analyzer.group_similar_questions(questions)

    assert len(calls) == 2  # one embedding per distinct question, not three
    assert groups[0]['count'] == 2
    assert groups[1]['count'] == 1


def test_lexical_near_duplicates_merge_without_ai(monkeypatch):
    """Rewordings sharing >=90% of tokens merge before any embedding call."""
    analyzer = make_analyzer(monkeypatch)
    calls = []
    monkeypatch.setattr(analyzer, '_ollama_embedding',
                        lambda text: calls.append(text) or [1.0, 0.0])

    base = 'how do i configure the antivirus scanner for inbound file transfers'
    questions = [question(base), question(base + ' please')]
    groups = analyzer.group_similar_questions(questions)

    assert calls == []  # merged lexically; single bucket means no embeddings
    assert len(groups) == 1
    assert groups[0]['count'] == 2


def test_borderline_groups_merged_when_verifier_agrees(monkeypatch):
    """Pairs just below the threshold are merged when the LLM says same topic."""
    analyzer = make_analyzer(monkeypatch, threshold='0.85')
    monkeypatch.setenv('LLM_VERIFY_MARGIN', '0.05')

    # Two questions with similarity ~0.83: below 0.85 but inside the margin
    fake = np.array([[1.0, 0.0], [0.83, np.sqrt(1 - 0.83 ** 2)]])
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake)

    questions = [question('How do I reset my password?'),
                 question('Steps for changing my password?')]

    asked = []

    def verifier(a, b):
        asked.append((a, b))
        return True

    groups = analyzer.group_similar_questions(questions, verifier=verifier)
    assert len(asked) == 1
    assert len(groups) == 1
    assert groups[0]['count'] == 2


def test_borderline_groups_stay_apart_when_verifier_disagrees(monkeypatch):
    analyzer = make_analyzer(monkeypatch, threshold='0.85')
    monkeypatch.setenv('LLM_VERIFY_MARGIN', '0.05')

    fake = np.array([[1.0, 0.0], [0.83, np.sqrt(1 - 0.83 ** 2)]])
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake)

    questions = [question('How do I reset my password?'),
                 question('How do I reset my API key?')]
    groups = analyzer.group_similar_questions(questions, verifier=lambda a, b: False)
    assert len(groups) == 2


def test_clearly_different_groups_skip_the_verifier(monkeypatch):
    """The verifier is only consulted inside the borderline band."""
    analyzer = make_analyzer(monkeypatch, threshold='0.85')

    fake = np.array([[1.0, 0.0], [0.0, 1.0]])  # similarity ~0: far below band
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake)

    def never(a, b):
        raise AssertionError('verifier should not be called')

    questions = [question('How do I reset my password?'),
                 question('What is the deploy schedule?')]
    groups = analyzer.group_similar_questions(questions, verifier=never)
    assert len(groups) == 2


def test_average_link_prevents_chaining(monkeypatch):
    """
    Regression for the real-world mega-group: in a domain-homogeneous corpus
    every adjacent pair can clear the threshold (A~B, B~C) while A and C are
    unrelated. Single-link chains them into one group; average-link must not.
    """
    analyzer = make_analyzer(monkeypatch, threshold='0.75')
    matrix = np.array([
        [1.0, 0.80, 0.20],
        [0.80, 1.0, 0.80],
        [0.20, 0.80, 1.0],
    ])
    clusters = analyzer._cluster_buckets(3, matrix)
    # B joins A (0.8). C's average to {A,B} is (0.2+0.8)/2 = 0.5 < 0.75: stays out
    assert clusters == [[0, 1], [2]]


def test_average_link_keeps_two_tight_clusters_apart(monkeypatch):
    """Two tight pairs with elevated cross-similarity stay two groups."""
    analyzer = make_analyzer(monkeypatch, threshold='0.75')
    matrix = np.array([
        [1.0, 0.90, 0.76, 0.60],
        [0.90, 1.0, 0.60, 0.60],
        [0.76, 0.60, 1.0, 0.90],
        [0.60, 0.60, 0.90, 1.0],
    ])
    clusters = analyzer._cluster_buckets(4, matrix)
    # C's avg to {A,B} = (0.76+0.60)/2 = 0.68 < 0.75 despite the 0.76 best link
    assert clusters == [[0, 1], [2, 3]]


def test_large_corpus_uses_leader_clustering(monkeypatch):
    """Above LARGE_CLUSTERING_THRESHOLD, grouping avoids the full n^2 matrix."""
    analyzer = make_analyzer(monkeypatch)
    monkeypatch.setenv('LARGE_CLUSTERING_THRESHOLD', '2')  # force the large path

    fake = np.array([[1.0, 0.0], [1.0, 0.05], [0.0, 1.0]])
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake)

    def never(a, b):
        raise AssertionError('verifier must be skipped on the large path')

    questions = [question('How do I reset my password?'),
                 question('Steps to reset my password quickly?'),
                 question('What is the deploy schedule?')]
    groups = analyzer.group_similar_questions(questions, verifier=never)

    assert len(groups) == 2
    assert groups[0]['count'] == 2
    assert groups[1]['count'] == 1
    assert 0.0 < groups[0]['avg_similarity'] <= 1.0
    assert groups[1]['avg_similarity'] == 1.0


def test_nomic_model_gets_clustering_prefix(monkeypatch):
    """nomic-embed-text is trained with task prefixes; we must send one."""
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.85')
    monkeypatch.setenv('OLLAMA_MODEL', 'nomic-embed-text')
    analyzer = SimilarityAnalyzer(provider='ollama', use_disk_cache=False)
    assert analyzer.embed_prefix == 'clustering: '

    sent = []
    monkeypatch.setattr(analyzer, '_ollama_embedding',
                        lambda text: sent.append(text) or [1.0, 0.0])
    analyzer.get_embeddings_batch(['how do i reset my password?'])
    assert sent == ['clustering: how do i reset my password?']


def test_other_models_get_no_prefix(monkeypatch):
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.85')
    monkeypatch.setenv('OLLAMA_MODEL', 'mxbai-embed-large')
    analyzer = SimilarityAnalyzer(provider='ollama', use_disk_cache=False)
    assert analyzer.embed_prefix == ''


def test_similarity_stats_recorded(monkeypatch):
    analyzer = make_analyzer(monkeypatch)
    fake = np.array([[1.0, 0.0], [0.6, 0.8], [0.0, 1.0]])
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake)

    questions = [question('a much longer question one?'),
                 question('another quite different two?'),
                 question('completely unrelated three?')]
    analyzer.group_similar_questions(questions)

    stats = analyzer.last_similarity_stats
    assert stats is not None
    assert stats['max'] == 0.8  # best pair: [0.6,0.8] vs [0,1]
    assert 0.0 <= stats['median'] <= stats['p90'] <= stats['max']


def test_default_threshold_is_model_aware(monkeypatch):
    monkeypatch.delenv('SIMILARITY_THRESHOLD', raising=False)
    monkeypatch.setenv('OLLAMA_MODEL', 'test-embed')
    analyzer = SimilarityAnalyzer(provider='ollama', use_disk_cache=False)
    # Field-calibrated: unrelated questions in a single-domain channel score
    # ~0.65-0.72 with nomic, so the default must sit above that band
    assert analyzer.similarity_threshold == 0.80
    assert analyzer.threshold_pinned is False

    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.9')
    pinned = SimilarityAnalyzer(provider='ollama', use_disk_cache=False)
    assert pinned.similarity_threshold == 0.9
    assert pinned.threshold_pinned is True


def test_threshold_auto_adjusts_when_top_pair_stands_out(monkeypatch):
    monkeypatch.delenv('SIMILARITY_THRESHOLD', raising=False)
    monkeypatch.setenv('OLLAMA_MODEL', 'test-embed')
    analyzer = SimilarityAnalyzer(provider='ollama', use_disk_cache=False)

    # Best pair 0.78 (below the 0.80 default) but far above the other pairs:
    # a genuine cluster the default just missed
    fake = np.array([[1.0, 0.0, 0.0],
                     [0.78, 0.6247, 0.0],
                     [0.0, 0.0, 1.0]])
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake)

    questions = [question('a longer question number one?'),
                 question('a different question number two?'),
                 question('an unrelated question number three?')]
    groups = analyzer.group_similar_questions(questions)

    assert analyzer.threshold_auto_adjusted is True
    assert analyzer.similarity_threshold == 0.76  # best pair 0.78, minus 0.02
    assert any(g['count'] == 2 for g in groups)


def test_no_auto_adjust_into_the_noise_band(monkeypatch):
    """
    Regression for the real-world 70%-average blob: when ALL pairs sit in a
    narrow band (single-domain corpus), relaxing the threshold would merge
    unrelated topics. The analyzer must refuse and keep singletons.
    """
    monkeypatch.delenv('SIMILARITY_THRESHOLD', raising=False)
    monkeypatch.setenv('OLLAMA_MODEL', 'test-embed')
    analyzer = SimilarityAnalyzer(provider='ollama', use_disk_cache=False)

    # Pairwise sims ~0.70-0.72: a dense noise band with no standout pair
    fake = np.array([[1.0, 0.0, 0.0],
                     [0.72, 0.6940, 0.0],
                     [0.70, 0.2824, 0.6559]])
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake)

    questions = [question('a longer question number one?'),
                 question('a different question number two?'),
                 question('an unrelated question number three?')]
    groups = analyzer.group_similar_questions(questions)

    assert analyzer.threshold_auto_adjusted is False
    assert analyzer.similarity_threshold == 0.80  # unchanged
    assert all(g['count'] == 1 for g in groups)  # honest singletons, no blob


def test_verifier_merge_rejected_when_combined_group_is_loose(monkeypatch):
    """An LLM 'same topic' yes cannot re-create a mixed mega-group."""
    analyzer = make_analyzer(monkeypatch, threshold='0.85')

    matrix = np.array([
        [1.00, 0.90, 0.84, 0.20],
        [0.90, 1.00, 0.20, 0.20],
        [0.84, 0.20, 1.00, 0.90],
        [0.20, 0.20, 0.90, 1.00],
    ])

    def never(a, b):
        raise AssertionError('verifier must not be consulted for a loose merge')

    buckets = [[question(f'question number {i}?')] for i in range(4)]
    clusters = analyzer._merge_borderline_clusters(
        [[0, 1], [2, 3]], matrix, buckets, never)
    # Combined avg would be (.9+.9+.84+.2+.2+.2)/6 = 0.54: guard skips it
    assert clusters == [[0, 1], [2, 3]]


def test_pinned_threshold_never_auto_adjusts(monkeypatch):
    analyzer = make_analyzer(monkeypatch, threshold='0.85')  # env-pinned

    fake = np.array([[1.0, 0.0], [0.6, 0.8], [-1.0, 0.0]])
    monkeypatch.setattr(analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: fake)

    questions = [question('a longer question number one?'),
                 question('a different question number two?'),
                 question('an opposite question number three?')]
    groups = analyzer.group_similar_questions(questions)

    assert analyzer.threshold_auto_adjusted is False
    assert all(g['count'] == 1 for g in groups)


def test_embedding_cache_roundtrip(tmp_path):
    cache = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path))
    assert cache.get('hello') is None

    cache.set('hello', [0.1, 0.2])
    cache.save()

    reloaded = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path))
    assert reloaded.get('hello') == [0.1, 0.2]


def test_embedding_cache_survives_corruption(tmp_path):
    cache = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path))
    cache.set('hello', [0.1])
    cache.save()
    cache.cache_path.write_text('{not valid json')

    reloaded = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path))
    assert reloaded.get('hello') is None  # starts fresh instead of crashing


def test_concurrent_cache_instances_merge_on_save(tmp_path):
    """Two instances saving to the same file keep each other's entries."""
    first = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path))
    second = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path))

    first.set('alpha', [0.1])
    first.save()
    second.set('beta', [0.2])
    second.save()  # must not clobber 'alpha' written after second loaded

    reloaded = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path))
    assert reloaded.get('alpha') == [0.1]
    assert reloaded.get('beta') == [0.2]


def test_cache_evicts_oldest_beyond_max_entries(tmp_path):
    from slack_question_analyzer.disk_cache import JsonDiskCache
    cache = JsonDiskCache('ollama', 'test-model', str(tmp_path), max_entries=2)
    cache.set('one', [1])
    cache.set('two', [2])
    cache.set('three', [3])
    cache.save()

    reloaded = JsonDiskCache('ollama', 'test-model', str(tmp_path))
    assert reloaded.get('one') is None  # oldest evicted
    assert reloaded.get('two') == [2]
    assert reloaded.get('three') == [3]


def test_disabled_cache_does_not_write(tmp_path):
    cache = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path), enabled=False)
    cache.set('hello', [0.1])
    cache.save()
    assert not cache.cache_path.exists()
