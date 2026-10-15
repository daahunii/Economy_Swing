"""Reviewed identifiers and source attribution, never market observations."""

FED = "미국 연방준비제도 / FRED"
EIA = "미국 에너지정보청(EIA) / FRED"

FRED_INDICATORS = [
    dict(id="us10y", name="미국 10년 국채금리", symbol="US 10Y", unit="%", market="US", fred_id="DGS10", source_name=FED, explanation="장기 자금 조달 비용과 미래 이익에 적용하는 할인율을 살펴보는 지표입니다.", caution="경기 악화로 금리가 하락할 수 있어 성장주 상승을 단정할 수 없습니다."),
    dict(id="us2y", name="미국 2년 국채금리", symbol="US 2Y", unit="%", market="US", fred_id="DGS2", source_name=FED, explanation="시장이 예상하는 단기 통화정책 경로를 살펴볼 수 있습니다.", caution="정책금리 자체와 시장이 예상하는 정책 경로는 서로 다릅니다."),
    dict(id="usdkrw", name="달러·원 환율", symbol="USD/KRW", unit="원/달러", market="KR", fred_id="DEXKOUS", source_name=FED, explanation="1달러를 사는 데 필요한 원화입니다. 상승하면 달러 대비 원화 약세를 뜻합니다.", caution="FRED의 뉴욕 정오 환율로 한국 시장 종가나 실시간 환율과 다릅니다."),
    dict(id="dollar_broad", name="미국 광의 달러 지수", symbol="BROAD USD", unit="pt", market="US", fred_id="DTWEXBGS", source_name=FED, explanation="여러 무역 상대국 통화 대비 달러의 가치를 보여주는 무역가중 지수입니다.", caution="ICE의 DXY와 다른 지수입니다. 두 값을 직접 비교하지 마세요."),
    dict(id="wti", name="WTI 현물유가", symbol="WTI SPOT", unit="달러/배럴", market="ALL", fred_id="DCOILWTICO", source_name=EIA, explanation="미국 쿠싱 지역의 WTI 현물 가격입니다. 에너지 매출과 운송·제조 비용에 영향을 줍니다.", caution="WTI 선물 가격과 다릅니다. 유가 변화의 수요·공급 원인을 함께 확인해야 합니다."),
    dict(id="brent", name="브렌트 현물유가", symbol="BRENT SPOT", unit="달러/배럴", market="ALL", fred_id="DCOILBRENTEU", source_name=EIA, explanation="유럽 브렌트 현물 가격으로 에너지 시장의 지역별 차이를 살펴봅니다.", caution="선물 가격과 다르며 공급 경로·운송 비용의 영향을 받습니다."),
    dict(id="natgas", name="헨리허브 천연가스", symbol="HENRY HUB", unit="달러/MMBtu", market="ALL", fred_id="DHHNGSP", source_name=EIA, explanation="미국 헨리허브의 천연가스 현물 가격입니다.", caution="한국의 LNG 도입가격과 다릅니다. 지역·계절·운송 비용을 함께 봐야 합니다."),
    dict(id="usfed", name="미국 실효 연방기금금리", symbol="FED FUNDS", unit="%", market="US", fred_id="DFF", source_name=FED, explanation="실제 연방기금 거래를 바탕으로 한 일별 금리입니다.", caution="연준이 발표하는 정책금리 목표 범위의 상단·하단과 구분해야 합니다."),
    dict(id="vix", name="미국 변동성 지수", symbol="VIX", unit="pt", market="US", fred_id="VIXCLS", source_name="Cboe / FRED · Copyright Cboe, 출처 표시 조건", explanation="옵션 가격에 반영된 미국 주식시장의 단기 예상 변동성을 나타냅니다.", caution="지연된 일별 종가입니다. 변동성이 낮아도 손실 위험이 없다는 뜻은 아닙니다."),
    dict(id="usdjpy", name="달러·엔 환율", symbol="USD/JPY", unit="엔/달러", market="ALL", fred_id="DEXJPUS", source_name=FED, explanation="1달러를 사는 데 필요한 엔화입니다. 상승하면 달러 대비 엔화 약세를 뜻합니다.", caution="뉴욕 정오 기준 환율이며 실시간 시세가 아닙니다."),
]

# Deliberately start with reviewed proxies. GRID includes non-US companies.
SECTOR_PROXIES = [
    ("us-0", "바이오", "Biotechnology", "US", "XBI", "SPDR S&P Biotech ETF", "us10y", -1),
    ("us-1", "반도체", "Semiconductors", "US", "SMH", "VanEck Semiconductor ETF", "us10y", -1),
    ("us-2", "전력 인프라", "Global grid infrastructure", "US", "GRID", "First Trust Smart Grid ETF · 글로벌 편입", "us10y", -1),
    ("us-3", "기술", "Technology", "US", "XLK", "Technology Select Sector SPDR", "vix", -1),
    ("us-4", "헬스케어", "Healthcare", "US", "XLV", "Health Care Select Sector SPDR", "us10y", -1),
    ("us-5", "금융", "Financials", "US", "XLF", "Financial Select Sector SPDR", "us2y", 1),
    ("us-6", "에너지", "Energy", "US", "XLE", "Energy Select Sector SPDR", "wti", 1),
    ("us-7", "유틸리티", "Utilities", "US", "XLU", "Utilities Select Sector SPDR", "us10y", -1),
    ("us-8", "리츠·부동산", "Real estate", "US", "XLRE", "Real Estate Select Sector SPDR", "us10y", -1),
    ("us-9", "산업재", "Industrials", "US", "XLI", "Industrial Select Sector SPDR", "dollar_broad", -1),
    ("kr-0", "반도체", "Semiconductors", "KR", "091160", "KODEX 반도체", "usdkrw", 1),
    ("kr-1", "자동차", "Automobiles", "KR", "091180", "KODEX 자동차", "usdkrw", 1),
    ("kr-bank", "은행", "Banks", "KR", "091170", "KODEX 은행", "us2y", 1),
    ("kr-steel", "철강", "Steel", "KR", "117680", "KODEX 철강", "wti", -1),
]
