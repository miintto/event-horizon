import logging
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("horizon.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        hash = uuid4().hex[:8]
        path = request.url.path

        logger.info(
            "Request  [%s] %s %s",
            hash,
            request.method,
            f"{path}?{request.query_params}" if request.query_params else path,
        )
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Response [%s] %s %s - ERROR", hash, request.method, path)
            raise

        logger.info(
            "Response [%s] %s %s - %d", hash, request.method, path, response.status_code
        )
        return response
