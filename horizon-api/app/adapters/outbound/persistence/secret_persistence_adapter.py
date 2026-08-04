from sqlalchemy import delete, select

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.secret import SecretModel
from app.application.ports.repository import SecretRepository
from app.domain.models import Secret


class SecretPersistenceAdapter(BasePersistenceAdapter, SecretRepository):
    async def find_by_id(self, id_: int) -> Secret | None:
        session = self._scoped_session()
        result = await session.execute(select(SecretModel).where(SecretModel.id == id_))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_by_name(self, name: str) -> Secret | None:
        session = self._scoped_session()
        result = await session.execute(
            select(SecretModel).where(SecretModel.name == name)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all(self, offset: int, limit: int) -> list[Secret]:
        session = self._scoped_session()
        result = await session.execute(
            select(SecretModel).order_by(SecretModel.name).offset(offset).limit(limit)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def save(self, secret: Secret) -> Secret:
        session = self._scoped_session()
        model = await session.merge(SecretModel.from_domain(secret))
        await session.flush()
        return model.to_domain()

    async def delete_by_id(self, id_: int):
        session = self._scoped_session()
        await session.execute(delete(SecretModel).where(SecretModel.id == id_))
