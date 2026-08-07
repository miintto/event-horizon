export type MetricFormat = "percent" | "bytes" | "rate" | "load" | "count";

export const MIB = 1024 * 1024;

function formatBytes(value: number): string {
  const units = ["B", "KB", "MB", "GB", "TB", "PB"];
  let v = value;
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i += 1;
  }
  const digits = v >= 100 || i === 0 ? 0 : 1;
  return `${v.toFixed(digits)} ${units[i]}`;
}

export function formatMetric(format: MetricFormat, value: number): string {
  switch (format) {
    case "percent":
      return `${value.toFixed(value >= 100 ? 0 : 1)}%`;
    case "bytes":
      return formatBytes(value);
    case "rate":
      return `${formatBytes(value)}/s`;
    case "load":
      return value.toFixed(2);
    case "count":
      return value.toFixed(0);
  }
}

export function formatCores(value: string | number): string {
  return String(Number(value));
}

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

export function formatTime(iso: string): string {
  const d = new Date(iso);
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return `${pad2(d.getMonth() + 1)}-${pad2(d.getDate())} ${formatTime(iso)}`;
}

export function formatRelative(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  if (!Number.isFinite(diffMs)) return "—";

  const sec = Math.max(0, Math.floor(diffMs / 1000));
  if (sec < 60) return `${sec}s ago`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ago`;
  const hour = Math.floor(min / 60);
  if (hour < 24) return `${hour}h ago`;
  return `${Math.floor(hour / 24)}d ago`;
}
