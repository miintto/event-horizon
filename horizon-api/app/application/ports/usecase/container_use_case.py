from abc import ABC, abstractmethod

from app.domain.models import Container


class ContainerUseCase(ABC):
    @abstractmethod
    async def get_container(self, container_id: int) -> Container: ...

    @abstractmethod
    async def get_containers(
        self, host_id: int | None, workload_id: int | None = None
    ) -> list[Container]: ...
