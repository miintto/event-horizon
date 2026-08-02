from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.models.user import User, UserRole


@dataclass
class RegisterCommand:
    actor_id: int
    name: str | None
    email: str
    password: str
    role: UserRole = UserRole.MEMBER


@dataclass
class LoginCommand:
    email: str
    password: str


@dataclass
class TokenResult:
    access_token: str
    expires_in: int


class AuthUseCase(ABC):
    @abstractmethod
    async def register(self, command: RegisterCommand) -> TokenResult: ...

    @abstractmethod
    async def login(self, command: LoginCommand) -> TokenResult: ...

    @abstractmethod
    async def create_admin(
        self, name: str | None, email: str, password: str
    ) -> User: ...
