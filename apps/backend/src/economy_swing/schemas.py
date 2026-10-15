from typing import Literal
from enum import IntEnum
from pydantic import BaseModel, Field

class Point(BaseModel):
    date: str
    value: float

class Horizon(IntEnum):
    FIVE = 5
    TWENTY = 20
    SIXTY = 60

class Indicator(BaseModel):
    id: str
    name: str
    symbol: str
    unit: str
    market: str
    explanation: str
    caution: str
    value: float | None
    change_1d: float | None
    change_5d: float | None
    change_20d: float | None
    change_unit: str
    series: list[Point]
    source_name: str = "합성 fixture"
    source_url: str | None = None
    source_series_id: str | None = None
    observed_at: str | None = None
    source_updated_at: str | None = None
    fetched_at: str | None = None
    status: Literal["fresh", "stale", "missing", "invalid", "demo"] = "demo"
    status_message: str = "실제 시장 데이터가 아닙니다."
    frequency: str = "Daily"

class Event(BaseModel):
    date: str
    entry_date: str
    exit_date: str
    return_pct: float
    benchmark_return_pct: float
    excess_return_pp: float
    max_drawdown_pct: float

class Study(BaseModel):
    sample_count: int
    average_return: float | None
    median_return: float | None
    average_excess: float | None
    win_rate: float | None
    excess_win_rate: float | None
    worst_drawdown: float | None
    events: list[Event]

class Sector(BaseModel):
    id: str
    name: str
    english_name: str
    market: str
    driver_id: str
    direction: int
    score: float | None
    components: dict[str,float]
    return_20d: float | None
    excess_20d: float | None
    confidence: Literal["low"] = "low"
    reason: str
    risk: str
    series: list[Point]
    study: Study
    source_name: str = "합성 fixture"
    source_url: str | None = None
    proxy_symbol: str | None = None
    proxy_name: str | None = None
    benchmark_name: str | None = None
    observed_at: str | None = None
    status: Literal["fresh", "stale", "missing", "demo"] = "demo"
    status_message: str = "합성 예시입니다."

class Relationship(BaseModel):
    id: str
    sector_id: str
    sector_name: str
    market: str
    driver_id: str
    driver_name: str
    direction: int
    horizon: int
    threshold: float
    study: Study
    status: Literal["fresh", "stale", "missing", "demo"] = "demo"
    status_message: str = "합성 예시입니다."
    period_start: str | None = None
    period_end: str | None = None
    methodology: str = "5개 공통 관측치 상대 변화 ±0.5%, 다음 공통 관측치 종가 진입, 중첩 제외"

class Term(BaseModel):
    id: str
    title: str
    category: str
    definition: str
    example: str
    caution: str

class Dashboard(BaseModel):
    data_mode: Literal["demo", "live"] = "live"
    as_of: str
    generated_at: str
    source: str
    model_version: str
    weights: dict[str,float]
    calendar_note: str
    limitations: list[str]
    indicators: list[Indicator]
    sectors: list[Sector]
    relationships: list[Relationship]
    terms: list[Term]
    observed_through: str | None = None
    issues: list[str] = Field(default_factory=list)
    live_indicator_count: int = 0
    live_sector_count: int = 0
    toss_status: str = "not-configured"

class ApiError(BaseModel):
    code: str
    message: str
    request_id: str
    details: dict = Field(default_factory=dict)
