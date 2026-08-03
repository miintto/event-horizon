from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"


@dataclass(kw_only=True)
class User:
    id: int | None = None
    name: str | None = None
    email: str
    password_hash: str
    role: UserRole = UserRole.MEMBER
    is_active: bool = True
    created_at: datetime | None = None

    @property
    def pk(self) -> int:
        return self.id  # type: ignore
