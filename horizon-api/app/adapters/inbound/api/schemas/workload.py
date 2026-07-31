from datetime import datetime

from pydantic import BaseModel

from app.application.ports.usecase.workload_use_case import WorkloadResult
from app.domain.models.workload import Workload


class WorkloadResponse(BaseModel):
    id: int
    name: str
    container_count: int | None = None
    running_count: int | None = None
    host_count: int | None = None
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, workload: Workload) -> WorkloadResponse:
        return cls(
            id=workload.id,
            name=workload.name,
            created_at=workload.created_at,
        )

    @classmethod
    def from_result(cls, result: WorkloadResult) -> WorkloadResponse:
        return cls(
            id=result.id,
            name=result.name,
            container_count=result.container_count,
            running_count=result.running_count,
            host_count=result.host_count,
            created_at=result.created_at,
        )
