from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DeploymentStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(kw_only=True)
class Deployment:
    id: int | None = None
    host_id: int
    workload_id: int
    revision_id: int
    container_id: int | None = None
    status: DeploymentStatus = DeploymentStatus.PENDING
    error_message: str | None = None
    claimed_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None

    @property
    def pk(self) -> int:
        return self.id  # type: ignore
