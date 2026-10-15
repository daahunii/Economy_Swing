"use client";
import { Change, Pill, SectionHead } from "@/components/ui/research-ui";
import { ConnectionNotice } from "@/components/ui/data-status";
import {
  api,
  type Dashboard,
  type Relationship,
  type Sector,
} from "@/lib/api/client";
import { country, fmt, signed } from "@/lib/format";
import { FlaskConical, Info, LoaderCircle } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
export function RelationshipView({
  data,
  sectors,
  beginner,
}: {
  data: Dashboard;
  sectors: Sector[];
  beginner: boolean;
}) {
  const searchParams = useSearchParams();
  const [id, setId] = useState(sectors[0]?.id || "");
  const [horizon, setHorizon] = useState<5 | 20 | 60>(20);
  const [result, setResult] = useState<Relationship | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const params = searchParams;
    setId(params.get("id") || sectors[0]?.id || "");
    const h = Number(params.get("horizon"));
    if (h === 5 || h === 20 || h === 60) setHorizon(h);
  }, [searchParams]);
  const effectiveId = sectors.some((s) => s.id === id) ? id : sectors[0]?.id;
  useEffect(() => {
    if (!effectiveId) return;
    const controller = new AbortController();
    setBusy(true);
    setError("");
    setResult(null);
    api
      .GET("/api/v1/relationships/{sector_id}", {
        params: { path: { sector_id: effectiveId }, query: { horizon } },
        signal: AbortSignal.any([
          controller.signal,
          AbortSignal.timeout(60000),
        ]),
      })
      .then(({ data, error }) => {
        if (!data || error) throw Error();
        setResult(data);
      })
      .catch((e) => {
        if (e.name !== "AbortError")
          setError("관계 분석을 불러오지 못했습니다.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setBusy(false);
      });
    return () => controller.abort();
  }, [effectiveId, horizon, attempt]);
  function update(nextId: string, nextHorizon: 5 | 20 | 60) {
    setId(nextId);
    setHorizon(nextHorizon);
    const url = new URL(window.location.href);
    url.searchParams.set("id", nextId);
    url.searchParams.set("horizon", String(nextHorizon));
    window.history.replaceState({}, "", url);
  }
  const study = result?.study;
  return (
    <>
      <section className="panel research-controls">
        <div>
          <span className="eyebrow">PREDEFINED EVENT STUDY</span>
          <h2>과거 관계 탐색</h2>
          <p>
            저장된 조건을 조회합니다. 자유 조건 백테스트는 이후 단계에
            추가합니다.
          </p>
        </div>
        <div className="research-selects">
          <label>
            분석 대상 섹터
            <select
              value={effectiveId}
              onChange={(e) => update(e.target.value, horizon)}
            >
              {sectors.map((s) => (
                <option key={s.id} value={s.id}>
                  {country(s.market)} · {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            관찰 기간
            <select
              value={horizon}
              onChange={(e) =>
                update(effectiveId, Number(e.target.value) as 5 | 20 | 60)
              }
            >
              <option value={5}>5관측치 후</option>
              <option value={20}>20관측치 후</option>
              <option value={60}>60관측치 후</option>
            </select>
          </label>
        </div>
      </section>
      {busy ? (
        <div className="loading">
          <LoaderCircle className="spin" />
          과거 사건을 계산하고 있습니다.
        </div>
      ) : error ? (
        <div className="empty-state">
          <p>{error}</p>
          <button
            className="outline-button"
            onClick={() => setAttempt((n) => n + 1)}
          >
            다시 시도
          </button>
        </div>
      ) : (
        result &&
        study &&
        (result.status === "missing" ? (
          <ConnectionNotice message={result.status_message} />
        ) : (
          <>
            <div className="relationship-condition">
              <span className="small-icon">
                <FlaskConical size={19} />
              </span>
              <div>
                <h3>
                  {result.driver_name} 5관측치 상대 변화{" "}
                  {result.direction > 0 ? "≥ +" : "≤ -"}
                  {result.threshold}% → {result.sector_name}
                </h3>
                <p>
                  조건 최초 돌파 → 다음 관측치 종가 진입 → {horizon}관측치 후
                  종가 비교 · 이벤트 창 중첩 제외
                </p>
              </div>
              <Pill>신뢰도 낮음</Pill>
            </div>
            <div className="study-grid">
              {[
                ["평균 수익률", signed(study.average_return), "절대 성과"],
                [
                  "시장 대비 초과 수익률",
                  signed(study.average_excess, "%p"),
                  country(result.market) + " 벤치마크 대비",
                ],
                [
                  "역사적 상승 승률",
                  study.win_rate == null ? "—" : fmt(study.win_rate, 1) + "%",
                  "미래 확률이 아닙니다",
                ],
                [
                  "유효 사건 수",
                  study.sample_count + "개",
                  "평가 기간에 도달한 사건",
                ],
              ].map(([label, value, sub]) => (
                <div className="panel study-stat" key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                  <small>{sub}</small>
                </div>
              ))}
            </div>
            <section className="panel">
              <SectionHead
                title="이벤트별 결과"
                sub={
                  data.data_mode === "demo"
                    ? `${data.indicators[0]?.series[0]?.date || "—"} ~ ${data.as_of.slice(0, 10)} · 합성 평일 기준`
                    : `${result.period_start || "—"} ~ ${result.period_end || "—"} · 공통 관측일 · 최신 수정 자료 기반 탐색`
                }
              />
              {study.events.length ? (
                <div className="table-wrap">
                  <table className="events-table">
                    <thead>
                      <tr>
                        <th>조건 발생일</th>
                        <th>진입일 → 평가일</th>
                        <th>섹터 수익률</th>
                        <th>시장 수익률</th>
                        <th>초과 수익률</th>
                        <th>구간 최대 낙폭</th>
                      </tr>
                    </thead>
                    <tbody>
                      {study.events.map((e) => (
                        <tr key={e.date}>
                          <td>{e.date}</td>
                          <td className="muted">
                            {e.entry_date} → {e.exit_date}
                          </td>
                          <td>
                            <Change value={e.return_pct} />
                          </td>
                          <td>{signed(e.benchmark_return_pct)}</td>
                          <td>
                            <Change value={e.excess_return_pp} unit="%p" />
                          </td>
                          <td className="negative">
                            {signed(e.max_drawdown_pct)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state">
                  이 조건에서 평가 가능한 사건이 없습니다.
                </div>
              )}
            </section>
            <section className="panel explanation">
              <h3>
                {beginner
                  ? "결과를 읽기 전에 확인하세요"
                  : "METHODOLOGY & LIMITATIONS"}
              </h3>
              <p>
                {data.data_mode === "demo"
                  ? "모든 사건은 합성 자료에서 추출했습니다."
                  : "실제 관측자료에서 공통 날짜만 맞춰 분석했습니다. 최신 수정 자료 기반이며 당시 발표 정보만으로 재현한 백테스트는 아닙니다."}{" "}
                금리 지표의 이벤트 조건은 금리차(bp)가 아니라 수준값의 상대
                변화율(%)입니다.
              </p>
              <div className="caution">
                <Info size={16} />
                <p>
                  비용·배당·세금 미반영. 최초 임계값 돌파만 선택하고 관찰 창이
                  겹치는 사건은 제외합니다. 표본 수가 기간마다 달라질 수
                  있습니다. 평균 초과 수익률은 포트폴리오 성과가 아닙니다.
                </p>
              </div>
              <div className="method-stats">
                <span>
                  중앙값 수익률 <strong>{signed(study.median_return)}</strong>
                </span>
                <span>
                  시장 초과 승률{" "}
                  <strong>
                    {study.excess_win_rate == null
                      ? "—"
                      : fmt(study.excess_win_rate, 1) + "%"}
                  </strong>
                </span>
                <span>
                  사건 중 최악의 낙폭{" "}
                  <strong>{signed(study.worst_drawdown)}</strong>
                </span>
              </div>
            </section>
          </>
        ))
      )}
    </>
  );
}
