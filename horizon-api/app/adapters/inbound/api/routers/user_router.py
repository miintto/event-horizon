from fastapi import APIRouter, Depends, Query

from app.adapters.inbound.api.auth import verify_admin
from app.adapters.inbound.api.dependencies import get_user_service
from app.adapters.inbound.api.schemas.user import (
    UserListResponse,
    UserResponse,
    UserSearchQueryParam,
)
from app.application.ports.usecase import UserUseCase

router = APIRouter(prefix="/users", tags=["user"], dependencies=[Depends(verify_admin)])


@router.get(
    "",
    response_model=UserListResponse,
    response_model_exclude_none=True,
)
async def get_users(
    query: UserSearchQueryParam = Query(),
    service: UserUseCase = Depends(get_user_service),
):
    users = await service.get_users(query.to_query())
    return UserListResponse.from_result(users)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    response_model_exclude_none=True,
)
async def get_user(
    user_id: int,
    service: UserUseCase = Depends(get_user_service),
):
    user = await service.get_user(user_id=user_id)
    return UserResponse.from_domain(user)
