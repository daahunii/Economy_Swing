export const fmt = (n: number, d = 2) =>
  n.toLocaleString("ko-KR", {
    minimumFractionDigits: d,
    maximumFractionDigits: d,
  });
export const signed = (n: number | null | undefined, suffix = "%") =>
  n == null ? "—" : `${n > 0 ? "+" : ""}${fmt(n)}${suffix}`;
export const country = (market: string) =>
  market === "US" ? "미국" : market === "KR" ? "한국" : "글로벌";
export const path = (section: string) =>
  section === "dashboard" ? "/" : `/${section}`;
