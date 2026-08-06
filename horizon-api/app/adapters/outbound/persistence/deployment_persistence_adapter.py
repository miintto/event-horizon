from datetime import UTC, datetime

from sqlalchemy import func, select, update

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.deployment import DeploymentModel
from app.application.ports.repository import DeploymentRepository
from app.domain.models import Deployment, DeploymentStatus


class DeploymentPersistenceAdapter(BasePersistenceAdapter, DeploymentRepository):
    async def find_by_id(self, id_: int) -> Deployment | None:
        session = self._scoped_session()
        result = await session.execute(
            select(DeploymentModel).where(DeploymentModel.id == id_)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all(
        self, host_id: int | None, workload_id: int | None
    ) -> list[Deployment]:
        session = self._scoped_session()
        stmt = select(DeploymentModel).order_by(DeploymentModel.id.desc())
        if host_id is not None:
            stmt = stmt.where(DeploymentModel.host_id == host_id)
        if workload_id is not None:
            stmt = stmt.where(DeploymentModel.workload_id == workload_id)
        result = await session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]

    async def find_active(self, workload_id: int) -> Deployment | None:
        session = self._scoped_session()
        result = await session.execute(
            select(DeploymentModel).where(
                DeploymentModel.workload_id == workload_id,
                DeploymentModel.status.in_(
                    (DeploymentStatus.PENDING, DeploymentStatus.RUNNING)
                ),
            )
        )
        model = result.scalars().first()
        return model.to_domain() if model else None

    async def find_oldest_pending(self, host_id: int) -> Deployment | None:
        session = self._scoped_session()
        result = await session.execute(
            select(DeploymentModel)
            .where(
                DeploymentModel.host_id == host_id,
                DeploymentModel.status == DeploymentStatus.PENDING,
            )
            .order_by(DeploymentModel.id)
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def update_status_to_failed(
        self, active_before: datetime, error_message: str
    ) -> int:
        session = self._scoped_session()
        stmt = (
            update(DeploymentModel)
            .where(
                DeploymentModel.status.in_(
                    (DeploymentStatus.PENDING, DeploymentStatus.RUNNING)
                ),
                func.coalesce(DeploymentModel.claimed_at, DeploymentModel.created_at)
                < active_before,
            )
            .values(
                status=DeploymentStatus.FAILED,
                error_message=error_message,
                finished_at=datetime.now(UTC),
            )
        )
        result = await session.execute(stmt)
        return result.rowcount  # type: ignore

    async def save(self, deployment: Deployment) -> Deployment:
        session = self._scoped_session()
        model = await session.merge(DeploymentModel.from_domain(deployment))
        await session.flush()
        return model.to_domain()
