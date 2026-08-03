from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.models import Host, HostStatus


class HostResponse(BaseModel):
    id: int
    agent_uuid: UUID
    hostname: str
    status: HostStatus
    last_seen_at: datetime | None = None
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, host: Host) -> HostResponse:
        return cls(
            id=host.pk,
            agent_uuid=host.agent_uuid,
            hostname=host.hostname,
            status=host.status,
            last_seen_at=host.last_seen_at,
            created_at=host.created_at,
        )
