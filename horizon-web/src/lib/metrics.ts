import type { MetricFormat } from "@/lib/format";
import type {
  AggregateInterval,
  ContainerMetricKind,
  MetricKind,
} from "@/lib/types";

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

export function resolveRange(
  rawInterval: string | null,
  rawRange: string | null,
): { interval: AggregateInterval; range: RangeKey } {
  const parsedInterval: AggregateInterval = INTERVAL_OPTIONS.some(
    (o) => o.value === rawInterval,
  )
    ? (rawInterval as AggregateInterval)
    : DEFAULT_INTERVAL;
  const range: RangeKey = RANGE_OPTIONS.some((o) => o.value === rawRange)
    ? (rawRange as RangeKey)
    : DEFAULT_RANGE;
  const interval: AggregateInterval = isComboAllowed(parsedInterval, range)
    ? parsedInterval
    : finestIntervalFor(range);
  return { interval, range };
}

export function rangeWindow(range: RangeKey): {
  startAt: string;
  endAt: string;
} {
  const endAt = new Date();
  const startAt = new Date(endAt.getTime() - rangeMs(range));
  return { startAt: startAt.toISOString(), endAt: endAt.toISOString() };
}

export const SERIES_COLORS = [
  "var(--viz-series-1)",
  "var(--viz-series-2)",
  "var(--viz-series-3)",
  "var(--viz-series-4)",
  "var(--viz-series-5)",
  "var(--viz-series-6)",
  "var(--viz-series-7)",
  "var(--viz-series-8)",
];

export interface ChartDef<K extends string = MetricKind> {
  title: string;
  format: MetricFormat;
  series: { label: string; kind: K; colorVar: string }[];
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

export const CONTAINER_CHARTS: ChartDef<ContainerMetricKind>[] = [
  {
    title: "CPU (cores)",
    format: "load",
    series: [
      { label: "cores", kind: "cpu_usage", colorVar: "var(--viz-series-1)" },
    ],
  },
  {
    title: "Memory",
    format: "bytes",
    series: [
      { label: "used", kind: "memory_used", colorVar: "var(--viz-series-1)" },
      {
        label: "limit",
        kind: "memory_limit",
        colorVar: "var(--viz-threshold)",
      },
    ],
  },
  {
    title: "Network RX",
    format: "rate",
    series: [
      { label: "rx", kind: "net_rx_rate", colorVar: "var(--viz-series-1)" },
    ],
  },
  {
    title: "Network TX",
    format: "rate",
    series: [
      { label: "tx", kind: "net_tx_rate", colorVar: "var(--viz-series-1)" },
    ],
  },
  {
    title: "Block Read",
    format: "rate",
    series: [
      {
        label: "read",
        kind: "block_read_rate",
        colorVar: "var(--viz-series-1)",
      },
    ],
  },
  {
    title: "Block Write",
    format: "rate",
    series: [
      {
        label: "write",
        kind: "block_write_rate",
        colorVar: "var(--viz-series-1)",
      },
    ],
  },
  {
    title: "Processes",
    format: "count",
    series: [{ label: "pids", kind: "pids", colorVar: "var(--viz-series-1)" }],
  },
];
