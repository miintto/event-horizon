"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { StatusBadge, WorkloadBadge } from "@/components/Badges";
import type { ChartSeries } from "@/components/LineChart";
import { MetricCard } from "@/components/MetricCard";
import { ErrorBox, PageHeader, PageShell } from "@/components/PageShell";
import { RangeControls } from "@/components/RangeControls";
import {
  getContainers,
  getWorkloads,
  listHosts,
  queryContainerMetrics,
  queryHostMetrics,
} from "@/lib/api";
import type { MetricFormat } from "@/lib/format";
import { rangeWindow, resolveRange, SERIES_COLORS } from "@/lib/metrics";
import type {
  Container,
  ContainerMetricKind,
  ContainerMetricSeries,
  Host,
  HostMetricSeries,
  MetricKind,
  MetricPoint,
  Workload,
} from "@/lib/types";

interface ResolvedChart {
  title: string;
  format: MetricFormat;
  series: ChartSeries[];
}

const HOST_SUMMARY_CHARTS: {
  title: string;
  kind: MetricKind;
  format: MetricFormat;
}[] = [
  { title: "CPU Usage", kind: "cpu_usage", format: "percent" },
  { title: "Memory Used", kind: "memory_used", format: "bytes" },
];

const WORKLOAD_SUMMARY_CHARTS: {
  title: string;
  kind: ContainerMetricKind;
  format: MetricFormat;
}[] = [
  { title: "CPU (cores)", kind: "cpu_usage", format: "load" },
  { title: "Memory", kind: "memory_used", format: "bytes" },
];

export default function DashboardPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <Overview />
    </Suspense>
  );
}

function Overview() {
  const sp = useSearchParams();
  const { interval, range } = resolveRange(sp.get("interval"), sp.get("range"));

  const [hosts, setHosts] = useState<Host[]>([]);
  const [workloads, setWorkloads] = useState<Workload[]>([]);
  const [hostCharts, setHostCharts] = useState<ResolvedChart[]>([]);
  const [workloadCharts, setWorkloadCharts] = useState<ResolvedChart[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      const { startAt, endAt } = rangeWindow(range);

      try {
        const [hostList, workloadList, containerList] = await Promise.all([
          listHosts(),
          getWorkloads().catch(() => [] as Workload[]),
          getContainers().catch(() => [] as Container[]),
        ]);
        if (!active) return;
        setHosts(hostList);
        setWorkloads(workloadList);

        const hostIds = hostList.map((h) => h.id);

        const workloadIdByContainer = new Map<number, number>();
        for (const c of containerList) {
          if (c.workload_id != null) {
            workloadIdByContainer.set(c.id, c.workload_id);
          }
        }
        const containerIds = [...workloadIdByContainer.keys()];

        const [hostSeries, workloadSeries] = await Promise.all([
          Promise.all(
            HOST_SUMMARY_CHARTS.map((c) =>
              hostIds.length === 0
                ? Promise.resolve([] as HostMetricSeries[])
                : queryHostMetrics({
                    metric: c.kind,
                    interval,
                    startAt,
                    endAt,
                    hostIds,
                  }).catch(() => [] as HostMetricSeries[]),
            ),
          ),
          Promise.all(
            WORKLOAD_SUMMARY_CHARTS.map((c) =>
              containerIds.length === 0
                ? Promise.resolve([] as ContainerMetricSeries[])
                : queryContainerMetrics({
                    metric: c.kind,
                    interval,
                    startAt,
                    endAt,
                    containerIds,
                  }).catch(() => [] as ContainerMetricSeries[]),
            ),
          ),
        ]);
        if (!active) return;

        const hostNameById = new Map(hostList.map((h) => [h.id, h.hostname]));
        const hostColorById = new Map(
          hostList.map((h, i) => [
            h.id,
            SERIES_COLORS[i % SERIES_COLORS.length],
          ]),
        );

        setHostCharts(
          HOST_SUMMARY_CHARTS.map((c, i) => ({
            title: c.title,
            format: c.format,
            series: hostSeries[i].map((s) => ({
              label: hostNameById.get(s.host_id) ?? `#${s.host_id}`,
              colorVar: hostColorById.get(s.host_id) ?? SERIES_COLORS[0],
              points: s.points,
            })),
          })),
        );

        const workloadColorById = new Map(
          workloadList.map((w, i) => [
            w.id,
            SERIES_COLORS[i % SERIES_COLORS.length],
          ]),
        );

        setWorkloadCharts(
          WORKLOAD_SUMMARY_CHARTS.map((c, i) => {
            const pointsByWorkload = sumByWorkload(
              workloadSeries[i],
              workloadIdByContainer,
            );
            return {
              title: c.title,
              format: c.format,
              series: workloadList
                .filter((w) => pointsByWorkload.has(w.id))
                .map((w) => ({
                  label: w.name,
                  colorVar: workloadColorById.get(w.id) ?? SERIES_COLORS[0],
                  points: pointsByWorkload.get(w.id) ?? [],
                })),
            };
          }),
        );
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "Cannot load hosts.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [interval, range, reloadKey]);

  function containerHref(workloadId: number) {
    const params = new URLSearchParams(sp.toString());
    params.delete("container_id");
    params.set("workload_id", String(workloadId));
    return `/workloads/containers?${params.toString()}`;
  }

  return (
    <PageShell>
      <PageHeader
        title="Overview"
        subtitle="A lightweight infrastructure monitoring dashboard"
      />

      <div className="mb-6">
        <RangeControls
          interval={interval}
          range={range}
          busy={loading}
          onRefresh={() => setReloadKey((k) => k + 1)}
        />
      </div>

      {error ? (
        <ErrorBox>
          <p className="font-medium">Fail to load API Server</p>
          <p className="mt-1 text-red-400/80">{error}</p>
          <p className="mt-2 text-xs text-neutral-500">
            Check that horizon-api is running and NEXT_PUBLIC_API_URL is set.
          </p>
        </ErrorBox>
      ) : loading && hostCharts.length === 0 ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : (
        <>
          <section className="mt-8">
            <BlockTitle>Host Metrics</BlockTitle>
            <div className="mb-6 grid gap-4 sm:grid-cols-2">
              {hostCharts.map((c) => (
                <MetricCard key={c.title} {...c} />
              ))}
            </div>

            <BlockTitle>Host Status</BlockTitle>
            {hosts.length === 0 ? (
              <p className="text-sm text-neutral-400">No hosts.</p>
            ) : (
              <ul className="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-4">
                {hosts.map((host) => (
                  <li key={host.id}>
                    <Link
                      href={`/hosts?host_id=${host.id}`}
                      className="flex h-full flex-col gap-2 rounded-lg border border-neutral-800 bg-neutral-900 p-4 hover:border-neutral-700 hover:bg-neutral-800/60"
                    >
                      <p
                        title={host.hostname}
                        className="truncate font-medium text-neutral-100"
                      >
                        {host.hostname}
                      </p>
                      <StatusBadge status={host.status} />
                      <p
                        title={host.agent_uuid}
                        className="mt-auto truncate text-xs text-neutral-500"
                      >
                        {host.agent_uuid}
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="mt-12">
            {workloads.length === 0 ? (
              <p className="text-sm text-neutral-400">No workloads.</p>
            ) : (
              <>
                <BlockTitle>Workload Metrics</BlockTitle>
                <div className="mb-6 grid gap-4 sm:grid-cols-2">
                  {workloadCharts.map((c) => (
                    <MetricCard key={c.title} {...c} />
                  ))}
                </div>

                <BlockTitle>Workload Status</BlockTitle>
                <ul className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-4">
                  {workloads.map((w) => (
                    <li key={w.id}>
                      <Link
                        href={containerHref(w.id)}
                        className="flex h-full flex-col gap-2 rounded-lg border border-neutral-800 bg-neutral-900 p-4 hover:border-neutral-700 hover:bg-neutral-800/60"
                      >
                        <p
                          title={w.name}
                          className="truncate font-medium text-neutral-100"
                        >
                          {w.name}
                        </p>
                        <WorkloadBadge running={w.running_count ?? 0} />
                        <p className="mt-auto truncate text-xs text-neutral-500">
                          {plural(w.running_count ?? 0, "container")}
                        </p>
                      </Link>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>
        </>
      )}
    </PageShell>
  );
}

function BlockTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="mb-2 text-xs font-medium tracking-wide text-neutral-500 uppercase">
      {children}
    </h3>
  );
}

function plural(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}

function sumByWorkload(
  series: ContainerMetricSeries[],
  workloadIdByContainer: Map<number, number>,
): Map<number, MetricPoint[]> {
  const bucketsByWorkload = new Map<number, Map<string, number>>();

  for (const s of series) {
    const workloadId = workloadIdByContainer.get(s.container_id);
    if (workloadId == null) continue;

    let buckets = bucketsByWorkload.get(workloadId);
    if (!buckets) {
      buckets = new Map<string, number>();
      bucketsByWorkload.set(workloadId, buckets);
    }
    for (const p of s.points) {
      if (p.value == null) continue;
      buckets.set(p.bucket, (buckets.get(p.bucket) ?? 0) + p.value);
    }
  }

  const result = new Map<number, MetricPoint[]>();
  for (const [workloadId, buckets] of bucketsByWorkload) {
    result.set(
      workloadId,
      [...buckets.entries()]
        .sort((a, b) => Date.parse(a[0]) - Date.parse(b[0]))
        .map(([bucket, value]) => ({ bucket, value })),
    );
  }
  return result;
}
