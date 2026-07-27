from abc import ABC, abstractmethod

from app.domain.models.container import Container


class ContainerRepository(ABC):
    @abstractmethod
    async def upsert_all(self, containers: list[Container]) -> list[Container]: ...
