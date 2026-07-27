from app.application.ports.repository.container_repository import ContainerRepository
from app.application.ports.usecase.container_use_case import ContainerUseCase
from app.domain.exceptions import ContainerNotFoundException
from app.domain.models.container import Container
from app.infrastructure.transaction import transactional


class ContainerService(ContainerUseCase):
    def __init__(self, container_repository: ContainerRepository):
        self._container_repository = container_repository

    @transactional
    async def get_container(self, container_id: int) -> Container:
        container = await self._container_repository.find_by_id(container_id)
        if not container:
            raise ContainerNotFoundException
        return container

    @transactional
    async def list_containers(self, host_id: int | None) -> list[Container]:
        return await self._container_repository.find_all(host_id)
