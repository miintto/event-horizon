from abc import ABC, abstractmethod

from app.domain.models.container_metric import ContainerMetric


class ContainerMetricRepository(ABC):
    @abstractmethod
    async def save_all(self, datapoints: list[ContainerMetric]) -> int: ...
