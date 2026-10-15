"use client";
import { MarketChart } from "@/components/charts/market-chart";
import { Change, SectionHead } from "@/components/ui/research-ui";
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
  const chart = data.indicators.find(
    (i) =>
      i.id ===
      (market === "KR" ? "kospi" : market === "US" ? "sp500" : chartId),
  )!;
  const focus = sectors[0];
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
          <SectionHead
            title="시장 흐름"
            sub="큰 흐름을 확인하는 두 시장의 벤치마크"
          />
          <div className="chart-controls">
            <div className="chart-tabs">
              {data.indicators
                .filter(
                  (i) =>
                    ["sp500", "kospi"].includes(i.id) &&
                    (market === "ALL" || i.market === market),
                )
                .map((i) => (
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
            <Change value={chart.change_20d} />
            <span>최근 20관측치</span>
          </div>
          <MarketChart points={chart.series.slice(-period)} unit={chart.unit} />
          <div className="chart-foot">
            <span>
              <span className="legend-dot" />
              {chart.symbol} · 합성 경로
            </span>
            <small>가격 지수 예시 / {chart.unit}</small>
          </div>
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
          <small className="insight-disclaimer">
            AI 해석이 아닌 예시 탐색 흐름입니다.
          </small>
        </section>
      </div>
      <div className="dashboard-bottom">
        <section className="panel">
          <SectionHead
            title="섹터 리서치 우선순위"
            sub="경제 환경 · 과거 관계 · 상대 모멘텀의 실험 점수"
            href={`/sectors?market=${market}`}
          />
          <SectorTable sectors={sectors.slice(0, 5)} compact />
          <div className="panel-foot">
            <Info size={13} />
            기회 점수는 상승 확률이 아닙니다. 합성 데이터 모델입니다.
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
                  : "Data confidence: Low · Synthetic fixture"}
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
