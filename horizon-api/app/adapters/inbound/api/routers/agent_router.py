from fastapi import APIRouter, BackgroundTasks, Depends, Response, status

from app.adapters.inbound.api.auth import verify_agent
from app.adapters.inbound.api.dependencies import (
    get_collect_service,
    get_deployment_service,
)
from app.adapters.inbound.api.schemas.agent import (
    DeploymentClaimRequest,
    DeploymentClaimResponse,
    DeploymentResultRequest,
)
from app.adapters.inbound.api.schemas.deployment import DeploymentResponse
from app.adapters.inbound.api.schemas.metric import (
    HostMetricBatchRequest,
    HostMetricCollectResponse,
)
from app.application.ports.usecase import CollectUseCase, DeploymentUseCase

router = APIRouter(
    prefix="/agents", tags=["agent"], dependencies=[Depends(verify_agent)]
)


@router.post(
    "/metrics",
    response_model=HostMetricCollectResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
)
async def collect_metrics(
    body: HostMetricBatchRequest,
    background_tasks: BackgroundTasks,
    service: CollectUseCase = Depends(get_collect_service),
):
    result = await service.collect(body.to_command())
    background_tasks.add_task(service.post_collect, result.host_id)
    return HostMetricCollectResponse.from_result(result)


@router.post(
    "/deployments/claim",
    response_model=DeploymentClaimResponse,
    response_model_exclude_none=True,
)
async def claim_deployment(
    body: DeploymentClaimRequest,
    service: DeploymentUseCase = Depends(get_deployment_service),
):
    result = await service.claim(body.to_command())
    if not result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return DeploymentClaimResponse.from_result(result)


@router.post(
    "/deployments/{deployment_id}/result",
    response_model=DeploymentResponse,
    response_model_exclude_none=True,
)
async def report_deployment(
    deployment_id: int,
    body: DeploymentResultRequest,
    service: DeploymentUseCase = Depends(get_deployment_service),
):
    deployment = await service.report(body.to_command(deployment_id))
    return DeploymentResponse.from_domain(deployment)
