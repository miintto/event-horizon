from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.enums import AggregateInterval, ContainerMetricKind
from app.domain.models.container_metric import ContainerMetric, ContainerMetricSeries


class ContainerMetricRepository(ABC):
    @abstractmethod
    async def save_all(self, datapoints: list[ContainerMetric]) -> int: ...

    @abstractmethod
    async def aggregate_series(
        self,
        metric: ContainerMetricKind,
        container_ids: list[int] | None,
        interval: AggregateInterval,
        start_at: datetime,
        end_at: datetime,
    ) -> list[ContainerMetricSeries]: ...
