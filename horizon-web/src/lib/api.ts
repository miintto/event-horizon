import { getToken, redirectToLogin } from "@/lib/auth";
import type {
  AggregateInterval,
  Container,
  ContainerMetricKind,
  ContainerMetricSeries,
  Deployment,
  Host,
  HostMetricSeries,
  MetricKind,
  RevisionDefinitionInput,
  Secret,
  SecretListResponse,
  TokenResponse,
  Workload,
  WorkloadRevision,
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiGet<T>(path: string): Promise<T> {
  const token = getToken();
  if (!token) {
    redirectToLogin();
    throw new Error("Unauthorized");
  }

  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 401) {
    redirectToLogin();
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    throw new Error(await describeError(res, "GET", path));
  }
  return res.json() as Promise<T>;
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const token = getToken();
  if (!token) {
    redirectToLogin();
    throw new Error("Unauthorized");
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (res.status === 401) {
    redirectToLogin();
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    throw new Error(await describeError(res, "POST", path));
  }
  return res.json() as Promise<T>;
}

async function apiPut<T>(path: string, body: unknown): Promise<T> {
  const token = getToken();
  if (!token) {
    redirectToLogin();
    throw new Error("Unauthorized");
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (res.status === 401) {
    redirectToLogin();
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    throw new Error(await describeError(res, "PUT", path));
  }
  return res.json() as Promise<T>;
}

async function apiDelete(path: string): Promise<void> {
  const token = getToken();
  if (!token) {
    redirectToLogin();
    throw new Error("Unauthorized");
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 401) {
    redirectToLogin();
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    throw new Error(await describeError(res, "DELETE", path));
  }
}

async function describeError(
  res: Response,
  method: string,
  path: string,
): Promise<string> {
  try {
    const body = await res.json();
    const detail = body?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((d) => {
          const field = Array.isArray(d.loc) ? d.loc.slice(1).join(".") : "";
          return field ? `${field}: ${d.msg}` : d.msg;
        })
        .join("\n");
    }
  } catch {}
  return `horizon-api ${method} ${path} failed (${res.status})`;
}

export async function login(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    throw new Error(
      res.status === 401
        ? "Incorrect email or password"
        : `Sign-in failed (${res.status})`,
    );
  }
  return res.json() as Promise<TokenResponse>;
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

export function getContainers(params?: {
  hostId?: number;
  workloadId?: number;
}): Promise<Container[]> {
  const search = new URLSearchParams();
  if (params?.hostId != null) {
    search.set("host_id", String(params.hostId));
  }
  if (params?.workloadId != null) {
    search.set("workload_id", String(params.workloadId));
  }
  const qs = search.toString();
  return apiGet<Container[]>(`/api/containers${qs ? `?${qs}` : ""}`);
}

export function getContainer(containerId: number): Promise<Container> {
  return apiGet<Container>(`/api/containers/${containerId}`);
}

export function getWorkloads(hostId?: number): Promise<Workload[]> {
  const params = new URLSearchParams();
  if (hostId != null) {
    params.set("host_id", String(hostId));
  }
  const qs = params.toString();
  return apiGet<Workload[]>(`/api/workloads${qs ? `?${qs}` : ""}`);
}

export function getWorkload(workloadId: number): Promise<Workload> {
  return apiGet<Workload>(`/api/workloads/${workloadId}`);
}

export function createWorkload(
  name: string,
  definition: RevisionDefinitionInput,
): Promise<Workload> {
  return apiPost<Workload>("/api/workloads", { name, ...definition });
}

export function getRevisions(workloadId: number): Promise<WorkloadRevision[]> {
  return apiGet<WorkloadRevision[]>(`/api/workloads/${workloadId}/revisions`);
}

export function createRevision(
  workloadId: number,
  definition: RevisionDefinitionInput,
): Promise<WorkloadRevision> {
  return apiPost<WorkloadRevision>(
    `/api/workloads/${workloadId}/revisions`,
    definition,
  );
}

export function getDeployments(params?: {
  hostId?: number;
  workloadId?: number;
}): Promise<Deployment[]> {
  const search = new URLSearchParams();
  if (params?.hostId != null) {
    search.set("host_id", String(params.hostId));
  }
  if (params?.workloadId != null) {
    search.set("workload_id", String(params.workloadId));
  }
  const qs = search.toString();
  return apiGet<Deployment[]>(`/api/deployments${qs ? `?${qs}` : ""}`);
}

export function createDeployment(body: {
  hostId: number;
  workloadId: number;
  revisionId?: number;
}): Promise<Deployment> {
  return apiPost<Deployment>("/api/deployments", {
    host_id: body.hostId,
    workload_id: body.workloadId,
    revision_id: body.revisionId,
  });
}

export function getSecrets(params?: {
  page?: number;
  size?: number;
}): Promise<SecretListResponse> {
  const search = new URLSearchParams();
  if (params?.page != null) {
    search.set("page", String(params.page));
  }
  if (params?.size != null) {
    search.set("size", String(params.size));
  }
  const qs = search.toString();
  return apiGet<SecretListResponse>(`/api/secrets${qs ? `?${qs}` : ""}`);
}

export function createSecret(name: string, value: string): Promise<Secret> {
  return apiPost<Secret>("/api/secrets", { name, value });
}

export function updateSecret(secretId: number, value: string): Promise<Secret> {
  return apiPut<Secret>(`/api/secrets/${secretId}`, { value });
}

export function deleteSecret(secretId: number): Promise<void> {
  return apiDelete(`/api/secrets/${secretId}`);
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
