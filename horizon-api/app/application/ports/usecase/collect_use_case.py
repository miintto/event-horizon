from abc import ABC, abstractmethod

from app.application.command.collect import CollectCommand, CollectResult


class CollectUseCase(ABC):
    @abstractmethod
    async def collect(self, command: CollectCommand) -> CollectResult: ...

    @abstractmethod
    async def post_collect(self, host_id: int): ...
