from sqlalchemy import func, select, update

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.container import ContainerModel
from app.adapters.outbound.persistence.models.workload import WorkloadModel
from app.application.ports.repository.workload_repository import WorkloadRepository
from app.application.ports.usecase.workload_use_case import WorkloadResult
from app.domain.models.container import ContainerState
from app.domain.models.workload import Workload


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

    async def find_all_with_counts(self, host_id: int | None) -> list[WorkloadResult]:
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
            # 인스턴스가 아직 없는 정의도 목록에 나와야 하므로 outer join
            .outerjoin(ContainerModel, join_condition)
            .group_by(WorkloadModel.id)
            .order_by(WorkloadModel.id)
        )
        if host_id is not None:
            # host 필터를 준 경우엔 그 host 에 인스턴스가 있는 workload 만
            stmt = stmt.having(func.count(ContainerModel.id) > 0)
        result = await session.execute(stmt)
        return [
            WorkloadResult(
                id=model.id,
                name=model.name,
                container_count=container_count,
                running_count=running_count,
                host_count=host_count,
                created_at=model.created_at,
            )
            for model, container_count, running_count, host_count in result.all()
        ]

    async def save(self, workload: Workload) -> Workload:
        session = self._scoped_session()
        model = WorkloadModel(name=workload.name)
        session.add(model)
        await session.flush()
        return model.to_domain()

    async def update_current_revision_id(
        self, workload_id: int, revision_id: int
    ) -> None:
        session = self._scoped_session()
        await session.execute(
            update(WorkloadModel)
            .where(WorkloadModel.id == workload_id)
            .values(current_revision_id=revision_id)
        )
