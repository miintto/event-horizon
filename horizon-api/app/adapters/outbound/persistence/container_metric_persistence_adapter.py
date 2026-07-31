from dataclasses import asdict
from datetime import datetime
from itertools import groupby

from sqlalchemy import Float, cast, func, select
from sqlalchemy.dialects.postgresql import insert

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.container_metric import (
    ContainerMetricModel,
)
from app.application.ports.repository.container_metric_repository import (
    ContainerMetricRepository,
)
from app.domain.enums import AggregateInterval, ContainerMetricKind
from app.domain.models.container_metric import ContainerMetric, ContainerMetricSeries
from app.domain.models.host_metric import MetricPoint


class ContainerMetricPersistenceAdapter(
    BasePersistenceAdapter, ContainerMetricRepository
):
    _COLUMN_MAP = {
        ContainerMetricKind.CPU_USAGE: ContainerMetricModel.cpu_usage,
        ContainerMetricKind.CPU_THROTTLED_TIME: ContainerMetricModel.cpu_throttled_time,
        ContainerMetricKind.MEMORY_USED: ContainerMetricModel.memory_used,
        ContainerMetricKind.MEMORY_LIMIT: ContainerMetricModel.memory_limit,
        ContainerMetricKind.BLOCK_READ_RATE: ContainerMetricModel.block_read,
        ContainerMetricKind.BLOCK_WRITE_RATE: ContainerMetricModel.block_write,
        ContainerMetricKind.NET_RX_RATE: ContainerMetricModel.net_rx,
        ContainerMetricKind.NET_TX_RATE: ContainerMetricModel.net_tx,
        ContainerMetricKind.PIDS: ContainerMetricModel.pids,
    }

    _RATE_METRICS = (
        ContainerMetricKind.BLOCK_READ_RATE,
        ContainerMetricKind.BLOCK_WRITE_RATE,
        ContainerMetricKind.NET_RX_RATE,
        ContainerMetricKind.NET_TX_RATE,
    )

    async def save_all(self, datapoints: list[ContainerMetric]) -> int:
        if not datapoints:
            return 0

        session = self._scoped_session()
        stmt = (
            insert(ContainerMetricModel)
            .values([asdict(datapoint) for datapoint in datapoints])
            .on_conflict_do_nothing(index_elements=["container_id", "collected_at"])
        )
        result = await session.execute(stmt)
        return result.rowcount

    async def aggregate_series(
        self,
        metric: ContainerMetricKind,
        container_ids: list[int] | None,
        interval: AggregateInterval,
        start_at: datetime,
        end_at: datetime,
    ) -> list[ContainerMetricSeries]:
        session = self._scoped_session()
        seconds = interval.seconds
        epoch = func.extract("epoch", ContainerMetricModel.collected_at)
        bucket = func.to_timestamp(func.floor(epoch / seconds) * seconds)

        column = self._COLUMN_MAP[metric]
        if metric in self._RATE_METRICS:
            value = cast(func.max(column) - func.min(column), Float) / seconds
        else:
            value = func.avg(column)

        stmt = (
            select(
                ContainerMetricModel.container_id,
                bucket.label("bucket"),
                value.label("value"),
            )
            .where(
                ContainerMetricModel.collected_at >= start_at,
                ContainerMetricModel.collected_at < end_at,
            )
            .group_by(ContainerMetricModel.container_id, bucket)
            .order_by(ContainerMetricModel.container_id, bucket)
        )
        if container_ids:
            stmt = stmt.where(ContainerMetricModel.container_id.in_(container_ids))

        result = await session.execute(stmt)

        return [
            ContainerMetricSeries(
                container_id=container_id,
                points=[
                    MetricPoint(bucket=row.bucket, value=row.value) for row in rows
                ],
            )
            for container_id, rows in groupby(result, key=lambda row: row.container_id)
        ]
