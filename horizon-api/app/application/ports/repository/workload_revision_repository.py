from abc import ABC, abstractmethod

from app.domain.models import WorkloadRevision


class WorkloadRevisionRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> WorkloadRevision | None: ...

    @abstractmethod
    async def find_all(self, workload_id: int) -> list[WorkloadRevision]: ...

    @abstractmethod
    async def find_by_revision(
        self, workload_id: int, revision: int
    ) -> WorkloadRevision | None: ...

    @abstractmethod
    async def find_max_revision(self, workload_id: int) -> int | None: ...

    @abstractmethod
    async def save(self, revision: WorkloadRevision) -> WorkloadRevision: ...
