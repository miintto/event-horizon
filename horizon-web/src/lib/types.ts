export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export type HostStatus = "online" | "offline";

export interface Host {
  id: number;
  agent_uuid: string;
  hostname: string;
  status: HostStatus;
  last_seen_at?: string;
  created_at?: string;
}

export type MetricKind =
  | "cpu_usage"
  | "memory_used"
  | "memory_total"
  | "disk_used"
  | "disk_total"
  | "load_avg_1"
  | "load_avg_5"
  | "load_avg_15"
  | "net_rx_rate"
  | "net_tx_rate";

export type AggregateInterval = "1m" | "5m" | "10m" | "1h";

export interface MetricPoint {
  bucket: string;
  value?: number;
}

export interface HostMetricSeries {
  host_id: number;
  points: MetricPoint[];
}

export type ContainerState =
  | "created"
  | "running"
  | "paused"
  | "restarting"
  | "removing"
  | "exited"
  | "dead";

export interface Container {
  id: number;
  host_id: number;
  workload_id?: number;
  docker_id: string;
  name: string;
  image: string;
  state: ContainerState;
  compose_project?: string;
  compose_service?: string;
  exit_code?: number;
  started_at?: string;
  last_seen_at?: string;
  created_at?: string;
}

export type ContainerMetricKind =
  | "cpu_usage"
  | "cpu_throttled_time"
  | "memory_used"
  | "memory_limit"
  | "block_read_rate"
  | "block_write_rate"
  | "net_rx_rate"
  | "net_tx_rate"
  | "pids";

export interface ContainerMetricSeries {
  container_id: number;
  points: MetricPoint[];
}

/** 정의 본문. 서버가 JSONB 로 보관하며 형태 검증만 한다 */
export type ContainerSpec = Record<string, unknown>;

export interface WorkloadRevision {
  id: number;
  workload_id: number;
  revision: number;
  image: string;
  cpu_limit?: string;
  memory_limit?: number;
  spec: ContainerSpec;
  created_at?: string;
}

export interface RevisionDefinitionInput {
  image: string;
  cpu_limit?: number;
  memory_limit?: number;
  spec?: ContainerSpec;
}

export interface Workload {
  id: number;
  name: string;
  current_revision_id?: number;
  container_count?: number;
  running_count?: number;
  host_count?: number;
  created_at?: string;
}

/** 값(평문·암호문)은 어떤 응답에도 실리지 않는다 */
export interface Secret {
  id: number;
  name: string;
  created_at?: string;
  updated_at?: string;
}

export interface SecretListResponse {
  secrets: Secret[];
}

export const SECRET_VALUE_MAX = 4096;
export const SECRET_NAME_MAX = 255;
