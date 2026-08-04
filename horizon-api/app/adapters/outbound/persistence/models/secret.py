from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models import Secret
from app.infrastructure.database import Base


class SecretModel(Base):
    __tablename__ = "secret"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (UniqueConstraint("name", name="uq_secret_name"),)

    def to_domain(self) -> Secret:
        return Secret(
            id=self.id,
            name=self.name,
            ciphertext=self.ciphertext,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, secret: Secret) -> SecretModel:
        kwargs = {
            "name": secret.name,
            "ciphertext": secret.ciphertext,
        }
        if secret.id is not None:
            kwargs["id"] = secret.id
        if secret.created_at is not None:
            kwargs["created_at"] = secret.created_at
        return cls(**kwargs)
