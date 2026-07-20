from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.enums import AggregateInterval, MetricKind
from app.domain.models.host_metric import HostMetric, HostMetricSeries


class HostMetricRepository(ABC):
    @abstractmethod
    async def save_all(self, datapoints: list[HostMetric]) -> int: ...

    @abstractmethod
    async def aggregate_series(
        self,
        metric: MetricKind,
        host_ids: list[int] | None,
        interval: AggregateInterval,
        start_at: datetime,
        end_at: datetime,
    ) -> list[HostMetricSeries]: ...
