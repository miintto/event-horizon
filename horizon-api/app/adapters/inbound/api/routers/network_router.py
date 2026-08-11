from fastapi import APIRouter, Depends, Query, status

from app.adapters.inbound.api.auth import verify_admin
from app.adapters.inbound.api.dependencies import get_network_service
from app.adapters.inbound.api.schemas.network import (
    NetworkAttachRequest,
    NetworkCreateRequest,
    NetworkHostStateListResponse,
    NetworkListResponse,
    NetworkResponse,
    NetworkSearchQueryParam,
)
from app.adapters.inbound.api.schemas.workload import WorkloadResponse
from app.application.ports.usecase import NetworkUseCase

router = APIRouter(prefix="/networks", tags=["network"])


@router.get(
    "",
    response_model=NetworkListResponse,
    response_model_exclude_none=True,
)
async def get_networks(
    query: NetworkSearchQueryParam = Query(),
    service: NetworkUseCase = Depends(get_network_service),
):
    networks = await service.get_networks(query.to_query())
    return NetworkListResponse.from_result(networks)


@router.post(
    "",
    response_model=NetworkResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin)],
)
async def create_network(
    body: NetworkCreateRequest,
    service: NetworkUseCase = Depends(get_network_service),
):
    network = await service.create_network(body.to_command())
    return NetworkResponse.from_domain(network)


@router.delete(
    "/{network_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin)],
)
async def delete_network(
    network_id: int,
    service: NetworkUseCase = Depends(get_network_service),
):
    await service.delete_network(network_id=network_id)


@router.get(
    "/{network_id}/workloads",
    response_model=list[WorkloadResponse],
    response_model_exclude_none=True,
)
async def get_network_workloads(
    network_id: int,
    service: NetworkUseCase = Depends(get_network_service),
):
    workloads = await service.get_workloads(network_id=network_id)
    return [WorkloadResponse.from_domain(w) for w in workloads]


@router.post(
    "/{network_id}/workloads",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin)],
)
async def attach_workload(
    network_id: int,
    body: NetworkAttachRequest,
    service: NetworkUseCase = Depends(get_network_service),
):
    await service.attach_workload(body.to_command(network_id))


@router.delete(
    "/{network_id}/workloads/{workload_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin)],
)
async def detach_workload(
    network_id: int,
    workload_id: int,
    service: NetworkUseCase = Depends(get_network_service),
):
    await service.detach_workload(network_id=network_id, workload_id=workload_id)


@router.get(
    "/{network_id}/state",
    response_model=NetworkHostStateListResponse,
    response_model_exclude_none=True,
)
async def get_network_state(
    network_id: int,
    service: NetworkUseCase = Depends(get_network_service),
):
    states = await service.get_host_states(network_id=network_id)
    return NetworkHostStateListResponse.from_result(states)
