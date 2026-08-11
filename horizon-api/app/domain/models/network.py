from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


@dataclass(kw_only=True)
class Network:
    id: int | None = None
    name: str
    driver: str = "bridge"
    options: dict[str, str] = field(default_factory=dict)
    created_at: datetime | None = None

    @property
    def pk(self) -> int:
        return self.id  # type: ignore


@dataclass(kw_only=True)
class WorkloadNetwork:
    id: int | None = None
    workload_id: int
    network_id: int
    alias: str | None = None
    created_at: datetime | None = None

    @property
    def pk(self) -> int:
        return self.id  # type: ignore


class NetworkSyncStatus(StrEnum):
    SYNCED = "SYNCED"
    FAILED = "FAILED"


@dataclass(kw_only=True)
class NetworkHostState:
    id: int | None = None
    network_id: int
    host_id: int
    status: NetworkSyncStatus
    error_message: str | None = None
    synced_at: datetime | None = None

    @property
    def pk(self) -> int:
        return self.id  # type: ignore
