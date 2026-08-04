from abc import ABC, abstractmethod

from app.domain.models import Secret


class SecretRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Secret | None: ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Secret | None: ...

    @abstractmethod
    async def find_all(self, offset: int, limit: int) -> list[Secret]: ...

    @abstractmethod
    async def save(self, secret: Secret) -> Secret: ...

    @abstractmethod
    async def delete_by_id(self, id_: int): ...
