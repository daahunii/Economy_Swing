"""Read official FRED table pages, including the deferred extra-rows block.

No JavaScript execution, arbitrary URLs, synthesized gaps or credential required.
The public table is a documented source page, not a stable API; parsing is tested.
"""
import math
import re
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

from .http import ProviderError, get_bytes

class FredTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table = False
        self.extra = False
        self.cell = False
        self.buffer = ""
        self.row = []
        self.rows = []
        self.extra_text = ""
        self.metadata = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self.table = attrs.get("id") == "data-table-observations"
        if tag == "div" and attrs.get("id") == "extra-rows":
            self.extra = True
        if tag == "tr":
            self.row = []
        if tag in ("td", "th"):
            self.cell = True
            self.buffer = ""

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell:
            self.row.append(self.buffer.strip())
            self.cell = False
        if tag == "tr" and len(self.row) == 2:
            if self.table:
                self.rows.append(tuple(self.row))
            else:
                self.metadata[self.row[0]] = self.row[1]
        if tag == "table":
            self.table = False
        if tag == "div" and self.extra:
            self.extra = False

    def handle_data(self, value):
        if self.cell:
            self.buffer += value
        if self.extra:
            self.extra_text += value

def parse_table(body: str, series_id: str, *, today: date | None = None) -> tuple[list[dict], str | None]:
    parser = FredTableParser()
    parser.feed(body)
    if parser.metadata.get("Series ID") != series_id:
        raise ProviderError("invalid-series", "FRED 시계열 식별자가 일치하지 않습니다.")
    if not parser.metadata.get("Frequency", "").startswith("Daily"):
        raise ProviderError("invalid-frequency", "예상한 일별 자료가 아닙니다.")
    rows = parser.rows + re.findall(r"#\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^#\n]+)", parser.extra_text)
    points = {}
    today = today or datetime.now(timezone.utc).date()
    for day, raw in rows:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            continue
        try:
            observed = date.fromisoformat(day)
        except ValueError:
            raise ProviderError("invalid-date", "FRED 관측일 형식을 확인할 수 없습니다.") from None
        if raw.strip() in (".", "", "NA") or observed > today:
            continue
        try:
            value = float(raw.strip())
        except ValueError:
            raise ProviderError("invalid-value", "FRED 관측값이 숫자가 아닙니다.") from None
        if not math.isfinite(value):
            raise ProviderError("invalid-value", "유효하지 않은 FRED 관측값입니다.")
        if day in points and points[day] != value:
            raise ProviderError("conflicting-value", "같은 관측일의 자료가 서로 다릅니다.")
        points[day] = value
    if len(points) < 2:
        raise ProviderError("empty-series", "비교할 수 있는 FRED 관측치가 부족합니다.")
    updated = parser.metadata.get("Last Updated")
    if updated:
        try:
            updated = datetime.strptime(updated.rsplit(" ", 1)[0], "%Y-%m-%d %I:%M %p").replace(tzinfo=ZoneInfo("America/Chicago")).isoformat()
        except ValueError:
            updated = None
    return [{"date": day, "value": points[day]} for day in sorted(points)[-1300:]], updated

def fetch_series(series_id: str) -> tuple[list[dict], str | None]:
    if not re.fullmatch(r"[A-Z0-9]+", series_id):
        raise ProviderError("invalid-series", "허용되지 않은 시계열 식별자입니다.")
    body = get_bytes(f"https://fred.stlouisfed.org/data/{series_id}").decode("utf-8")
    return parse_table(body, series_id)
