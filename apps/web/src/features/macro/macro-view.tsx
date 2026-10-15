"use client";
import { MarketChart } from "@/components/charts/market-chart";
import { IndicatorSource } from "@/components/ui/data-status";
import { Change, Pill, SectionHead } from "@/components/ui/research-ui";
import { type Dashboard } from "@/lib/api/client";
import { country, fmt } from "@/lib/format";
import { ArrowUpRight, Database, Info } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
export function MacroView({
  data,
  market,
  beginner,
}: {
  data: Dashboard;
  market: string;
  beginner: boolean;
}) {
  const searchParams = useSearchParams();
  const [selected, setSelected] = useState("us10y");
  useEffect(() => {
    setSelected(searchParams.get("id") || "us10y");
  }, [searchParams]);
  const items = data.indicators.filter(
    (i) => market === "ALL" || i.market === market || i.market === "ALL",
  );
  const item = items.find((i) => i.id === selected) || items[0];
  if (!item)
    return <div className="empty-state">해당 시장의 지표가 없습니다.</div>;
  function select(id: string) {
    setSelected(id);
    const url = new URL(window.location.href);
    url.searchParams.set("id", id);
    window.history.replaceState({}, "", url);
  }
  return (
    <div className="explorer-grid">
      <div className="macro-mobile-picker">
        <label>
          확인할 경제 지표
          <select
            aria-label="모바일 경제 지표 선택"
            value={item.id}
            onChange={(e) => select(e.target.value)}
          >
            {items.map((i) => (
              <option key={i.id} value={i.id}>
                {i.name} · {i.symbol}
              </option>
            ))}
          </select>
        </label>
      </div>
      <section className="panel indicator-list">
        <SectionHead
          title="주요 경제 지표"
          sub={`${items.length}개 지표 · ${data.data_mode === "demo" ? "합성 관측치" : "공식 일별 관측자료"}`}
        />
        {items.map((i) => (
          <button
            className={`indicator-row ${item.id === i.id ? "selected" : ""}`}
            key={i.id}
            onClick={() => select(i.id)}
          >
            <span>
              <strong>{i.name}</strong>
              <small>{i.symbol}</small>
            </span>
            <span>
              <strong>
                {fmt(i.value, (i.value ?? 0) > 100 ? 1 : 2)}{" "}
                <small>{i.unit}</small>
              </strong>
              <Change value={i.change_1d} unit={i.change_unit} />
            </span>
          </button>
        ))}
      </section>
      <div className="detail-column">
        <section className="panel">
          <div className="detail-heading">
            <div>
              <Pill>
                {country(item.market)} · {item.symbol}
              </Pill>
              <h2>{item.name}</h2>
            </div>
            <span className="muted tiny">
              {item.status === "demo"
                ? "합성 예시"
                : item.observed_at
                  ? `관측 ${item.observed_at}`
                  : "자료 미확보"}
            </span>
          </div>
          <div className="large-number">
            {fmt(item.value)}
            <small>{item.unit}</small>
          </div>
          <div className="change-grid">
            {[
              { label: "1관측치", value: item.change_1d },
              { label: "5관측치", value: item.change_5d },
              { label: "20관측치", value: item.change_20d },
            ].map(({ label, value }) => (
              <div key={label}>
                <small>{label} 변화</small>
                <Change value={value} unit={item.change_unit} />
              </div>
            ))}
          </div>
          {item.series.length > 0 ? (
            <MarketChart points={item.series.slice(-120)} unit={item.unit} />
          ) : (
            <div className="empty-state">
              <p>{item.status_message}</p>
            </div>
          )}
        </section>
        <section className="panel explanation">
          <span className="eyebrow">
            {beginner ? "쉽게 말하면" : "INTERPRETATION"}
          </span>
          <h3>이 지표가 왜 중요할까요?</h3>
          <p>{item.explanation}</p>
          <div className="caution">
            <Info size={16} />
            <p>{item.caution}</p>
          </div>
          <h4>연결된 섹터</h4>
          <div className="related-sectors">
            {data.sectors
              .filter((s) => s.driver_id === item.id)
              .map((s) => (
                <Link key={s.id} href={`/sectors?id=${s.id}`}>
                  {s.name}
                  <small>{country(s.market)}</small>
                  <ArrowUpRight size={13} />
                </Link>
              ))}
            {!data.sectors.some((s) => s.driver_id === item.id) && (
              <span className="muted">
                이 지표에 연결한 섹터는 아직 없습니다.
              </span>
            )}
          </div>
          <IndicatorSource item={item} />
        </section>
      </div>
    </div>
  );
}
