"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { ChartSeries } from "@/components/LineChart";
import { MetricCard } from "@/components/MetricCard";
import { RangeControls } from "@/components/RangeControls";
import { getHost, getWorkloads, queryHostMetrics } from "@/lib/api";
import type { MetricFormat } from "@/lib/format";
import { HOST_CHARTS, rangeWindow, resolveRange } from "@/lib/metrics";
import type { Host, MetricKind, MetricPoint, Workload } from "@/lib/types";

interface ResolvedChart {
  title: string;
  format: MetricFormat;
  series: ChartSeries[];
}

export default function HostPage() {
  return (
    <Suspense fallback={<Shell>Loading……</Shell>}>
      <HostOverview />
    </Suspense>
  );
}

function HostOverview() {
  const sp = useSearchParams();
  const hostId = Number(sp.get("host_id"));
  const { interval, range } = resolveRange(sp.get("interval"), sp.get("range"));

  const [host, setHost] = useState<Host | null>(null);
  const [workloads, setWorkloads] = useState<Workload[]>([]);
  const [hostCharts, setHostCharts] = useState<ResolvedChart[]>([]);
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
        const [hostRes, workloadList, pointsList] = await Promise.all([
          getHost(hostId).catch(() => null),
          getWorkloads(hostId).catch(() => [] as Workload[]),
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

        const pointsByKind = new Map<MetricKind, MetricPoint[]>(
          kinds.map((k, i) => [k, pointsList[i]]),
        );

        setHost(hostRes);
        setWorkloads(workloadList);
        setHostCharts(
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
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-neutral-100">
            {host?.hostname ?? (hostId ? `host #${hostId}` : "Host")}
          </h1>
          {host && <StatusBadge status={host.status} />}
        </div>
        {host && (
          <p className="mt-1 text-xs text-neutral-500">{host.agent_uuid}</p>
        )}
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
          ) : loading && hostCharts.length === 0 ? (
            <p className="text-sm text-neutral-500">Loading…</p>
          ) : (
            <>
              <section>
                <h2 className="mb-3 text-sm font-medium text-neutral-400">
                  Host
                </h2>
                <div className="grid gap-4 sm:grid-cols-2">
                  {hostCharts.map((c) => (
                    <MetricCard key={c.title} {...c} />
                  ))}
                </div>
              </section>

              <section className="mt-8">
                <h2 className="mb-3 text-sm font-medium text-neutral-400">
                  Workloads {workloads.length > 0 && `(${workloads.length})`}
                </h2>
                {workloads.length === 0 ? (
                  <p className="text-sm text-neutral-500">No workloads.</p>
                ) : (
                  <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
                    {workloads.map((w) => (
                      <li key={w.id}>
                        <Link
                          href={`/workload?workload_id=${w.id}`}
                          className="block px-4 py-3 hover:bg-neutral-800/60"
                        >
                          <p className="truncate font-medium text-neutral-100">
                            {w.name}
                          </p>
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

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
      {children}
    </main>
  );
}

function StatusBadge({ status }: { status: Host["status"] }) {
  const online = status === "online";
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium">
      <span
        className={`inline-block h-2 w-2 rounded-full ${
          online ? "bg-emerald-500" : "bg-neutral-600"
        }`}
      />
      <span className={online ? "text-emerald-400" : "text-neutral-400"}>
        {status}
      </span>
    </span>
  );
}
