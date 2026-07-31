from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.domain.models.workload import Workload


@dataclass
class WorkloadResult:
    id: int
    name: str
    container_count: int = 0
    running_count: int = 0
    host_count: int = 0
    created_at: datetime | None = None


class WorkloadUseCase(ABC):
    @abstractmethod
    async def get_workload(self, workload_id: int) -> Workload: ...

    @abstractmethod
    async def get_workloads(self, host_id: int | None) -> list[WorkloadResult]: ...
