"use client";
import { Pill } from "@/components/ui/research-ui";
import { type Dashboard } from "@/lib/api/client";
import { BookOpen, Info, Search } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
export function LearnView({ data }: { data: Dashboard }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("전체");
  const searchParams = useSearchParams();
  const [selected, setSelected] = useState("");
  useEffect(() => {
    setSelected(searchParams.get("id") || "");
    setQuery(searchParams.get("q") || "");
    setCategory(searchParams.get("category") || "전체");
  }, [searchParams]);
  useEffect(() => {
    if (selected)
      document.getElementById(selected)?.scrollIntoView({ block: "start" });
  }, [selected]);
  function updateFilter(key: string, value: string) {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.history.replaceState({}, "", url);
  }
  const categories = ["전체", ...new Set(data.terms.map((t) => t.category))];
  const terms = data.terms.filter(
    (t) =>
      (category === "전체" || category === t.category) &&
      `${t.title} ${t.definition}`.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <div className="learn-intro">
        <div>
          <BookOpen size={26} />
          <h2>
            작은 개념 하나가,
            <br />
            시장을 보는 관점을 바꿉니다.
          </h2>
          <p>의미를 이해하고, 비교하고, 예외를 확인하세요.</p>
        </div>
        <div className="learn-intro-steps">
          <span>
            01 <strong>무슨 뜻인가요?</strong>
          </span>
          <span>
            02 <strong>어떻게 읽나요?</strong>
          </span>
          <span>
            03 <strong>무엇을 주의하나요?</strong>
          </span>
        </div>
      </div>
      <div className="learn-toolbar">
        <div className="category-tabs">
          {categories.map((c) => (
            <button
              className={category === c ? "active" : ""}
              key={c}
              aria-pressed={category === c}
              onClick={() => {
                setCategory(c);
                updateFilter("category", c);
              }}
            >
              {c}
            </button>
          ))}
        </div>
        <label className="inline-search">
          <Search size={15} />
          <input
            aria-label="용어 검색"
            placeholder="알고 싶은 용어 검색"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              updateFilter("q", e.target.value);
            }}
          />
        </label>
      </div>
      <div className="term-grid">
        {terms.map((t) => (
          <article
            key={t.id}
            className={`panel term-card ${selected === t.id ? "focused" : ""}`}
            id={t.id}
          >
            <Pill>{t.category}</Pill>
            <h2>{t.title}</h2>
            <p>{t.definition}</p>
            <div className="term-example">
              <span>쉽게 예를 들면</span>
              <p>{t.example}</p>
            </div>
            <div className="term-caution">
              <Info size={14} />
              <p>{t.caution}</p>
            </div>
          </article>
        ))}
      </div>
      {!terms.length && (
        <div className="empty-state">
          <Search size={25} />
          <p>검색한 용어가 없습니다.</p>
        </div>
      )}
    </>
  );
}
