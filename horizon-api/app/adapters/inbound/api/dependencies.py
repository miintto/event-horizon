from app.adapters.outbound.persistence.container_metric_persistence_adapter import (
    ContainerMetricPersistenceAdapter,
)
from app.adapters.outbound.persistence.container_persistence_adapter import (
    ContainerPersistenceAdapter,
)
from app.adapters.outbound.persistence.deployment_persistence_adapter import (
    DeploymentPersistenceAdapter,
)
from app.adapters.outbound.persistence.host_metric_persistence_adapter import (
    HostMetricPersistenceAdapter,
)
from app.adapters.outbound.persistence.host_persistence_adapter import (
    HostPersistenceAdapter,
)
from app.adapters.outbound.persistence.secret_persistence_adapter import (
    SecretPersistenceAdapter,
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
from app.adapters.outbound.security.fernet_cipher import FernetCipher
from app.adapters.outbound.security.jwt_provider import JwtProvider
from app.application.ports.security import TokenProvider
from app.application.ports.usecase import (
    AuthUseCase,
    CollectUseCase,
    ContainerMetricUseCase,
    ContainerUseCase,
    DeploymentUseCase,
    HostMetricUseCase,
    HostUseCase,
    SecretUseCase,
    UserUseCase,
    WorkloadUseCase,
)
from app.application.services.auth.auth_service import AuthService
from app.application.services.collect.collect_service import CollectService
from app.application.services.container.container_service import ContainerService
from app.application.services.deployment.deployment_service import DeploymentService
from app.application.services.host.host_service import HostService
from app.application.services.metric.container_metric_service import (
    ContainerMetricService,
)
from app.application.services.metric.host_metric_service import HostMetricService
from app.application.services.secret.secret_service import SecretService
from app.application.services.user.user_service import UserService
from app.application.services.workload.workload_service import WorkloadService
from app.infrastructure.config import settings

# Repository
_container_metric_repository = ContainerMetricPersistenceAdapter()
_container_repository = ContainerPersistenceAdapter()
_deployment_repository = DeploymentPersistenceAdapter()
_host_metric_repository = HostMetricPersistenceAdapter()
_host_repository = HostPersistenceAdapter()
_secret_repository = SecretPersistenceAdapter()
_user_repository = UserPersistenceAdapter()
_workload_repository = WorkloadPersistenceAdapter()
_workload_revision_repository = WorkloadRevisionPersistenceAdapter()

# Security
_password_hasher = BcryptPasswordHasher()
_secret_cipher = FernetCipher(
    key=settings.secret_encryption_key,
    previous_key=settings.secret_encryption_key_previous,
)
_token_provider = JwtProvider(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm,
    expire_secs=settings.jwt_expire_secs,
)

# Service
_auth_service = AuthService(
    user_repository=_user_repository,
    password_hasher=_password_hasher,
    token_provider=_token_provider,
    expire_secs=settings.jwt_expire_secs,
)
_collect_service = CollectService(
    host_metric_repository=_host_metric_repository,
    host_repository=_host_repository,
    container_repository=_container_repository,
    container_metric_repository=_container_metric_repository,
    stale_after_secs=settings.container_stale_after_secs,
)
_container_metric_service = ContainerMetricService(
    container_metric_repository=_container_metric_repository,
)
_container_service = ContainerService(
    container_repository=_container_repository,
)
_deployment_service = DeploymentService(
    container_repository=_container_repository,
    deployment_repository=_deployment_repository,
    host_repository=_host_repository,
    secret_repository=_secret_repository,
    workload_repository=_workload_repository,
    workload_revision_repository=_workload_revision_repository,
    secret_cipher=_secret_cipher,
    timeout_secs=settings.deployment_timeout_secs,
)
_host_metric_service = HostMetricService(
    host_metric_repository=_host_metric_repository,
)
_host_service = HostService(
    host_repository=_host_repository,
)
_secret_service = SecretService(
    secret_repository=_secret_repository,
    secret_cipher=_secret_cipher,
)
_user_service = UserService(
    user_repository=_user_repository,
)
_workload_service = WorkloadService(
    workload_repository=_workload_repository,
    workload_revision_repository=_workload_revision_repository,
)


async def get_token_provider() -> TokenProvider:
    return _token_provider


async def get_auth_service() -> AuthUseCase:
    return _auth_service


async def get_collect_service() -> CollectUseCase:
    return _collect_service


async def get_container_metric_service() -> ContainerMetricUseCase:
    return _container_metric_service


async def get_container_service() -> ContainerUseCase:
    return _container_service


async def get_deployment_service() -> DeploymentUseCase:
    return _deployment_service


async def get_host_metric_service() -> HostMetricUseCase:
    return _host_metric_service


async def get_host_service() -> HostUseCase:
    return _host_service


async def get_secret_service() -> SecretUseCase:
    return _secret_service


async def get_user_service() -> UserUseCase:
    return _user_service


async def get_workload_service() -> WorkloadUseCase:
    return _workload_service
