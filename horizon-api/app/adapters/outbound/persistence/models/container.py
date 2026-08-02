from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.container import Container, ContainerState
from app.infrastructure.database import Base


class ContainerModel(Base):
    __tablename__ = "container"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = mapped_column(Integer, nullable=False)
    workload_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    revision_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    docker_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[ContainerState] = mapped_column(
        Enum(ContainerState, native_enum=False), nullable=False
    )
    compose_project: Mapped[str | None] = mapped_column(String(255), nullable=True)
    compose_service: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("host_id", "docker_id", name="uq_container_host_docker"),
        Index("ix_container_workload_id", "workload_id"),
    )

    def to_domain(self) -> Container:
        return Container(
            id=self.id,
            host_id=self.host_id,
            workload_id=self.workload_id,
            revision_id=self.revision_id,
            docker_id=self.docker_id,
            name=self.name,
            image=self.image,
            state=self.state,
            compose_project=self.compose_project,
            compose_service=self.compose_service,
            exit_code=self.exit_code,
            started_at=self.started_at,
            last_seen_at=self.last_seen_at,
            created_at=self.created_at,
        )
