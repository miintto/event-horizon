"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { ChartSeries } from "@/components/LineChart";
import { MetricCard } from "@/components/MetricCard";
import { RangeControls } from "@/components/RangeControls";
import {
  getHost,
  listContainers,
  queryContainerMetrics,
  queryHostMetrics,
} from "@/lib/api";
import type { MetricFormat } from "@/lib/format";
import { rangeWindow, resolveRange } from "@/lib/metrics";
import type { Container, ContainerMetricSeries, Host } from "@/lib/types";

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
  const [containers, setContainers] = useState<Container[]>([]);
  const [hostCharts, setHostCharts] = useState<ResolvedChart[]>([]);
  const [containerCharts, setContainerCharts] = useState<ResolvedChart[]>([]);
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

      const hostPoints = (metric: "cpu_usage" | "memory_used") =>
        queryHostMetrics({
          metric,
          interval,
          startAt,
          endAt,
          hostIds: [hostId],
        })
          .then((s) => s[0]?.points ?? [])
          .catch(() => []);

      try {
        const containerList = await listContainers(hostId).catch(
          () => [] as Container[],
        );
        const containerIds = containerList.map((c) => c.id);
        const containerSeries = (metric: "cpu_usage" | "memory_used") =>
          containerIds.length === 0
            ? Promise.resolve([] as ContainerMetricSeries[])
            : queryContainerMetrics({
                metric,
                interval,
                startAt,
                endAt,
                containerIds,
              }).catch(() => [] as ContainerMetricSeries[]);

        const [hostRes, hostCpu, hostMem, containerCpu, containerMem] =
          await Promise.all([
            getHost(hostId).catch(() => null),
            hostPoints("cpu_usage"),
            hostPoints("memory_used"),
            containerSeries("cpu_usage"),
            containerSeries("memory_used"),
          ]);
        if (!active) return;

        const nameById = new Map(
          containerList.map((c) => [c.id, c.name] as const),
        );
        const containerChart = (
          title: string,
          format: MetricFormat,
          series: ContainerMetricSeries[],
        ): ResolvedChart => ({
          title,
          format,
          series: series.map((s, i) => ({
            label: nameById.get(s.container_id) ?? `#${s.container_id}`,
            colorVar: SERIES_COLORS[i % SERIES_COLORS.length],
            points: s.points,
          })),
        });

        setHost(hostRes);
        setContainers(containerList);
        setHostCharts([
          {
            title: "CPU",
            format: "percent",
            series: [
              {
                label: "cpu",
                colorVar: "var(--viz-series-1)",
                points: hostCpu,
              },
            ],
          },
          {
            title: "Memory",
            format: "bytes",
            series: [
              {
                label: "used",
                colorVar: "var(--viz-series-1)",
                points: hostMem,
              },
            ],
          },
        ]);
        setContainerCharts([
          containerChart("CPU (cores)", "load", containerCpu),
          containerChart("Memory", "bytes", containerMem),
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
  }, [hostId, interval, range, reloadKey]);

  const validHost = Number.isFinite(hostId) && hostId > 0;
  const detailQuery = new URLSearchParams({
    host_id: String(hostId),
    interval,
    range,
  }).toString();

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
                <div className="mt-3 flex justify-end">
                  <Link
                    href={`/host/metrics?${detailQuery}`}
                    className="group inline-flex items-center gap-0.5 text-sm font-medium text-neutral-400 transition-colors hover:text-neutral-100"
                  >
                    More
                    <ChevronRight />
                  </Link>
                </div>
              </section>

              <section className="mt-8">
                <h2 className="mb-3 text-sm font-medium text-neutral-400">
                  Containers {containers.length > 0 && `(${containers.length})`}
                </h2>
                {containers.length === 0 ? (
                  <p className="text-sm text-neutral-500">No containers.</p>
                ) : (
                  <>
                    {containerCharts.some((c) => c.series.length > 0) && (
                      <div className="mb-4 grid gap-4 sm:grid-cols-2">
                        {containerCharts.map((c) => (
                          <MetricCard key={c.title} {...c} />
                        ))}
                      </div>
                    )}
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
                                {c.image}
                              </p>
                            </div>
                            <StateBadge state={c.state} />
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </section>
            </>
          )}
        </>
      )}
    </Shell>
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

function ChevronRight() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className="transition-transform group-hover:translate-x-0.5"
    >
      <path d="m9 18 6-6-6-6" />
    </svg>
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
