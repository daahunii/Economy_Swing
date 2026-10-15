"use client";
import { Pill, Score, SectionHead } from "@/components/ui/research-ui";
import { type Dashboard, type Sector } from "@/lib/api/client";
import { country, fmt } from "@/lib/format";
import { ArrowRight, ArrowUpRight, Info, Search } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { SectorTable } from "./sector-table";
export function SectorsView({
  data,
  sectors,
  beginner,
}: {
  data: Dashboard;
  sectors: Sector[];
  beginner: boolean;
}) {
  const searchParams = useSearchParams();
  const [selected, setSelected] = useState("");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("score");
  const detailRef = useRef<HTMLElement>(null);
  useEffect(() => {
    setSelected(searchParams.get("id") || "");
    setQuery(searchParams.get("q") || "");
    setSort(searchParams.get("sort") === "return" ? "return" : "score");
  }, [searchParams]);
  useEffect(() => {
    if (selected) detailRef.current?.scrollIntoView({ block: "start" });
  }, [selected]);
  function updateFilter(key: string, value: string) {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.history.replaceState({}, "", url);
  }
  const active = sectors.find((s) => s.id === selected);
  const filtered = sectors
    .filter((s) =>
      `${s.name} ${s.english_name}`.toLowerCase().includes(query.toLowerCase()),
    )
    .sort((a, b) =>
      sort === "return"
        ? (b.excess_20d ?? -Infinity) - (a.excess_20d ?? -Infinity)
        : (b.score ?? -1) - (a.score ?? -1),
    );
  const driver = data.indicators.find((i) => i.id === active?.driver_id);
  return (
    <>
      {active && (
        <section ref={detailRef} className="panel sector-detail">
          <div className="detail-heading">
            <div>
              <Pill>
                {country(active.market)} · {active.english_name}
              </Pill>
              <h2>
                {active.name} <Score value={active.score} />
              </h2>
            </div>
            <Link
              href={`/relationships?id=${active.id}`}
              className="outline-button"
            >
              과거 관계 보기
              <ArrowUpRight size={14} />
            </Link>
          </div>
          <div className="sector-detail-grid">
            <div>
              <h3>점수의 구성</h3>
              {data.data_mode === "live" ? (
                <div className="data-quality">
                  <p>
                    기회 점수는 실제 데이터 모델의 검증이 끝날 때까지
                    보류합니다.
                  </p>
                  <p>{active.status_message}</p>
                  <p>
                    대용 지표: {active.proxy_name} ({active.proxy_symbol})
                  </p>
                  <p>벤치마크: {active.benchmark_name}</p>
                  <p>최신 관측일: {active.observed_at || "미확보"}</p>
                </div>
              ) : (
                <>
                  {" "}
                  {[
                    ["macro", "거시 환경"],
                    ["historical", "과거 관계"],
                    ["momentum", "상대 모멘텀"],
                  ].map(([id, label]) => (
                    <div className="score-breakdown" key={id}>
                      <span>
                        {label}
                        <small>{Math.round(data.weights[id] * 100)}%</small>
                      </span>
                      <div className="bar-track">
                        <span
                          style={{ width: `${active.components[id] || 0}%` }}
                        />
                      </div>
                      <strong>
                        {active.components[id] == null
                          ? "—"
                          : fmt(active.components[id], 1)}
                      </strong>
                    </div>
                  ))}
                  <small className="muted">
                    뉴스·밸류에이션 미적용 · {data.model_version}
                  </small>
                </>
              )}
            </div>
            <div className="sector-thesis">
              <span className="eyebrow">
                {beginner ? "근거와 주의점" : "THESIS & RISK"}
              </span>
              <p>{active.reason}</p>
              <div className="caution">
                <Info size={15} />
                <p>{active.risk}</p>
              </div>
              <Link className="text-link" href={`/macro?id=${driver?.id}`}>
                {driver?.name} 살펴보기
                <ArrowRight size={13} />
              </Link>
            </div>
          </div>
        </section>
      )}
      <section className="panel">
        <SectionHead
          title="섹터 비교"
          sub={`${filtered.length}개 섹터 · ${data.data_mode === "demo" ? "합성 모델 점수" : "실제 ETF 관측자료 · 기회 점수 검증 전"}`}
        />
        <div className="table-toolbar">
          <label className="inline-search">
            <Search size={15} />
            <input
              placeholder="섹터 검색"
              aria-label="섹터 검색"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                updateFilter("q", e.target.value);
              }}
            />
          </label>
          <select
            aria-label="정렬 기준"
            value={sort}
            onChange={(e) => {
              setSort(e.target.value);
              updateFilter("sort", e.target.value);
            }}
          >
            <option value="score">기회 점수순</option>
            <option value="return">시장 대비 성과순</option>
          </select>
        </div>
        {filtered.length ? (
          <SectorTable sectors={filtered} />
        ) : (
          <div className="empty-state">
            <Search size={24} />
            <p>검색 조건에 맞는 섹터가 없습니다.</p>
          </div>
        )}
      </section>
    </>
  );
}
