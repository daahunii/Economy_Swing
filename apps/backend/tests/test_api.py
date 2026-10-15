from fastapi.testclient import TestClient
from economy_swing.api import app
from economy_swing.application import build_dashboard

client=TestClient(app)

def test_demo_contract_and_sector_coverage():
    r=client.get("/api/v1/dashboard")
    assert r.status_code==200
    data=r.json()
    assert data["data_mode"]=="demo"
    assert len(data["indicators"])==10
    assert len(data["sectors"])==20
    assert all(s["confidence"]=="low" for s in data["sectors"])
    assert r.headers["X-Request-ID"]
    assert len(client.get("/api/v1/sectors?market=KR").json())==10

def test_bad_filter_and_missing_resource_have_structured_errors():
    for url,status in [("/api/v1/sectors?market=BAD",422),("/api/v1/relationships/us-0?horizon=999",422),("/api/v1/sectors/invalid",404)]:
        r=client.get(url)
        assert r.status_code==status
        assert r.json()["request_id"]
        assert r.json()["code"]

def test_study_is_reproducible_and_events_do_not_overlap():
    url="/api/v1/relationships/us-0?horizon=20"
    assert client.get(url).json()==client.get(url).json()
    events=client.get(url).json()["study"]["events"]
    assert len(events)>0
    for earlier,later in zip(events,events[1:]):
        assert earlier["exit_date"]<later["date"]
    assert all(e["date"]<e["entry_date"]<e["exit_date"] for e in events)

def test_each_eligible_score_matches_component_contribution():
    data=build_dashboard()
    for s in data.sectors:
        if s.score is not None:
            assert s.score==round(sum(s.components[k]*w for k,w in data.weights.items()),1)
        else:
            assert s.study.sample_count<3
