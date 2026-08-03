from sqlalchemy import func, select, update

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.container import ContainerModel
from app.adapters.outbound.persistence.models.workload import WorkloadModel
from app.application.ports.repository import WorkloadRepository
from app.domain.models import ContainerState, Workload, WorkloadDetail


class WorkloadPersistenceAdapter(BasePersistenceAdapter, WorkloadRepository):
    async def find_by_id(self, id_: int) -> Workload | None:
        session = self._scoped_session()
        result = await session.execute(
            select(WorkloadModel).where(WorkloadModel.id == id_)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_by_name(self, name: str) -> Workload | None:
        session = self._scoped_session()
        result = await session.execute(
            select(WorkloadModel).where(WorkloadModel.name == name)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all_with_counts(self, host_id: int | None) -> list[Workload]:
        session = self._scoped_session()
        join_condition = ContainerModel.workload_id == WorkloadModel.id
        if host_id is not None:
            join_condition &= ContainerModel.host_id == host_id

        stmt = (
            select(
                WorkloadModel,
                func.count(ContainerModel.id).label("container_count"),
                func.count(ContainerModel.id)
                .filter(ContainerModel.state == ContainerState.RUNNING)
                .label("running_count"),
                func.count(func.distinct(ContainerModel.host_id)).label("host_count"),
            )
            .outerjoin(ContainerModel, join_condition)
            .group_by(WorkloadModel.id)
            .order_by(WorkloadModel.id)
        )
        if host_id is not None:
            stmt = stmt.having(func.count(ContainerModel.id) > 0)
        result = await session.execute(stmt)
        return [
            Workload(
                id=model.id,
                name=model.name,
                current_revision_id=model.current_revision_id,
                created_at=model.created_at,
                detail=WorkloadDetail(
                    container_count=container_count,
                    running_count=running_count,
                    host_count=host_count,
                ),
            )
            for model, container_count, running_count, host_count in result.all()
        ]

    async def update_current_revision_id(
        self, workload_id: int, revision_id: int
    ) -> None:
        session = self._scoped_session()
        await session.execute(
            update(WorkloadModel)
            .where(WorkloadModel.id == workload_id)
            .values(current_revision_id=revision_id)
        )

    async def save(self, workload: Workload) -> Workload:
        session = self._scoped_session()
        model = WorkloadModel(name=workload.name)
        session.add(model)
        await session.flush()
        return model.to_domain()
