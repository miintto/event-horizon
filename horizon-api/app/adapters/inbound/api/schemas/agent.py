import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.adapters.inbound.api.schemas.workload import ContainerSpecResponse
from app.application.command.deployment import (
    ClaimResult,
    DeploymentClaimCommand,
    DeploymentReportCommand,
)
from app.application.command.network_sync import (
    NetworkDesiredState,
    NetworkSyncCommand,
    NetworkSyncResult,
)
from app.domain.models import DeploymentStatus, NetworkSyncStatus


class DeploymentClaimRequest(BaseModel):
    agent_uuid: uuid.UUID

    def to_command(self) -> DeploymentClaimCommand:
        return DeploymentClaimCommand(agent_uuid=self.agent_uuid)


class DeploymentResultRequest(BaseModel):
    agent_uuid: uuid.UUID
    status: DeploymentStatus
    docker_id: str | None = None
    removed_docker_ids: list[str] = Field(default_factory=list)
    error_message: str | None = None

    @field_validator("error_message")
    @classmethod
    def truncate_error_message(cls, value: str | None) -> str | None:
        return value[:500] if value else value

    def to_command(self, deployment_id: int) -> DeploymentReportCommand:
        return DeploymentReportCommand(
            agent_uuid=self.agent_uuid,
            deployment_id=deployment_id,
            status=self.status,
            docker_id=self.docker_id,
            removed_docker_ids=self.removed_docker_ids,
            error_message=self.error_message,
        )


class NetworkSyncResultRequest(BaseModel):
    network_name: str
    status: NetworkSyncStatus
    error_message: str | None = None

    @field_validator("error_message")
    @classmethod
    def truncate_error_message(cls, value: str | None) -> str | None:
        return value[:1024] if value else value

    def to_result(self) -> NetworkSyncResult:
        return NetworkSyncResult(
            network_name=self.network_name,
            status=self.status,
            error_message=self.error_message,
        )


class NetworkSyncRequest(BaseModel):
    agent_uuid: uuid.UUID
    results: list[NetworkSyncResultRequest] = Field(default_factory=list)

    def to_command(self) -> NetworkSyncCommand:
        return NetworkSyncCommand(
            agent_uuid=self.agent_uuid,
            results=[result.to_result() for result in self.results],
        )


class NetworkAttachmentResponse(BaseModel):
    name: str
    driver: str
    options: dict[str, str] = Field(default_factory=dict)
    aliases: list[str] = Field(default_factory=list)


class DeploymentClaimResponse(BaseModel):
    deployment_id: int
    container_name: str
    image: str
    spec: ContainerSpecResponse
    cpu_limit: Decimal | None = None
    memory_limit: int | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    networks: list[NetworkAttachmentResponse] = Field(default_factory=list)
    previous_docker_ids: list[str] = Field(default_factory=list)

    @classmethod
    def from_result(cls, result: ClaimResult) -> DeploymentClaimResponse:
        return cls.model_construct(
            deployment_id=result.deployment_id,
            container_name=result.container_name,
            image=result.image,
            spec=ContainerSpecResponse.model_validate(
                result.spec, from_attributes=True
            ),
            cpu_limit=result.cpu_limit,
            memory_limit=result.memory_limit,
            labels=result.labels,
            networks=[
                NetworkAttachmentResponse.model_construct(
                    name=n.name,
                    driver=n.driver,
                    options=n.options,
                    aliases=n.aliases,
                )
                for n in result.networks
            ],
            previous_docker_ids=result.previous_docker_ids,
        )


class NetworkMemberResponse(BaseModel):
    workload_id: int
    alias: str


class NetworkDesiredResponse(BaseModel):
    name: str
    driver: str
    options: dict[str, str] = Field(default_factory=dict)
    members: list[NetworkMemberResponse] = Field(default_factory=list)


class NetworkSyncResponse(BaseModel):
    networks: list[NetworkDesiredResponse] = Field(default_factory=list)

    @classmethod
    def from_result(cls, state: NetworkDesiredState) -> NetworkSyncResponse:
        return cls.model_construct(
            networks=[
                NetworkDesiredResponse.model_construct(
                    name=network.name,
                    driver=network.driver,
                    options=network.options,
                    members=[
                        NetworkMemberResponse.model_construct(
                            workload_id=member.workload_id,
                            alias=member.alias,
                        )
                        for member in network.members
                    ],
                )
                for network in state.networks
            ]
        )
