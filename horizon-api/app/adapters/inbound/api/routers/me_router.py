from fastapi import APIRouter, Depends

from app.adapters.inbound.api.auth import verify_user
from app.adapters.inbound.api.dependencies import get_user_service
from app.adapters.inbound.api.schemas.user import UserResponse
from app.application.ports.usecase import UserUseCase

router = APIRouter(prefix="/me", tags=["me"])


@router.get(
    "",
    response_model=UserResponse,
    response_model_exclude_none=True,
)
async def get_me(
    user_id: int = Depends(verify_user),
    service: UserUseCase = Depends(get_user_service),
):
    user = await service.get_user(user_id=user_id)
    return UserResponse.from_domain(user)
