from abc import ABC, abstractmethod

from app.application.command.deployment import (
    ClaimResult,
    DeploymentClaimCommand,
    DeploymentCreateCommand,
    DeploymentReportCommand,
    DeploymentSearchQuery,
)
from app.domain.models import Deployment


class DeploymentUseCase(ABC):
    @abstractmethod
    async def get_deployment(self, deployment_id: int) -> Deployment: ...

    @abstractmethod
    async def get_deployments(
        self, query: DeploymentSearchQuery
    ) -> list[Deployment]: ...

    @abstractmethod
    async def create_deployment(
        self, command: DeploymentCreateCommand
    ) -> Deployment: ...

    @abstractmethod
    async def claim(self, command: DeploymentClaimCommand) -> ClaimResult | None: ...

    @abstractmethod
    async def report(self, command: DeploymentReportCommand) -> Deployment: ...
