from sqlalchemy import func, select

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.workload_revision import (
    WorkloadRevisionModel,
)
from app.application.ports.repository.workload_revision_repository import (
    WorkloadRevisionRepository,
)
from app.domain.models.workload_revision import WorkloadRevision


class WorkloadRevisionPersistenceAdapter(
    BasePersistenceAdapter, WorkloadRevisionRepository
):
    async def find_by_id(self, id_: int) -> WorkloadRevision | None:
        session = self._scoped_session()
        result = await session.execute(
            select(WorkloadRevisionModel).where(WorkloadRevisionModel.id == id_)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all(self, workload_id: int) -> list[WorkloadRevision]:
        session = self._scoped_session()
        result = await session.execute(
            select(WorkloadRevisionModel)
            .where(WorkloadRevisionModel.workload_id == workload_id)
            .order_by(WorkloadRevisionModel.revision.desc())
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def find_by_revision(
        self, workload_id: int, revision: int
    ) -> WorkloadRevision | None:
        session = self._scoped_session()
        result = await session.execute(
            select(WorkloadRevisionModel).where(
                WorkloadRevisionModel.workload_id == workload_id,
                WorkloadRevisionModel.revision == revision,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_max_revision(self, workload_id: int) -> int | None:
        session = self._scoped_session()
        result = await session.execute(
            select(func.max(WorkloadRevisionModel.revision)).where(
                WorkloadRevisionModel.workload_id == workload_id
            )
        )
        return result.scalar_one()

    async def save(self, revision: WorkloadRevision) -> WorkloadRevision:
        session = self._scoped_session()
        model = await session.merge(WorkloadRevisionModel.from_domain(revision))
        await session.flush()
        return model.to_domain()
