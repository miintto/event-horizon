from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class MetricPoint:
    bucket: datetime
    value: float | None


@dataclass(kw_only=True)
class HostMetricSeries:
    host_id: int
    points: list[MetricPoint]


@dataclass(kw_only=True)
class ContainerMetricSeries:
    container_id: int
    points: list[MetricPoint]
