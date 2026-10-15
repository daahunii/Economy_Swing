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
    value: float
    change_1d: float
    change_5d: float
    change_20d: float
    change_unit: str
    series: list[Point]

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
    return_20d: float
    excess_20d: float
    confidence: Literal["low"] = "low"
    reason: str
    risk: str
    series: list[Point]
    study: Study

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

class Term(BaseModel):
    id: str
    title: str
    category: str
    definition: str
    example: str
    caution: str

class Dashboard(BaseModel):
    data_mode: Literal["demo"] = "demo"
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

class ApiError(BaseModel):
    code: str
    message: str
    request_id: str
    details: dict = Field(default_factory=dict)
