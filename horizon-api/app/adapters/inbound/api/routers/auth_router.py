from fastapi import APIRouter, Depends, status

from app.adapters.inbound.api.auth import verify_admin
from app.adapters.inbound.api.dependencies import get_auth_service
from app.adapters.inbound.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.application.ports.usecase import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin)],
)
async def register(
    body: RegisterRequest,
    service: AuthUseCase = Depends(get_auth_service),
):
    result = await service.register(body.to_command())
    return TokenResponse.from_result(result)


@router.post(
    "/login",
    response_model=TokenResponse,
    response_model_exclude_none=True,
)
async def login(
    body: LoginRequest,
    service: AuthUseCase = Depends(get_auth_service),
):
    result = await service.login(body.to_command())
    return TokenResponse.from_result(result)
