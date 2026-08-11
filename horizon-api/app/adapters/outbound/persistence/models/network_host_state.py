from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models import NetworkHostState, NetworkSyncStatus
from app.infrastructure.database import Base


class NetworkHostStateModel(Base):
    __tablename__ = "network_host_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    network_id: Mapped[int] = mapped_column(Integer, nullable=False)
    host_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[NetworkSyncStatus] = mapped_column(
        Enum(NetworkSyncStatus, native_enum=False), nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("network_id", "host_id", name="uq_network_host_state"),
    )

    def to_domain(self) -> NetworkHostState:
        return NetworkHostState(
            id=self.id,
            network_id=self.network_id,
            host_id=self.host_id,
            status=self.status,
            error_message=self.error_message,
            synced_at=self.synced_at,
        )

    @classmethod
    def from_domain(cls, state: NetworkHostState) -> NetworkHostStateModel:
        kwargs = {
            "network_id": state.network_id,
            "host_id": state.host_id,
            "status": state.status,
            "error_message": state.error_message,
            "synced_at": state.synced_at,
        }
        if state.id is not None:
            kwargs["id"] = state.id
        return cls(**kwargs)
