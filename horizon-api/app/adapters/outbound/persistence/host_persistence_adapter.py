from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.host import HostModel
from app.application.ports.repository.host_repository import HostRepository
from app.domain.models.host import Host, HostStatus


class HostPersistenceAdapter(BasePersistenceAdapter, HostRepository):
    async def find_by_id(self, id_: int) -> Host | None:
        session = self._scoped_session()
        result = await session.execute(select(HostModel).where(HostModel.id == id_))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all(self) -> list[Host]:
        session = self._scoped_session()
        result = await session.execute(select(HostModel).order_by(HostModel.id))
        return [model.to_domain() for model in result.scalars().all()]

    async def upsert_by_agent_uuid(self, agent_uuid: UUID, hostname: str) -> Host:
        session = self._scoped_session()
        now = datetime.now(UTC)
        stmt = (
            insert(HostModel)
            .values(
                agent_uuid=agent_uuid,
                hostname=hostname,
                status=HostStatus.ONLINE,
                last_seen_at=now,
            )
            .on_conflict_do_update(
                index_elements=[HostModel.agent_uuid],
                set_={
                    "hostname": hostname,
                    "status": HostStatus.ONLINE,
                    "last_seen_at": now,
                },
            )
            .returning(HostModel)
        )
        result = await session.execute(stmt)
        return result.scalar_one().to_domain()
