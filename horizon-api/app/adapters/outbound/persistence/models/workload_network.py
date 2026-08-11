from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models import WorkloadNetwork
from app.infrastructure.database import Base


class WorkloadNetworkModel(Base):
    __tablename__ = "workload_network"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workload_id: Mapped[int] = mapped_column(Integer, nullable=False)
    network_id: Mapped[int] = mapped_column(Integer, nullable=False)
    alias: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workload_id", "network_id", name="uq_workload_network"),
        Index("ix_workload_network_network_id", "network_id"),
    )

    def to_domain(self) -> WorkloadNetwork:
        return WorkloadNetwork(
            id=self.id,
            workload_id=self.workload_id,
            network_id=self.network_id,
            alias=self.alias,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, attachment: WorkloadNetwork) -> WorkloadNetworkModel:
        kwargs = {
            "workload_id": attachment.workload_id,
            "network_id": attachment.network_id,
            "alias": attachment.alias,
        }
        if attachment.id is not None:
            kwargs["id"] = attachment.id
        if attachment.created_at is not None:
            kwargs["created_at"] = attachment.created_at
        return cls(**kwargs)
