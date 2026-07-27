from abc import ABC, abstractmethod

from app.domain.models.container import Container


class ContainerUseCase(ABC):
    @abstractmethod
    async def get_container(self, container_id: int) -> Container: ...

    @abstractmethod
    async def list_containers(self, host_id: int | None) -> list[Container]: ...
