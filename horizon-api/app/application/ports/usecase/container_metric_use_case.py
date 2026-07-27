from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import AggregateInterval, ContainerMetricKind
from app.domain.models.container_metric import ContainerMetricSeries


@dataclass
class ContainerMetricQuery:
    metric: ContainerMetricKind
    container_ids: list[int] | None
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime


class ContainerMetricUseCase(ABC):
    @abstractmethod
    async def query(
        self, query: ContainerMetricQuery
    ) -> list[ContainerMetricSeries]: ...
