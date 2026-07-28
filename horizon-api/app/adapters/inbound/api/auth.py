import secrets

from fastapi import Header

from app.domain.exceptions import UnauthorizedException
from app.infrastructure.config import settings


async def verify_agent(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {settings.ingest_api_key}"
    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise UnauthorizedException
