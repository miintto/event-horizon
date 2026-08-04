from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.models import UserRole


@dataclass(frozen=True, kw_only=True)
class TokenClaims:
    user_id: int
    role: UserRole


class TokenProvider(ABC):
    @abstractmethod
    def encode(self, user_id: int, role: UserRole) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> TokenClaims: ...
