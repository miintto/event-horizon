from sqlalchemy import delete, select

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.network import NetworkModel
from app.adapters.outbound.persistence.models.workload_network import (
    WorkloadNetworkModel,
)
from app.application.ports.repository import NetworkRepository
from app.domain.models import Network, WorkloadNetwork


class NetworkPersistenceAdapter(BasePersistenceAdapter, NetworkRepository):
    async def find_by_id(self, id_: int) -> Network | None:
        session = self._scoped_session()
        result = await session.execute(
            select(NetworkModel).where(NetworkModel.id == id_)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_by_name(self, name: str) -> Network | None:
        session = self._scoped_session()
        result = await session.execute(
            select(NetworkModel).where(NetworkModel.name == name)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all(self, offset: int, limit: int) -> list[Network]:
        session = self._scoped_session()
        result = await session.execute(
            select(NetworkModel).order_by(NetworkModel.name).offset(offset).limit(limit)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def find_all_by_names(self, names: list[str]) -> list[Network]:
        if not names:
            return []

        session = self._scoped_session()
        result = await session.execute(
            select(NetworkModel)
            .where(NetworkModel.name.in_(names))
            .order_by(NetworkModel.name)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def find_all_with_members(
        self,
    ) -> list[tuple[Network, list[WorkloadNetwork]]]:
        session = self._scoped_session()
        result = await session.execute(
            select(NetworkModel, WorkloadNetworkModel)
            .outerjoin(
                WorkloadNetworkModel,
                WorkloadNetworkModel.network_id == NetworkModel.id,
            )
            .order_by(NetworkModel.name, WorkloadNetworkModel.id)
        )

        networks: dict[int, tuple[Network, list[WorkloadNetwork]]] = {}
        for model, attachment in result.all():
            _, members = networks.setdefault(model.id, (model.to_domain(), []))
            if attachment is not None:
                members.append(attachment.to_domain())
        return list(networks.values())

    async def save(self, network: Network) -> Network:
        session = self._scoped_session()
        model = await session.merge(NetworkModel.from_domain(network))
        await session.flush()
        return model.to_domain()

    async def delete_by_id(self, id_: int):
        session = self._scoped_session()
        await session.execute(delete(NetworkModel).where(NetworkModel.id == id_))
