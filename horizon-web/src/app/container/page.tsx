"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { ChartSeries } from "@/components/LineChart";
import { MetricCard } from "@/components/MetricCard";
import { RangeControls } from "@/components/RangeControls";
import { getContainer, queryContainerMetrics } from "@/lib/api";
import type { MetricFormat } from "@/lib/format";
import {
  CONTAINER_CHARTS,
  DEFAULT_INTERVAL,
  DEFAULT_RANGE,
  finestIntervalFor,
  INTERVAL_OPTIONS,
  isComboAllowed,
  RANGE_OPTIONS,
  type RangeKey,
} from "@/lib/metrics";
import type {
  AggregateInterval,
  Container,
  ContainerMetricKind,
  MetricPoint,
} from "@/lib/types";

interface ResolvedChart {
  title: string;
  format: MetricFormat;
  series: ChartSeries[];
}

export default function ContainerPage() {
  return (
    <Suspense fallback={<Shell>Loading……</Shell>}>
      <ContainerDetail />
    </Suspense>
  );
}

function ContainerDetail() {
  const sp = useSearchParams();
  const containerId = Number(sp.get("container_id"));

  const rawInterval = sp.get("interval");
  const parsedInterval: AggregateInterval = INTERVAL_OPTIONS.some(
    (o) => o.value === rawInterval,
  )
    ? (rawInterval as AggregateInterval)
    : DEFAULT_INTERVAL;
  const rawRange = sp.get("range");
  const rangeKey: RangeKey = RANGE_OPTIONS.some((o) => o.value === rawRange)
    ? (rawRange as RangeKey)
    : DEFAULT_RANGE;
  const interval: AggregateInterval = isComboAllowed(parsedInterval, rangeKey)
    ? parsedInterval
    : finestIntervalFor(rangeKey);

  const [container, setContainer] = useState<Container | null>(null);
  const [charts, setCharts] = useState<ResolvedChart[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!Number.isFinite(containerId) || containerId <= 0) return;

    let active = true;

    async function load() {
      setLoading(true);
      setError(null);

      const endAt = new Date();
      const rangeMs = RANGE_OPTIONS.find((r) => r.value === rangeKey)!.ms;
      const startAt = new Date(endAt.getTime() - rangeMs);
      const kinds = [
        ...new Set(
          CONTAINER_CHARTS.flatMap((c) => c.series.map((s) => s.kind)),
        ),
      ];

      try {
        const [containerRes, pointsList] = await Promise.all([
          getContainer(containerId).catch(() => null),
          Promise.all(
            kinds.map((kind) =>
              queryContainerMetrics({
                metric: kind,
                interval,
                startAt: startAt.toISOString(),
                endAt: endAt.toISOString(),
                containerIds: [containerId],
              })
                .then((s) => s[0]?.points ?? [])
                .catch(() => [] as MetricPoint[]),
            ),
          ),
        ]);
        if (!active) return;
        setContainer(containerRes);
        const pointsByKind = new Map<ContainerMetricKind, MetricPoint[]>(
          kinds.map((k, i) => [k, pointsList[i]]),
        );
        setCharts(
          CONTAINER_CHARTS.map((c) => ({
            title: c.title,
            format: c.format,
            series: c.series.map((s) => ({
              label: s.label,
              colorVar: s.colorVar,
              points: pointsByKind.get(s.kind) ?? [],
            })),
          })),
        );
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
  }, [containerId, interval, rangeKey, reloadKey]);

  const validContainer = Number.isFinite(containerId) && containerId > 0;

  return (
    <Shell>
      <header className="mb-6">
        {container && (
          <Link
            href={`/host?host_id=${container.host_id}`}
            className="mb-2 inline-block text-xs text-neutral-500 hover:text-neutral-300"
          >
            ← host #{container.host_id}
          </Link>
        )}
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-neutral-100">
            {container?.name ??
              (containerId ? `container #${containerId}` : "Container")}
          </h1>
          {container && <StateBadge state={container.state} />}
        </div>
        {container && (
          <p className="mt-1 text-xs text-neutral-500">{container.image}</p>
        )}
      </header>

      {!validContainer ? (
        <div className="rounded-md border border-red-900/50 bg-red-950/40 p-4 text-sm text-red-300">
          Invalid container_id
        </div>
      ) : (
        <>
          <div className="mb-6">
            <RangeControls
              interval={interval}
              range={rangeKey}
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
            <div className="grid gap-4 sm:grid-cols-2">
              {charts.map((c) => (
                <MetricCard key={c.title} {...c} />
              ))}
            </div>
          )}
        </>
      )}
    </Shell>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
      {children}
    </main>
  );
}

function StateBadge({ state }: { state: Container["state"] }) {
  const running = state === "running";
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium">
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
