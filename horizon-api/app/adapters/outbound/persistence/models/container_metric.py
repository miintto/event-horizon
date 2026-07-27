from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, Index, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class ContainerMetricModel(Base):
    __tablename__ = "container_metric"

    container_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True
    )
    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False)
    cpu_throttled_time: Mapped[int] = mapped_column(BigInteger, nullable=False)
    memory_used: Mapped[int] = mapped_column(BigInteger, nullable=False)
    block_read: Mapped[int] = mapped_column(BigInteger, nullable=False)
    block_write: Mapped[int] = mapped_column(BigInteger, nullable=False)
    pids: Mapped[int] = mapped_column(Integer, nullable=False)
    memory_limit: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    net_rx: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    net_tx: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index(
            "ix_container_metric_collected_at",
            "collected_at",
            postgresql_using="brin",
        ),
    )
