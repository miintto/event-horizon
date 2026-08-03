from abc import ABC, abstractmethod

from app.application.command.metric import HostMetricQuery
from app.domain.models import HostMetricSeries


class HostMetricUseCase(ABC):
    @abstractmethod
    async def query(self, query: HostMetricQuery) -> list[HostMetricSeries]: ...
