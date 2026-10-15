"use client";
import { MarketChart } from "@/components/charts/market-chart";
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
      <section className="panel indicator-list">
        <SectionHead
          title="주요 경제 지표"
          sub={`${items.length}개 지표 · 일별 합성 관측치`}
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
                {fmt(i.value, i.value > 100 ? 1 : 2)} <small>{i.unit}</small>
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
            <span className="muted tiny">합성 예시</span>
          </div>
          <div className="large-number">
            {fmt(item.value)}
            <small>{item.unit}</small>
          </div>
          <div className="change-grid">
            {[
              ["1관측치", item.change_1d],
              ["5관측치", item.change_5d],
              ["20관측치", item.change_20d],
            ].map(([label, value]) => (
              <div key={label}>
                <small>{label} 변화</small>
                <Change value={Number(value)} unit={item.change_unit} />
              </div>
            ))}
          </div>
          <MarketChart points={item.series.slice(-120)} unit={item.unit} />
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
                이 지표에 연결한 예시 섹터는 아직 없습니다.
              </span>
            )}
          </div>
          <div className="source-line">
            <Database size={13} />
            출처: 합성 fixture · 관측일 2026.10.14 · 실제 기관 자료 아님
          </div>
        </section>
      </div>
    </div>
  );
}
