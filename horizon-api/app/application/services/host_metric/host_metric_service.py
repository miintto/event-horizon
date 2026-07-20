from app.application.ports.repository.host_metric_repository import (
    HostMetricRepository,
)
from app.application.ports.repository.host_repository import HostRepository
from app.application.ports.usecase.host_metric_use_case import (
    HostMetricCollectCommand,
    HostMetricCollectResult,
    HostMetricQuery,
    HostMetricUseCase,
)
from app.domain.models.host_metric import HostMetricSeries
from app.infrastructure.transaction import transactional


class HostMetricService(HostMetricUseCase):
    def __init__(
        self,
        host_metric_repository: HostMetricRepository,
        host_repository: HostRepository,
    ):
        self._host_metric_repository = host_metric_repository
        self._host_repository = host_repository

    @transactional
    async def collect(
        self, command: HostMetricCollectCommand
    ) -> HostMetricCollectResult:
        host = await self._host_repository.upsert_by_agent_uuid(
            agent_uuid=command.agent_uuid, hostname=command.hostname
        )
        metrics = [dp.to_domain(host.id) for dp in command.datapoints]
        ingested = await self._host_metric_repository.save_all(metrics)
        return HostMetricCollectResult(ingested=ingested)

    @transactional
    async def query(self, query: HostMetricQuery) -> list[HostMetricSeries]:
        return await self._host_metric_repository.aggregate_series(
            metric=query.metric,
            host_ids=query.host_ids,
            interval=query.interval,
            start_at=query.start_at,
            end_at=query.end_at,
        )
