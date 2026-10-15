from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from economy_swing import live
from economy_swing.api import app
from economy_swing.providers.http import ProviderError

def mock_observations():
    today=datetime.now(timezone.utc).date()
    return [{"date":(today-timedelta(days=40-i)).isoformat(),"value":100+i} for i in range(40)]

def test_live_mode_contains_no_demo_scores_or_prices(monkeypatch):
    monkeypatch.setenv("ECONOMY_DATA_MODE","live")
    monkeypatch.setattr(live.fred,"fetch_series",lambda id:(mock_observations(),None))
    live.clear_live_cache()
    data=TestClient(app).get("/api/v1/dashboard").json()
    assert data["data_mode"]=="live"
    assert data["live_indicator_count"]==10
    assert data["live_sector_count"]==0
    assert all(s["score"] is None and not s["series"] for s in data["sectors"])
    assert all(s["return_20d"] is None for s in data["sectors"])
    assert all(i["source_url"].startswith("https://fred.stlouisfed.org/series/") for i in data["indicators"])
    relation=TestClient(app).get("/api/v1/relationships/us-0?horizon=20").json()
    assert relation["status"]=="missing"
    assert relation["study"]["average_return"] is None
    live.clear_live_cache()

def test_failed_source_stays_missing_without_fixture_fallback(monkeypatch):
    def fail(id):raise ProviderError("network","공급자 연결 실패")
    monkeypatch.setattr(live.fred,"fetch_series",fail)
    live.clear_live_cache()
    data=live.build_live_dashboard()
    assert data.data_mode=="live"
    assert data.live_indicator_count==0
    assert all(i.value is None and not i.series and i.status=="missing" for i in data.indicators)
    assert len(data.issues)>=10
    live.clear_live_cache()

def test_cache_failure_retains_last_good_value_with_stale_status():
    live.clear_live_cache()
    now=datetime.now(timezone.utc)
    points=mock_observations()
    live.cached_source("test",lambda:(points,None),now=now)
    live._cache["test"]["until"]=0
    def fail():raise ProviderError("network","공급자 연결 실패")
    result=live.cached_source("test",fail,now=now+timedelta(hours=1))
    assert result["points"]==points
    assert result["fetched_at"]==now.isoformat()
    assert live.observation_status(result["points"],now,result["error"])=="stale"
    live.clear_live_cache()

def test_model_unvalidated_even_with_successful_toss_prices(monkeypatch):
    monkeypatch.setenv("TOSS_ACCESS_TOKEN","unit-test-only")
    monkeypatch.setattr(live.fred,"fetch_series",lambda id:(mock_observations(),None))
    monkeypatch.setattr(live.toss,"fetch_daily",lambda *args,**kwargs:mock_observations())
    live.clear_live_cache()
    data=live.build_live_dashboard()
    assert data.live_sector_count==14
    assert all(s.score is None for s in data.sectors)
    assert all(s.return_20d is not None for s in data.sectors)
    assert all(abs(s.excess_20d or 0)<.01 for s in data.sectors)
    live.clear_live_cache()
