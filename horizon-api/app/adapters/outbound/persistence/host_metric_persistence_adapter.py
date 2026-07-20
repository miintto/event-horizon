from dataclasses import asdict
from datetime import datetime
from itertools import groupby

from sqlalchemy import Float, cast, func, select
from sqlalchemy.dialects.postgresql import insert

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.host_metric import HostMetricModel
from app.application.ports.repository.host_metric_repository import HostMetricRepository
from app.domain.enums import AggregateInterval, MetricKind
from app.domain.models.host_metric import (
    HostMetric,
    HostMetricSeries,
    MetricPoint,
)


class HostMetricPersistenceAdapter(BasePersistenceAdapter, HostMetricRepository):
    _COLUMN_MAP = {
        MetricKind.CPU_USAGE: HostMetricModel.cpu_usage,
        MetricKind.MEMORY_USED: HostMetricModel.memory_used,
        MetricKind.MEMORY_TOTAL: HostMetricModel.memory_total,
        MetricKind.DISK_USED: HostMetricModel.disk_used,
        MetricKind.DISK_TOTAL: HostMetricModel.disk_total,
        MetricKind.LOAD_AVG_1: HostMetricModel.load_avg_1,
        MetricKind.LOAD_AVG_5: HostMetricModel.load_avg_5,
        MetricKind.LOAD_AVG_15: HostMetricModel.load_avg_15,
        MetricKind.NET_RX_RATE: HostMetricModel.net_rx,
        MetricKind.NET_TX_RATE: HostMetricModel.net_tx,
    }

    async def save_all(self, metrics: list[HostMetric]) -> int:
        if not metrics:
            return 0

        session = self._scoped_session()
        stmt = (
            insert(HostMetricModel)
            .values([asdict(metric) for metric in metrics])
            .on_conflict_do_nothing(index_elements=["host_id", "collected_at"])
        )
        result = await session.execute(stmt)
        return result.rowcount

    async def aggregate_series(
        self,
        metric: MetricKind,
        host_ids: list[int] | None,
        interval: AggregateInterval,
        start_at: datetime,
        end_at: datetime,
    ) -> list[HostMetricSeries]:
        session = self._scoped_session()
        seconds = interval.seconds
        epoch = func.extract("epoch", HostMetricModel.collected_at)
        bucket = func.to_timestamp(func.floor(epoch / seconds) * seconds)

        column = self._COLUMN_MAP[metric]
        if metric in (MetricKind.NET_RX_RATE, MetricKind.NET_TX_RATE):
            value = cast(func.max(column) - func.min(column), Float) / seconds
        else:
            value = func.avg(column)

        stmt = (
            select(
                HostMetricModel.host_id,
                bucket.label("bucket"),
                value.label("value"),
            )
            .where(
                HostMetricModel.collected_at >= start_at,
                HostMetricModel.collected_at < end_at,
            )
            .group_by(HostMetricModel.host_id, bucket)
            .order_by(HostMetricModel.host_id, bucket)
        )
        if host_ids:
            stmt = stmt.where(HostMetricModel.host_id.in_(host_ids))

        result = await session.execute(stmt)

        return [
            HostMetricSeries(
                host_id=host_id,
                points=[
                    MetricPoint(bucket=row.bucket, value=row.value) for row in rows
                ],
            )
            for host_id, rows in groupby(result, key=lambda row: row.host_id)
        ]
