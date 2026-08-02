from abc import ABC, abstractmethod

from app.domain.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...
