from datetime import datetime

from fastapi import Query
from pydantic import BaseModel

from app.application.command.deployment import (
    DeploymentCreateCommand,
    DeploymentSearchQuery,
)
from app.domain.models import Deployment, DeploymentStatus


class DeploymentSearchQueryParam(BaseModel):
    host_id: int | None = Query(default=None)
    workload_id: int | None = Query(default=None)

    def to_query(self) -> DeploymentSearchQuery:
        return DeploymentSearchQuery(host_id=self.host_id, workload_id=self.workload_id)


class DeploymentCreateRequest(BaseModel):
    host_id: int
    workload_id: int
    revision_id: int | None = None

    def to_command(self) -> DeploymentCreateCommand:
        return DeploymentCreateCommand(
            host_id=self.host_id,
            workload_id=self.workload_id,
            revision_id=self.revision_id,
        )


class DeploymentResponse(BaseModel):
    id: int
    host_id: int
    workload_id: int
    revision_id: int
    container_id: int | None = None
    status: DeploymentStatus
    error_message: str | None = None
    claimed_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, deployment: Deployment) -> DeploymentResponse:
        return cls.model_construct(
            id=deployment.pk,
            host_id=deployment.host_id,
            workload_id=deployment.workload_id,
            revision_id=deployment.revision_id,
            container_id=deployment.container_id,
            status=deployment.status,
            error_message=deployment.error_message,
            claimed_at=deployment.claimed_at,
            finished_at=deployment.finished_at,
            created_at=deployment.created_at,
        )
