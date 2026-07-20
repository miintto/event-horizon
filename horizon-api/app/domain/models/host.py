import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class HostStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"


@dataclass(kw_only=True)
class Host:
    id: int | None = None
    agent_uuid: uuid.UUID
    hostname: str
    status: HostStatus = HostStatus.OFFLINE
    last_seen_at: datetime | None = None
    created_at: datetime | None = None
