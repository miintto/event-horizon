from datetime import datetime

from fastapi import Query
from pydantic import BaseModel

from app.application.command.user import UserSearchQuery
from app.domain.models import User, UserRole


class UserSearchQueryParam(BaseModel):
    page: int = Query(1, ge=1)
    size: int = Query(10, ge=1, le=50)
    role: UserRole | None = Query(None)
    is_active: bool | None = Query(None)
    email: str | None = Query(None, max_length=255)

    def to_query(self) -> UserSearchQuery:
        return UserSearchQuery(
            page=self.page,
            size=self.size,
            role=self.role,
            is_active=self.is_active,
            email=self.email,
        )


class UserResponse(BaseModel):
    id: int
    name: str | None = None
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls.model_construct(
            id=user.pk,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )


class UserListResponse(BaseModel):
    users: list[UserResponse]

    @classmethod
    def from_result(cls, users: list[User]) -> UserListResponse:
        return cls(users=[UserResponse.from_domain(u) for u in users])
