import { LineChart, type ChartSeries } from "@/components/LineChart";
import { formatMetric, type MetricFormat } from "@/lib/format";

export interface MetricCardProps {
  title: string;
  format: MetricFormat;
  series: ChartSeries[];
}

function latestValue(points: { value?: number }[]): number | undefined {
  for (let i = points.length - 1; i >= 0; i -= 1) {
    if (points[i].value != null) return points[i].value;
  }
  return undefined;
}

export function MetricCard({ title, format, series }: MetricCardProps) {
  const single = series.length === 1;

  return (
    <div className="viz rounded-lg border border-neutral-800 bg-neutral-900 p-3">
      <div className="mb-3 flex items-baseline justify-between gap-4">
        <h3 className="text-sm font-semibold text-neutral-200">{title}</h3>
        {single && (
          <span
            className="text-xl font-semibold text-neutral-100"
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {formatLatest(format, series[0].points)}
          </span>
        )}
      </div>

      <LineChart series={series} format={format} />

      {!single && (
        <div className="mt-2 flex flex-wrap justify-end gap-x-4 gap-y-1">
          {series.map((s) => (
            <span key={s.label} className="flex items-center gap-1.5 text-xs">
              <span
                className="inline-block h-2 w-2 rounded-sm"
                style={{ background: s.colorVar }}
              />
              <span className="text-neutral-400">{s.label}</span>
              <span
                className="font-medium text-neutral-100"
                style={{ fontVariantNumeric: "tabular-nums" }}
              >
                {formatLatest(format, s.points)}
              </span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function formatLatest(
  format: MetricFormat,
  points: { value?: number }[],
): string {
  const v = latestValue(points);
  return v != null ? formatMetric(format, v) : "—";
}
