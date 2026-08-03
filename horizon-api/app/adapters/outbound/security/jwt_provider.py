from datetime import UTC, datetime, timedelta

from jwt import PyJWTError, decode, encode

from app.application.ports.security import TokenProvider
from app.domain.exceptions import UnauthorizedException


class JwtProvider(TokenProvider):
    def __init__(self, secret_key: str, algorithm: str, expire_secs: int):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_secs = expire_secs

    def issue(self, user_id: int) -> str:
        now = datetime.now(UTC)
        return encode(
            {
                "sub": str(user_id),
                "iat": now,
                "exp": now + timedelta(seconds=self._expire_secs),
            },
            self._secret_key,
            algorithm=self._algorithm,
        )

    def resolve(self, token: str) -> int:
        try:
            payload = decode(token, self._secret_key, algorithms=[self._algorithm])
            return int(payload["sub"])
        except PyJWTError, KeyError, TypeError, ValueError:
            raise UnauthorizedException
