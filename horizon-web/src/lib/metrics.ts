import type { MetricFormat } from "@/lib/format";
import type { AggregateInterval, MetricKind } from "@/lib/types";

export const INTERVAL_OPTIONS: { value: AggregateInterval; label: string }[] = [
  { value: "1m", label: "1 min" },
  { value: "5m", label: "5 min" },
  { value: "10m", label: "10 min" },
  { value: "1h", label: "1 hour" },
];

export type RangeKey = "1h" | "4h" | "24h" | "1w";
export const RANGE_OPTIONS: { value: RangeKey; label: string; ms: number }[] = [
  { value: "1h", label: "Past 1 Hour", ms: 60 * 60 * 1000 },
  { value: "4h", label: "Past 4 Hours", ms: 4 * 60 * 60 * 1000 },
  { value: "24h", label: "Past 24 Hours", ms: 24 * 60 * 60 * 1000 },
  { value: "1w", label: "Past 1 Week", ms: 7 * 24 * 60 * 60 * 1000 },
];

export const DEFAULT_INTERVAL: AggregateInterval = "1m";
export const DEFAULT_RANGE: RangeKey = "1h";

export const INTERVAL_MAX_RANGE_MS: Record<AggregateInterval, number> = {
  "1m": 3 * 60 * 60 * 1000, // 3 hours
  "5m": 16 * 60 * 60 * 1000, // 16 hours
  "10m": 36 * 60 * 60 * 1000, // 36 hours
  "1h": 8 * 24 * 60 * 60 * 1000, // 8 days
};

function rangeMs(range: RangeKey): number {
  return RANGE_OPTIONS.find((r) => r.value === range)!.ms;
}

export function isComboAllowed(
  interval: AggregateInterval,
  range: RangeKey,
): boolean {
  return rangeMs(range) <= INTERVAL_MAX_RANGE_MS[interval];
}

export function finestIntervalFor(range: RangeKey): AggregateInterval {
  const valid = INTERVAL_OPTIONS.filter(
    (o) => INTERVAL_MAX_RANGE_MS[o.value] >= rangeMs(range),
  );
  return valid[0].value;
}

export interface ChartDef {
  title: string;
  format: MetricFormat;
  series: { label: string; kind: MetricKind; colorVar: string }[];
}

export const HOST_CHARTS: ChartDef[] = [
  {
    title: "CPU Usage",
    format: "percent",
    series: [
      { label: "cpu", kind: "cpu_usage", colorVar: "var(--viz-series-1)" },
    ],
  },
  {
    title: "Memory Usage",
    format: "bytes",
    series: [
      { label: "used", kind: "memory_used", colorVar: "var(--viz-series-1)" },
    ],
  },
  {
    title: "Disk Used",
    format: "bytes",
    series: [
      { label: "used", kind: "disk_used", colorVar: "var(--viz-series-1)" },
    ],
  },
  {
    title: "Network",
    format: "rate",
    series: [
      { label: "rx", kind: "net_rx_rate", colorVar: "var(--viz-series-1)" },
      { label: "tx", kind: "net_tx_rate", colorVar: "var(--viz-series-2)" },
    ],
  },
  {
    title: "Load Average",
    format: "load",
    series: [
      { label: "1m", kind: "load_avg_1", colorVar: "var(--viz-series-1)" },
      { label: "5m", kind: "load_avg_5", colorVar: "var(--viz-series-2)" },
      { label: "15m", kind: "load_avg_15", colorVar: "var(--viz-series-3)" },
    ],
  },
];
