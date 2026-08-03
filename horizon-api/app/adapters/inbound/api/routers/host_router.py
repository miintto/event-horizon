from fastapi import APIRouter, Depends

from app.adapters.inbound.api.dependencies import get_host_service
from app.adapters.inbound.api.schemas.host import HostResponse
from app.application.ports.usecase import HostUseCase

router = APIRouter(prefix="/hosts", tags=["host"])


@router.get(
    "",
    response_model=list[HostResponse],
    response_model_exclude_none=True,
)
async def get_hosts(
    service: HostUseCase = Depends(get_host_service),
):
    hosts = await service.get_hosts()
    return [HostResponse.from_domain(host) for host in hosts]


@router.get(
    "/{host_id}",
    response_model=HostResponse,
    response_model_exclude_none=True,
)
async def get_host(
    host_id: int,
    service: HostUseCase = Depends(get_host_service),
):
    host = await service.get_host(host_id=host_id)
    return HostResponse.from_domain(host)
