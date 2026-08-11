from abc import ABC, abstractmethod

from app.application.command.network_sync import NetworkDesiredState, NetworkSyncCommand


class NetworkSyncUseCase(ABC):
    @abstractmethod
    async def sync(self, command: NetworkSyncCommand) -> NetworkDesiredState: ...
