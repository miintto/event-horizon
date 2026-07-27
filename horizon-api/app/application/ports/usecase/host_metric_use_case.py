import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import AggregateInterval, MetricKind
from app.domain.models.container import Container, ContainerState
from app.domain.models.container_metric import ContainerMetric
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
class ContainerMetricDatapoint:
    collected_at: datetime
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

    def to_domain(self, container_id: int) -> ContainerMetric:
        return ContainerMetric(
            container_id=container_id,
            collected_at=self.collected_at,
            cpu_usage=self.cpu_usage,
            cpu_throttled_time=self.cpu_throttled_time,
            memory_used=self.memory_used,
            block_read=self.block_read,
            block_write=self.block_write,
            pids=self.pids,
            memory_limit=self.memory_limit,
            net_rx=self.net_rx,
            net_tx=self.net_tx,
            extra=self.extra,
        )


@dataclass
class ContainerCollectItem:
    docker_id: str
    name: str
    image: str
    state: ContainerState
    compose_project: str | None = None
    compose_service: str | None = None
    exit_code: int | None = None
    started_at: datetime | None = None
    datapoints: list[ContainerMetricDatapoint] = field(default_factory=list)

    def to_domain(self, host_id: int) -> Container:
        return Container(
            host_id=host_id,
            docker_id=self.docker_id,
            name=self.name,
            image=self.image,
            state=self.state,
            compose_project=self.compose_project,
            compose_service=self.compose_service,
            exit_code=self.exit_code,
            started_at=self.started_at,
        )


@dataclass
class HostMetricCollectCommand:
    agent_uuid: uuid.UUID
    hostname: str
    datapoints: list[HostMetricDatapoint]
    containers: list[ContainerCollectItem] = field(default_factory=list)


@dataclass
class HostMetricCollectResult:
    ingested: int
    container_ingested: int = 0


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
