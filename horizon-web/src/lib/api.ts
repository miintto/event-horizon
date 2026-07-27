import type {
  AggregateInterval,
  Container,
  ContainerMetricKind,
  ContainerMetricSeries,
  Host,
  HostMetricSeries,
  MetricKind,
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`horizon-api GET ${path} failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function listHosts(): Promise<Host[]> {
  return apiGet<Host[]>("/api/hosts");
}

export function getHost(hostId: number): Promise<Host> {
  return apiGet<Host>(`/api/hosts/${hostId}`);
}

export interface MetricQuery {
  metric: MetricKind;
  interval: AggregateInterval;
  startAt: string; // ISO 8601
  endAt: string; // ISO 8601
  hostIds?: number[];
}

export function queryHostMetrics(
  query: MetricQuery,
): Promise<HostMetricSeries[]> {
  const params = new URLSearchParams({
    metric: query.metric,
    interval: query.interval,
    start_at: query.startAt,
    end_at: query.endAt,
  });
  for (const id of query.hostIds ?? []) {
    params.append("host_ids", String(id));
  }
  return apiGet<HostMetricSeries[]>(`/api/metrics/hosts?${params.toString()}`);
}

export function listContainers(hostId?: number): Promise<Container[]> {
  const params = new URLSearchParams();
  if (hostId != null) {
    params.set("host_id", String(hostId));
  }
  const qs = params.toString();
  return apiGet<Container[]>(`/api/containers${qs ? `?${qs}` : ""}`);
}

export function getContainer(containerId: number): Promise<Container> {
  return apiGet<Container>(`/api/containers/${containerId}`);
}

export interface ContainerMetricQuery {
  metric: ContainerMetricKind;
  interval: AggregateInterval;
  startAt: string; // ISO 8601
  endAt: string; // ISO 8601
  containerIds?: number[];
}

export function queryContainerMetrics(
  query: ContainerMetricQuery,
): Promise<ContainerMetricSeries[]> {
  const params = new URLSearchParams({
    metric: query.metric,
    interval: query.interval,
    start_at: query.startAt,
    end_at: query.endAt,
  });
  for (const id of query.containerIds ?? []) {
    params.append("container_ids", String(id));
  }
  return apiGet<ContainerMetricSeries[]>(
    `/api/metrics/containers?${params.toString()}`,
  );
}
