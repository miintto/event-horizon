from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.application.command.collect import (
    CollectCommand,
    CollectResult,
    ContainerCollectItem,
    ContainerMetricDatapoint,
    HostMetricDatapoint,
)
from app.application.command.metric import ContainerMetricQuery, HostMetricQuery
from app.domain.enums import AggregateInterval, ContainerMetricKind, HostMetricKind
from app.domain.models import ContainerMetricSeries, ContainerState, HostMetricSeries


class BaseMetricQueryParam(BaseModel):
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime

    @model_validator(mode="after")
    def _check_range(self) -> BaseMetricQueryParam:
        if self.start_at >= self.end_at:
            raise ValueError("start_at must be earlier than end_at")
        if self.interval.max_range < (self.end_at - self.start_at).total_seconds():
            raise ValueError(
                "Requested time range is too wide for the selected interval"
            )
        return self


class HostMetricQueryParam(BaseMetricQueryParam):
    metric: HostMetricKind
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime
    host_ids: list[int] | None = None

    def to_query(self) -> HostMetricQuery:
        return HostMetricQuery(
            metric=self.metric,
            host_ids=self.host_ids,
            interval=self.interval,
            start_at=self.start_at,
            end_at=self.end_at,
        )


class ContainerMetricQueryParam(BaseMetricQueryParam):
    metric: ContainerMetricKind
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime
    container_ids: list[int] | None = None

    def to_query(self) -> ContainerMetricQuery:
        return ContainerMetricQuery(
            metric=self.metric,
            container_ids=self.container_ids,
            interval=self.interval,
            start_at=self.start_at,
            end_at=self.end_at,
        )


class HostMetricDatapointRequest(BaseModel):
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

    def to_datapoint(self) -> HostMetricDatapoint:
        return HostMetricDatapoint(
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


class ContainerMetricDatapointRequest(BaseModel):
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

    def to_datapoint(self) -> ContainerMetricDatapoint:
        return ContainerMetricDatapoint(
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


class ContainerCollectItemRequest(BaseModel):
    docker_id: str = Field(max_length=64)
    name: str = Field(max_length=255)
    image: str = Field(max_length=255)
    state: ContainerState
    compose_project: str | None = Field(default=None, max_length=255)
    compose_service: str | None = Field(default=None, max_length=255)
    exit_code: int | None = None
    started_at: datetime | None = None
    datapoints: list[ContainerMetricDatapointRequest] = Field(default_factory=list)

    def to_collect_item(self) -> ContainerCollectItem:
        return ContainerCollectItem(
            docker_id=self.docker_id,
            name=self.name,
            image=self.image,
            state=self.state,
            compose_project=self.compose_project,
            compose_service=self.compose_service,
            exit_code=self.exit_code,
            started_at=self.started_at,
            datapoints=[dp.to_datapoint() for dp in self.datapoints],
        )


class HostMetricBatchRequest(BaseModel):
    agent_uuid: UUID
    hostname: str = Field(max_length=255)
    datapoints: list[HostMetricDatapointRequest]
    containers: list[ContainerCollectItemRequest] = Field(default_factory=list)

    def to_command(self) -> CollectCommand:
        return CollectCommand(
            agent_uuid=self.agent_uuid,
            hostname=self.hostname,
            datapoints=[dp.to_datapoint() for dp in self.datapoints],
            containers=[c.to_collect_item() for c in self.containers],
        )


class MetricPointResponse(BaseModel):
    bucket: datetime
    value: float | None


class HostMetricSeriesResponse(BaseModel):
    host_id: int
    points: list[MetricPointResponse]

    @classmethod
    def from_domain(cls, series: HostMetricSeries) -> HostMetricSeriesResponse:
        return cls(
            host_id=series.host_id,
            points=[
                MetricPointResponse(bucket=point.bucket, value=point.value)
                for point in series.points
            ],
        )


class HostMetricCollectResponse(BaseModel):
    ingested: int
    container_ingested: int

    @classmethod
    def from_result(cls, result: CollectResult) -> HostMetricCollectResponse:
        return cls(
            ingested=result.ingested, container_ingested=result.container_ingested
        )


class ContainerMetricSeriesResponse(BaseModel):
    container_id: int
    points: list[MetricPointResponse]

    @classmethod
    def from_domain(
        cls, series: ContainerMetricSeries
    ) -> ContainerMetricSeriesResponse:
        return cls(
            container_id=series.container_id,
            points=[
                MetricPointResponse(bucket=point.bucket, value=point.value)
                for point in series.points
            ],
        )
