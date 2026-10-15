"""Read-only demo use cases; the fixture repository is isolated from production."""
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from .domain import bounded, event_study, percent_return, weighted_score
from .schemas import Dashboard, Indicator, Relationship, Sector, Term

TERMS = [
    Term(id="yield",title="국채금리",category="거시경제",definition="정부에 돈을 빌려주는 채권에 시장이 요구하는 수익률입니다.",example="금리가 낮아지면 성장 기업의 미래 이익에 적용하는 할인율 부담이 줄 수 있습니다.",caution="경기 침체 우려 때문에 금리가 내려갈 수도 있습니다. 주가 상승을 보장하지 않습니다."),
    Term(id="excess",title="초과 수익률",category="과거 검증",definition="같은 기간 대상 수익률에서 시장 벤치마크 수익률을 뺀 값입니다.",example="섹터 +8%, 시장 +5%이면 초과 수익률은 +3%p입니다.",caution="통화·배당·기간 기준이 같아야 비교할 수 있습니다."),
    Term(id="win",title="역사적 승률",category="과거 검증",definition="유효한 과거 이벤트 중 수익률이 양수였던 비율입니다.",example="유효한 10개 사건 중 6개가 상승했다면 승률은 60%입니다.",caution="미래 상승 확률이 아닙니다. 표본 크기와 중첩을 함께 확인해야 합니다."),
    Term(id="drawdown",title="최대 낙폭 · MDD",category="위험",definition="관측 구간의 누적 고점에서 가장 크게 하락한 비율입니다.",example="100에서 120으로 오른 뒤 90까지 하락했다면 고점 대비 낙폭은 -25%입니다.",caution="시작과 끝 가격만으로 계산할 수 없습니다. 개별 사건의 낙폭과 포트폴리오 낙폭은 다릅니다."),
    Term(id="bp",title="bp와 %p",category="거시경제",definition="두 비율의 차이는 %p로 표시하며 1%p는 100bp입니다.",example="국채금리가 4.0%에서 3.8%로 낮아지면 -0.2%p, 즉 -20bp입니다.",caution="비율의 차이와 상대 변화율(%)을 혼동하지 않아야 합니다."),
    Term(id="score",title="기회 점수",category="모델",definition="정해진 모델에서 리서치 순서를 비교하기 위한 상대적 점수입니다.",example="초기 모델은 거시 35%, 과거 관계 40%, 모멘텀 25%를 합산합니다.",caution="84점이 상승 확률 84%라는 뜻은 아닙니다. 현재 모델은 합성 자료용 실험 모델입니다."),
    Term(id="per",title="PER · 주가수익비율",category="기업 재무",definition="주가가 연간 주당순이익의 몇 배인지 보여주는 지표입니다.",example="주가 20,000원, 주당순이익 1,000원이면 PER은 20배입니다.",caution="적자 기업에는 일반적인 해석이 어렵습니다. 낮다고 저평가로 확정할 수 없습니다."),
    Term(id="roe",title="ROE · 자기자본이익률",category="기업 재무",definition="주주의 자본에 비해 회사가 얼마나 이익을 냈는지 나타냅니다.",example="평균 자기자본 1조 원으로 순이익 1,000억 원을 냈다면 ROE는 10%입니다.",caution="부채 증가나 자본 감소로도 높아질 수 있습니다. 부채와 현금흐름을 함께 봐야 합니다."),
]

@lru_cache(maxsize=1)
def fixture():
    return json.loads((Path(__file__).parent/"fixtures/demo.json").read_text())

def relationship(sector_id: str, horizon: int) -> Relationship:
    data=fixture()
    sector=next(s for s in data["sectors"] if s["id"]==sector_id)
    driver=next(i for i in data["indicators"] if i["id"]==sector["driver_id"])
    benchmark=next(i for i in data["indicators"] if i["id"]==("sp500" if sector["market"]=="US" else "kospi"))
    return Relationship(id=sector_id,sector_id=sector_id,sector_name=sector["name"],market=sector["market"],driver_id=driver["id"],driver_name=driver["name"],direction=sector["direction"],horizon=horizon,threshold=.5,study=event_study(driver["series"],sector["series"],benchmark["series"],sector["direction"],horizon))

@lru_cache(maxsize=1)
def build_dashboard() -> Dashboard:
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
        relation=relationship(item["id"],20)
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
    return Dashboard(as_of=data["as_of"],generated_at=datetime.now(timezone.utc).isoformat(),source="합성 fixture · 실제 시장 데이터 아님",model_version=data["scoring"]["version"],weights=data["scoring"]["weights"],calendar_note=data["calendar_note"],limitations=["모든 가격·금리·점수는 합성 예시이며 투자 판단에 사용할 수 없습니다.","실제 공급자·DB·정기 수집·당시 시점 데이터는 아직 연결하지 않았습니다.","이벤트는 5관측치 상대 변화 0.5% 임계값 돌파로 정의하며 다음 관측치 종가에 진입합니다.","실제 거래소 휴장일·세금·거래비용·배당·환전은 반영하지 않습니다.","과거 관계는 관찰 결과이며 인과관계나 미래 수익을 보장하지 않습니다."],indicators=indicators,sectors=sectors,relationships=relations,terms=TERMS)
