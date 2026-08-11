from datetime import UTC, datetime

from app.application.command.network_sync import (
    NetworkDesired,
    NetworkDesiredState,
    NetworkMember,
    NetworkSyncCommand,
    NetworkSyncResult,
)
from app.application.ports.repository import (
    HostRepository,
    NetworkHostStateRepository,
    NetworkRepository,
    WorkloadRepository,
)
from app.application.ports.usecase import NetworkSyncUseCase
from app.domain.exceptions import HostNotFoundException
from app.domain.models import NetworkHostState
from app.infrastructure.transaction import transactional


class NetworkSyncService(NetworkSyncUseCase):
    def __init__(
        self,
        host_repository: HostRepository,
        network_host_state_repository: NetworkHostStateRepository,
        network_repository: NetworkRepository,
        workload_repository: WorkloadRepository,
    ):
        self._host_repository = host_repository
        self._network_host_state_repository = network_host_state_repository
        self._network_repository = network_repository
        self._workload_repository = workload_repository

    @transactional
    async def sync(self, command: NetworkSyncCommand) -> NetworkDesiredState:
        host = await self._host_repository.find_by_agent_uuid(command.agent_uuid)
        if not host:
            raise HostNotFoundException

        await self._record_results(host.pk, command.results)
        return await self._build_desired_state()

    async def _record_results(self, host_id: int, results: list[NetworkSyncResult]):
        if not results:
            return

        networks = {
            network.name: network
            for network in await self._network_repository.find_all_by_names(
                [result.network_name for result in results]
            )
        }

        now = datetime.now(UTC)
        await self._network_host_state_repository.upsert_all(
            [
                NetworkHostState(
                    network_id=networks[result.network_name].pk,
                    host_id=host_id,
                    status=result.status,
                    error_message=result.error_message,
                    synced_at=now,
                )
                for result in results
                if result.network_name in networks
            ]
        )

    async def _build_desired_state(self) -> NetworkDesiredState:
        pairs = await self._network_repository.find_all_with_members()
        names = {
            workload.pk: workload.name
            for workload in await self._workload_repository.find_all_by_ids(
                list({member.workload_id for _, members in pairs for member in members})
            )
        }

        return NetworkDesiredState(
            networks=[
                NetworkDesired(
                    name=network.name,
                    driver=network.driver,
                    options=network.options,
                    members=[
                        NetworkMember(
                            workload_id=member.workload_id,
                            alias=member.alias or names[member.workload_id],
                        )
                        for member in members
                        if member.workload_id in names
                    ],
                )
                for network, members in pairs
            ]
        )
