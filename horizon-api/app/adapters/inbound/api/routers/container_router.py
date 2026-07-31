from fastapi import APIRouter, Depends

from app.adapters.inbound.api.dependencies import get_container_service
from app.adapters.inbound.api.schemas.container import ContainerResponse
from app.application.ports.usecase.container_use_case import ContainerUseCase

router = APIRouter(prefix="/containers", tags=["container"])


@router.get(
    "",
    response_model=list[ContainerResponse],
    response_model_exclude_none=True,
)
async def list_containers(
    host_id: int | None = None,
    workload_id: int | None = None,
    service: ContainerUseCase = Depends(get_container_service),
):
    containers = await service.get_containers(host_id=host_id, workload_id=workload_id)
    return [ContainerResponse.from_domain(c) for c in containers]


@router.get(
    "/{container_id}",
    response_model=ContainerResponse,
    response_model_exclude_none=True,
)
async def get_container(
    container_id: int,
    service: ContainerUseCase = Depends(get_container_service),
):
    container = await service.get_container(container_id=container_id)
    return ContainerResponse.from_domain(container)
