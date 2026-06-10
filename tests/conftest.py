import pytest


@pytest.fixture(autouse=True)
def isolated_topic_bank(tmp_path, monkeypatch):
    """Every test gets its own topic bank — never the repo's real one."""
    monkeypatch.setenv('TOPIC_BANK_PATH', str(tmp_path / 'topic_bank.json'))
