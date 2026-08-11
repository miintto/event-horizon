import uuid
from dataclasses import dataclass, field

from app.domain.models import NetworkSyncStatus


@dataclass
class NetworkSyncResult:
    network_name: str
    status: NetworkSyncStatus
    error_message: str | None = None


@dataclass
class NetworkSyncCommand:
    agent_uuid: uuid.UUID
    results: list[NetworkSyncResult] = field(default_factory=list)


@dataclass
class NetworkMember:
    workload_id: int
    alias: str


@dataclass
class NetworkDesired:
    name: str
    driver: str
    options: dict[str, str] = field(default_factory=dict)
    members: list[NetworkMember] = field(default_factory=list)


@dataclass
class NetworkDesiredState:
    networks: list[NetworkDesired] = field(default_factory=list)
