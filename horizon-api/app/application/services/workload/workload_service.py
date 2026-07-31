from app.application.ports.repository.workload_repository import WorkloadRepository
from app.application.ports.usecase.workload_use_case import (
    WorkloadResult,
    WorkloadUseCase,
)
from app.domain.exceptions import WorkloadNotFoundException
from app.domain.models.workload import Workload
from app.infrastructure.transaction import transactional


class WorkloadService(WorkloadUseCase):
    def __init__(self, workload_repository: WorkloadRepository):
        self._workload_repository = workload_repository

    @transactional
    async def get_workload(self, workload_id: int) -> Workload:
        workload = await self._workload_repository.find_by_id(workload_id)
        if not workload:
            raise WorkloadNotFoundException
        return workload

    @transactional
    async def get_workloads(self, host_id: int | None) -> list[WorkloadResult]:
        return await self._workload_repository.find_all_with_counts(host_id)
