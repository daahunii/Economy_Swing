import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Economy Swing · 시장을 읽는 새로운 관점",
  description:
    "경제 변화부터 과거 근거, 섹터 탐색까지. 근거로 연결하는 투자 리서치. 현재는 합성 데이터로 제공되는 개발 미리보기입니다.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <Suspense
          fallback={
            <div className="loading">Economy Swing을 준비하고 있습니다.</div>
          }
        >
          {children}
        </Suspense>
      </body>
    </html>
  );
}
