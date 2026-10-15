import { fmt, signed } from "@/lib/format";
import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";
import Link from "next/link";
export function Change({
  value,
  unit = "%",
}: {
  value: number;
  unit?: string;
}) {
  return (
    <span className={`change ${value >= 0 ? "positive" : "negative"}`}>
      {value >= 0 ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}{" "}
      {signed(value, unit)}
    </span>
  );
}
export function Score({ value }: { value: number | null }) {
  return (
    <span className={`score ${value != null && value >= 65 ? "high" : ""}`}>
      {value == null ? "보류" : fmt(value, 1)}
    </span>
  );
}
export function Pill({ children }: { children: React.ReactNode }) {
  return <span className="pill">{children}</span>;
}
export function SectionHead({
  title,
  sub,
  href,
}: {
  title: string;
  sub?: string;
  href?: string;
}) {
  return (
    <div className="section-head">
      <div>
        <h2>{title}</h2>
        {sub && <p>{sub}</p>}
      </div>
      {href && (
        <Link href={href} className="text-link">
          전체 보기 <ArrowRight size={14} />
        </Link>
      )}
    </div>
  );
}
