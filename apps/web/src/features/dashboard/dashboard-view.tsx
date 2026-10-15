"use client";
import { MarketChart } from "@/components/charts/market-chart";
import { Change, SectionHead } from "@/components/ui/research-ui";
import { ConnectionNotice } from "@/components/ui/data-status";
import { MetricCard } from "@/features/macro/metric-card";
import { SectorTable } from "@/features/sectors/sector-table";
import { type Dashboard, type Sector } from "@/lib/api/client";
import { country, fmt } from "@/lib/format";
import {
  Activity,
  ArrowRight,
  ChevronRight,
  Info,
  Layers3,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";
export function DashboardView({
  data,
  sectors,
  market,
  beginner,
}: {
  data: Dashboard;
  sectors: Sector[];
  market: string;
  beginner: boolean;
}) {
  const [chartId, setChartId] = useState("sp500");
  const [period, setPeriod] = useState(60);
  const benchmarkCharts = data.indicators.filter(
    (i) =>
      ["sp500", "kospi"].includes(i.id) &&
      i.series.length > 0 &&
      (market === "ALL" || i.market === market),
  );
  const charts = benchmarkCharts.length
    ? benchmarkCharts
    : data.indicators
        .filter(
          (i) =>
            i.series.length > 0 &&
            (market === "ALL" || i.market === market || i.market === "ALL"),
        )
        .slice(0, 5);
  const chart = charts.find((i) => i.id === chartId) || charts[0];
  const focus = sectors.find(
    (s) => s.series.length > 0 && s.study.sample_count > 0,
  );
  const focusDriver = data.indicators.find((i) => i.id === focus?.driver_id);
  return (
    <>
      <div className="metric-grid">
        {["us10y", "usdkrw", "wti", "vix"].map((id) => (
          <MetricCard
            key={id}
            item={data.indicators.find((i) => i.id === id)!}
          />
        ))}
      </div>
      <div className="dashboard-middle">
        <section className="panel chart-panel">
          {chart ? (
            <>
              <SectionHead
                title={benchmarkCharts.length ? "시장 흐름" : "경제 지표 흐름"}
                sub={
                  benchmarkCharts.length
                    ? "확정 일봉으로 확인하는 시장의 흐름"
                    : "시세 연결 전에는 공식 경제지표의 실제 관측 흐름을 표시합니다"
                }
              />
              <div className="chart-controls">
                <div className="chart-tabs">
                  {charts.map((i) => (
                    <button
                      key={i.id}
                      onClick={() => setChartId(i.id)}
                      className={chart.id === i.id ? "active" : ""}
                    >
                      <span />
                      {i.symbol}
                    </button>
                  ))}
                </div>
                <div className="period-tabs">
                  {[
                    [20, "1M"],
                    [60, "3M"],
                    [120, "6M"],
                    [260, "1Y"],
                  ].map(([n, label]) => (
                    <button
                      key={n}
                      className={period === n ? "active" : ""}
                      onClick={() => setPeriod(Number(n))}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="chart-stat">
                <strong>{fmt(chart.value)}</strong>
                <Change value={chart.change_20d} unit={chart.change_unit} />
                <span>최근 20관측치</span>
              </div>
              <MarketChart
                points={chart.series.slice(-period)}
                unit={chart.unit}
              />
              <div className="chart-foot">
                <span>
                  <span className="legend-dot" />
                  {chart.symbol} ·{" "}
                  {data.data_mode === "demo" ? "합성 경로" : chart.source_name}
                </span>
                <small>
                  {chart.observed_at || "예시 관측값"} / {chart.unit}
                </small>
              </div>
            </>
          ) : (
            <ConnectionNotice message="공식 경제지표의 수집을 완료하지 못했습니다. 데이터 안내에서 수집 상태를 확인해 주세요." />
          )}
        </section>
        <section className="insight-panel">
          <span className="insight-kicker">
            <Sparkles size={15} />
            RESEARCH SPOTLIGHT
          </span>
          <h2>
            변화를 기회로
            <br />
            연결하는 방법.
          </h2>
          <p>
            경제 지표에서 출발해
            <br />
            산업의 과거 반응을 살펴보세요.
          </p>
          {focus && focusDriver && (
            <>
              <div className="flow-step">
                <span className="step-number">01</span>
                <div>
                  <small>경제 변수</small>
                  <strong>{focusDriver.name}</strong>
                  <span>{focus.direction > 0 ? "상승" : "하락"} 조건 관찰</span>
                </div>
                <Activity size={18} />
              </div>
              <div className="flow-connector" />
              <div className="flow-step">
                <span className="step-number">02</span>
                <div>
                  <small>관련 산업</small>
                  <strong>{focus.name}</strong>
                  <span>
                    {country(focus.market)} · 과거 사건{" "}
                    {focus.study.sample_count}개
                  </span>
                </div>
                <Layers3 size={18} />
              </div>
              <Link
                className="insight-button"
                href={`/relationships?id=${focus.id}`}
              >
                과거 근거 살펴보기
                <ArrowRight size={15} />
              </Link>
            </>
          )}
          {!focus && (
            <p>
              섹터의 실제 시세가 연결되면 경제 변수와 과거 반응을 함께 탐색할 수
              있습니다.
            </p>
          )}
          <small className="insight-disclaimer">
            {data.data_mode === "demo"
              ? "AI 해석이 아닌 예시 탐색 흐름입니다."
              : "실제 관측자료 기반 탐색 · 기회 점수 모델 검증 전"}
          </small>
        </section>
      </div>
      <div className="dashboard-bottom">
        <section className="panel">
          <SectionHead
            title={
              data.data_mode === "demo"
                ? "섹터 리서치 우선순위"
                : "섹터 관측 목록"
            }
            sub={
              data.data_mode === "demo"
                ? "경제 환경 · 과거 관계 · 상대 모멘텀의 실험 점수"
                : "실제 시세와 대용 ETF를 확인합니다. 미연결 값은 표시하지 않습니다."
            }
            href={`/sectors?market=${market}`}
          />
          {data.data_mode === "live" &&
          !sectors.some((s) => s.series.length > 0) ? (
            <ConnectionNotice />
          ) : (
            <SectorTable sectors={sectors.slice(0, 5)} compact />
          )}
          <div className="panel-foot">
            <Info size={13} />
            {data.data_mode === "demo"
              ? "기회 점수는 상승 확률이 아닙니다. 합성 데이터 모델입니다."
              : "실제 데이터의 점수는 검증 전까지 보류합니다. 가격 변화와 모델 신뢰도는 다릅니다."}
          </div>
        </section>
        <section className="panel why-panel">
          <SectionHead
            title="숫자 너머의 맥락"
            sub="오늘 하나씩 이해하는 투자 언어"
          />
          <Link href="/learn?id=excess" className="learn-teaser">
            <span className="small-icon">
              <TrendingUp size={19} />
            </span>
            <div>
              <h3>올랐다면, 잘한 걸까요?</h3>
              <p>
                시장도 함께 올랐다면 이야기는 달라집니다. 초과 수익률로 비교해
                보세요.
              </p>
              <span>
                초과 수익률 알아보기 <ArrowRight size={13} />
              </span>
            </div>
          </Link>
          <div className="evidence-note">
            <ShieldCheck size={18} />
            <div>
              <strong>근거의 질도 함께 봅니다</strong>
              <p>
                {beginner
                  ? "표본이 적거나 자료가 불완전하면, 높은 점수도 충분한 근거가 되지 않습니다."
                  : "Data confidence: Low · Model validation pending"}
              </p>
            </div>
          </div>
          <div className="mini-flow">
            <span>MACRO</span>
            <ChevronRight size={12} />
            <span>HISTORY</span>
            <ChevronRight size={12} />
            <span>SECTOR</span>
          </div>
        </section>
      </div>
    </>
  );
}
