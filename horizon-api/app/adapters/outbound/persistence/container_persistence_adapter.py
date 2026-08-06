from datetime import UTC, datetime

from sqlalchemy import select, tuple_, update
from sqlalchemy.dialects.postgresql import insert

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.container import ContainerModel
from app.application.ports.repository import ContainerRepository
from app.domain.models import Container, ContainerState


class ContainerPersistenceAdapter(BasePersistenceAdapter, ContainerRepository):
    async def find_by_id(self, id_: int) -> Container | None:
        session = self._scoped_session()
        result = await session.execute(
            select(ContainerModel).where(ContainerModel.id == id_)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all(
        self, host_id: int | None, workload_id: int | None = None
    ) -> list[Container]:
        session = self._scoped_session()
        stmt = select(ContainerModel).order_by(ContainerModel.id.desc())
        if host_id is not None:
            stmt = stmt.where(ContainerModel.host_id == host_id)
        if workload_id is not None:
            stmt = stmt.where(ContainerModel.workload_id == workload_id)
        result = await session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]

    async def find_docker_ids_alive(self, workload_id: int, host_id: int) -> list[str]:
        session = self._scoped_session()
        result = await session.execute(
            select(ContainerModel.docker_id).where(
                ContainerModel.workload_id == workload_id,
                ContainerModel.host_id == host_id,
                ContainerModel.state != ContainerState.EXITED,
            )
        )
        return list(result.scalars().all())

    async def upsert_all(self, containers: list[Container]) -> list[Container]:
        if not containers:
            return []

        session = self._scoped_session()
        now = datetime.now(UTC)
        deduped = list({(c.host_id, c.docker_id): c for c in containers}.values())

        keys = [(c.host_id, c.docker_id) for c in deduped]
        existing = (
            (
                await session.execute(
                    select(ContainerModel).where(
                        tuple_(ContainerModel.host_id, ContainerModel.docker_id).in_(
                            keys
                        )
                    )
                )
            )
            .scalars()
            .all()
        )
        existing_by_key = {(m.host_id, m.docker_id): m for m in existing}

        result: list[Container] = []

        for c in deduped:
            model = existing_by_key.get((c.host_id, c.docker_id))
            if model is None:
                continue
            model.state = c.state
            model.exit_code = c.exit_code
            model.started_at = c.started_at
            model.last_seen_at = now
            result.append(model.to_domain())

        new_items = [
            c for c in deduped if (c.host_id, c.docker_id) not in existing_by_key
        ]
        if new_items:
            stmt = (
                insert(ContainerModel)
                .values(
                    [
                        {
                            "host_id": c.host_id,
                            "docker_id": c.docker_id,
                            "name": c.name,
                            "image": c.image,
                            "state": c.state,
                            "compose_project": c.compose_project,
                            "compose_service": c.compose_service,
                            "exit_code": c.exit_code,
                            "started_at": c.started_at,
                            "last_seen_at": now,
                        }
                        for c in new_items
                    ]
                )
                .on_conflict_do_nothing(
                    index_elements=[
                        ContainerModel.host_id,
                        ContainerModel.docker_id,
                    ]
                )
                .returning(ContainerModel)
            )
            inserted = (await session.execute(stmt)).scalars().all()
            result.extend(model.to_domain() for model in inserted)

        return result

    async def upsert_with_revision(self, container: Container) -> Container:
        session = self._scoped_session()
        now = datetime.now(UTC)

        model = (
            await session.execute(
                select(ContainerModel).where(
                    ContainerModel.host_id == container.host_id,
                    ContainerModel.docker_id == container.docker_id,
                )
            )
        ).scalar_one_or_none()

        if model is None:
            model = ContainerModel(
                host_id=container.host_id,
                docker_id=container.docker_id,
                name=container.name,
                image=container.image,
                state=container.state,
                last_seen_at=now,
            )
            session.add(model)

        model.workload_id = container.workload_id
        model.revision_id = container.revision_id
        model.name = container.name
        model.image = container.image
        await session.flush()
        return model.to_domain()

    async def mark_exited(self, host_id: int, docker_ids: list[str]) -> int:
        if not docker_ids:
            return 0

        session = self._scoped_session()
        stmt = (
            update(ContainerModel)
            .where(
                ContainerModel.host_id == host_id,
                ContainerModel.docker_id.in_(docker_ids),
                ContainerModel.state != ContainerState.EXITED,
            )
            .values(state=ContainerState.EXITED)
        )
        result = await session.execute(stmt)
        return result.rowcount  # type: ignore

    async def update_state_to_exited(self, host_id: int, seen_before: datetime) -> int:
        session = self._scoped_session()
        stmt = (
            update(ContainerModel)
            .where(
                ContainerModel.host_id == host_id,
                ContainerModel.last_seen_at < seen_before,
                ContainerModel.state != ContainerState.EXITED,
            )
            .values(state=ContainerState.EXITED)
        )
        result = await session.execute(stmt)
        return result.rowcount  # type: ignore
