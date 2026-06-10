"""Tests for the Flask API server: jobs, history, health, and validation."""

import json
import time

import numpy as np
import pytest

import api_server
from api_server import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(api_server, 'ANALYSES_DIR', tmp_path / 'analyses')
    monkeypatch.setattr(api_server, '_jobs', {})
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def fake_engine(monkeypatch):
    """Make QuestionAnalyzer run instantly with deterministic embeddings."""
    vectors = {
        'how do i reset my password?': [1.0, 0.0, 0.0],
        'how can i reset my password?': [0.99, 0.05, 0.0],
        'what is the deploy schedule for production releases?': [0.0, 1.0, 0.0],
    }

    def fake_batch(self, texts, progress_callback=None):
        if progress_callback:
            progress_callback(len(texts), len(texts))
        return np.array([vectors[t] for t in texts])

    monkeypatch.setattr('src.similarity_analyzer.SimilarityAnalyzer.get_embeddings_batch',
                        fake_batch)


SAMPLE_CONTENT = (
    "2024-01-05\nHow do I reset my password?\n"
    "-----------------------------------------------------------\n"
    "2024-01-08\nHow can I reset my password?\n"
    "-----------------------------------------------------------\n"
    "2024-01-09\nWhat is the deploy schedule for production releases?\n"
)


def wait_for_job(client, job_id, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = client.get(f'/api/jobs/{job_id}')
        body = response.get_json()
        if body['status'] in ('done', 'error'):
            return body
        time.sleep(0.05)
    pytest.fail('job did not finish in time')


def test_analyze_job_lifecycle(client, fake_engine):
    response = client.post('/api/analyze', json={'content': SAMPLE_CONTENT})
    assert response.status_code == 202
    job_id = response.get_json()['job_id']

    body = wait_for_job(client, job_id)
    assert body['status'] == 'done'
    assert body['data']['total_questions'] == 3
    assert body['data']['total_groups'] == 1
    assert body['analysis_id']
    assert body['progress']['stage'] == 'complete'


def test_analysis_is_persisted_and_listed(client, fake_engine):
    job_id = client.post('/api/analyze', json={'content': SAMPLE_CONTENT}).get_json()['job_id']
    finished = wait_for_job(client, job_id)

    listed = client.get('/api/analyses').get_json()
    assert listed['success']
    assert len(listed['analyses']) == 1
    assert listed['analyses'][0]['id'] == finished['analysis_id']
    assert listed['analyses'][0]['total_questions'] == 3

    latest = client.get('/api/analyses/latest').get_json()
    assert latest['success']
    assert latest['data']['total_questions'] == 3

    single = client.get(f"/api/analyses/{finished['analysis_id']}").get_json()
    assert single['data']['total_groups'] == 1


def test_latest_analysis_404_when_empty(client):
    assert client.get('/api/analyses/latest').status_code == 404


def test_weekly_stats_endpoint(client, fake_engine):
    job_id = client.post('/api/analyze', json={'content': SAMPLE_CONTENT}).get_json()['job_id']
    finished = wait_for_job(client, job_id)

    latest = client.get('/api/analyses/latest/weekly')
    assert latest.status_code == 200
    weekly = latest.get_json()['data']
    # All three sample questions fall inside the week ending 2024-01-09
    assert weekly['totalThisWeek'] == 3
    assert weekly['groups'][0]['count'] == 2

    by_id = client.get(f"/api/analyses/{finished['analysis_id']}/weekly")
    assert by_id.status_code == 200
    assert by_id.get_json()['data']['totalThisWeek'] == 3


def test_weekly_stats_404s(client):
    assert client.get('/api/analyses/latest/weekly').status_code == 404
    assert client.get('/api/analyses/nope/weekly').status_code == 404


def test_analysis_path_traversal_blocked(client):
    assert client.get('/api/analyses/..%2F..%2Fetc%2Fpasswd').status_code == 404


def test_unknown_job(client):
    assert client.get('/api/jobs/nope').status_code == 404


def test_analyze_validation(client):
    assert client.post('/api/analyze', json={}).status_code == 400
    assert client.post('/api/analyze', json={'content': '  '}).status_code == 400
    assert client.post('/api/analyze',
                       json={'content': 'x?', 'provider': 'bogus'}).status_code == 400
    assert client.post('/api/analyze',
                       json={'content': 'x?', 'threshold': 2}).status_code == 400
    assert client.post('/api/analyze',
                       json={'content': 'x?', 'threshold': 'abc'}).status_code == 400


def test_health_reports_unreachable_ollama(client, monkeypatch):
    import requests as requests_module

    def refuse(*args, **kwargs):
        raise requests_module.ConnectionError('connection refused')

    monkeypatch.setattr(api_server.requests, 'get', refuse)
    body = client.get('/api/health').get_json()
    assert body['status'] == 'unavailable'
    assert body['ollama']['reachable'] is False
    assert 'ollama serve' in body['message']


def test_health_reports_missing_model(client, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {'models': [{'name': 'llama3:latest'}]}

    monkeypatch.setattr(api_server.requests, 'get', lambda *a, **k: FakeResponse())
    body = client.get('/api/health').get_json()
    assert body['status'] == 'degraded'
    assert body['ollama']['reachable'] is True
    assert body['ollama']['model_available'] is False


def test_health_ok(client, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {'models': [{'name': 'nomic-embed-text:latest'}]}

    monkeypatch.setattr(api_server.requests, 'get', lambda *a, **k: FakeResponse())
    body = client.get('/api/health').get_json()
    assert body['status'] == 'ok'
    assert body['ollama']['model_available'] is True


def test_ui_is_served(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/ui_kits/analyzer/index.html' in response.headers['Location']

    page = client.get('/ui_kits/analyzer/index.html')
    assert page.status_code == 200
    assert b'Question Analyzer' in page.data

    assert client.get('/ui_kits/analyzer/api.js').status_code == 200
    assert client.get('/styles.css').status_code == 200
