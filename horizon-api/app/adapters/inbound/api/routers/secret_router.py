from fastapi import APIRouter, Depends, Query, status

from app.adapters.inbound.api.auth import verify_admin
from app.adapters.inbound.api.dependencies import get_secret_service
from app.adapters.inbound.api.schemas.secret import (
    SecretCreateRequest,
    SecretListResponse,
    SecretResponse,
    SecretSearchQueryParam,
    SecretUpdateRequest,
)
from app.application.ports.usecase import SecretUseCase

router = APIRouter(
    prefix="/secrets", tags=["secret"], dependencies=[Depends(verify_admin)]
)


@router.get(
    "",
    response_model=SecretListResponse,
    response_model_exclude_none=True,
)
async def get_secrets(
    query: SecretSearchQueryParam = Query(),
    service: SecretUseCase = Depends(get_secret_service),
):
    result = await service.get_secrets(query.to_query())
    return SecretListResponse.from_result(result)


@router.post(
    "",
    response_model=SecretResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_secret(
    body: SecretCreateRequest,
    service: SecretUseCase = Depends(get_secret_service),
):
    secret = await service.create_secret(body.to_command())
    return SecretResponse.from_domain(secret)


@router.put(
    "/{secret_id}",
    response_model=SecretResponse,
    response_model_exclude_none=True,
)
async def update_secret(
    secret_id: int,
    body: SecretUpdateRequest,
    service: SecretUseCase = Depends(get_secret_service),
):
    secret = await service.update_secret(body.to_command(secret_id))
    return SecretResponse.from_domain(secret)


@router.delete(
    "/{secret_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_secret(
    secret_id: int,
    service: SecretUseCase = Depends(get_secret_service),
):
    await service.delete_secret(secret_id=secret_id)
