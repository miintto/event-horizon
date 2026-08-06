from fastapi import APIRouter, Depends, Query, status

from app.adapters.inbound.api.dependencies import get_deployment_service
from app.adapters.inbound.api.schemas.deployment import (
    DeploymentCreateRequest,
    DeploymentResponse,
    DeploymentSearchQueryParam,
)
from app.application.ports.usecase import DeploymentUseCase

router = APIRouter(prefix="/deployments", tags=["deployment"])


@router.get(
    "",
    response_model=list[DeploymentResponse],
    response_model_exclude_none=True,
)
async def get_deployments(
    query: DeploymentSearchQueryParam = Query(),
    service: DeploymentUseCase = Depends(get_deployment_service),
):
    deployments = await service.get_deployments(query.to_query())
    return [DeploymentResponse.from_domain(d) for d in deployments]


@router.post(
    "",
    response_model=DeploymentResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_deployment(
    body: DeploymentCreateRequest,
    service: DeploymentUseCase = Depends(get_deployment_service),
):
    deployment = await service.create_deployment(body.to_command())
    return DeploymentResponse.from_domain(deployment)


@router.get(
    "/{deployment_id}",
    response_model=DeploymentResponse,
    response_model_exclude_none=True,
)
async def get_deployment(
    deployment_id: int,
    service: DeploymentUseCase = Depends(get_deployment_service),
):
    deployment = await service.get_deployment(deployment_id=deployment_id)
    return DeploymentResponse.from_domain(deployment)
