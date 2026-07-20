from fastapi import APIRouter, Depends, Query, status

from app.adapters.inbound.api.dependencies import get_host_metric_service
from app.adapters.inbound.api.schemas.host_metric import (
    HostMetricBatchRequest,
    HostMetricCollectResponse,
    HostMetricQueryParam,
    HostMetricSeriesResponse,
)
from app.application.ports.usecase.host_metric_use_case import HostMetricUseCase

router = APIRouter(prefix="/hosts", tags=["host-metric"])


@router.post(
    "/metrics",
    response_model=HostMetricCollectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def collect_metrics(
    body: HostMetricBatchRequest,
    service: HostMetricUseCase = Depends(get_host_metric_service),
):
    result = await service.collect(body.to_command())
    return HostMetricCollectResponse.from_result(result)


@router.get(
    "/metrics",
    response_model=list[HostMetricSeriesResponse],
    response_model_exclude_none=True,
)
async def query_metrics(
    query: HostMetricQueryParam = Query(),
    service: HostMetricUseCase = Depends(get_host_metric_service),
):
    series = await service.query(query.to_query())
    return [HostMetricSeriesResponse.from_domain(s) for s in series]
