from fastapi import APIRouter, Depends, Query, status

from app.adapters.inbound.api.dependencies import (
    get_container_metric_service,
    get_metric_service,
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
from app.application.ports.usecase.container_metric_use_case import (
    ContainerMetricUseCase,
)
from app.application.ports.usecase.metric_use_case import MetricUseCase

router = APIRouter(prefix="/metrics", tags=["metric"])


@router.get(
    "/hosts",
    response_model=list[HostMetricSeriesResponse],
    response_model_exclude_none=True,
)
async def query_host_metrics(
    query: HostMetricQueryParam = Query(),
    service: MetricUseCase = Depends(get_metric_service),
):
    series = await service.query(query.to_query())
    return [HostMetricSeriesResponse.from_domain(s) for s in series]


@router.post(
    "/hosts",
    response_model=HostMetricCollectResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def collect_host_metrics(
    body: HostMetricBatchRequest,
    service: MetricUseCase = Depends(get_metric_service),
):
    result = await service.collect(body.to_command())
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
