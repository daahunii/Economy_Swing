"use client";

import { Pill } from "@/components/ui/research-ui";
import { DashboardView } from "@/features/dashboard/dashboard-view";
import { LearnView } from "@/features/learn/learn-view";
import { MacroView } from "@/features/macro/macro-view";
import { SectorsView } from "@/features/sectors/sectors-view";
import { api, type Dashboard } from "@/lib/api/client";
import { country, path, localTime } from "@/lib/format";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  ChartColumnIncreasing,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Database,
  ExternalLink,
  FlaskConical,
  Globe2,
  Info,
  Layers3,
  LayoutDashboard,
  LoaderCircle,
  PanelLeftClose,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  X,
} from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { RelationshipView } from "./relationship-view";

const NAV = [
  { id: "dashboard", label: "대시보드", en: "OVERVIEW", icon: LayoutDashboard },
  { id: "macro", label: "경제 지표", en: "MACRO", icon: Activity },
  { id: "sectors", label: "섹터 탐색", en: "SECTORS", icon: Layers3 },
  {
    id: "relationships",
    label: "과거 관계 분석",
    en: "RESEARCH",
    icon: FlaskConical,
  },
  { id: "learn", label: "쉽게 배우기", en: "LEARN", icon: BookOpen },
];
const TITLES: Record<string, [string, string, string]> = {
  dashboard: [
    "MARKET OVERVIEW",
    "오늘의 시장을 한눈에.",
    "경제의 변화와 과거의 근거를 연결해, 다음 리서치를 시작하세요.",
  ],
  macro: [
    "MACRO EXPLORER",
    "변화를 먼저 읽는 시선.",
    "숫자의 방향뿐 아니라, 변화의 의미와 반대 요인까지 살펴보세요.",
  ],
  sectors: [
    "SECTOR DISCOVERY",
    "경제에서 산업으로.",
    "현재 환경과 과거 관계, 시장 대비 흐름을 함께 비교합니다.",
  ],
  relationships: [
    "HISTORICAL RELATIONSHIPS",
    "과거에 근거를 묻다.",
    "같은 조건이 나타났을 때, 이후 시장은 어떻게 움직였을까요?",
  ],
  learn: [
    "LEARNING LIBRARY",
    "숫자가 이해되는 순간.",
    "어려운 금융 용어를 의미, 예시, 주의점으로 연결합니다.",
  ],
};
export function ResearchApp({ section }: { section: string }) {
  const searchParams = useSearchParams();
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  const [market, setMarket] = useState("ALL");
  const [beginner, setBeginner] = useState(true);
  const [search, setSearch] = useState("");
  const [ready, setReady] = useState(false);
  const sourceDialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    setReady(true);
    try {
      setBeginner(localStorage.getItem("economy-swing:beginner") !== "off");
    } catch {}
    const selected = searchParams.get("market");
    setMarket(
      selected && ["ALL", "US", "KR"].includes(selected) ? selected : "ALL",
    );
  }, [searchParams]);
  useEffect(() => {
    const controller = new AbortController();
    setError("");
    api
      .GET("/api/v1/dashboard", {
        signal: AbortSignal.any([
          controller.signal,
          AbortSignal.timeout(60000),
        ]),
      })
      .then(({ data, error, response }) => {
        if (!data || error || !response.ok)
          throw new Error("API 응답을 확인할 수 없습니다.");
        setData(data);
      })
      .catch((e) => {
        if (e.name !== "AbortError")
          setError("자료를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.");
      });
    return () => controller.abort();
  }, [reload]);
  function toggleBeginner() {
    setBeginner(!beginner);
    try {
      localStorage.setItem("economy-swing:beginner", beginner ? "off" : "on");
    } catch {}
  }
  function selectMarket(value: string) {
    setMarket(value);
    const url = new URL(window.location.href);
    url.searchParams.set("market", value);
    window.history.replaceState({}, "", url);
  }
  const sectors =
    data?.sectors.filter((s) => market === "ALL" || s.market === market) || [];
  const searched =
    search && data
      ? [
          ...data.indicators.map((i) => ({
            name: i.name,
            detail: i.symbol,
            href: `/macro?id=${i.id}`,
          })),
          ...data.sectors.map((s) => ({
            name: s.name,
            detail: country(s.market),
            href: `/sectors?id=${s.id}`,
          })),
          ...data.terms.map((t) => ({
            name: t.title,
            detail: "용어",
            href: `/learn?id=${t.id}`,
          })),
        ]
          .filter((r) =>
            `${r.name} ${r.detail}`
              .toLowerCase()
              .includes(search.toLowerCase()),
          )
          .slice(0, 7)
      : [];
  const [eyebrow, title, description] = TITLES[section];
  const isDemo = data?.data_mode === "demo";
  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        본문으로 이동
      </a>
      <aside className="sidebar">
        <Link href="/" className="brand">
          <span className="brand-mark">
            <TrendingUp size={22} strokeWidth={2.5} />
          </span>
          <span>
            economy<span className="brand-light">swing</span>
            <small>EVIDENCE INTO OPPORTUNITY</small>
          </span>
        </Link>
        <div className="workspace">
          <span className="workspace-icon">ES</span>
          <div>
            나의 리서치 공간<small>Personal workspace</small>
          </div>
          <ChevronDown size={14} />
        </div>
        <div className="nav-caption">WORKSPACE</div>
        <nav aria-label="주요 메뉴">
          {NAV.map((n) => (
            <Link
              key={n.id}
              className={`nav-item ${section === n.id ? "active" : ""}`}
              href={path(n.id)}
              aria-current={section === n.id ? "page" : undefined}
            >
              <n.icon size={19} />
              <span>{n.label}</span>
              {section === n.id && <span className="nav-dot" />}
            </Link>
          ))}
        </nav>
        <div className="nav-caption future-caption">COMING NEXT</div>
        <div className="future-item">
          <ChartColumnIncreasing size={18} />
          기업 분석<span>MVP 3</span>
        </div>
        <div className="future-item">
          <ShieldCheck size={18} />
          성과 추적<span>MVP 4</span>
        </div>
        <div className="sidebar-bottom">
          <div className="research-note">
            <span className="small-icon">
              <Sparkles size={17} />
            </span>
            <strong>이유를 아는 투자 탐색</strong>
            <p>
              예측보다 근거를,
              <br />
              숫자보다 맥락을 살펴보세요.
            </p>
            <Link href="/learn">
              투자 용어 알아보기 <ArrowUpRight size={14} />
            </Link>
          </div>
          <button
            className="source-nav"
            onClick={() => sourceDialog.current?.showModal()}
          >
            <Database size={16} />
            데이터 및 모델 안내
            <ExternalLink size={13} />
          </button>
          <div className="sidebar-footer">
            <span className="avatar">ES</span>
            <div>
              Economy Swing<small>Research preview · v0.1</small>
            </div>
          </div>
        </div>
      </aside>
      <div className="workspace-main">
        <header className="topbar">
          <div className="breadcrumb">
            <PanelLeftClose size={17} />
            <span>Workspace</span>
            <ChevronRight size={13} />
            <strong>{NAV.find((n) => n.id === section)?.label}</strong>
          </div>
          <div className="topbar-tools">
            <div className="global-search">
              <Search size={15} />
              <input
                aria-label="지표·섹터·용어 검색"
                placeholder="지표, 섹터, 용어 검색"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Escape") setSearch("");
                }}
              />
              {search && (
                <button aria-label="검색 지우기" onClick={() => setSearch("")}>
                  <X size={13} />
                </button>
              )}
              {search && (
                <div className="search-results">
                  {searched.length ? (
                    searched.map((r) => (
                      <Link
                        key={r.href}
                        href={r.href}
                        onClick={() => setSearch("")}
                      >
                        <span>{r.name}</span>
                        <small>{r.detail}</small>
                        <ArrowUpRight size={13} />
                      </Link>
                    ))
                  ) : (
                    <p>검색 결과가 없습니다.</p>
                  )}
                </div>
              )}
            </div>
            <span className="tool-divider" />
            <button
              onClick={toggleBeginner}
              className="mode-button"
              aria-pressed={beginner}
            >
              <BookOpen size={15} />
              <span>쉬운 설명</span>
              <span className={`toggle ${beginner ? "on" : ""}`}>
                <span />
              </span>
            </button>
          </div>
        </header>
        <main id="main-content" className="content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">
                <span />
                {eyebrow}
              </div>
              <h1>{title}</h1>
              <p>{description}</p>
            </div>
            <div className="heading-meta">
              <span className="demo-badge">
                <span />
                {!data
                  ? "CONNECTING"
                  : isDemo
                    ? "DEMO DATA"
                    : "REAL OBSERVATIONS"}
              </span>
              <small>
                {!data
                  ? "공급자 연결 확인 중"
                  : isDemo
                    ? `예시 기준일 · ${data.as_of.slice(0, 10)}`
                    : `최신 관측일 · ${data.observed_through || "미확보"}`}
              </small>
            </div>
          </div>
          <div className={`demo-banner ${isDemo ? "" : "live-banner"}`}>
            <Info size={16} />
            <p>
              <strong>
                {isDemo
                  ? "합성 예시 모드입니다."
                  : "공식 자료의 실제 관측값을 연결합니다."}
              </strong>
              {isDemo
                ? " 모든 수치와 순위는 합성 예시이며 실제 시장 상황을 나타내지 않습니다."
                : " 실시간 시세가 아니며 지표마다 기준일이 다릅니다. 확보하지 못한 값은 표시하지 않습니다."}
            </p>
            <button onClick={() => sourceDialog.current?.showModal()}>
              데이터 안내 <ArrowUpRight size={14} />
            </button>
          </div>
          {error ? (
            <div className="empty-state">
              <Database size={32} />
              <h2>데이터 연결을 확인해 주세요</h2>
              <p>{error}</p>
              <button
                className="primary-button"
                onClick={() => setReload((v) => v + 1)}
              >
                <RefreshCw size={16} />
                다시 연결
              </button>
            </div>
          ) : !data ? (
            <div className="loading">
              <LoaderCircle className="spin" size={24} />
              <p>리서치 데이터를 준비하고 있습니다.</p>
            </div>
          ) : (
            <>
              {section !== "learn" && (
                <div className="view-toolbar">
                  <div className="segmented" aria-label="시장 선택">
                    {[
                      ["ALL", "전체 시장"],
                      ["US", "미국"],
                      ["KR", "한국"],
                    ].map(([v, label]) => (
                      <button
                        key={v}
                        className={market === v ? "selected" : ""}
                        onClick={() => selectMarket(v)}
                        aria-pressed={market === v}
                      >
                        {v === "ALL" && <Globe2 size={14} />} {label}
                      </button>
                    ))}
                  </div>
                  <span className="data-caption">
                    <span />
                    {isDemo
                      ? "합성 데이터 · 신뢰도 낮음"
                      : `실제 지표 ${data.live_indicator_count ?? 0}개 · 섹터 ${data.live_sector_count ?? 0}개 연결`}{" "}
                    <button
                      aria-label="신뢰도 설명"
                      onClick={() => sourceDialog.current?.showModal()}
                    >
                      <CircleHelp size={13} />
                    </button>
                  </span>
                </div>
              )}
              {section === "dashboard" && (
                <DashboardView
                  data={data}
                  sectors={sectors}
                  market={market}
                  beginner={beginner}
                />
              )}
              {section === "macro" && (
                <MacroView data={data} market={market} beginner={beginner} />
              )}
              {section === "sectors" && (
                <SectorsView
                  data={data}
                  sectors={sectors}
                  beginner={beginner}
                />
              )}
              {section === "relationships" && (
                <RelationshipView
                  data={data}
                  sectors={sectors}
                  beginner={beginner}
                />
              )}
              {section === "learn" && <LearnView data={data} />}
              {!isDemo && !!data.issues?.length && (
                <details className="data-issues">
                  <summary>지연·연결 대기 항목 {data.issues.length}개</summary>
                  {data.issues.map((issue) => (
                    <p key={issue}>{issue}</p>
                  ))}
                </details>
              )}
            </>
          )}
          <footer className="content-footer">
            <span>
              <TrendingUp size={14} /> ECONOMY SWING
            </span>
            <p>
              근거를 연결하는 리서치. 기회 점수는 미래 상승 확률이 아닙니다.
            </p>
            <span>DEVELOPMENT PREVIEW</span>
          </footer>
        </main>
      </div>
      <dialog ref={sourceDialog} className="source-dialog">
        <div className="dialog-head">
          <div>
            <span className="eyebrow">DATA & MODEL</span>
            <h2>데이터를 먼저 이해하세요</h2>
          </div>
          <button
            aria-label="안내 닫기"
            onClick={() => sourceDialog.current?.close()}
          >
            <X size={21} />
          </button>
        </div>
        <div className="dialog-content">
          <Pill>
            {isDemo
              ? "합성 예시 · 실제 데이터 미연동"
              : "실제 공개 관측자료 · 시세 연결 상태"}
          </Pill>
          <p>
            {isDemo
              ? "화면의 관측값은 고정된 수식으로 만든 fixture이며 Python으로 계산한 결과입니다."
              : "금리·환율은 연방준비제도, 원자재는 EIA, VIX는 Cboe 자료를 FRED에서 수집합니다. 토스증권이 설정되면 실제 지수와 ETF 일봉을 조회합니다."}
          </p>
          {!isDemo && (
            <>
              <p>
                관측일: {data?.observed_through || "미확보"}
                <br />
                조회 스냅샷: {localTime(data?.generated_at)}
                <br />
                토스증권:{" "}
                {data?.toss_status === "configured"
                  ? "인증 토큰 설정됨 · 자료별 수집 상태 확인"
                  : "백엔드 인증 설정 필요"}
              </p>
              <p>
                연결된 실제 지표 {data?.live_indicator_count ?? 0}개 / 섹터{" "}
                {data?.live_sector_count ?? 0}개
              </p>
            </>
          )}
          <h3>계산 모델</h3>
          <p>
            {isDemo
              ? "거시 35% + 과거 관계 40% + 모멘텀 25%. 합성 자료용 실험 설정이며 유효 사건 3개 미만은 점수를 보류합니다."
              : "실제 관측자료의 기회 점수는 검증 전까지 보류합니다. 데모의 가중치와 정규화를 실제 시장의 신뢰할 수 있는 순위로 제시하지 않습니다."}
          </p>
          <h3>확인해야 할 한계</h3>
          <ul>
            {(
              data?.limitations || ["실제 데이터 공급자, DB, 정기 수집 미연결"]
            ).map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
          <p className="muted">
            {data?.calendar_note} · 모델{" "}
            {data?.model_version || "sector-mvp-v1"}
          </p>
        </div>
        <button
          className="primary-button dialog-close"
          onClick={() => sourceDialog.current?.close()}
        >
          <Check size={15} />
          확인했습니다
        </button>
      </dialog>
      {!ready && <noscript>이 리서치 화면은 JavaScript가 필요합니다.</noscript>}
    </div>
  );
}
