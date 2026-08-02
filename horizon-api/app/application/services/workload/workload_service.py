from app.application.ports.repository.workload_repository import WorkloadRepository
from app.application.ports.repository.workload_revision_repository import (
    WorkloadRevisionRepository,
)
from app.application.ports.usecase.workload_use_case import (
    RevisionCreateCommand,
    RevisionDefinition,
    WorkloadCreateCommand,
    WorkloadResult,
    WorkloadUseCase,
)
from app.domain.exceptions import (
    DuplicateWorkloadNameException,
    WorkloadNotFoundException,
    WorkloadRevisionNotFoundException,
)
from app.domain.models.workload import Workload
from app.domain.models.workload_revision import WorkloadRevision
from app.infrastructure.transaction import transactional


class WorkloadService(WorkloadUseCase):
    def __init__(
        self,
        workload_repository: WorkloadRepository,
        workload_revision_repository: WorkloadRevisionRepository,
    ):
        self._workload_repository = workload_repository
        self._workload_revision_repository = workload_revision_repository

    @transactional
    async def get_workload(self, workload_id: int) -> Workload:
        workload = await self._workload_repository.find_by_id(workload_id)
        if not workload:
            raise WorkloadNotFoundException
        return workload

    @transactional
    async def get_workloads(self, host_id: int | None) -> list[WorkloadResult]:
        return await self._workload_repository.find_all_with_counts(host_id)

    @transactional
    async def create_workload(self, command: WorkloadCreateCommand) -> Workload:
        if await self._workload_repository.find_by_name(command.name):
            raise DuplicateWorkloadNameException

        workload = await self._workload_repository.save(Workload(name=command.name))
        revision = await self._create_revision(workload.id, 1, command.definition)
        workload.current_revision_id = revision.id
        return workload

    @transactional
    async def get_revisions(self, workload_id: int) -> list[WorkloadRevision]:
        await self.get_workload(workload_id)
        return await self._workload_revision_repository.find_all(workload_id)

    @transactional
    async def get_revision(self, workload_id: int, revision: int) -> WorkloadRevision:
        result = await self._workload_revision_repository.find_by_revision(
            workload_id, revision
        )
        if not result:
            raise WorkloadRevisionNotFoundException
        return result

    @transactional
    async def add_revision(self, command: RevisionCreateCommand) -> WorkloadRevision:
        await self.get_workload(command.workload_id)

        max_revision = await self._workload_revision_repository.find_max_revision(
            command.workload_id
        )
        return await self._create_revision(
            command.workload_id, (max_revision or 0) + 1, command.definition
        )

    async def _create_revision(
        self, workload_id: int, revision: int, definition: RevisionDefinition
    ) -> WorkloadRevision:
        saved = await self._workload_revision_repository.save(
            WorkloadRevision(
                workload_id=workload_id,
                revision=revision,
                image=definition.image,
                cpu_limit=definition.cpu_limit,
                memory_limit=definition.memory_limit,
                spec=definition.spec,
            )
        )
        await self._workload_repository.update_current_revision_id(
            workload_id, saved.id
        )
        return saved
