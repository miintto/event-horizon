from abc import ABC, abstractmethod

from app.domain.models import NetworkHostState


class NetworkHostStateRepository(ABC):
    @abstractmethod
    async def find_all_by_network_id(
        self, network_id: int
    ) -> list[NetworkHostState]: ...

    @abstractmethod
    async def upsert_all(self, states: list[NetworkHostState]): ...
