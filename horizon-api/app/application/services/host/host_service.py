from app.application.ports.repository.host_repository import HostRepository
from app.application.ports.usecase.host_use_case import HostUseCase
from app.domain.exceptions import HostNotFoundException
from app.domain.models.host import Host
from app.infrastructure.transaction import transactional


class HostService(HostUseCase):
    def __init__(self, host_repository: HostRepository):
        self._host_repository = host_repository

    @transactional
    async def get_host(self, host_id: int) -> Host:
        host = await self._host_repository.find_by_id(host_id)
        if not host:
            raise HostNotFoundException
        return host

    @transactional
    async def list_hosts(self) -> list[Host]:
        return await self._host_repository.find_all()
