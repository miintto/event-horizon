from abc import ABC, abstractmethod

from app.domain.models import Network, WorkloadNetwork


class NetworkRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Network | None: ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Network | None: ...

    @abstractmethod
    async def find_all(self, offset: int, limit: int) -> list[Network]: ...

    @abstractmethod
    async def find_all_by_names(self, names: list[str]) -> list[Network]: ...

    @abstractmethod
    async def find_all_with_members(
        self,
    ) -> list[tuple[Network, list[WorkloadNetwork]]]: ...

    @abstractmethod
    async def save(self, network: Network) -> Network: ...

    @abstractmethod
    async def delete_by_id(self, id_: int): ...
