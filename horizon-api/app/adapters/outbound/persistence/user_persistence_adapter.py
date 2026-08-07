from sqlalchemy import select

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.user import UserModel
from app.application.ports.repository import UserRepository
from app.domain.models import User, UserRole


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

    async def find_all(
        self,
        offset: int,
        limit: int,
        role: UserRole | None = None,
        is_active: bool | None = None,
        email: str | None = None,
    ) -> list[User]:
        session = self._scoped_session()
        stmt = select(UserModel)
        if role is not None:
            stmt = stmt.where(UserModel.role == role)
        if is_active is not None:
            stmt = stmt.where(UserModel.is_active == is_active)
        if email:
            keyword = (
                email.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            )
            stmt = stmt.where(UserModel.email.ilike(f"%{keyword}%", escape="\\"))

        result = await session.execute(
            stmt.order_by(UserModel.id).offset(offset).limit(limit)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def save(self, user: User) -> User:
        session = self._scoped_session()
        model = await session.merge(UserModel.from_domain(user))
        await session.flush()
        return model.to_domain()
