from app.application.command.metric import ContainerMetricQuery
from app.application.ports.repository import ContainerMetricRepository
from app.application.ports.usecase import ContainerMetricUseCase
from app.domain.models import ContainerMetricSeries
from app.infrastructure.transaction import transactional


class ContainerMetricService(ContainerMetricUseCase):
    def __init__(self, container_metric_repository: ContainerMetricRepository):
        self._container_metric_repository = container_metric_repository

    @transactional
    async def query(self, query: ContainerMetricQuery) -> list[ContainerMetricSeries]:
        return await self._container_metric_repository.aggregate_series(
            metric=query.metric,
            container_ids=query.container_ids,
            interval=query.interval,
            start_at=query.start_at,
            end_at=query.end_at,
        )
