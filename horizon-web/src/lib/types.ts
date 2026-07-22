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
