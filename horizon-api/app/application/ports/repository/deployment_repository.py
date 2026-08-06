from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.models import Deployment


class DeploymentRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id_: int) -> Deployment | None: ...

    @abstractmethod
    async def find_all(
        self, host_id: int | None, workload_id: int | None
    ) -> list[Deployment]: ...

    @abstractmethod
    async def find_active(self, workload_id: int) -> Deployment | None: ...

    @abstractmethod
    async def find_oldest_pending(self, host_id: int) -> Deployment | None: ...

    @abstractmethod
    async def update_status_to_failed(
        self, active_before: datetime, error_message: str
    ) -> int: ...

    @abstractmethod
    async def save(self, deployment: Deployment) -> Deployment: ...
