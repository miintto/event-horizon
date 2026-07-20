import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import AggregateInterval, MetricKind
from app.domain.models.host_metric import HostMetric, HostMetricSeries


@dataclass
class HostMetricDatapoint:
    collected_at: datetime
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

    def to_domain(self, host_id: int) -> HostMetric:
        return HostMetric(
            host_id=host_id,
            collected_at=self.collected_at,
            cpu_usage=self.cpu_usage,
            memory_used=self.memory_used,
            memory_total=self.memory_total,
            disk_used=self.disk_used,
            disk_total=self.disk_total,
            net_rx=self.net_rx,
            net_tx=self.net_tx,
            load_avg_1=self.load_avg_1,
            load_avg_5=self.load_avg_5,
            load_avg_15=self.load_avg_15,
            extra=self.extra,
        )


@dataclass
class HostMetricCollectCommand:
    agent_uuid: uuid.UUID
    hostname: str
    datapoints: list[HostMetricDatapoint]


@dataclass
class HostMetricCollectResult:
    ingested: int


@dataclass
class HostMetricQuery:
    metric: MetricKind
    host_ids: list[int] | None
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime


class HostMetricUseCase(ABC):
    @abstractmethod
    async def collect(
        self, command: HostMetricCollectCommand
    ) -> HostMetricCollectResult: ...

    @abstractmethod
    async def query(self, query: HostMetricQuery) -> list[HostMetricSeries]: ...
