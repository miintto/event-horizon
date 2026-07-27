from app.adapters.outbound.persistence.container_metric_persistence_adapter import (
    ContainerMetricPersistenceAdapter,
)
from app.adapters.outbound.persistence.container_persistence_adapter import (
    ContainerPersistenceAdapter,
)
from app.adapters.outbound.persistence.host_metric_persistence_adapter import (
    HostMetricPersistenceAdapter,
)
from app.adapters.outbound.persistence.host_persistence_adapter import (
    HostPersistenceAdapter,
)
from app.application.ports.usecase.host_metric_use_case import (
    HostMetricUseCase,
)
from app.application.ports.usecase.host_use_case import HostUseCase
from app.application.services.host.host_service import HostService
from app.application.services.host_metric.host_metric_service import (
    HostMetricService,
)

# Repository
_host_repository = HostPersistenceAdapter()
_host_metric_repository = HostMetricPersistenceAdapter()
_container_repository = ContainerPersistenceAdapter()
_container_metric_repository = ContainerMetricPersistenceAdapter()

# Service
_host_service = HostService(
    host_repository=_host_repository,
)
_host_metric_service = HostMetricService(
    host_metric_repository=_host_metric_repository,
    host_repository=_host_repository,
    container_repository=_container_repository,
    container_metric_repository=_container_metric_repository,
)


async def get_host_service() -> HostUseCase:
    return _host_service


async def get_host_metric_service() -> HostMetricUseCase:
    return _host_metric_service
