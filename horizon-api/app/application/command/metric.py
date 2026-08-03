from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import AggregateInterval, ContainerMetricKind, HostMetricKind


@dataclass
class HostMetricQuery:
    metric: HostMetricKind
    host_ids: list[int] | None
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime


@dataclass
class ContainerMetricQuery:
    metric: ContainerMetricKind
    container_ids: list[int] | None
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime
