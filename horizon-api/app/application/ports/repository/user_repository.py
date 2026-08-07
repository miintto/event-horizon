from abc import ABC, abstractmethod

from app.domain.models import User, UserRole


class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def find_all(
        self,
        offset: int,
        limit: int,
        role: UserRole | None = None,
        is_active: bool | None = None,
        email: str | None = None,
    ) -> list[User]: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...
