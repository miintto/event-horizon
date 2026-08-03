from dataclasses import dataclass

from app.domain.models import UserRole


@dataclass
class RegisterCommand:
    actor_id: int
    name: str | None
    email: str
    password: str
    role: UserRole = UserRole.MEMBER


@dataclass
class LoginCommand:
    email: str
    password: str


@dataclass
class TokenResult:
    access_token: str
    expires_in: int
