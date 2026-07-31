from fastapi import APIRouter, Depends

from app.adapters.inbound.api.dependencies import get_workload_service
from app.adapters.inbound.api.schemas.workload import WorkloadResponse
from app.application.ports.usecase.workload_use_case import WorkloadUseCase

router = APIRouter(prefix="/workloads", tags=["workload"])


@router.get(
    "",
    response_model=list[WorkloadResponse],
    response_model_exclude_none=True,
)
async def list_workloads(
    host_id: int | None = None,
    service: WorkloadUseCase = Depends(get_workload_service),
):
    results = await service.get_workloads(host_id=host_id)
    return [WorkloadResponse.from_result(r) for r in results]


@router.get(
    "/{workload_id}",
    response_model=WorkloadResponse,
    response_model_exclude_none=True,
)
async def get_workload(
    workload_id: int,
    service: WorkloadUseCase = Depends(get_workload_service),
):
    workload = await service.get_workload(workload_id=workload_id)
    return WorkloadResponse.from_domain(workload)
