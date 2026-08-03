from abc import ABC, abstractmethod

from app.application.command.metric import ContainerMetricQuery
from app.domain.models import ContainerMetricSeries


class ContainerMetricUseCase(ABC):
    @abstractmethod
    async def query(
        self, query: ContainerMetricQuery
    ) -> list[ContainerMetricSeries]: ...
