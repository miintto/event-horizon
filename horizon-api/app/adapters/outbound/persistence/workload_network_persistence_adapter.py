from sqlalchemy import delete, select

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.workload_network import (
    WorkloadNetworkModel,
)
from app.application.ports.repository import WorkloadNetworkRepository
from app.domain.models import WorkloadNetwork


class WorkloadNetworkPersistenceAdapter(
    BasePersistenceAdapter, WorkloadNetworkRepository
):
    async def find_by_workload_and_network(
        self, workload_id: int, network_id: int
    ) -> WorkloadNetwork | None:
        session = self._scoped_session()
        result = await session.execute(
            select(WorkloadNetworkModel).where(
                WorkloadNetworkModel.workload_id == workload_id,
                WorkloadNetworkModel.network_id == network_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all_by_workload_id(self, workload_id: int) -> list[WorkloadNetwork]:
        session = self._scoped_session()
        result = await session.execute(
            select(WorkloadNetworkModel)
            .where(WorkloadNetworkModel.workload_id == workload_id)
            .order_by(WorkloadNetworkModel.id)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def find_all_by_network_id(self, network_id: int) -> list[WorkloadNetwork]:
        session = self._scoped_session()
        result = await session.execute(
            select(WorkloadNetworkModel)
            .where(WorkloadNetworkModel.network_id == network_id)
            .order_by(WorkloadNetworkModel.id)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def save(self, attachment: WorkloadNetwork) -> WorkloadNetwork:
        session = self._scoped_session()
        model = await session.merge(WorkloadNetworkModel.from_domain(attachment))
        await session.flush()
        return model.to_domain()

    async def delete_by_id(self, id_: int):
        session = self._scoped_session()
        await session.execute(
            delete(WorkloadNetworkModel).where(WorkloadNetworkModel.id == id_)
        )

    async def delete_all_by_network_id(self, network_id: int):
        session = self._scoped_session()
        await session.execute(
            delete(WorkloadNetworkModel).where(
                WorkloadNetworkModel.network_id == network_id
            )
        )
