from fastapi import APIRouter

from app.adapters.inbound.api.routers.host_metric_router import (
    router as host_metric_router,
)
from app.adapters.inbound.api.routers.host_router import (
    router as host_router,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(host_router)
api_router.include_router(host_metric_router)
