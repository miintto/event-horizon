from datetime import UTC, datetime, timedelta

from jwt import PyJWTError, decode, encode

from app.application.ports.security import TokenClaims, TokenProvider
from app.domain.exceptions import UnauthorizedException
from app.domain.models import UserRole


class JwtProvider(TokenProvider):
    def __init__(self, secret_key: str, algorithm: str, expire_secs: int):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_secs = expire_secs

    def encode(self, user_id: int, role: UserRole) -> str:
        now = datetime.now(UTC)
        return encode(
            {
                "sub": str(user_id),
                "role": role.value,
                "iat": now,
                "exp": now + timedelta(seconds=self._expire_secs),
            },
            self._secret_key,
            algorithm=self._algorithm,
        )

    def decode(self, token: str) -> TokenClaims:
        try:
            payload = decode(token, self._secret_key, algorithms=[self._algorithm])
            return TokenClaims(
                user_id=int(payload["sub"]),
                role=UserRole(payload["role"]),
            )
        except PyJWTError, KeyError, TypeError, ValueError:
            raise UnauthorizedException
