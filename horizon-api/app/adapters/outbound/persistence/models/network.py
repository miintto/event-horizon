from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models import Network
from app.infrastructure.database import Base


class NetworkModel(Base):
    __tablename__ = "network"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    driver: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="bridge"
    )
    options: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("name", name="uq_network_name"),)

    def to_domain(self) -> Network:
        return Network(
            id=self.id,
            name=self.name,
            driver=self.driver,
            options=self.options,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, network: Network) -> NetworkModel:
        kwargs = {
            "name": network.name,
            "driver": network.driver,
            "options": network.options,
        }
        if network.id is not None:
            kwargs["id"] = network.id
        if network.created_at is not None:
            kwargs["created_at"] = network.created_at
        return cls(**kwargs)
