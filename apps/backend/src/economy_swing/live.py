"""Actual observations, isolated from demo fixtures and experimental demo scoring."""
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from .catalog import FRED_INDICATORS, SECTOR_PROXIES
from .content import TERMS
from .domain import event_study, percent_return
from .providers import fred, toss
from .providers.http import ProviderError
from .schemas import Dashboard, Indicator, Relationship, Sector, Study

_cache = {}
_cache_lock = threading.Lock()
_snapshot_lock = threading.Lock()
_snapshot = None
_snapshot_until = 0.0

def empty_study() -> Study:
    return Study(sample_count=0, average_return=None, median_return=None, average_excess=None, win_rate=None, excess_win_rate=None, worst_drawdown=None, events=[])

def clear_live_cache():
    global _snapshot, _snapshot_until
    with _cache_lock:
        _cache.clear()
    _snapshot = None
    _snapshot_until = 0

def cached_source(key, fetch, *, now):
    clock = time.monotonic()
    with _cache_lock:
        old = _cache.get(key)
        if old and clock < old["until"]:
            return old
    try:
        points, updated = fetch()
        result = dict(points=points, updated=updated, fetched_at=now.isoformat(), error=None, until=clock + 1800)
    except ProviderError as exc:
        result = dict(points=(old or {}).get("points", []), updated=(old or {}).get("updated"), fetched_at=(old or {}).get("fetched_at"), error=str(exc), until=clock + 60)
    with _cache_lock:
        _cache[key] = result
    return result

def observation_status(points, now, error):
    if not points:
        return "missing"
    age = (now.date() - datetime.fromisoformat(points[-1]["date"]).date()).days
    return "stale" if error or age > 7 else "fresh"

def change(points, count, unit):
    if len(points) <= count:
        return None
    start, end = points[-1-count]["value"], points[-1]["value"]
    if unit == "%":
        return round((end - start) * 100, 2)
    if start <= 0 or end <= 0:
        return None
    return round(percent_return(start, end), 2)

def fred_indicator(spec, now):
    result = cached_source("fred:" + spec["fred_id"], lambda: fred.fetch_series(spec["fred_id"]), now=now)
    points = result["points"]
    metadata = {k: v for k, v in spec.items() if k != "fred_id"}
    status = observation_status(points, now, result["error"])
    message = result["error"] or ("지표 발표 주기에 따른 지연 관측값입니다." if status == "fresh" else "최근 관측치가 오래되었습니다.")
    return Indicator(**metadata, source_url=f"https://fred.stlouisfed.org/series/{spec['fred_id']}", source_series_id=spec["fred_id"], value=points[-1]["value"] if points else None, series=points, change_1d=change(points, 1, spec["unit"]), change_5d=change(points, 5, spec["unit"]), change_20d=change(points, 20, spec["unit"]), change_unit="bp" if spec["unit"] == "%" else "%", observed_at=points[-1]["date"] if points else None, fetched_at=result["fetched_at"], source_updated_at=result["updated"], status=status, status_message=message)

def toss_series(symbol, now, market_indicator=False):
    return cached_source("toss:" + symbol, lambda: (toss.fetch_daily(symbol, now=now, market_indicator=market_indicator), None), now=now)

def toss_benchmark(id, name, symbol, market, unit, now, *, index=False):
    result = toss_series(symbol, now, index)
    points = result["points"]
    return Indicator(id=id, name=name, symbol=symbol, unit=unit, market=market, explanation="해당 시장의 흐름을 비교하기 위한 가격 기준입니다.", caution="완료된 일봉만 사용하며 배당 재투자 총수익률은 보장하지 않습니다." + (" SPY는 S&P 500 지수 자체가 아닌 ETF 대용 지표입니다." if symbol == "SPY" else ""), value=points[-1]["value"] if points else None, series=points, change_1d=change(points, 1, unit), change_5d=change(points, 5, unit), change_20d=change(points, 20, unit), change_unit="%", source_name="토스증권 Open API", source_url="https://developers.tossinvest.com/docs/market-data", source_series_id=symbol, observed_at=points[-1]["date"] if points else None, fetched_at=result["fetched_at"], status=observation_status(points, now, result["error"]), status_message=result["error"] or "당일 미확정 봉을 제외한 최근 일봉입니다.")

def study_from_series(driver, target, benchmark, direction, horizon):
    # Exact common dates only: never forward-fill future macro releases.
    maps = [{p.date: p.value for p in driver}, {p["date"]: p["value"] for p in target}, {p.date: p.value for p in benchmark}]
    dates = sorted(set(maps[0]) & set(maps[1]) & set(maps[2]))
    aligned = [[{"date": d, "value": mapping[d]} for d in dates] for mapping in maps]
    if len(dates) < horizon + 7:
        return empty_study(), None, None
    result = event_study(*aligned, direction, horizon, path_series=target)
    return Study(**result), dates[0], dates[-1]

def build_relationship(sector, driver, benchmark, horizon):
    unavailable = not sector.series or driver is None or not driver.series or benchmark is None or not benchmark.series
    if unavailable:
        study, start, end = empty_study(), None, None
    else:
        study, start, end = study_from_series(driver.series, [p.model_dump() for p in sector.series], benchmark.series, sector.direction, horizon)
    enough = start is not None
    status = "missing" if unavailable or not enough else "stale" if "stale" in (sector.status, driver.status, benchmark.status) else "fresh"
    return Relationship(id=sector.id, sector_id=sector.id, sector_name=sector.name, market=sector.market, driver_id=sector.driver_id, driver_name=driver.name if driver else sector.driver_id, direction=sector.direction, horizon=horizon, threshold=.5, study=study, status=status, status_message="변수·섹터·벤치마크의 실제 일봉 연결과 충분한 공통 관측치가 필요합니다." if status == "missing" else "최신 수정 자료 기반 탐색이며 당시 시점의 발표값 백테스트는 아닙니다.", period_start=start, period_end=end)

def build_live_dashboard():
    global _snapshot, _snapshot_until
    with _snapshot_lock:
        if _snapshot is not None and time.monotonic() < _snapshot_until:
            return _snapshot
        now = datetime.now(timezone.utc)
        with ThreadPoolExecutor(max_workers=5) as pool:
            indicators = list(pool.map(lambda spec: fred_indicator(spec, now), FRED_INDICATORS))
        has_toss = toss.configured()
        benchmarks = {}
        sector_results = {}
        if has_toss:
            for spec in [("sp500", "미국 시장 · SPY ETF 대용", "SPY", "US", "달러"), ("kospi", "코스피", "KOSPI", "KR", "pt")]:
                b = toss_benchmark(*spec, now, index=spec[0] == "kospi")
                indicators.append(b)
                benchmarks[spec[3]] = b
            with ThreadPoolExecutor(max_workers=3) as pool:
                results = list(pool.map(lambda spec: toss_series(spec[4], now), SECTOR_PROXIES))
            sector_results = {spec[0]: result for spec, result in zip(SECTOR_PROXIES, results)}
        lookup = {i.id: i for i in indicators}
        sectors, relationships = [], []
        for id, name, en, market, symbol, proxy_name, driver_id, direction in SECTOR_PROXIES:
            source = sector_results.get(id, {})
            points = source.get("points", [])
            benchmark = benchmarks.get(market)
            ret = change(points, 20, "price")
            # Benchmark must use exactly the same endpoints, never its own latest date.
            excess = None
            if ret is not None and benchmark:
                bmap = {p.date: p.value for p in benchmark.series}
                first, last = points[-21]["date"], points[-1]["date"]
                if first in bmap and last in bmap and bmap[first] > 0 and bmap[last] > 0:
                    excess = round(ret - percent_return(bmap[first], bmap[last]), 2)
            status = observation_status(points, now, source.get("error"))
            status_message = source.get("error") or ("실제 일봉으로 조회했습니다. 기회 점수 모델은 검증 전이므로 보류합니다." if points else "토스증권 백엔드 인증 토큰을 설정하면 실제 ETF 일봉을 조회합니다.")
            sector = Sector(id=id, name=name, english_name=en, market=market, driver_id=driver_id, direction=direction, score=None, components={}, return_20d=ret, excess_20d=excess, reason=f"{proxy_name}({symbol})를 산업의 대용 지표로 사용합니다. 실험용 데모 점수를 실제 데이터에 적용하지 않습니다.", risk="대용 ETF의 편입·보수·환노출과 배당 처리 차이가 있습니다. 상관관계는 인과관계를 뜻하지 않습니다.", series=points, study=empty_study(), source_name="토스증권 Open API", source_url="https://developers.tossinvest.com/docs/market-data", proxy_symbol=symbol, proxy_name=proxy_name, benchmark_name="SPY ETF (USD)" if market == "US" else "KOSPI 가격지수 (KRW)", observed_at=points[-1]["date"] if points else None, status=status, status_message=status_message)
            relation = build_relationship(sector, lookup.get(driver_id), benchmark, 20)
            sector.study = relation.study
            sectors.append(sector)
            relationships.append(relation)
        issues = [f"{i.name}: {i.status_message}" for i in indicators if i.status != "fresh"]
        issues += [f"{s.name} ({s.proxy_symbol}): {s.status_message}" for s in sectors if has_toss and s.status != "fresh"]
        if not has_toss:
            issues.append("토스증권 인증 토큰 미설정: 미국 시장 ETF·한국 지수·섹터 시세는 연결 대기 중입니다.")
        valid_dates = [i.observed_at for i in indicators if i.observed_at]
        count = sum(i.value is not None for i in indicators)
        _snapshot = Dashboard(data_mode="live", as_of=now.isoformat(), generated_at=now.isoformat(), observed_through=max(valid_dates) if valid_dates else None, source="FRED 공식 공개 관측자료 · 토스증권 Open API(설정 시)", model_version="live-research-v1-unscored", weights={}, calendar_note="실제 관측일만 사용합니다. 지표·거래소마다 휴장일과 발표일이 다르며 결측일은 채우지 않습니다.", limitations=["실시간 체결가가 아닌 발표 주기에 따른 거시 관측값과 확정 일봉입니다.", "지표의 최신 관측일·공급자 갱신 시각·수집 시각은 서로 다릅니다.", "실제 데이터의 기회 점수는 모델 검증 전까지 산출하지 않습니다.", "과거 관계는 최신 수정 자료·공통 관측일 기반 탐색이며 당시 발표 정보 기반 백테스트가 아닙니다.", "거래비용·환전·세금과 배당 재투자를 반영한 포트폴리오 성과가 아닙니다.", "토스 토큰은 서버 환경변수로만 관리하며 만료 시 재설정이 필요합니다.", "데이터 캐시는 실행 인스턴스 단위입니다. 영구 DB와 예약 수집은 미연동입니다."], indicators=indicators, sectors=sectors, relationships=relationships, terms=TERMS, issues=issues, live_indicator_count=count, live_sector_count=sum(bool(s.series) for s in sectors), toss_status="configured" if has_toss else "not-configured")
        _snapshot_until = time.monotonic() + (180 if count else 30)
        return _snapshot

def live_relationship(sector_id, horizon):
    data = build_live_dashboard()
    sector = next(s for s in data.sectors if s.id == sector_id)
    driver = next((i for i in data.indicators if i.id == sector.driver_id), None)
    benchmark = next((i for i in data.indicators if i.id == ("sp500" if sector.market == "US" else "kospi")), None)
    return build_relationship(sector, driver, benchmark, horizon)
