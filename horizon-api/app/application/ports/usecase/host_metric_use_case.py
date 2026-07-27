from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import AggregateInterval, MetricKind
from app.domain.models.host_metric import HostMetricSeries


@dataclass
class HostMetricQuery:
    metric: MetricKind
    host_ids: list[int] | None
    interval: AggregateInterval
    start_at: datetime
    end_at: datetime


class HostMetricUseCase(ABC):
    @abstractmethod
    async def query(self, query: HostMetricQuery) -> list[HostMetricSeries]: ...
