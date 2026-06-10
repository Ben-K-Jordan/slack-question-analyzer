"""Tests for LLM topic labeling and its keyword fallback."""

import numpy as np
import pytest

from src.group_labeler import GroupLabeler
from src.analyzer import QuestionAnalyzer


# ---- Output parsing ----

def test_parse_label_valid_json():
    label = GroupLabeler._parse_label('{"topic": "Password Reset", "summary": "Users ask how to reset."}')
    assert label == {'topic': 'Password Reset', 'summary': 'Users ask how to reset.'}


def test_parse_label_json_wrapped_in_prose():
    label = GroupLabeler._parse_label('Sure! {"topic": "VPN Access", "summary": "x"} hope that helps')
    assert label['topic'] == 'VPN Access'


def test_parse_label_rejects_garbage_and_missing_topic():
    assert GroupLabeler._parse_label('not json at all') is None
    assert GroupLabeler._parse_label('{"summary": "no topic"}') is None


def test_parse_label_truncates_rambling_topics():
    long_topic = ' '.join(['word'] * 15)
    label = GroupLabeler._parse_label(f'{{"topic": "{long_topic}", "summary": "s"}}')
    assert len(label['topic'].split()) == 6


# ---- Ollama generation ----

class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_label_group_via_ollama(monkeypatch):
    labeler = GroupLabeler('ollama')
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured['url'] = url
        captured['body'] = json
        return FakeResponse({'response': '{"topic": "Password Reset", "summary": "How to reset passwords."}'})

    monkeypatch.setattr('src.group_labeler.requests.post', fake_post)
    label = labeler.label_group(['How do I reset my password?', 'Password reset steps?'])

    assert label['topic'] == 'Password Reset'
    assert captured['url'].endswith('/api/generate')
    assert 'How do I reset my password?' in captured['body']['prompt']
    assert captured['body']['format'] == 'json'


def test_label_group_returns_none_on_failure(monkeypatch):
    labeler = GroupLabeler('ollama')

    def boom(*args, **kwargs):
        raise ConnectionError('refused')

    monkeypatch.setattr('src.group_labeler.requests.post', boom)
    assert labeler.label_group(['Anything?']) is None


def test_available_false_when_ollama_unreachable(monkeypatch):
    import requests as requests_module

    def refuse(*args, **kwargs):
        raise requests_module.ConnectionError('refused')

    monkeypatch.setattr('src.group_labeler.requests.get', refuse)
    assert GroupLabeler('ollama').available() is False


def test_available_checks_model_is_pulled(monkeypatch):
    monkeypatch.setattr('src.group_labeler.requests.get',
                        lambda *a, **k: FakeResponse({'models': [{'name': 'llama3.2:latest'}]}))
    labeler = GroupLabeler('ollama')
    labeler.model = 'llama3.2'
    assert labeler.available() is True

    other = GroupLabeler('ollama')
    other.model = 'mistral'
    assert other.available() is False


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


def make_analyzer(monkeypatch, **kwargs):
    monkeypatch.setenv('SIMILARITY_THRESHOLD', '0.85')
    analyzer = QuestionAnalyzer(provider='ollama', use_disk_cache=False, **kwargs)
    monkeypatch.setattr(analyzer.similarity_analyzer, 'get_embeddings_batch',
                        lambda texts, progress_callback=None: np.array([VECTORS[t] for t in texts]))
    return analyzer


def test_llm_labels_applied_to_groups(monkeypatch):
    analyzer = make_analyzer(monkeypatch, label_groups=True)
    monkeypatch.setattr(analyzer.labeler, 'available', lambda: True)
    monkeypatch.setattr(analyzer.labeler, 'label_group',
                        lambda texts: {'topic': 'Password Reset', 'summary': 'People ask how to reset passwords.'})

    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    group = results['groups'][0]
    assert group['topic'] == 'Password Reset'
    assert group['summary'] == 'People ask how to reset passwords.'


def test_keyword_fallback_when_labels_disabled(monkeypatch):
    analyzer = make_analyzer(monkeypatch, label_groups=False)
    assert analyzer.labeler is None

    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    group = results['groups'][0]
    assert group['topic']  # keyword-derived
    assert 'password' in group['topic'].lower()
    assert group['summary'] is None


def test_keyword_fallback_when_llm_fails(monkeypatch):
    analyzer = make_analyzer(monkeypatch, label_groups=True)
    monkeypatch.setattr(analyzer.labeler, 'available', lambda: True)
    monkeypatch.setattr(analyzer.labeler, 'label_group', lambda texts: None)

    results = analyzer.analyze_slack_content(SAMPLE_CONTENT)
    assert results['groups'][0]['topic']  # fell back to keywords, not missing
