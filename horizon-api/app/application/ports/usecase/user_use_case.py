from abc import ABC, abstractmethod

from app.application.command.user import UserSearchQuery
from app.domain.models import User


class UserUseCase(ABC):
    @abstractmethod
    async def get_user(self, user_id: int) -> User: ...

    @abstractmethod
    async def get_users(self, query: UserSearchQuery) -> list[User]: ...
