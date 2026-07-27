"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { ChartSeries } from "@/components/LineChart";
import { MetricCard } from "@/components/MetricCard";
import { RangeControls } from "@/components/RangeControls";
import { getHost, queryHostMetrics } from "@/lib/api";
import type { MetricFormat } from "@/lib/format";
import { HOST_CHARTS, rangeWindow, resolveRange } from "@/lib/metrics";
import type { Host, MetricKind, MetricPoint } from "@/lib/types";

interface ResolvedChart {
  title: string;
  format: MetricFormat;
  series: ChartSeries[];
}

export default function HostMetricsPage() {
  return (
    <Suspense fallback={<Shell>Loading……</Shell>}>
      <HostMetrics />
    </Suspense>
  );
}

function HostMetrics() {
  const sp = useSearchParams();
  const hostId = Number(sp.get("host_id"));
  const { interval, range } = resolveRange(sp.get("interval"), sp.get("range"));

  const [host, setHost] = useState<Host | null>(null);
  const [charts, setCharts] = useState<ResolvedChart[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!Number.isFinite(hostId) || hostId <= 0) return;

    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      const { startAt, endAt } = rangeWindow(range);
      const kinds = [
        ...new Set(HOST_CHARTS.flatMap((c) => c.series.map((s) => s.kind))),
      ];

      try {
        const [hostRes, pointsList] = await Promise.all([
          getHost(hostId).catch(() => null),
          Promise.all(
            kinds.map((kind) =>
              queryHostMetrics({
                metric: kind,
                interval,
                startAt,
                endAt,
                hostIds: [hostId],
              })
                .then((s) => s[0]?.points ?? [])
                .catch(() => [] as MetricPoint[]),
            ),
          ),
        ]);
        if (!active) return;
        setHost(hostRes);
        const pointsByKind = new Map<MetricKind, MetricPoint[]>(
          kinds.map((k, i) => [k, pointsList[i]]),
        );
        setCharts(
          HOST_CHARTS.map((c) => ({
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
  }, [hostId, interval, range, reloadKey]);

  const validHost = Number.isFinite(hostId) && hostId > 0;

  return (
    <Shell>
      <header className="mb-6">
        <Link
          href={`/host?host_id=${hostId}`}
          className="mb-2 inline-block text-xs text-neutral-500 hover:text-neutral-300"
        >
          ← {host?.hostname ?? `host #${hostId}`}
        </Link>
        <h1 className="text-2xl font-semibold text-neutral-100">
          Host metrics
        </h1>
      </header>

      {!validHost ? (
        <div className="rounded-md border border-red-900/50 bg-red-950/40 p-4 text-sm text-red-300">
          Invalid host_id
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
