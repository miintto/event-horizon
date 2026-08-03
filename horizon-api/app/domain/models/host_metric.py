from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class HostMetric:
    host_id: int
    cpu_usage: float
    memory_used: int
    memory_total: int
    disk_used: int
    disk_total: int
    net_rx: int
    net_tx: int
    load_avg_1: float | None = None
    load_avg_5: float | None = None
    load_avg_15: float | None = None
    extra: dict | None = None
    collected_at: datetime
