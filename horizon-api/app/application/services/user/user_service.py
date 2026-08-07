from app.application.command.user import UserSearchQuery
from app.application.ports.repository import UserRepository
from app.application.ports.usecase import UserUseCase
from app.domain.exceptions import UserNotFoundException
from app.domain.models import User
from app.infrastructure.transaction import transactional


class UserService(UserUseCase):
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    @transactional
    async def get_user(self, user_id: int) -> User:
        if not (user := await self._user_repository.find_by_id(user_id)):
            raise UserNotFoundException
        return user

    @transactional
    async def get_users(self, query: UserSearchQuery) -> list[User]:
        return await self._user_repository.find_all(
            offset=query.offset,
            limit=query.size,
            role=query.role,
            is_active=query.is_active,
            email=query.email,
        )
