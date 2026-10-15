"use client";
import type { Point } from "@/lib/api/client";
import { useId } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function MarketChart({
  points,
  compact = false,
  unit = "",
}: {
  points: Point[];
  compact?: boolean;
  unit?: string;
}) {
  const id = useId().replace(/:/g, "");
  return (
    <div
      className={compact ? "sparkline" : "market-chart"}
      role="img"
      aria-label={`${points.length}개 관측치 추세. 시작 ${points[0]?.value.toFixed(2)}, 마지막 ${points.at(-1)?.value.toFixed(2)} ${unit}`}
    >
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <AreaChart
          data={points}
          margin={
            compact
              ? { top: 5, right: 0, bottom: 0, left: 0 }
              : { top: 18, right: 10, bottom: 0, left: -15 }
          }
        >
          <defs>
            <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#25836c" stopOpacity={0.16} />
              <stop offset="100%" stopColor="#25836c" stopOpacity={0} />
            </linearGradient>
          </defs>
          {!compact && (
            <>
              <CartesianGrid stroke="#edf0ee" vertical={false} />
              <XAxis
                dataKey="date"
                tickFormatter={(v) => v.slice(5).replace("-", ".")}
                axisLine={false}
                tickLine={false}
                minTickGap={45}
                tick={{ fontSize: 14, fill: "#617267" }}
                dy={10}
              />
              <YAxis
                domain={["auto", "auto"]}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 14, fill: "#617267" }}
                tickFormatter={(v) =>
                  Number(v).toLocaleString("ko-KR", {
                    maximumFractionDigits: 1,
                  })
                }
                width={64}
              />
              <Tooltip
                contentStyle={{
                  border: "1px solid #e1e7e3",
                  borderRadius: 12,
                  fontSize: 14,
                }}
                labelFormatter={(v) => String(v)}
                formatter={(v) => [
                  `${Number(v).toLocaleString("ko-KR", { maximumFractionDigits: 2 })} ${unit}`,
                  "관측값",
                ]}
              />
            </>
          )}
          <Area
            type="monotone"
            dataKey="value"
            stroke="#25836c"
            strokeWidth={compact ? 1.7 : 2.5}
            fill={`url(#${id})`}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
