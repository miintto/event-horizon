import secrets

from fastapi import Depends, Header

from app.adapters.inbound.api.dependencies import get_token_issuer
from app.application.ports.security.token_issuer import TokenIssuer
from app.domain.exceptions import UnauthorizedException
from app.infrastructure.config import settings

BEARER_PREFIX = "Bearer "


async def verify_agent(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {settings.ingest_api_key}"
    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise UnauthorizedException


async def verify_user(
    authorization: str | None = Header(default=None),
    token_issuer: TokenIssuer = Depends(get_token_issuer),
) -> int:
    if authorization is None or not authorization.startswith(BEARER_PREFIX):
        raise UnauthorizedException
    return token_issuer.resolve(authorization.removeprefix(BEARER_PREFIX))
