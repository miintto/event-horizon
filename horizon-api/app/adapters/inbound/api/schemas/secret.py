from datetime import datetime

from fastapi import Query
from pydantic import BaseModel, Field

from app.application.command.secret import (
    SecretCreateCommand,
    SecretSearchQuery,
    SecretUpdateCommand,
)
from app.domain.models import Secret


class SecretSearchQueryParam(BaseModel):
    page: int = Query(1, ge=1)
    size: int = Query(10, ge=1, le=50)

    def to_query(self) -> SecretSearchQuery:
        return SecretSearchQuery(page=self.page, size=self.size)


class SecretCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    value: str = Field(min_length=1, max_length=4096)

    def to_command(self) -> SecretCreateCommand:
        return SecretCreateCommand(name=self.name, value=self.value)


class SecretUpdateRequest(BaseModel):
    value: str = Field(min_length=1, max_length=4096)

    def to_command(self, secret_id: int) -> SecretUpdateCommand:
        return SecretUpdateCommand(secret_id=secret_id, value=self.value)


class SecretResponse(BaseModel):
    id: int
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, secret: Secret) -> SecretResponse:
        return cls.model_construct(
            id=secret.pk,
            name=secret.name,
            created_at=secret.created_at,
            updated_at=secret.updated_at,
        )


class SecretListResponse(BaseModel):
    secrets: list[SecretResponse]

    @classmethod
    def from_result(cls, secrets: list[Secret]) -> SecretListResponse:
        return cls(secrets=[SecretResponse.from_domain(s) for s in secrets])
