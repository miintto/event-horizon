from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.application.command.workload import (
    RevisionCreateCommand,
    RevisionDefinition,
    WorkloadCreateCommand,
)
from app.domain.models import (
    ContainerSpec,
    EnvVar,
    Healthcheck,
    LogConfig,
    Mount,
    Network,
    PortBinding,
    RestartPolicy,
    SecretRef,
    Workload,
    WorkloadRevision,
)


class EnvVarRequest(BaseModel):
    name: str = Field(min_length=1)
    value: str


class SecretRefRequest(BaseModel):
    name: str = Field(min_length=1)
    ref: str = Field(min_length=1)


class PortBindingRequest(BaseModel):
    protocol: str = "tcp"
    host_port: int | None = Field(default=None, ge=1, le=65535)
    container_port: int = Field(ge=1, le=65535)


class MountRequest(BaseModel):
    type: str
    source: str
    target: str
    read_only: bool = False


class RestartPolicyRequest(BaseModel):
    name: str
    max_retry: int = Field(default=0, ge=0)


class HealthcheckRequest(BaseModel):
    test: list[str] = Field(min_length=1)
    interval_secs: int | None = Field(default=None, gt=0)
    timeout_secs: int | None = Field(default=None, gt=0)
    retries: int | None = Field(default=None, ge=0)


class NetworkRequest(BaseModel):
    mode: str | None = None
    names: list[str] = Field(default_factory=list)


class LogConfigRequest(BaseModel):
    driver: str
    options: dict[str, str] = Field(default_factory=dict)


class BaseContainerSpec(BaseModel):
    command: list[str] | None = None
    entrypoint: list[str] | None = None
    env: list[EnvVarRequest] = Field(default_factory=list)
    secrets: list[SecretRefRequest] = Field(default_factory=list)
    ports: list[PortBindingRequest] = Field(default_factory=list)
    mounts: list[MountRequest] = Field(default_factory=list)
    restart_policy: RestartPolicyRequest | None = None
    healthcheck: HealthcheckRequest | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    network: NetworkRequest | None = None
    log: LogConfigRequest | None = None


class ContainerSpecRequest(BaseContainerSpec):
    @model_validator(mode="after")
    def validate_env_names(self) -> Self:
        names = [e.name for e in self.env] + [s.name for s in self.secrets]
        if len(names) != len(set(names)):
            raise ValueError("`env` and `secrets` must not share variable names")
        return self

    def to_domain(self) -> ContainerSpec:
        return ContainerSpec(
            command=self.command,
            entrypoint=self.entrypoint,
            env=[EnvVar(**e.model_dump()) for e in self.env],
            secrets=[SecretRef(**s.model_dump()) for s in self.secrets],
            ports=[PortBinding(**p.model_dump()) for p in self.ports],
            mounts=[Mount(**m.model_dump()) for m in self.mounts],
            restart_policy=(
                RestartPolicy(**self.restart_policy.model_dump())
                if self.restart_policy
                else None
            ),
            healthcheck=(
                Healthcheck(**self.healthcheck.model_dump())
                if self.healthcheck
                else None
            ),
            labels=self.labels,
            network=Network(**self.network.model_dump()) if self.network else None,
            log=LogConfig(**self.log.model_dump()) if self.log else None,
        )


class RevisionDefinitionRequest(BaseModel):
    image: str = Field(min_length=1, max_length=255)
    cpu_limit: Decimal | None = Field(default=None, gt=0)
    memory_limit: int | None = Field(default=None, ge=6 * 1024 * 1024)
    spec: ContainerSpecRequest = Field(default_factory=ContainerSpecRequest)

    def to_definition(self) -> RevisionDefinition:
        return RevisionDefinition(
            image=self.image,
            cpu_limit=self.cpu_limit,
            memory_limit=self.memory_limit,
            spec=self.spec.to_domain(),
        )


class WorkloadCreateRequest(RevisionDefinitionRequest):
    name: str = Field(min_length=1, max_length=512)

    def to_command(self) -> WorkloadCreateCommand:
        return WorkloadCreateCommand(name=self.name, definition=self.to_definition())


class RevisionCreateRequest(RevisionDefinitionRequest):
    def to_command(self, workload_id: int) -> RevisionCreateCommand:
        return RevisionCreateCommand(
            workload_id=workload_id, definition=self.to_definition()
        )


class WorkloadResponse(BaseModel):
    id: int
    name: str
    current_revision_id: int | None = None
    container_count: int | None = None
    running_count: int | None = None
    host_count: int | None = None
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, workload: Workload) -> WorkloadResponse:
        detail = workload.detail
        return cls(
            id=workload.pk,
            name=workload.name,
            current_revision_id=workload.current_revision_id,
            container_count=detail.container_count if detail else None,
            running_count=detail.running_count if detail else None,
            host_count=detail.host_count if detail else None,
            created_at=workload.created_at,
        )


class ContainerSpecResponse(BaseContainerSpec):
    pass


class WorkloadRevisionResponse(BaseModel):
    id: int
    workload_id: int
    revision: int
    image: str
    cpu_limit: Decimal | None = None
    memory_limit: int | None = None
    spec: ContainerSpecResponse
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, revision: WorkloadRevision) -> WorkloadRevisionResponse:
        return cls(
            id=revision.pk,
            workload_id=revision.workload_id,
            revision=revision.revision,
            image=revision.image,
            cpu_limit=revision.cpu_limit,
            memory_limit=revision.memory_limit,
            spec=ContainerSpecResponse.model_validate(
                revision.spec, from_attributes=True
            ),
            created_at=revision.created_at,
        )
