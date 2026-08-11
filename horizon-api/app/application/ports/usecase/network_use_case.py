from abc import ABC, abstractmethod

from app.application.command.network import (
    NetworkAttachCommand,
    NetworkCreateCommand,
    NetworkSearchQuery,
)
from app.domain.models import Network, NetworkHostState, Workload, WorkloadNetwork


class NetworkUseCase(ABC):
    @abstractmethod
    async def get_networks(self, query: NetworkSearchQuery) -> list[Network]: ...

    @abstractmethod
    async def create_network(self, command: NetworkCreateCommand) -> Network: ...

    @abstractmethod
    async def delete_network(self, network_id: int): ...

    @abstractmethod
    async def get_workloads(self, network_id: int) -> list[Workload]: ...

    @abstractmethod
    async def attach_workload(
        self, command: NetworkAttachCommand
    ) -> WorkloadNetwork: ...

    @abstractmethod
    async def detach_workload(self, network_id: int, workload_id: int): ...

    @abstractmethod
    async def get_host_states(self, network_id: int) -> list[NetworkHostState]: ...
