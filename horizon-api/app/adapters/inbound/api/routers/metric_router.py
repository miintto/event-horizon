from fastapi import APIRouter, Depends, Query

from app.adapters.inbound.api.auth import verify_user
from app.adapters.inbound.api.dependencies import (
    get_container_metric_service,
    get_host_metric_service,
)
from app.adapters.inbound.api.schemas.metric import (
    ContainerMetricQueryParam,
    ContainerMetricSeriesResponse,
    HostMetricQueryParam,
    HostMetricSeriesResponse,
)
from app.application.ports.usecase import ContainerMetricUseCase, HostMetricUseCase

router = APIRouter(prefix="/metrics", tags=["metric"])


@router.get(
    "/hosts",
    response_model=list[HostMetricSeriesResponse],
    response_model_exclude_none=True,
    dependencies=[Depends(verify_user)],
)
async def query_host_metrics(
    query: HostMetricQueryParam = Query(),
    service: HostMetricUseCase = Depends(get_host_metric_service),
):
    series = await service.query(query.to_query())
    return [HostMetricSeriesResponse.from_domain(s) for s in series]


@router.get(
    "/containers",
    response_model=list[ContainerMetricSeriesResponse],
    response_model_exclude_none=True,
    dependencies=[Depends(verify_user)],
)
async def query_container_metrics(
    query: ContainerMetricQueryParam = Query(),
    service: ContainerMetricUseCase = Depends(get_container_metric_service),
):
    series = await service.query(query.to_query())
    return [ContainerMetricSeriesResponse.from_domain(s) for s in series]
