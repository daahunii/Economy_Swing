"""Versioned educational content, independent of demo or live data."""
from .schemas import Term

TERMS = [
    Term(id="yield",title="국채금리",category="거시경제",definition="정부에 돈을 빌려주는 채권에 시장이 요구하는 수익률입니다.",example="금리가 낮아지면 성장 기업의 미래 이익에 적용하는 할인율 부담이 줄 수 있습니다.",caution="경기 침체 우려 때문에 금리가 내려갈 수도 있습니다. 주가 상승을 보장하지 않습니다."),
    Term(id="excess",title="초과 수익률",category="과거 검증",definition="같은 기간 대상 수익률에서 시장 벤치마크 수익률을 뺀 값입니다.",example="섹터 +8%, 시장 +5%이면 초과 수익률은 +3%p입니다.",caution="통화·배당·기간 기준이 같아야 비교할 수 있습니다."),
    Term(id="win",title="역사적 승률",category="과거 검증",definition="유효한 과거 이벤트 중 수익률이 양수였던 비율입니다.",example="유효한 10개 사건 중 6개가 상승했다면 승률은 60%입니다.",caution="미래 상승 확률이 아닙니다. 표본 크기와 중첩을 함께 확인해야 합니다."),
    Term(id="drawdown",title="최대 낙폭 · MDD",category="위험",definition="관측 구간의 누적 고점에서 가장 크게 하락한 비율입니다.",example="100에서 120으로 오른 뒤 90까지 하락했다면 고점 대비 낙폭은 -25%입니다.",caution="시작과 끝 가격만으로 계산할 수 없습니다. 개별 사건의 낙폭과 포트폴리오 낙폭은 다릅니다."),
    Term(id="bp",title="bp와 %p",category="거시경제",definition="두 비율의 차이는 %p로 표시하며 1%p는 100bp입니다.",example="국채금리가 4.0%에서 3.8%로 낮아지면 -0.2%p, 즉 -20bp입니다.",caution="비율의 차이와 상대 변화율(%)을 혼동하지 않아야 합니다."),
    Term(id="score",title="기회 점수",category="모델",definition="정해진 모델에서 리서치 순서를 비교하기 위한 상대적 점수입니다.",example="초기 모델은 거시 35%, 과거 관계 40%, 모멘텀 25%를 합산합니다.",caution="84점이 상승 확률 84%라는 뜻은 아닙니다. 예시 가중치는 합성 자료 실험용이며 실제 자료의 점수는 검증 전까지 보류합니다."),
    Term(id="per",title="PER · 주가수익비율",category="기업 재무",definition="주가가 연간 주당순이익의 몇 배인지 보여주는 지표입니다.",example="주가 20,000원, 주당순이익 1,000원이면 PER은 20배입니다.",caution="적자 기업에는 일반적인 해석이 어렵습니다. 낮다고 저평가로 확정할 수 없습니다."),
    Term(id="roe",title="ROE · 자기자본이익률",category="기업 재무",definition="주주의 자본에 비해 회사가 얼마나 이익을 냈는지 나타냅니다.",example="평균 자기자본 1조 원으로 순이익 1,000억 원을 냈다면 ROE는 10%입니다.",caution="부채 증가나 자본 감소로도 높아질 수 있습니다. 부채와 현금흐름을 함께 봐야 합니다."),
]
