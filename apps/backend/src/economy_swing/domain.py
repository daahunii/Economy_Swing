"""Pure calculations: no HTTP, provider calls, or database dependencies."""
from statistics import mean, median

def percent_return(start: float, end: float) -> float:
    if start <= 0 or end <= 0:
        raise ValueError("Prices must be positive")
    return (end / start - 1) * 100

def maximum_drawdown(prices: list[float]) -> float:
    if not prices or any(p <= 0 for p in prices):
        raise ValueError("A positive price path is required")
    peak, worst = prices[0], 0.0
    for price in prices:
        peak = max(peak, price)
        worst = min(worst, percent_return(peak, price))
    return worst

def weighted_score(components: dict[str, float], weights: dict[str, float]) -> float:
    if set(components) != set(weights) or abs(sum(weights.values()) - 1) > 1e-9:
        raise ValueError("Complete components and weights summing to 1 required")
    if any(not 0 <= v <= 100 for v in components.values()) or any(w < 0 for w in weights.values()):
        raise ValueError("Invalid score or weight")
    return round(sum(components[k] * weights[k] for k in weights), 1)

def bounded(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 1)

def event_study(driver, target, benchmark, direction: int, horizon: int, threshold: float = .5):
    """5-observation driver return crosses threshold; next-close entry.

    Independent non-overlapping windows, no incomplete windows, aligned dates only.
    This fixture study is explicitly not a point-in-time macro release backtest.
    """
    if direction not in (-1,1) or horizon < 1 or threshold <= 0:
        raise ValueError("Invalid event definition")
    if [p["date"] for p in driver] != [p["date"] for p in target] or [p["date"] for p in target] != [p["date"] for p in benchmark]:
        raise ValueError("Aligned observations required")
    events=[]
    prior=False
    next_allowed=5
    for i in range(5,len(driver)):
        signal=percent_return(driver[i-5]["value"],driver[i]["value"])*direction>=threshold
        crossing=signal and not prior
        prior=signal
        entry=i+1
        end=entry+horizon
        if not crossing or i<next_allowed or end>=len(target):
            continue
        ret=percent_return(target[entry]["value"],target[end]["value"])
        base=percent_return(benchmark[entry]["value"],benchmark[end]["value"])
        path=[p["value"] for p in target[entry:end+1]]
        events.append(dict(date=driver[i]["date"],entry_date=target[entry]["date"],exit_date=target[end]["date"],return_pct=round(ret,3),benchmark_return_pct=round(base,3),excess_return_pp=round(ret-base,3),max_drawdown_pct=round(maximum_drawdown(path),3)))
        next_allowed=end+1
    if not events:
        return dict(sample_count=0,average_return=None,median_return=None,average_excess=None,win_rate=None,excess_win_rate=None,worst_drawdown=None,events=[])
    return dict(sample_count=len(events),average_return=round(mean(e["return_pct"] for e in events),2),median_return=round(median(e["return_pct"] for e in events),2),average_excess=round(mean(e["excess_return_pp"] for e in events),2),win_rate=round(mean(e["return_pct"]>0 for e in events)*100,1),excess_win_rate=round(mean(e["excess_return_pp"]>0 for e in events)*100,1),worst_drawdown=min(e["max_drawdown_pct"] for e in events),events=events)
