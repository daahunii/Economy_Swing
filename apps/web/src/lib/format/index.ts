export const fmt = (n: number | null | undefined, d = 2) =>
  n == null
    ? "—"
    : n.toLocaleString("ko-KR", {
        minimumFractionDigits: d,
        maximumFractionDigits: d,
      });
export const signed = (n: number | null | undefined, suffix = "%") =>
  n == null ? "—" : `${n > 0 ? "+" : ""}${fmt(n)}${suffix}`;
export const country = (market: string) =>
  market === "US" ? "미국" : market === "KR" ? "한국" : "글로벌";
export const path = (section: string) =>
  section === "dashboard" ? "/" : `/${section}`;
export const localTime = (stamp: string | null | undefined) => {
  if (!stamp) return "확인 불가";
  const date = new Date(stamp);
  return Number.isNaN(date.getTime())
    ? "확인 불가"
    : new Intl.DateTimeFormat("ko-KR", {
        timeZone: "Asia/Seoul",
        dateStyle: "short",
        timeStyle: "short",
      }).format(date) + " KST";
};
