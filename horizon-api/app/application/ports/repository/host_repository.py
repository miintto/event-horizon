from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models import Host


class HostRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Host | None: ...

    @abstractmethod
    async def find_all(self) -> list[Host]: ...

    @abstractmethod
    async def upsert_by_agent_uuid(self, agent_uuid: UUID, hostname: str) -> Host: ...
