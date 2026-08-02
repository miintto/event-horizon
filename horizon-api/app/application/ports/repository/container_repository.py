from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.models.container import Container


class ContainerRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Container | None: ...

    @abstractmethod
    async def find_all(
        self, host_id: int | None, workload_id: int | None = None
    ) -> list[Container]: ...

    @abstractmethod
    async def upsert_all(self, containers: list[Container]) -> list[Container]: ...

    @abstractmethod
    async def update_state_to_exited(
        self, host_id: int, seen_before: datetime
    ) -> int: ...
