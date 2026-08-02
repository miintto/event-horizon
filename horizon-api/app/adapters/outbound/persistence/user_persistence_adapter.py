from sqlalchemy import select

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.user import UserModel
from app.application.ports.repository.user_repository import UserRepository
from app.domain.models.user import User


class UserPersistenceAdapter(BasePersistenceAdapter, UserRepository):
    async def find_by_id(self, id_: int) -> User | None:
        session = self._scoped_session()
        result = await session.execute(select(UserModel).where(UserModel.id == id_))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_by_email(self, email: str) -> User | None:
        session = self._scoped_session()
        result = await session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def save(self, user: User) -> User:
        session = self._scoped_session()
        model = await session.merge(UserModel.from_domain(user))
        await session.flush()
        return model.to_domain()
