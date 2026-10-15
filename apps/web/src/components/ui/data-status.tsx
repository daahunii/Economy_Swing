import Link from "next/link";
import { ArrowRight, Database } from "lucide-react";
import { type Indicator } from "@/lib/api/client";
import { localTime } from "@/lib/format";

export function ConnectionNotice({
  message = "토스증권 시세 인증이 아직 연결되지 않았습니다. 공식 경제지표는 경제 지표 메뉴에서 확인할 수 있습니다.",
}: {
  message?: string;
}) {
  return (
    <div className="connection-card">
      <Database size={22} />
      <h3>실제 시세 연결이 필요합니다</h3>
      <p>{message}</p>
      <Link href="/macro">
        수집된 경제지표 살펴보기 <ArrowRight size={15} />
      </Link>
    </div>
  );
}

export function IndicatorSource({ item }: { item: Indicator }) {
  if (item.status === "demo")
    return (
      <div className="data-provenance">
        합성 예시 데이터 · 실제 기관 자료 아님
      </div>
    );
  return (
    <div className="data-provenance">
      <strong>{item.source_name}</strong>
      <span>
        관측일: {item.observed_at || "미확보"} · {item.frequency}
      </span>
      <span>공급자 갱신: {localTime(item.source_updated_at)}</span>
      <span>수집: {localTime(item.fetched_at)}</span>
      <span className={`data-quality ${item.status}`}>
        {item.status === "fresh"
          ? "정상 수집"
          : item.status === "stale"
            ? "지연 자료"
            : item.status === "missing"
              ? "자료 미확보"
              : "자료 확인 필요"}{" "}
        · {item.status_message}
      </span>
      {item.source_url && (
        <a href={item.source_url} target="_blank" rel="noreferrer">
          원본 자료 확인 · {item.source_series_id}
        </a>
      )}
    </div>
  );
}
