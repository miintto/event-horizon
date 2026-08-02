from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.models.workload import Workload
from app.domain.models.workload_revision import ContainerSpec, WorkloadRevision


@dataclass
class WorkloadResult:
    id: int
    name: str
    container_count: int = 0
    running_count: int = 0
    host_count: int = 0
    created_at: datetime | None = None


@dataclass
class RevisionDefinition:
    image: str
    cpu_limit: Decimal | None = None
    memory_limit: int | None = None
    spec: ContainerSpec = field(default_factory=ContainerSpec)


@dataclass
class WorkloadCreateCommand:
    name: str
    definition: RevisionDefinition


@dataclass
class RevisionCreateCommand:
    workload_id: int
    definition: RevisionDefinition


class WorkloadUseCase(ABC):
    @abstractmethod
    async def get_workload(self, workload_id: int) -> Workload: ...

    @abstractmethod
    async def get_workloads(self, host_id: int | None) -> list[WorkloadResult]: ...

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
