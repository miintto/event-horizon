from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import insert

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.container import ContainerModel
from app.application.ports.repository.container_repository import ContainerRepository
from app.domain.models.container import Container


class ContainerPersistenceAdapter(BasePersistenceAdapter, ContainerRepository):
    async def upsert_all(self, containers: list[Container]) -> list[Container]:
        if not containers:
            return []

        session = self._scoped_session()
        now = datetime.now(UTC)
        deduped = {(c.host_id, c.docker_id): c for c in containers}

        stmt = insert(ContainerModel).values(
            [
                {
                    "host_id": container.host_id,
                    "docker_id": container.docker_id,
                    "name": container.name,
                    "image": container.image,
                    "state": container.state,
                    "compose_project": container.compose_project,
                    "compose_service": container.compose_service,
                    "exit_code": container.exit_code,
                    "started_at": container.started_at,
                    "last_seen_at": now,
                }
                for container in deduped.values()
            ]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[ContainerModel.host_id, ContainerModel.docker_id],
            set_={
                "name": stmt.excluded.name,
                "image": stmt.excluded.image,
                "state": stmt.excluded.state,
                "compose_project": stmt.excluded.compose_project,
                "compose_service": stmt.excluded.compose_service,
                "exit_code": stmt.excluded.exit_code,
                "started_at": stmt.excluded.started_at,
                "last_seen_at": stmt.excluded.last_seen_at,
            },
        ).returning(ContainerModel)

        result = await session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]
