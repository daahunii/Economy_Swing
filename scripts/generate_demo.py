"""Generate a deterministic, isolated synthetic fixture, never live market data."""
import json
import math
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
dates = []
day = date(2026, 10, 14)
while len(dates) < 520:
    if day.weekday() < 5:
        dates.append(day.isoformat())
    day -= timedelta(days=1)
dates.reverse()

def points(base, trend, wave, phase):
    return [{"date": d, "value": round(base * (1 + trend * i + wave * math.sin(i / 18 + phase) + wave / 2 * math.sin(i / 7 + phase)), 4)} for i, d in enumerate(dates)]

indicators = []
definitions = [
    ("us10y", "미국 10년 국채금리", "US 10Y", "%", "US", 4.3, -.00015, .08, 0, "금리가 내려가면 미래 이익의 현재 가치를 계산할 때 적용하는 할인율 부담이 줄 수 있습니다.", "금리 하락이 경기 악화를 반영하면 기업 실적 우려가 더 클 수 있습니다."),
    ("us2y", "미국 2년 국채금리", "US 2Y", "%", "US", 4.5, -.0002, .07, .3, "단기 국채금리는 통화정책 기대를 살펴보는 지표입니다.", "정책금리 자체와 시장이 예상하는 정책 경로는 다릅니다."),
    ("usdkrw", "달러·원 환율", "USD/KRW", "원", "KR", 1300, .00007, .025, 1, "환율 상승은 달러 대비 원화 약세를 뜻하며 수출 기업의 원화 매출에 영향을 줄 수 있습니다.", "원재료 수입 비용, 환헤지, 생산 위치도 함께 봐야 합니다."),
    ("dxy", "달러 인덱스", "DXY", "pt", "US", 102, .00002, .022, .8, "달러가 주요 통화 대비 어느 정도 강한지 보여줍니다.", "각 국가의 금리와 성장 차이를 함께 봐야 합니다."),
    ("wti", "서부텍사스산 원유", "WTI", "달러", "ALL", 74, -.00008, .1, 2, "유가는 에너지 기업 매출과 운송·제조업 비용에 영향을 줍니다.", "수요 감소와 공급 증가에 의한 하락은 의미가 다릅니다."),
    ("gold", "금", "GOLD", "달러", "ALL", 2200, .0003, .035, .2, "금은 금리·달러·위험 회피 수요의 영향을 함께 받습니다.", "안전자산 수요만으로 가격 방향을 확정할 수 없습니다."),
    ("copper", "구리", "COPPER", "달러", "ALL", 4.1, .0001, .065, 1.8, "구리는 산업 수요와 원자재 비용을 살펴보는 지표입니다.", "공급 차질로 오르는 경우 경기 개선 신호와 구분해야 합니다."),
    ("vix", "미국 변동성 지수", "VIX", "pt", "US", 20, -.0001, .22, 2.8, "옵션 가격에 반영된 시장의 예상 변동성을 보여줍니다.", "낮다고 위험이 없거나 상승이 보장되는 것은 아닙니다."),
    ("sp500", "미국 시장 벤치마크", "S&P 500", "pt", "US", 5000, .0005, .04, .5, "미국 섹터 성과와 비교할 시장 기준입니다.", "이 화면에서는 실제 지수가 아닌 합성 경로를 사용합니다."),
    ("kospi", "한국 시장 벤치마크", "KOSPI", "pt", "KR", 2500, .0003, .055, 1.5, "한국 섹터 성과와 비교할 시장 기준입니다.", "이 화면에서는 실제 지수가 아닌 합성 경로를 사용합니다."),
]
for id, name, symbol, unit, market, base, trend, wave, phase, explanation, caution in definitions:
    indicators.append(dict(id=id, name=name, symbol=symbol, unit=unit, market=market, explanation=explanation, caution=caution, series=points(base,trend,wave,phase)))

names_us = [("바이오", "Biotechnology", "us10y", -1), ("반도체", "Semiconductors", "us10y", -1), ("전력 인프라", "Power infrastructure", "copper", 1), ("기술", "Technology", "vix", -1), ("헬스케어", "Healthcare", "us10y", -1), ("금융", "Financials", "us2y", 1), ("에너지", "Energy", "wti", 1), ("유틸리티", "Utilities", "us10y", -1), ("리츠", "Real estate", "us10y", -1), ("산업재", "Industrials", "copper", 1)]
names_kr = [("반도체", "Semiconductors", "usdkrw", 1), ("자동차", "Automobiles", "usdkrw", 1), ("바이오", "Biotechnology", "us10y", -1), ("방산", "Defense", "usdkrw", 1), ("조선", "Shipbuilding", "usdkrw", 1), ("원전", "Nuclear power", "wti", 1), ("전력기기", "Power equipment", "copper", 1), ("2차전지", "Batteries", "us10y", -1), ("화학", "Chemicals", "wti", -1), ("금융", "Financials", "us2y", 1)]
sectors = []
for market, names in [("US",names_us),("KR",names_kr)]:
    for i,(name,en,driver,direction) in enumerate(names):
        sectors.append(dict(id=f"{market.lower()}-{i}",name=name,english_name=en,market=market,driver_id=driver,direction=direction,series=points(100,.0003+.00005*(i%5),.07+i*.004,i*.41+(0 if market=="US" else .8))))

payload = {"data_mode":"demo", "as_of": "2026-10-14T23:59:00Z", "calendar_note":"합성 평일 캘린더이며 실제 거래소 휴장일은 반영하지 않습니다.", "indicators":indicators, "sectors":sectors, "scoring":json.loads((ROOT/"config/scoring/sector-mvp-v1.json").read_text())}
target=ROOT/"apps/backend/src/economy_swing/fixtures/demo.json"
target.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")))
print(f"Wrote deterministic demo: {len(dates)} observations, {len(indicators)} indicators, {len(sectors)} sectors")
