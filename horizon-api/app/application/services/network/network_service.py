from app.application.command.network import (
    NetworkAttachCommand,
    NetworkCreateCommand,
    NetworkSearchQuery,
)
from app.application.ports.repository import (
    NetworkHostStateRepository,
    NetworkRepository,
    WorkloadNetworkRepository,
    WorkloadRepository,
)
from app.application.ports.usecase import NetworkUseCase
from app.domain.exceptions import (
    DuplicateNetworkAttachmentException,
    DuplicateNetworkNameException,
    NetworkNotFoundException,
    WorkloadNotFoundException,
)
from app.domain.models import Network, NetworkHostState, Workload, WorkloadNetwork
from app.infrastructure.transaction import transactional


class NetworkService(NetworkUseCase):
    def __init__(
        self,
        network_host_state_repository: NetworkHostStateRepository,
        network_repository: NetworkRepository,
        workload_network_repository: WorkloadNetworkRepository,
        workload_repository: WorkloadRepository,
    ):
        self._network_host_state_repository = network_host_state_repository
        self._network_repository = network_repository
        self._workload_network_repository = workload_network_repository
        self._workload_repository = workload_repository

    @transactional
    async def get_networks(self, query: NetworkSearchQuery) -> list[Network]:
        return await self._network_repository.find_all(
            offset=query.offset, limit=query.size
        )

    @transactional
    async def create_network(self, command: NetworkCreateCommand) -> Network:
        if await self._network_repository.find_by_name(command.name):
            raise DuplicateNetworkNameException

        return await self._network_repository.save(
            Network(
                name=command.name,
                driver=command.driver,
                options=command.options,
            )
        )

    @transactional
    async def delete_network(self, network_id: int):
        if not await self._network_repository.find_by_id(network_id):
            raise NetworkNotFoundException

        await self._workload_network_repository.delete_all_by_network_id(network_id)
        await self._network_repository.delete_by_id(network_id)

    @transactional
    async def get_workloads(self, network_id: int) -> list[Workload]:
        if not await self._network_repository.find_by_id(network_id):
            raise NetworkNotFoundException

        attachments = await self._workload_network_repository.find_all_by_network_id(
            network_id
        )
        if not attachments:
            return []

        return await self._workload_repository.find_all_by_ids(
            [attachment.workload_id for attachment in attachments]
        )

    @transactional
    async def attach_workload(self, command: NetworkAttachCommand) -> WorkloadNetwork:
        if not await self._network_repository.find_by_id(command.network_id):
            raise NetworkNotFoundException
        elif not await self._workload_repository.find_by_id(command.workload_id):
            raise WorkloadNotFoundException
        elif await self._workload_network_repository.find_by_workload_and_network(
            workload_id=command.workload_id, network_id=command.network_id
        ):
            raise DuplicateNetworkAttachmentException

        return await self._workload_network_repository.save(
            WorkloadNetwork(
                workload_id=command.workload_id,
                network_id=command.network_id,
                alias=command.alias,
            )
        )

    @transactional
    async def detach_workload(self, network_id: int, workload_id: int):
        attachment = (
            await self._workload_network_repository.find_by_workload_and_network(
                workload_id=workload_id, network_id=network_id
            )
        )
        if not attachment:
            raise NetworkNotFoundException

        await self._workload_network_repository.delete_by_id(attachment.pk)

    @transactional
    async def get_host_states(self, network_id: int) -> list[NetworkHostState]:
        if not await self._network_repository.find_by_id(network_id):
            raise NetworkNotFoundException

        return await self._network_host_state_repository.find_all_by_network_id(
            network_id
        )
