from abc import ABC, abstractmethod

from app.domain.models import WorkloadNetwork


class WorkloadNetworkRepository(ABC):
    @abstractmethod
    async def find_by_workload_and_network(
        self, workload_id: int, network_id: int
    ) -> WorkloadNetwork | None: ...

    @abstractmethod
    async def find_all_by_workload_id(
        self, workload_id: int
    ) -> list[WorkloadNetwork]: ...

    @abstractmethod
    async def find_all_by_network_id(
        self, network_id: int
    ) -> list[WorkloadNetwork]: ...

    @abstractmethod
    async def save(self, attachment: WorkloadNetwork) -> WorkloadNetwork: ...

    @abstractmethod
    async def delete_by_id(self, id_: int): ...

    @abstractmethod
    async def delete_all_by_network_id(self, network_id: int): ...
