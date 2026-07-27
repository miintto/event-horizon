from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.adapters.inbound.api.schemas.container_metric import (
    ContainerCollectItemRequest,
)
from app.application.ports.usecase.collect_use_case import (
    CollectCommand,
    CollectResult,
    HostMetricDatapoint,
)
from app.application.ports.usecase.host_metric_use_case import HostMetricQuery
from app.domain.enums import AggregateInterval, MetricKind
from app.domain.models.host_metric import HostMetricSeries


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


class HostMetricCollectResponse(BaseModel):
    ingested: int
    container_ingested: int

    @classmethod
    def from_result(cls, result: CollectResult) -> HostMetricCollectResponse:
        return cls(
            ingested=result.ingested, container_ingested=result.container_ingested
        )


class HostMetricQueryParam(BaseModel):
    metric: MetricKind
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime
    host_ids: list[int] | None = None

    @model_validator(mode="after")
    def _check_range(self) -> HostMetricQueryParam:
        if self.start_at >= self.end_at:
            raise ValueError("start_at must be earlier than end_at")
        if self.interval.max_range < (self.end_at - self.start_at).total_seconds():
            raise ValueError(
                "Requested time range is too wide for the selected interval"
            )
        return self

    def to_query(self) -> HostMetricQuery:
        return HostMetricQuery(
            metric=self.metric,
            host_ids=self.host_ids,
            interval=self.interval,
            start_at=self.start_at,
            end_at=self.end_at,
        )


class HostMetricPointResponse(BaseModel):
    bucket: datetime
    value: float | None


class HostMetricSeriesResponse(BaseModel):
    host_id: int
    points: list[HostMetricPointResponse]

    @classmethod
    def from_domain(cls, series: HostMetricSeries) -> HostMetricSeriesResponse:
        return cls(
            host_id=series.host_id,
            points=[
                HostMetricPointResponse(bucket=point.bucket, value=point.value)
                for point in series.points
            ],
        )
