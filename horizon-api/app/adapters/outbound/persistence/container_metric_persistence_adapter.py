from dataclasses import asdict

from sqlalchemy.dialects.postgresql import insert

from app.adapters.outbound.persistence.base import BasePersistenceAdapter
from app.adapters.outbound.persistence.models.container_metric import (
    ContainerMetricModel,
)
from app.application.ports.repository.container_metric_repository import (
    ContainerMetricRepository,
)
from app.domain.models.container_metric import ContainerMetric


class ContainerMetricPersistenceAdapter(
    BasePersistenceAdapter, ContainerMetricRepository
):
    async def save_all(self, datapoints: list[ContainerMetric]) -> int:
        if not datapoints:
            return 0

        session = self._scoped_session()
        stmt = (
            insert(ContainerMetricModel)
            .values([asdict(datapoint) for datapoint in datapoints])
            .on_conflict_do_nothing(index_elements=["container_id", "collected_at"])
        )
        result = await session.execute(stmt)
        return result.rowcount
