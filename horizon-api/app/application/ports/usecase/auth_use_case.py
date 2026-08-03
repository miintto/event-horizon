from abc import ABC, abstractmethod

from app.application.command.auth import LoginCommand, RegisterCommand, TokenResult
from app.domain.models import User


class AuthUseCase(ABC):
    @abstractmethod
    async def register(self, command: RegisterCommand) -> TokenResult: ...

    @abstractmethod
    async def login(self, command: LoginCommand) -> TokenResult: ...

    @abstractmethod
    async def create_admin(
        self, name: str | None, email: str, password: str
    ) -> User: ...
