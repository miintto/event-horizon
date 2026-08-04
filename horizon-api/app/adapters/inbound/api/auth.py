import secrets

from fastapi import Depends, Header

from app.adapters.inbound.api.dependencies import get_token_provider
from app.application.ports.security import TokenClaims, TokenProvider
from app.domain.exceptions import ForbiddenException, UnauthorizedException
from app.domain.models import UserRole
from app.infrastructure.config import settings

BEARER_PREFIX = "Bearer "


async def verify_agent(authorization: str | None = Header(default=None)):
    expected = f"Bearer {settings.ingest_api_key}"
    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise UnauthorizedException


async def _resolve_claims(
    authorization: str | None = Header(default=None),
    token_provider: TokenProvider = Depends(get_token_provider),
) -> TokenClaims:
    if authorization is None or not authorization.startswith(BEARER_PREFIX):
        raise UnauthorizedException
    return token_provider.decode(authorization.removeprefix(BEARER_PREFIX))


async def verify_user(claims: TokenClaims = Depends(_resolve_claims)) -> int:
    return claims.user_id


async def verify_admin(claims: TokenClaims = Depends(_resolve_claims)) -> int:
    if claims.role is not UserRole.ADMIN:
        raise ForbiddenException
    return claims.user_id
