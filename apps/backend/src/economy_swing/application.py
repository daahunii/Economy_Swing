"""Read-only demo use cases; the fixture repository is isolated from production."""
import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from .domain import bounded, event_study, percent_return, weighted_score
from .schemas import Dashboard, Indicator, Relationship, Sector, Term

from .content import TERMS

@lru_cache(maxsize=1)
def fixture():
    return json.loads((Path(__file__).parent/"fixtures/demo.json").read_text())

def demo_relationship(sector_id: str, horizon: int) -> Relationship:
    data=fixture()
    sector=next(s for s in data["sectors"] if s["id"]==sector_id)
    driver=next(i for i in data["indicators"] if i["id"]==sector["driver_id"])
    benchmark=next(i for i in data["indicators"] if i["id"]==("sp500" if sector["market"]=="US" else "kospi"))
    return Relationship(id=sector_id,sector_id=sector_id,sector_name=sector["name"],market=sector["market"],driver_id=driver["id"],driver_name=driver["name"],direction=sector["direction"],horizon=horizon,threshold=.5,study=event_study(driver["series"],sector["series"],benchmark["series"],sector["direction"],horizon))

@lru_cache(maxsize=1)
def build_demo_dashboard() -> Dashboard:
    data=fixture()
    indicators=[]
    for item in data["indicators"]:
        series=item["series"]
        def change(n):
            return round((series[-1]["value"]-series[-1-n]["value"])*100,2) if item["unit"]=="%" else round(percent_return(series[-1-n]["value"],series[-1]["value"]),2)
        indicators.append(Indicator(**item,value=series[-1]["value"],change_1d=change(1),change_5d=change(5),change_20d=change(20),change_unit="bp" if item["unit"]=="%" else "%"))
    lookup={i.id:i for i in indicators}
    sectors=[]
    relations=[]
    for item in data["sectors"]:
        relation=demo_relationship(item["id"],20)
        relations.append(relation)
        series=item["series"]
        ret=percent_return(series[-21]["value"],series[-1]["value"])
        base=lookup["sp500" if item["market"]=="US" else "kospi"]
        benchmark_ret=percent_return(base.series[-21].value,base.series[-1].value)
        driver=lookup[item["driver_id"]]
        raw_driver=percent_return(driver.series[-21].value,driver.series[-1].value)
        components={"macro":bounded(50+raw_driver*item["direction"]*6),"momentum":bounded(50+(ret-benchmark_ret)*4)}
        eligible=relation.study.sample_count>=data["scoring"]["minimum_events"]
        if eligible:
            components["historical"]=bounded(50+(relation.study.average_excess or 0)*5)
        score=weighted_score(components,data["scoring"]["weights"]) if eligible else None
        sectors.append(Sector(**item,score=score,components=components,return_20d=round(ret,2),excess_20d=round(ret-benchmark_ret,2),study=relation.study,reason=f"{driver.name} {'상승' if item['direction']>0 else '하락'} 조건을 과거 합성 경로와 비교했습니다.",risk=driver.caution))
    sectors.sort(key=lambda s:(s.score is not None,s.score or 0),reverse=True)
    return Dashboard(data_mode="demo",as_of=data["as_of"],generated_at=datetime.now(timezone.utc).isoformat(),source="합성 fixture · 실제 시장 데이터 아님",model_version=data["scoring"]["version"],weights=data["scoring"]["weights"],calendar_note=data["calendar_note"],limitations=["모든 가격·금리·점수는 합성 예시이며 투자 판단에 사용할 수 없습니다.","실제 공급자·DB·정기 수집·당시 시점 데이터는 아직 연결하지 않았습니다.","이벤트는 5관측치 상대 변화 0.5% 임계값 돌파로 정의하며 다음 관측치 종가에 진입합니다.","실제 거래소 휴장일·세금·거래비용·배당·환전은 반영하지 않습니다.","과거 관계는 관찰 결과이며 인과관계나 미래 수익을 보장하지 않습니다."],indicators=indicators,sectors=sectors,relationships=relations,terms=TERMS)


def data_mode() -> str:
    mode = os.getenv("ECONOMY_DATA_MODE", "live").lower()
    if mode not in ("live", "demo"):
        raise ValueError("ECONOMY_DATA_MODE must be live or demo")
    return mode


def build_dashboard() -> Dashboard:
    if data_mode() == "demo":
        return build_demo_dashboard()
    from .live import build_live_dashboard
    return build_live_dashboard()


def relationship(sector_id: str, horizon: int) -> Relationship:
    if data_mode() == "demo":
        return demo_relationship(sector_id, horizon)
    from .live import live_relationship
    return live_relationship(sector_id, horizon)
