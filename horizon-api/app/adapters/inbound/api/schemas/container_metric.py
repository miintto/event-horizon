from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.application.ports.usecase.collect_use_case import (
    ContainerCollectItem,
    ContainerMetricDatapoint,
)
from app.application.ports.usecase.container_metric_use_case import ContainerMetricQuery
from app.domain.enums import AggregateInterval, ContainerMetricKind
from app.domain.models.container import ContainerState
from app.domain.models.container_metric import ContainerMetricSeries


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


class ContainerMetricQueryParam(BaseModel):
    metric: ContainerMetricKind
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime
    container_ids: list[int] | None = None

    @model_validator(mode="after")
    def _check_range(self) -> ContainerMetricQueryParam:
        if self.start_at >= self.end_at:
            raise ValueError("start_at must be earlier than end_at")
        if self.interval.max_range < (self.end_at - self.start_at).total_seconds():
            raise ValueError(
                "Requested time range is too wide for the selected interval"
            )
        return self

    def to_query(self) -> ContainerMetricQuery:
        return ContainerMetricQuery(
            metric=self.metric,
            container_ids=self.container_ids,
            interval=self.interval,
            start_at=self.start_at,
            end_at=self.end_at,
        )


class ContainerMetricPointResponse(BaseModel):
    bucket: datetime
    value: float | None


class ContainerMetricSeriesResponse(BaseModel):
    container_id: int
    points: list[ContainerMetricPointResponse]

    @classmethod
    def from_domain(
        cls, series: ContainerMetricSeries
    ) -> ContainerMetricSeriesResponse:
        return cls(
            container_id=series.container_id,
            points=[
                ContainerMetricPointResponse(bucket=point.bucket, value=point.value)
                for point in series.points
            ],
        )
