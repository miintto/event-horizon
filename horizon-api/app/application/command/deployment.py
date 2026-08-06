import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.models import ContainerSpec, DeploymentStatus


@dataclass
class DeploymentCreateCommand:
    host_id: int
    workload_id: int
    revision_id: int | None = None


@dataclass
class DeploymentSearchQuery:
    host_id: int | None = None
    workload_id: int | None = None


@dataclass
class DeploymentClaimCommand:
    agent_uuid: uuid.UUID


@dataclass
class DeploymentReportCommand:
    agent_uuid: uuid.UUID
    deployment_id: int
    status: DeploymentStatus
    docker_id: str | None = None
    removed_docker_ids: list[str] = field(default_factory=list)
    error_message: str | None = None


@dataclass
class ClaimResult:
    deployment_id: int
    container_name: str
    image: str
    spec: ContainerSpec
    cpu_limit: Decimal | None = None
    memory_limit: int | None = None
    labels: dict[str, str] = field(default_factory=dict)
    previous_docker_ids: list[str] = field(default_factory=list)
