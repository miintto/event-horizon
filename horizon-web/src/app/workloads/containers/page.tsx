"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { StateBadge } from "@/components/Badges";
import type { ChartSeries } from "@/components/LineChart";
import { MetricCard } from "@/components/MetricCard";
import { ErrorBox, PageHeader, PageShell } from "@/components/PageShell";
import { RangeControls } from "@/components/RangeControls";
import { getContainers, getWorkload, queryContainerMetrics } from "@/lib/api";
import { type MetricFormat } from "@/lib/format";
import {
  CONTAINER_CHARTS,
  rangeWindow,
  resolveRange,
  SERIES_COLORS,
} from "@/lib/metrics";
import type {
  Container,
  ContainerMetricKind,
  ContainerMetricSeries,
  MetricPoint,
  Workload,
} from "@/lib/types";

import { WorkloadTabs } from "../WorkloadTabs";
import { ContainerList, shortId } from "./ContainerList";

interface ResolvedChart {
  title: string;
  format: MetricFormat;
  series: ChartSeries[];
}

export default function ContainerPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <ContainerDashboard />
    </Suspense>
  );
}

function maxByBucket(seriesList: MetricPoint[][]): MetricPoint[] {
  const byBucket = new Map<string, number>();
  for (const points of seriesList) {
    for (const p of points) {
      if (p.value == null) continue;
      const current = byBucket.get(p.bucket);
      if (current == null || p.value > current) {
        byBucket.set(p.bucket, p.value);
      }
    }
  }
  return [...byBucket.entries()]
    .sort((a, b) => Date.parse(a[0]) - Date.parse(b[0]))
    .map(([bucket, value]) => ({ bucket, value }));
}

function ContainerDashboard() {
  const sp = useSearchParams();
  const { interval, range } = resolveRange(sp.get("interval"), sp.get("range"));
  const paramWorkloadId = Number(sp.get("workload_id"));
  const paramContainerId = Number(sp.get("container_id"));

  const [workload, setWorkload] = useState<Workload | null>(null);
  const [containers, setContainers] = useState<Container[]>([]);
  const [containersLoading, setContainersLoading] = useState(true);
  const [charts, setCharts] = useState<ResolvedChart[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const workloadId =
    Number.isFinite(paramWorkloadId) && paramWorkloadId > 0
      ? paramWorkloadId
      : null;

  useEffect(() => {
    const id = workloadId;
    let active = true;

    async function loadContainers() {
      setWorkload(null);
      setContainers([]);
      if (id == null) {
        setContainersLoading(false);
        return;
      }

      setContainersLoading(true);
      try {
        const [detail, list] = await Promise.all([
          getWorkload(id),
          getContainers({ workloadId: id }),
        ]);
        if (active) {
          setWorkload(detail);
          setContainers(list);
        }
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "Cannot load containers.");
        }
      } finally {
        if (active) setContainersLoading(false);
      }
    }

    void loadContainers();

    return () => {
      active = false;
    };
  }, [workloadId, reloadKey]);

  const containerId = containers.some((c) => c.id === paramContainerId)
    ? paramContainerId
    : null;
  const container = containers.find((c) => c.id === containerId) ?? null;

  useEffect(() => {
    const items =
      containerId != null
        ? containers.filter((c) => c.id === containerId)
        : containers;
    let active = true;

    async function load() {
      if (items.length === 0) {
        setCharts([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      const { startAt, endAt } = rangeWindow(range);
      const containerIds = items.map((c) => c.id);
      const kinds = [
        ...new Set(
          CONTAINER_CHARTS.flatMap((c) => c.series.map((s) => s.kind)),
        ),
      ];

      try {
        const seriesList = await Promise.all(
          kinds.map((kind) =>
            queryContainerMetrics({
              metric: kind,
              interval,
              startAt,
              endAt,
              containerIds,
            }).catch(() => [] as ContainerMetricSeries[]),
          ),
        );
        if (!active) return;

        const pointsByKind = new Map<
          ContainerMetricKind,
          Map<number, MetricPoint[]>
        >(
          kinds.map((k, i) => [
            k,
            new Map(seriesList[i].map((s) => [s.container_id, s.points])),
          ]),
        );
        const pointsOf = (kind: ContainerMetricKind, containerId: number) =>
          pointsByKind.get(kind)?.get(containerId) ?? [];

        const overlay = items.length > 1;

        setCharts(
          CONTAINER_CHARTS.map((chart) => ({
            title: chart.title,
            format: chart.format,
            series: overlay
              ? [
                  ...items.map((c, ci) => ({
                    label: shortId(c),
                    colorVar: SERIES_COLORS[ci % SERIES_COLORS.length],
                    points: pointsOf(chart.series[0].kind, c.id),
                  })),
                  ...chart.series.slice(1).map((s) => ({
                    label: s.label,
                    colorVar: s.colorVar,
                    points: maxByBucket(
                      items.map((c) => pointsOf(s.kind, c.id)),
                    ),
                  })),
                ]
              : chart.series.map((s) => ({
                  label: s.label,
                  colorVar: s.colorVar,
                  points: pointsOf(s.kind, items[0].id),
                })),
          })),
        );
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "Cannot load data.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [containers, containerId, interval, range, reloadKey]);

  function hrefFor(id: number) {
    const params = new URLSearchParams(sp.toString());
    if (id === containerId) {
      params.delete("container_id");
    } else {
      params.set("container_id", String(id));
    }
    const qs = params.toString();
    return `/workloads/containers?${qs}`;
  }

  return (
    <PageShell>
      <PageHeader title={workload?.name ?? "Workload"} />
      <WorkloadTabs workloadId={workloadId} />

      <div className="mb-6">
        <RangeControls
          interval={interval}
          range={range}
          busy={loading || containersLoading}
          onRefresh={() => setReloadKey((k) => k + 1)}
        />
      </div>

      {error ? (
        <ErrorBox>{error}</ErrorBox>
      ) : (
        <>
          <section>
            <h2 className="mb-3 text-sm font-medium text-neutral-400">
              Containers {containers.length > 0 && `(${containers.length})`}
            </h2>
            {containersLoading ? (
              <p className="text-sm text-neutral-500">Loading…</p>
            ) : containers.length === 0 ? (
              <p className="text-sm text-neutral-400">No containers.</p>
            ) : (
              <ContainerList
                containers={containers}
                selectedId={containerId}
                hrefFor={hrefFor}
              />
            )}
          </section>

          {containersLoading || (loading && charts.length === 0) ? (
            <p className="mt-8 text-sm text-neutral-500">Loading…</p>
          ) : containers.length === 0 ? null : (
            <section className="mt-8">
              <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1">
                <h2 className="text-sm font-semibold text-neutral-200">
                  {container
                    ? shortId(container)
                    : `All containers (${containers.length})`}
                </h2>
                {container && <StateBadge state={container.state} />}
                {container && (
                  <span className="truncate text-xs text-neutral-500">
                    {container.name} · {container.image}
                  </span>
                )}
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                {charts.map((c) => (
                  <MetricCard key={c.title} {...c} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </PageShell>
  );
}
