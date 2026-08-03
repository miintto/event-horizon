from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class WorkloadDetail:
    container_count: int = 0
    running_count: int = 0
    host_count: int = 0


@dataclass(kw_only=True)
class Workload:
    id: int | None = None
    name: str
    current_revision_id: int | None = None
    created_at: datetime | None = None
    detail: WorkloadDetail | None = None

    @property
    def pk(self) -> int:
        return self.id  # type: ignore
