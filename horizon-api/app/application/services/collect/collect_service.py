from app.application.ports.repository.container_metric_repository import (
    ContainerMetricRepository,
)
from app.application.ports.repository.container_repository import ContainerRepository
from app.application.ports.repository.host_metric_repository import HostMetricRepository
from app.application.ports.repository.host_repository import HostRepository
from app.application.ports.usecase.collect_use_case import (
    CollectCommand,
    CollectResult,
    CollectUseCase,
    ContainerCollectItem,
)
from app.infrastructure.transaction import transactional


class CollectService(CollectUseCase):
    def __init__(
        self,
        host_metric_repository: HostMetricRepository,
        host_repository: HostRepository,
        container_repository: ContainerRepository,
        container_metric_repository: ContainerMetricRepository,
    ):
        self._host_metric_repository = host_metric_repository
        self._host_repository = host_repository
        self._container_repository = container_repository
        self._container_metric_repository = container_metric_repository

    @transactional
    async def collect(self, command: CollectCommand) -> CollectResult:
        host = await self._host_repository.upsert_by_agent_uuid(
            agent_uuid=command.agent_uuid, hostname=command.hostname
        )
        metrics = [dp.to_domain(host.id) for dp in command.datapoints]
        ingested = await self._host_metric_repository.save_all(metrics)
        container_ingested = await self._collect_containers(host.id, command.containers)
        return CollectResult(
            ingested=ingested, container_ingested=container_ingested
        )

    async def _collect_containers(
        self, host_id: int, items: list[ContainerCollectItem]
    ) -> int:
        if not items:
            return 0

        containers = await self._container_repository.upsert_all(
            [item.to_domain(host_id) for item in items]
        )
        container_ids = {container.docker_id: container.id for container in containers}
        metrics = [
            datapoint.to_domain(container_ids[item.docker_id])
            for item in items
            if item.docker_id in container_ids
            for datapoint in item.datapoints
        ]
        return await self._container_metric_repository.save_all(metrics)
