from fastapi import APIRouter, Depends, status

from app.adapters.inbound.api.dependencies import get_workload_service
from app.adapters.inbound.api.schemas.workload import (
    RevisionCreateRequest,
    WorkloadCreateRequest,
    WorkloadResponse,
    WorkloadRevisionResponse,
)
from app.application.ports.usecase import WorkloadUseCase

router = APIRouter(prefix="/workloads", tags=["workload"])


@router.get(
    "",
    response_model=list[WorkloadResponse],
    response_model_exclude_none=True,
)
async def get_workloads(
    host_id: int | None = None,
    service: WorkloadUseCase = Depends(get_workload_service),
):
    workloads = await service.get_workloads(host_id=host_id)
    return [WorkloadResponse.from_domain(w) for w in workloads]


@router.post(
    "",
    response_model=WorkloadResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_workload(
    body: WorkloadCreateRequest,
    service: WorkloadUseCase = Depends(get_workload_service),
):
    workload = await service.create_workload(body.to_command())
    return WorkloadResponse.from_domain(workload)


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


@router.get(
    "/{workload_id}/revisions",
    response_model=list[WorkloadRevisionResponse],
    response_model_exclude_none=True,
)
async def list_revisions(
    workload_id: int,
    service: WorkloadUseCase = Depends(get_workload_service),
):
    revisions = await service.get_revisions(workload_id=workload_id)
    return [WorkloadRevisionResponse.from_domain(r) for r in revisions]


@router.post(
    "/{workload_id}/revisions",
    response_model=WorkloadRevisionResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_revision(
    workload_id: int,
    body: RevisionCreateRequest,
    service: WorkloadUseCase = Depends(get_workload_service),
):
    revision = await service.add_revision(body.to_command(workload_id))
    return WorkloadRevisionResponse.from_domain(revision)


@router.get(
    "/{workload_id}/revisions/{revision}",
    response_model=WorkloadRevisionResponse,
    response_model_exclude_none=True,
)
async def get_revision(
    workload_id: int,
    revision: int,
    service: WorkloadUseCase = Depends(get_workload_service),
):
    result = await service.get_revision(workload_id=workload_id, revision=revision)
    return WorkloadRevisionResponse.from_domain(result)
