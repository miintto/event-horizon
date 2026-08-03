from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models import Workload
from app.infrastructure.database import Base


class WorkloadModel(Base):
    __tablename__ = "workload"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    current_revision_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("name", name="uq_workload_name"),)

    def to_domain(self) -> Workload:
        return Workload(
            id=self.id,
            name=self.name,
            current_revision_id=self.current_revision_id,
            created_at=self.created_at,
        )
