"""Tests for similarity grouping and the embedding cache."""

import numpy as np
import pytest

from src.similarity_analyzer import SimilarityAnalyzer, EmbeddingCache, EmbeddingError


def make_analyzer(monkeypatch, threshold='0.85'):
    monkeypatch.setenv('SIMILARITY_THRESHOLD', threshold)
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


def test_disabled_cache_does_not_write(tmp_path):
    cache = EmbeddingCache('ollama', 'test-model', cache_dir=str(tmp_path), enabled=False)
    cache.set('hello', [0.1])
    cache.save()
    assert not cache.cache_path.exists()
