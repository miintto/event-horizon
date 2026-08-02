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
from app.adapters.outbound.persistence.user_persistence_adapter import (
    UserPersistenceAdapter,
)
from app.adapters.outbound.persistence.workload_persistence_adapter import (
    WorkloadPersistenceAdapter,
)
from app.adapters.outbound.persistence.workload_revision_persistence_adapter import (
    WorkloadRevisionPersistenceAdapter,
)
from app.adapters.outbound.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.adapters.outbound.security.jwt_token_issuer import JwtTokenIssuer
from app.application.ports.security.token_issuer import TokenIssuer
from app.application.ports.usecase.auth_use_case import AuthUseCase
from app.application.ports.usecase.collect_use_case import CollectUseCase
from app.application.ports.usecase.container_metric_use_case import (
    ContainerMetricUseCase,
)
from app.application.ports.usecase.container_use_case import ContainerUseCase
from app.application.ports.usecase.host_metric_use_case import HostMetricUseCase
from app.application.ports.usecase.host_use_case import HostUseCase
from app.application.ports.usecase.workload_use_case import WorkloadUseCase
from app.application.services.auth.auth_service import AuthService
from app.application.services.collect.collect_service import CollectService
from app.application.services.container.container_service import ContainerService
from app.application.services.container_metric.container_metric_service import (
    ContainerMetricService,
)
from app.application.services.host.host_service import HostService
from app.application.services.host_metric.host_metric_service import HostMetricService
from app.application.services.workload.workload_service import WorkloadService
from app.infrastructure.config import settings

# Repository
_user_repository = UserPersistenceAdapter()
_host_repository = HostPersistenceAdapter()
_host_metric_repository = HostMetricPersistenceAdapter()
_container_repository = ContainerPersistenceAdapter()
_workload_repository = WorkloadPersistenceAdapter()
_workload_revision_repository = WorkloadRevisionPersistenceAdapter()
_container_metric_repository = ContainerMetricPersistenceAdapter()

# Security
_password_hasher = BcryptPasswordHasher()
_token_issuer = JwtTokenIssuer(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm,
    expire_secs=settings.jwt_expire_secs,
)

# Service
_auth_service = AuthService(
    user_repository=_user_repository,
    password_hasher=_password_hasher,
    token_issuer=_token_issuer,
    expire_secs=settings.jwt_expire_secs,
)
_host_service = HostService(
    host_repository=_host_repository,
)
_collect_service = CollectService(
    host_metric_repository=_host_metric_repository,
    host_repository=_host_repository,
    container_repository=_container_repository,
    container_metric_repository=_container_metric_repository,
    stale_after_secs=settings.container_stale_after_secs,
)
_host_metric_service = HostMetricService(
    host_metric_repository=_host_metric_repository,
)
_container_service = ContainerService(
    container_repository=_container_repository,
)
_workload_service = WorkloadService(
    workload_repository=_workload_repository,
    workload_revision_repository=_workload_revision_repository,
)
_container_metric_service = ContainerMetricService(
    container_metric_repository=_container_metric_repository,
)


async def get_token_issuer() -> TokenIssuer:
    return _token_issuer


async def get_auth_service() -> AuthUseCase:
    return _auth_service


async def get_host_service() -> HostUseCase:
    return _host_service


async def get_container_service() -> ContainerUseCase:
    return _container_service


async def get_workload_service() -> WorkloadUseCase:
    return _workload_service


async def get_collect_service() -> CollectUseCase:
    return _collect_service


async def get_host_metric_service() -> HostMetricUseCase:
    return _host_metric_service


async def get_container_metric_service() -> ContainerMetricUseCase:
    return _container_metric_service
