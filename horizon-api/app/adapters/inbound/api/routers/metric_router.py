from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from app.adapters.inbound.api.auth import verify_agent
from app.adapters.inbound.api.dependencies import (
    get_collect_service,
    get_container_metric_service,
    get_host_metric_service,
)
from app.adapters.inbound.api.schemas.container_metric import (
    ContainerMetricQueryParam,
    ContainerMetricSeriesResponse,
)
from app.adapters.inbound.api.schemas.host_metric import (
    HostMetricBatchRequest,
    HostMetricCollectResponse,
    HostMetricQueryParam,
    HostMetricSeriesResponse,
)
from app.application.ports.usecase.collect_use_case import CollectUseCase
from app.application.ports.usecase.container_metric_use_case import (
    ContainerMetricUseCase,
)
from app.application.ports.usecase.host_metric_use_case import HostMetricUseCase

router = APIRouter(prefix="/metrics", tags=["metric"])


@router.get(
    "/hosts",
    response_model=list[HostMetricSeriesResponse],
    response_model_exclude_none=True,
)
async def query_host_metrics(
    query: HostMetricQueryParam = Query(),
    service: HostMetricUseCase = Depends(get_host_metric_service),
):
    series = await service.query(query.to_query())
    return [HostMetricSeriesResponse.from_domain(s) for s in series]


@router.post(
    "/hosts",
    response_model=HostMetricCollectResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_agent)],
)
async def collect_host_metrics(
    body: HostMetricBatchRequest,
    background_tasks: BackgroundTasks,
    service: CollectUseCase = Depends(get_collect_service),
):
    result = await service.collect(body.to_command())
    background_tasks.add_task(service.post_collect, result.host_id)
    return HostMetricCollectResponse.from_result(result)


@router.get(
    "/containers",
    response_model=list[ContainerMetricSeriesResponse],
    response_model_exclude_none=True,
)
async def query_container_metrics(
    query: ContainerMetricQueryParam = Query(),
    service: ContainerMetricUseCase = Depends(get_container_metric_service),
):
    series = await service.query(query.to_query())
    return [ContainerMetricSeriesResponse.from_domain(s) for s in series]
