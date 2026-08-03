from app.application.command.metric import HostMetricQuery
from app.application.ports.repository import HostMetricRepository
from app.application.ports.usecase import HostMetricUseCase
from app.domain.models import HostMetricSeries
from app.infrastructure.transaction import transactional


class HostMetricService(HostMetricUseCase):
    def __init__(self, host_metric_repository: HostMetricRepository):
        self._host_metric_repository = host_metric_repository

    @transactional
    async def query(self, query: HostMetricQuery) -> list[HostMetricSeries]:
        return await self._host_metric_repository.aggregate_series(
            metric=query.metric,
            host_ids=query.host_ids,
            interval=query.interval,
            start_at=query.start_at,
            end_at=query.end_at,
        )
