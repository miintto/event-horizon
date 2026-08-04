from datetime import UTC, datetime, timedelta

from app.application.command.collect import (
    CollectCommand,
    CollectResult,
    ContainerCollectItem,
)
from app.application.ports.repository import (
    ContainerMetricRepository,
    ContainerRepository,
    HostMetricRepository,
    HostRepository,
)
from app.application.ports.usecase import CollectUseCase
from app.infrastructure.transaction import transactional


class CollectService(CollectUseCase):
    def __init__(
        self,
        host_metric_repository: HostMetricRepository,
        host_repository: HostRepository,
        container_repository: ContainerRepository,
        container_metric_repository: ContainerMetricRepository,
        stale_after_secs: int,
    ):
        self._host_metric_repository = host_metric_repository
        self._host_repository = host_repository
        self._container_repository = container_repository
        self._container_metric_repository = container_metric_repository
        self._stale_after_secs = stale_after_secs

    @transactional
    async def collect(self, command: CollectCommand) -> CollectResult:
        host = await self._host_repository.upsert_by_agent_uuid(
            agent_uuid=command.agent_uuid, hostname=command.hostname
        )
        metrics = [dp.to_domain(host.pk) for dp in command.datapoints]
        ingested = await self._host_metric_repository.save_all(metrics)
        container_ingested = await self._collect_containers(host.pk, command.containers)
        return CollectResult(
            host_id=host.pk,
            ingested=ingested,
            container_ingested=container_ingested,
        )

    @transactional
    async def post_collect(self, host_id: int):
        await self._container_repository.update_state_to_exited(
            host_id,
            datetime.now(UTC) - timedelta(seconds=self._stale_after_secs),
        )

    async def _collect_containers(
        self, host_id: int, items: list[ContainerCollectItem]
    ) -> int:
        if not items:
            return 0

        containers = await self._container_repository.upsert_all(
            [item.to_domain(host_id) for item in items]
        )
        container_ids = {container.docker_id: container.pk for container in containers}
        metrics = [
            datapoint.to_domain(container_ids[item.docker_id])
            for item in items
            if item.docker_id in container_ids
            for datapoint in item.datapoints
        ]
        return await self._container_metric_repository.save_all(metrics)
