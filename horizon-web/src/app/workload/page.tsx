"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { ChartSeries } from "@/components/LineChart";
import { MetricCard } from "@/components/MetricCard";
import { RangeControls } from "@/components/RangeControls";
import { getContainers, getWorkload, queryContainerMetrics } from "@/lib/api";
import type { MetricFormat } from "@/lib/format";
import { rangeWindow, resolveRange } from "@/lib/metrics";
import type { Container, ContainerMetricSeries, Workload } from "@/lib/types";

interface ResolvedChart {
  title: string;
  format: MetricFormat;
  series: ChartSeries[];
}

const SERIES_COLORS = [
  "var(--viz-series-1)",
  "var(--viz-series-2)",
  "var(--viz-series-3)",
  "var(--viz-series-4)",
  "var(--viz-series-5)",
  "var(--viz-series-6)",
  "var(--viz-series-7)",
  "var(--viz-series-8)",
];

export default function WorkloadPage() {
  return (
    <Suspense fallback={<Shell>Loading……</Shell>}>
      <WorkloadDetail />
    </Suspense>
  );
}

function WorkloadDetail() {
  const sp = useSearchParams();
  const workloadId = Number(sp.get("workload_id"));
  const { interval, range } = resolveRange(sp.get("interval"), sp.get("range"));

  const [workload, setWorkload] = useState<Workload | null>(null);
  const [containers, setContainers] = useState<Container[]>([]);
  const [charts, setCharts] = useState<ResolvedChart[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!Number.isFinite(workloadId) || workloadId <= 0) return;

    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      const { startAt, endAt } = rangeWindow(range);

      try {
        const containerList = await getContainers({ workloadId }).catch(
          () => [] as Container[],
        );
        const containerIds = containerList.map((c) => c.id);
        const series = (metric: "cpu_usage" | "memory_used") =>
          containerIds.length === 0
            ? Promise.resolve([] as ContainerMetricSeries[])
            : queryContainerMetrics({
                metric,
                interval,
                startAt,
                endAt,
                containerIds,
              }).catch(() => [] as ContainerMetricSeries[]);

        const [workloadRes, cpu, mem] = await Promise.all([
          getWorkload(workloadId).catch(() => null),
          series("cpu_usage"),
          series("memory_used"),
        ]);
        if (!active) return;

        const nameById = new Map(
          containerList.map((c) => [c.id, c.name] as const),
        );
        const chart = (
          title: string,
          format: MetricFormat,
          s: ContainerMetricSeries[],
        ): ResolvedChart => ({
          title,
          format,
          series: s.map((x, i) => ({
            label: nameById.get(x.container_id) ?? `#${x.container_id}`,
            colorVar: SERIES_COLORS[i % SERIES_COLORS.length],
            points: x.points,
          })),
        });

        setWorkload(workloadRes);
        setContainers(containerList);
        setCharts([
          chart("CPU (cores)", "load", cpu),
          chart("Memory", "bytes", mem),
        ]);
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "불러오지 못했습니다");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [workloadId, interval, range, reloadKey]);

  const validWorkload = Number.isFinite(workloadId) && workloadId > 0;

  return (
    <Shell>
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-neutral-100">
            {workload?.name ??
              (workloadId ? `workload #${workloadId}` : "Workload")}
          </h1>
        </div>
      </header>

      {!validWorkload ? (
        <div className="rounded-md border border-red-900/50 bg-red-950/40 p-4 text-sm text-red-300">
          Invalid workload_id
        </div>
      ) : (
        <>
          <div className="mb-6">
            <RangeControls
              interval={interval}
              range={range}
              busy={loading}
              onRefresh={() => setReloadKey((k) => k + 1)}
            />
          </div>

          {error ? (
            <div className="rounded-md border border-red-900/50 bg-red-950/40 p-4 text-sm text-red-300">
              {error}
            </div>
          ) : loading && charts.length === 0 ? (
            <p className="text-sm text-neutral-500">Loading…</p>
          ) : (
            <>
              {charts.some((c) => c.series.length > 0) && (
                <div className="mb-8 grid gap-4 sm:grid-cols-2">
                  {charts.map((c) => (
                    <MetricCard key={c.title} {...c} />
                  ))}
                </div>
              )}

              <section>
                <h2 className="mb-3 text-sm font-medium text-neutral-400">
                  Containers {containers.length > 0 && `(${containers.length})`}
                </h2>
                {containers.length === 0 ? (
                  <p className="text-sm text-neutral-500">No containers.</p>
                ) : (
                  <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
                    {containers.map((c) => (
                      <li key={c.id}>
                        <Link
                          href={`/container?container_id=${c.id}`}
                          className="flex items-center justify-between px-4 py-3 hover:bg-neutral-800/60"
                        >
                          <div className="min-w-0">
                            <p className="truncate font-medium text-neutral-100">
                              {c.name}
                            </p>
                            <p className="truncate text-xs text-neutral-500">
                              host #{c.host_id} · {c.image}
                            </p>
                          </div>
                          <StateBadge state={c.state} />
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </>
          )}
        </>
      )}
    </Shell>
  );
}

function CountBadge({ running, total }: { running: number; total: number }) {
  const active = running > 0;
  return (
    <span className="inline-flex shrink-0 items-center gap-1.5 text-xs font-medium">
      <span
        className={`inline-block h-2 w-2 rounded-full ${
          active ? "bg-emerald-500" : "bg-neutral-600"
        }`}
      />
      <span className={active ? "text-emerald-400" : "text-neutral-400"}>
        {running}/{total} running
      </span>
    </span>
  );
}

function StateBadge({ state }: { state: Container["state"] }) {
  const running = state === "running";
  return (
    <span className="inline-flex shrink-0 items-center gap-1.5 text-xs font-medium">
      <span
        className={`inline-block h-2 w-2 rounded-full ${
          running ? "bg-emerald-500" : "bg-neutral-600"
        }`}
      />
      <span className={running ? "text-emerald-400" : "text-neutral-400"}>
        {state}
      </span>
    </span>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
      {children}
    </main>
  );
}
