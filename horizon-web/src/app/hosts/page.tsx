"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { StatusBadge } from "@/components/Badges";
import { EntitySelect } from "@/components/EntitySelect";
import type { ChartSeries } from "@/components/LineChart";
import { MetricCard } from "@/components/MetricCard";
import { ErrorBox, PageHeader, PageShell } from "@/components/PageShell";
import { RangeControls } from "@/components/RangeControls";
import { listHosts, queryHostMetrics } from "@/lib/api";
import type { MetricFormat } from "@/lib/format";
import { HOST_CHARTS, rangeWindow, resolveRange } from "@/lib/metrics";
import type { Host, MetricKind, MetricPoint } from "@/lib/types";

interface ResolvedChart {
  title: string;
  format: MetricFormat;
  series: ChartSeries[];
}

export default function HostPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <HostDashboard />
    </Suspense>
  );
}

function HostDashboard() {
  const sp = useSearchParams();
  const { interval, range } = resolveRange(sp.get("interval"), sp.get("range"));
  const paramHostId = Number(sp.get("host_id"));

  const [hosts, setHosts] = useState<Host[]>([]);
  const [hostsLoading, setHostsLoading] = useState(true);
  const [charts, setCharts] = useState<ResolvedChart[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadHosts() {
      setHostsLoading(true);
      try {
        const list = await listHosts();
        if (active) setHosts(list);
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "Cannot load hosts.");
        }
      } finally {
        if (active) setHostsLoading(false);
      }
    }

    void loadHosts();

    return () => {
      active = false;
    };
  }, [reloadKey]);

  const hostId = hosts.some((h) => h.id === paramHostId)
    ? paramHostId
    : (hosts[0]?.id ?? null);
  const host = hosts.find((h) => h.id === hostId) ?? null;

  useEffect(() => {
    const id = hostId;
    let active = true;

    async function load() {
      if (id == null) {
        setCharts([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      const { startAt, endAt } = rangeWindow(range);
      const kinds = [
        ...new Set(HOST_CHARTS.flatMap((c) => c.series.map((s) => s.kind))),
      ];

      try {
        const pointsList = await Promise.all(
          kinds.map((kind) =>
            queryHostMetrics({
              metric: kind,
              interval,
              startAt,
              endAt,
              hostIds: [id],
            })
              .then((s) => s[0]?.points ?? [])
              .catch(() => [] as MetricPoint[]),
          ),
        );
        if (!active) return;

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
          setError(e instanceof Error ? e.message : "Cannot load charts.");
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

  return (
    <PageShell>
      <PageHeader title="Hosts" subtitle={host?.agent_uuid}>
        <EntitySelect
          paramKey="host_id"
          value={hostId}
          options={hosts.map((h) => ({ id: h.id, label: h.hostname }))}
          emptyLabel="No hosts"
        />
        {host && <StatusBadge status={host.status} />}
      </PageHeader>

      <div className="mb-6">
        <RangeControls
          interval={interval}
          range={range}
          busy={loading || hostsLoading}
          onRefresh={() => setReloadKey((k) => k + 1)}
        />
      </div>

      {error ? (
        <ErrorBox>{error}</ErrorBox>
      ) : hostsLoading || (loading && charts.length === 0) ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : hostId == null ? (
        <p className="text-sm text-neutral-400">No hosts.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {charts.map((c) => (
            <MetricCard key={c.title} {...c} />
          ))}
        </div>
      )}
    </PageShell>
  );
}
