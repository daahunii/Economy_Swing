import { MarketChart } from "@/components/charts/market-chart";
import { Change } from "@/components/ui/research-ui";
import type { Indicator } from "@/lib/api/client";
import { fmt } from "@/lib/format";
import { ArrowUpRight } from "lucide-react";
import Link from "next/link";
export function MetricCard({ item }: { item: Indicator }) {
  return (
    <Link href={`/macro?id=${item.id}`} className="metric-card">
      <div className="metric-label">
        {item.name}
        <ArrowUpRight size={14} />
      </div>
      <div className="metric-value">
        {fmt(item.value, (item.value ?? 0) > 100 ? 1 : 2)}
        <small>{item.unit}</small>
      </div>
      <div className="metric-bottom">
        <div>
          <Change value={item.change_1d} unit={item.change_unit} />
          <span className="muted tiny">직전 관측치 대비</span>
        </div>
        {item.series.length > 0 && (
          <MarketChart compact points={item.series.slice(-30)} />
        )}
      </div>
      <div className={`data-quality ${item.status}`}>
        {item.status === "demo"
          ? "합성 예시"
          : item.observed_at
            ? `관측 ${item.observed_at} · ${item.status === "stale" ? "지연" : "일별 자료"}`
            : "자료 미확보"}
      </div>
      <div className="data-quality">{item.source_name}</div>
    </Link>
  );
}
