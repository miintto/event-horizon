from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.network_host_state import (
    NetworkHostStateModel,
)
from app.application.ports.repository import NetworkHostStateRepository
from app.domain.models import NetworkHostState


class NetworkHostStatePersistenceAdapter(
    BasePersistenceAdapter, NetworkHostStateRepository
):
    async def find_all_by_network_id(self, network_id: int) -> list[NetworkHostState]:
        session = self._scoped_session()
        result = await session.execute(
            select(NetworkHostStateModel)
            .where(NetworkHostStateModel.network_id == network_id)
            .order_by(NetworkHostStateModel.host_id)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def upsert_all(self, states: list[NetworkHostState]):
        if not states:
            return

        session = self._scoped_session()
        deduped = list({(s.network_id, s.host_id): s for s in states}.values())

        stmt = insert(NetworkHostStateModel).values(
            [
                {
                    "network_id": state.network_id,
                    "host_id": state.host_id,
                    "status": state.status,
                    "error_message": state.error_message,
                    "synced_at": state.synced_at,
                }
                for state in deduped
            ]
        )
        await session.execute(
            stmt.on_conflict_do_update(
                index_elements=[
                    NetworkHostStateModel.network_id,
                    NetworkHostStateModel.host_id,
                ],
                set_={
                    "status": stmt.excluded.status,
                    "error_message": stmt.excluded.error_message,
                    "synced_at": stmt.excluded.synced_at,
                },
            )
        )
