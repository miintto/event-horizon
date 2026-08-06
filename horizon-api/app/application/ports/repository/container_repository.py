from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.models import Container


class ContainerRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Container | None: ...

    @abstractmethod
    async def find_all(
        self, host_id: int | None, workload_id: int | None = None
    ) -> list[Container]: ...

    @abstractmethod
    async def find_docker_ids_alive(
        self, workload_id: int, host_id: int
    ) -> list[str]: ...

    @abstractmethod
    async def upsert_all(self, containers: list[Container]) -> list[Container]: ...

    @abstractmethod
    async def upsert_with_revision(self, container: Container) -> Container: ...

    @abstractmethod
    async def mark_exited(self, host_id: int, docker_ids: list[str]) -> int: ...

    @abstractmethod
    async def update_state_to_exited(
        self, host_id: int, seen_before: datetime
    ) -> int: ...
