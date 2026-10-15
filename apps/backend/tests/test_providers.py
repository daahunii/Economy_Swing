from datetime import date, datetime, timezone

import pytest

from economy_swing.providers.fred import parse_table
from economy_swing.providers.toss import fetch_daily, parse_candles
from economy_swing.providers.http import ProviderError

def fred_html(rows, extra="", series="TEST", frequency="Daily"):
    return f'''<table><tr><th>Series ID</th><td>{series}</td></tr><tr><th>Frequency</th><td>{frequency}</td></tr><tr><th>Last Updated</th><td>2026-10-14 3:16 PM CDT</td></tr></table>
    <table id="data-table-observations">{''.join(f'<tr><th>{d}</th><td>{v}</td></tr>' for d,v in rows)}</table><div id="extra-rows">{extra}</div>'''

def test_fred_reads_deferred_rows_and_keeps_gaps_unfilled():
    body=fred_html([("2026-10-08","4.0"),("2026-10-09",".")],"#2026-10-12|4.1\n#2026-10-13|4.2\n#2026-10-16|5.0")
    points,updated=parse_table(body,"TEST",today=date(2026,10,15))
    assert [p["date"] for p in points]==["2026-10-08","2026-10-12","2026-10-13"]
    assert updated=="2026-10-14T15:16:00-05:00"

@pytest.mark.parametrize("body",[
    fred_html([("2026-10-08","4"),("2026-10-09","5")],series="WRONG"),
    fred_html([("2026-10-08","4"),("2026-10-09","nan")]),
    fred_html([("2026-10-08","4"),("2026-10-08","5")]),
    fred_html([("2026-10-08","4"),("2026-10-09","5")],frequency="Monthly"),
    '<html>access denied</html>',
])
def test_fred_rejects_unexpected_payloads(body):
    with pytest.raises(ProviderError):parse_table(body,"TEST",today=date(2026,10,15))

def test_candles_are_sorted_and_current_local_day_excluded():
    candles=[{"timestamp":"2026-10-15T00:00:00+09:00","closePrice":"103"},{"timestamp":"2026-10-14T00:00:00+09:00","closePrice":"102"},{"timestamp":"2026-10-13T00:00:00+09:00","closePrice":"100"}]
    points=parse_candles(candles,now=datetime(2026,10,15,10,tzinfo=timezone.utc))
    assert points==[{"date":"2026-10-13","value":100.0},{"date":"2026-10-14","value":102.0}]

def test_toss_pagination_passes_cursor_and_deduplicates(monkeypatch):
    from economy_swing.providers import toss
    calls=[]
    def fake_get(path,params):
        calls.append((path,dict(params)))
        if len(calls)==1:return {"candles":[{"timestamp":"2026-10-13T00:00:00+09:00","closePrice":"102"},{"timestamp":"2026-10-12T00:00:00+09:00","closePrice":"101"}],"nextBefore":"2026-10-12T00:00:00+09:00"}
        return {"candles":[{"timestamp":"2026-10-12T00:00:00+09:00","closePrice":"101"},{"timestamp":"2026-10-09T00:00:00+09:00","closePrice":"100"}],"nextBefore":None}
    monkeypatch.setattr(toss,"_get",fake_get)
    points=fetch_daily("091160",now=datetime(2026,10,15,tzinfo=timezone.utc))
    assert len(points)==3
    assert calls[1][1]["before"]=="2026-10-12T00:00:00+09:00"
    assert calls[0][1]["adjusted"]=="true"
    assert all(path=="/api/v1/candles" for path,_ in calls)

def test_brokerage_does_not_issue_tokens_or_call_orders(monkeypatch):
    with pytest.raises(ProviderError,match="토큰"):
        fetch_daily("SPY",now=datetime.now(timezone.utc))
