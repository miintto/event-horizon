from abc import ABC, abstractmethod

from app.domain.models.host import Host


class HostUseCase(ABC):
    @abstractmethod
    async def get_host(self, host_id: int) -> Host: ...

    @abstractmethod
    async def list_hosts(self) -> list[Host]: ...
