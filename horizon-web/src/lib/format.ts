export type MetricFormat = "percent" | "bytes" | "rate" | "load" | "count";

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

export function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}
