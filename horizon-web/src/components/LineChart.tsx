"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { formatMetric, formatTime, type MetricFormat } from "@/lib/format";

export interface ChartSeries {
  label: string;
  colorVar: string;
  points: { bucket: string; value?: number }[];
}

interface LineChartProps {
  series: ChartSeries[];
  format: MetricFormat;
}

const HEIGHT = 200;
const PAD = { top: 12, right: 14, bottom: 22, left: 52 };

export function LineChart({ series, format }: LineChartProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [hoverX, setHoverX] = useState<number | null>(null);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect.width;
      if (w) setWidth(w);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const model = useMemo(() => {
    const times = new Set<number>();
    const values: number[] = [];
    for (const s of series) {
      for (const p of s.points) {
        times.add(Date.parse(p.bucket));
        if (p.value != null) values.push(p.value);
      }
    }
    const sortedTimes = [...times].sort((a, b) => a - b);
    return {
      sortedTimes,
      tMin: sortedTimes[0] ?? 0,
      tMax: sortedTimes[sortedTimes.length - 1] ?? 0,
      dataMax: values.length ? Math.max(...values) : 1,
    };
  }, [series]);

  const plotW = Math.max(1, width - PAD.left - PAD.right);
  const plotH = HEIGHT - PAD.top - PAD.bottom;
  const { sortedTimes, tMin, tMax, dataMax } = model;
  const yTop = dataMax > 0 ? dataMax * 1.1 : 1;

  const xScale = (t: number) =>
    PAD.left +
    (tMax === tMin ? plotW / 2 : ((t - tMin) / (tMax - tMin)) * plotW);
  const yScale = (v: number) => PAD.top + plotH - (v / yTop) * plotH;

  const hasData = sortedTimes.length > 0;

  const hoverTime = useMemo(() => {
    if (hoverX == null || !hasData) return null;
    let best = sortedTimes[0];
    let bestD = Infinity;
    for (const t of sortedTimes) {
      const d = Math.abs(xScale(t) - hoverX);
      if (d < bestD) {
        bestD = d;
        best = t;
      }
    }
    return best;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hoverX, sortedTimes, tMin, tMax, plotW, hasData]);

  const yTicks = [0, yTop / 2, yTop];

  const xTickCount = hasData
    ? Math.max(2, Math.min(6, Math.floor(plotW / 90)))
    : 0;
  const xTicks =
    tMax === tMin
      ? hasData
        ? [tMin]
        : []
      : Array.from(
          { length: xTickCount },
          (_, i) => tMin + (i / (xTickCount - 1)) * (tMax - tMin),
        );

  return (
    <div ref={wrapRef} className="relative w-full" style={{ height: HEIGHT }}>
      {width > 0 && (
        <svg
          width={width}
          height={HEIGHT}
          className="block touch-pan-y"
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            setHoverX(e.clientX - rect.left);
          }}
          onMouseLeave={() => setHoverX(null)}
          onTouchStart={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            setHoverX(e.touches[0].clientX - rect.left);
          }}
          onTouchMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            setHoverX(e.touches[0].clientX - rect.left);
          }}
        >
          {/* y grid */}
          {yTicks.map((v, i) => (
            <g key={i}>
              <line
                x1={PAD.left}
                x2={width - PAD.right}
                y1={yScale(v)}
                y2={yScale(v)}
                stroke="var(--viz-grid)"
                strokeWidth={1}
              />
              <text
                x={PAD.left - 8}
                y={yScale(v)}
                textAnchor="end"
                dominantBaseline="middle"
                fontSize={10}
                fill="var(--viz-muted)"
                style={{ fontVariantNumeric: "tabular-nums" }}
              >
                {formatMetric(format, v)}
              </text>
            </g>
          ))}

          {/* x axis time labels */}
          {xTicks.map((t, i) => {
            const anchor =
              i === 0 ? "start" : i === xTicks.length - 1 ? "end" : "middle";
            return (
              <text
                key={`x-${i}`}
                x={xScale(t)}
                y={PAD.top + plotH + 14}
                textAnchor={anchor}
                fontSize={10}
                fill="var(--viz-muted)"
                style={{ fontVariantNumeric: "tabular-nums" }}
              >
                {formatTime(new Date(t).toISOString())}
              </text>
            );
          })}

          {!hasData ? (
            <text
              x={width / 2}
              y={HEIGHT / 2}
              textAnchor="middle"
              fontSize={11}
              fill="var(--viz-muted)"
            >
              No data
            </text>
          ) : (
            series.map((s) => {
              const d = buildPath(s.points, xScale, yScale);
              return (
                <path
                  key={s.label}
                  d={d}
                  fill="none"
                  stroke={s.colorVar}
                  strokeWidth={2}
                  strokeLinejoin="round"
                  strokeLinecap="round"
                />
              );
            })
          )}

          {/* hover crosshair + points */}
          {hoverTime != null && (
            <line
              x1={xScale(hoverTime)}
              x2={xScale(hoverTime)}
              y1={PAD.top}
              y2={PAD.top + plotH}
              stroke="var(--viz-baseline)"
              strokeWidth={1}
            />
          )}
          {hoverTime != null &&
            series.map((s) => {
              const p = s.points.find(
                (pt) => Date.parse(pt.bucket) === hoverTime,
              );
              if (!p || p.value == null) return null;
              return (
                <circle
                  key={s.label}
                  cx={xScale(hoverTime)}
                  cy={yScale(p.value)}
                  r={3.5}
                  fill={s.colorVar}
                  stroke="var(--viz-surface)"
                  strokeWidth={2}
                />
              );
            })}
        </svg>
      )}

      {width > 0 && hoverTime != null && (
        <Tooltip
          x={xScale(hoverTime)}
          containerWidth={width}
          time={new Date(hoverTime).toISOString()}
          rows={series
            .map((s) => {
              const p = s.points.find(
                (pt) => Date.parse(pt.bucket) === hoverTime,
              );
              return p?.value == null
                ? null
                : {
                    label: s.label,
                    colorVar: s.colorVar,
                    value: formatMetric(format, p.value),
                  };
            })
            .filter((r): r is NonNullable<typeof r> => r != null)}
        />
      )}
    </div>
  );
}

function buildPath(
  points: { bucket: string; value?: number }[],
  xScale: (t: number) => number,
  yScale: (v: number) => number,
): string {
  let d = "";
  let pen = false;
  for (const p of points) {
    if (p.value == null) {
      pen = false;
      continue;
    }
    const x = xScale(Date.parse(p.bucket));
    const y = yScale(p.value);
    d += `${pen ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)} `;
    pen = true;
  }
  return d.trim();
}

function Tooltip({
  x,
  containerWidth,
  time,
  rows,
}: {
  x: number;
  containerWidth: number;
  time: string;
  rows: { label: string; colorVar: string; value: string }[];
}) {
  if (rows.length === 0) return null;
  const left = Math.min(Math.max(x + 10, 8), containerWidth - 150);
  return (
    <div
      className="pointer-events-none absolute top-2 z-10 rounded-md border border-neutral-700 bg-neutral-900/95 px-2.5 py-1.5 text-xs shadow-lg"
      style={{ left }}
    >
      <div className="mb-1 text-[10px] text-neutral-500">
        {formatTime(time)}
      </div>
      <div className="flex flex-col gap-0.5">
        {rows.map((r) => (
          <div key={r.label} className="flex items-center gap-2">
            <span
              className="inline-block h-2 w-2 rounded-sm"
              style={{ background: r.colorVar }}
            />
            <span className="text-neutral-400">{r.label}</span>
            <span
              className="ml-auto font-medium text-neutral-100"
              style={{ fontVariantNumeric: "tabular-nums" }}
            >
              {r.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
