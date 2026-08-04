from abc import ABC, abstractmethod

from app.application.command.secret import (
    SecretCreateCommand,
    SecretSearchQuery,
    SecretUpdateCommand,
)
from app.domain.models import Secret


class SecretUseCase(ABC):
    @abstractmethod
    async def get_secrets(self, query: SecretSearchQuery) -> list[Secret]: ...

    @abstractmethod
    async def create_secret(self, command: SecretCreateCommand) -> Secret: ...

    @abstractmethod
    async def update_secret(self, command: SecretUpdateCommand) -> Secret: ...

    @abstractmethod
    async def delete_secret(self, secret_id: int): ...

    @abstractmethod
    async def set_secret(self, name: str, value: str) -> Secret: ...
