from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models import Deployment, DeploymentStatus
from app.infrastructure.database import Base


class DeploymentModel(Base):
    __tablename__ = "deployment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = mapped_column(Integer, nullable=False)
    workload_id: Mapped[int] = mapped_column(Integer, nullable=False)
    revision_id: Mapped[int] = mapped_column(Integer, nullable=False)
    container_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[DeploymentStatus] = mapped_column(
        Enum(DeploymentStatus, native_enum=False),
        nullable=False,
        default=DeploymentStatus.PENDING,
    )
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_deployment_workload_id", "workload_id"),
        Index("ix_deployment_host_status", "host_id", "status"),
        Index(
            "uq_deployment_active",
            "workload_id",
            unique=True,
            postgresql_where=status.in_(
                (DeploymentStatus.PENDING, DeploymentStatus.RUNNING)
            ),
        ),
    )

    def to_domain(self) -> Deployment:
        return Deployment(
            id=self.id,
            host_id=self.host_id,
            workload_id=self.workload_id,
            revision_id=self.revision_id,
            container_id=self.container_id,
            status=self.status,
            error_message=self.error_message,
            claimed_at=self.claimed_at,
            finished_at=self.finished_at,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, deployment: Deployment) -> DeploymentModel:
        kwargs = {
            "host_id": deployment.host_id,
            "workload_id": deployment.workload_id,
            "revision_id": deployment.revision_id,
            "container_id": deployment.container_id,
            "status": deployment.status,
            "error_message": deployment.error_message,
            "claimed_at": deployment.claimed_at,
            "finished_at": deployment.finished_at,
        }
        if deployment.id is not None:
            kwargs["id"] = deployment.id
        if deployment.created_at is not None:
            kwargs["created_at"] = deployment.created_at
        return cls(**kwargs)
