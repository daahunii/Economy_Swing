import pytest

@pytest.fixture(autouse=True)
def isolate_provider_environment(monkeypatch):
    """Unit tests never call a real brokerage or network implicitly."""
    monkeypatch.setenv("ECONOMY_DATA_MODE", "demo")
    monkeypatch.delenv("TOSS_ACCESS_TOKEN", raising=False)
