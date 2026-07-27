from abc import ABC, abstractmethod

from app.domain.models.container import Container


class ContainerRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Container | None: ...

    @abstractmethod
    async def find_all(self, host_id: int | None) -> list[Container]: ...

    @abstractmethod
    async def upsert_all(self, containers: list[Container]) -> list[Container]: ...
