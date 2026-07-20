import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.host import Host, HostStatus
from app.infrastructure.database import Base


class HostModel(Base):
    __tablename__ = "host"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_uuid: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, unique=True)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[HostStatus] = mapped_column(
        Enum(HostStatus, native_enum=False),
        nullable=False,
        default=HostStatus.OFFLINE,
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def to_domain(self) -> Host:
        return Host(
            id=self.id,
            agent_uuid=self.agent_uuid,
            hostname=self.hostname,
            status=self.status,
            last_seen_at=self.last_seen_at,
            created_at=self.created_at,
        )
