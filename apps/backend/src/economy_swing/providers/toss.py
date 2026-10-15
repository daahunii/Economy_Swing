"""Read-only Toss Securities official API adapter.

Use a preissued access token. Do not mint tokens per Vercel instance: issuance
invalidates an existing token, so renewal requires a shared token manager.
"""
import math
import os
import hashlib
import threading
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode

from .http import ProviderError, get_json

BASE_URL = "https://openapi.tossinvest.com"
_rate_lock = threading.Lock()
_last_request = 0.0
_failure = None

def configured() -> bool:
    return bool(os.getenv("TOSS_ACCESS_TOKEN", "").strip())

def _get(path: str, params: dict) -> dict:
    global _last_request, _failure
    token = os.getenv("TOSS_ACCESS_TOKEN", "").strip()
    if not token:
        raise ProviderError("not-configured", "토스증권 시세 연결을 위한 백엔드 토큰 설정이 필요합니다.")
    token_hash=hashlib.sha256(token.encode()).hexdigest()
    # Single-flight local limiter: chart groups allow 5 requests/sec.
    with _rate_lock:
        if _failure and _failure[0]==token_hash and time.monotonic()<_failure[1]:
            raise ProviderError(_failure[2], _failure[3])
        time.sleep(max(0, .25 - (time.monotonic() - _last_request)))
        _last_request = time.monotonic()
    try:
        payload = get_json(f"{BASE_URL}{path}?{urlencode(params)}", headers={"Authorization": f"Bearer {token}"})
    except ProviderError as exc:
        if exc.code in ("http-401", "http-403", "http-429", "network"):
            with _rate_lock:
                _failure=(token_hash,time.monotonic()+60,exc.code,str(exc))
        raise
    result = payload.get("result")
    if not isinstance(result, dict):
        raise ProviderError("invalid-response", "토스증권 시세 응답 형식을 확인할 수 없습니다.")
    return result

def parse_candles(candles: list[dict], *, now: datetime) -> list[dict]:
    points = {}
    for candle in candles:
        try:
            stamp = datetime.fromisoformat(candle["timestamp"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("timezone required")
            # Conservative: exclude the market-local calendar date currently in progress.
            if stamp.date() >= now.astimezone(stamp.tzinfo).date():
                continue
            value = float(candle["closePrice"])
            if not math.isfinite(value) or value <= 0:
                raise ValueError("positive close required")
            day = stamp.date().isoformat()
            if day in points and points[day] != value:
                raise ValueError("conflicting close")
            points[day] = value
        except (KeyError, TypeError, ValueError, AttributeError):
            raise ProviderError("invalid-candle", "토스증권 일봉의 시각 또는 종가가 올바르지 않습니다.") from None
    return [{"date": day, "value": points[day]} for day in sorted(points)]

def fetch_daily(symbol: str, *, now: datetime, market_indicator: bool = False) -> list[dict]:
    import re
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", symbol):
        raise ProviderError("invalid-symbol", "허용되지 않은 시세 심볼입니다.")
    path = f"/api/v1/market-indicators/{symbol}/candles" if market_indicator else "/api/v1/candles"
    params = {"interval": "1d", "count": 200}
    if not market_indicator:
        params["symbol"] = symbol
        params["adjusted"] = "true"
    result_points = {}
    seen_cursors = set()
    for _ in range(2):  # Bounded 400-bar history; no unbounded backfill in requests.
        result = _get(path, params)
        candles = result.get("candles")
        if not isinstance(candles, list):
            raise ProviderError("invalid-response", "토스증권 일봉 목록을 확인할 수 없습니다.")
        for p in parse_candles(candles, now=now):
            if p["date"] in result_points and result_points[p["date"]] != p["value"]:
                raise ProviderError("conflicting-candle", "페이지 간 종가가 일치하지 않습니다.")
            result_points[p["date"]] = p["value"]
        cursor = result.get("nextBefore")
        if not cursor:
            break
        if cursor in seen_cursors:
            raise ProviderError("invalid-pagination", "토스증권 페이지 커서가 반복되었습니다.")
        seen_cursors.add(cursor)
        params["before"] = cursor  # inclusive cursor is passed exactly; duplicate bars deduplicated.
    if len(result_points) < 2:
        raise ProviderError("insufficient-history", "토스증권의 확정 일봉이 부족합니다.")
    return [{"date": day, "value": result_points[day]} for day in sorted(result_points)]
