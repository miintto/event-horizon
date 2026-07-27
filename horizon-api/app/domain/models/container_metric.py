from dataclasses import dataclass
from datetime import datetime

from app.domain.models.host_metric import MetricPoint


@dataclass(kw_only=True)
class ContainerMetric:
    container_id: int
    cpu_usage: float
    cpu_throttled_time: int
    memory_used: int
    block_read: int
    block_write: int
    pids: int
    memory_limit: int | None = None
    net_rx: int | None = None
    net_tx: int | None = None
    extra: dict | None = None
    collected_at: datetime


@dataclass(kw_only=True)
class ContainerMetricSeries:
    container_id: int
    points: list[MetricPoint]
