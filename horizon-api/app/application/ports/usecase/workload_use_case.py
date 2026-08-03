from abc import ABC, abstractmethod

from app.application.command.workload import (
    RevisionCreateCommand,
    WorkloadCreateCommand,
)
from app.domain.models import Workload, WorkloadRevision


class WorkloadUseCase(ABC):
    @abstractmethod
    async def get_workload(self, workload_id: int) -> Workload: ...

    @abstractmethod
    async def get_workloads(self, host_id: int | None) -> list[Workload]: ...

    @abstractmethod
    async def create_workload(self, command: WorkloadCreateCommand) -> Workload: ...

    @abstractmethod
    async def get_revisions(self, workload_id: int) -> list[WorkloadRevision]: ...

    @abstractmethod
    async def get_revision(
        self, workload_id: int, revision: int
    ) -> WorkloadRevision: ...

    @abstractmethod
    async def add_revision(
        self, command: RevisionCreateCommand
    ) -> WorkloadRevision: ...
