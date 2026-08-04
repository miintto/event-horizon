from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.application.command.auth import LoginCommand, RegisterCommand, TokenResult
from app.domain.models import UserRole


class RegisterRequest(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)
    password_check: str
    role: UserRole = UserRole.MEMBER

    @model_validator(mode="after")
    def validate_password_check(self) -> Self:
        if self.password != self.password_check:
            raise ValueError("`password_check` does not match password")
        return self

    def to_command(self) -> RegisterCommand:
        return RegisterCommand(
            name=self.name,
            email=self.email,
            password=self.password,
            role=self.role,
        )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    def to_command(self) -> LoginCommand:
        return LoginCommand(email=self.email, password=self.password)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    @classmethod
    def from_result(cls, result: TokenResult) -> TokenResponse:
        return cls.model_construct(
            access_token=result.access_token,
            expires_in=result.expires_in,
        )
