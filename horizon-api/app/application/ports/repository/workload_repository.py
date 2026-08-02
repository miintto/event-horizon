from abc import ABC, abstractmethod

from app.application.ports.usecase.workload_use_case import WorkloadResult
from app.domain.models.workload import Workload


class WorkloadRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Workload | None: ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Workload | None: ...

    @abstractmethod
    async def find_all_with_counts(
        self, host_id: int | None
    ) -> list[WorkloadResult]: ...

    @abstractmethod
    async def save(self, workload: Workload) -> Workload: ...

    @abstractmethod
    async def update_current_revision_id(
        self, workload_id: int, revision_id: int
    ) -> None: ...
