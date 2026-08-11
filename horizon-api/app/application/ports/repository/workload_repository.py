from abc import ABC, abstractmethod

from app.domain.models import Workload


class WorkloadRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Workload | None: ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Workload | None: ...

    @abstractmethod
    async def find_all_by_ids(self, ids: list[int]) -> list[Workload]: ...

    @abstractmethod
    async def find_all_with_counts(self, host_id: int | None) -> list[Workload]: ...

    @abstractmethod
    async def update_current_revision_id(self, workload_id: int, revision_id: int): ...

    @abstractmethod
    async def save(self, workload: Workload) -> Workload: ...
