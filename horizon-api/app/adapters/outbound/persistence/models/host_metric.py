from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, Index, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class HostMetricModel(Base):
    __tablename__ = "host_metric"

    host_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True
    )
    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False)
    memory_used: Mapped[int] = mapped_column(BigInteger, nullable=False)
    memory_total: Mapped[int] = mapped_column(BigInteger, nullable=False)
    disk_used: Mapped[int] = mapped_column(BigInteger, nullable=False)
    disk_total: Mapped[int] = mapped_column(BigInteger, nullable=False)
    net_rx: Mapped[int] = mapped_column(BigInteger, nullable=False)
    net_tx: Mapped[int] = mapped_column(BigInteger, nullable=False)
    load_avg_1: Mapped[float | None] = mapped_column(Float, nullable=True)
    load_avg_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    load_avg_15: Mapped[float | None] = mapped_column(Float, nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index(
            "ix_host_metric_collected_at",
            "collected_at",
            postgresql_using="brin",
        ),
    )
