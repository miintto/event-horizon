import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.adapters.inbound.api.schemas.workload import ContainerSpecResponse
from app.application.command.deployment import (
    ClaimResult,
    DeploymentClaimCommand,
    DeploymentReportCommand,
)
from app.domain.models import DeploymentStatus


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


class DeploymentClaimResponse(BaseModel):
    deployment_id: int
    container_name: str
    image: str
    spec: ContainerSpecResponse
    cpu_limit: Decimal | None = None
    memory_limit: int | None = None
    labels: dict[str, str] = Field(default_factory=dict)
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
            previous_docker_ids=result.previous_docker_ids,
        )
