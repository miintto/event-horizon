from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.enums import AggregateInterval, HostMetricKind
from app.domain.models import HostMetric, HostMetricSeries


class HostMetricRepository(ABC):
    @abstractmethod
    async def aggregate_series(
        self,
        metric: HostMetricKind,
        host_ids: list[int] | None,
        interval: AggregateInterval,
        start_at: datetime,
        end_at: datetime,
    ) -> list[HostMetricSeries]: ...

    @abstractmethod
    async def save_all(self, datapoints: list[HostMetric]) -> int: ...
