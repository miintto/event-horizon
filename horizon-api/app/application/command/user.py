from dataclasses import dataclass

from app.domain.models import UserRole


@dataclass
class UserSearchQuery:
    page: int
    size: int
    role: UserRole | None = None
    is_active: bool | None = None
    email: str | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size
