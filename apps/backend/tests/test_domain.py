import pytest
from economy_swing.domain import percent_return, maximum_drawdown, weighted_score, event_study

def series(values):
    return [{"date":f"day-{i:02}","value":v} for i,v in enumerate(values)]

def test_return_and_drawdown_use_different_bases():
    assert percent_return(100,90)==pytest.approx(-10)
    assert maximum_drawdown([100,120,90,110])==pytest.approx(-25)

@pytest.mark.parametrize("start,end",[(0,100),(100,-1)])
def test_invalid_price_is_not_a_zero_return(start,end):
    with pytest.raises(ValueError):percent_return(start,end)

def test_weighted_score_rejects_missing_inputs():
    assert weighted_score({"macro":80,"history":60},{"macro":.25,"history":.75})==65
    with pytest.raises(ValueError):weighted_score({"macro":80},{"macro":.25,"history":.75})

def test_events_enter_next_close_and_exclude_incomplete_windows():
    driver=series([100]*5+[102]*6+[100]*6+[104]*3)
    target=series([100+i*2 for i in range(20)])
    benchmark=series([100+i for i in range(20)])
    result=event_study(driver,target,benchmark,1,3,1)
    assert result["sample_count"]==1  # last trigger lacks a complete future window
    event=result["events"][0]
    assert event["date"]=="day-05"
    assert event["entry_date"]=="day-06"
    assert event["exit_date"]=="day-09"
    assert event["return_pct"]==pytest.approx((118/112-1)*100,abs=.001)
    assert event["excess_return_pp"]==pytest.approx(((118/112)-(109/106))*100,abs=.001)

def test_misaligned_dates_are_rejected():
    a=series([100]*20)
    b=series([100]*20);b[5]["date"]="different"
    with pytest.raises(ValueError):event_study(a,b,a,1,5)

def test_no_events_have_null_statistics():
    a=series([100]*20)
    r=event_study(a,a,a,1,5)
    assert r["sample_count"]==0
    assert r["average_return"] is None
    assert r["win_rate"] is None
