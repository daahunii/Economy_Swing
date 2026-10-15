"use client";
import { Change, Score } from "@/components/ui/research-ui";
import { type Sector } from "@/lib/api/client";
import { country } from "@/lib/format";
import { ArrowUpRight, Layers3 } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
export function SectorTable({
  sectors,
  compact = false,
}: {
  sectors: Sector[];
  compact?: boolean;
}) {
  const searchParams = useSearchParams();
  function sectorHref(id: string) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("id", id);
    return `/sectors?${params}`;
  }
  return (
    <div className="table-wrap">
      <table className="sector-table">
        <thead>
          <tr>
            <th>#</th>
            <th>섹터 / 시장</th>
            <th>기회 점수</th>
            <th>20관측치 수익률</th>
            {!compact && <th>시장 대비</th>}
            <th>과거 표본</th>
            <th>
              <span className="sr-only">상세</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {sectors.map((s, i) => (
            <tr key={s.id}>
              <td className="rank">{String(i + 1).padStart(2, "0")}</td>
              <td>
                <Link href={sectorHref(s.id)} className="sector-name">
                  <span className={`sector-symbol tone-${i % 4}`}>
                    <Layers3 size={16} />
                  </span>
                  <span>
                    <strong>{s.name}</strong>
                    <small>
                      {country(s.market)} · {s.proxy_symbol || s.english_name}
                    </small>
                  </span>
                </Link>
              </td>
              <td>
                <Score value={s.score} />
              </td>
              <td>
                <Change value={s.return_20d} />
              </td>
              {!compact && (
                <td>
                  <Change value={s.excess_20d} unit="%p" />
                </td>
              )}
              <td>
                <span className="sample-count">
                  {s.status === "missing"
                    ? "연결 대기"
                    : `${s.study.sample_count}개`}
                </span>
                <small className="table-confidence">
                  {s.status === "demo"
                    ? "합성 예시"
                    : s.status === "missing"
                      ? "자료 미확보"
                      : s.status === "stale"
                        ? "자료 지연"
                        : "모델 검증 전"}
                </small>
              </td>
              <td>
                <Link
                  href={sectorHref(s.id)}
                  aria-label={`${s.name} ${country(s.market)} 상세`}
                >
                  <ArrowUpRight size={16} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
