from fastapi import APIRouter

from app.adapters.inbound.api.routers.container_router import router as container_router
from app.adapters.inbound.api.routers.host_router import router as host_router
from app.adapters.inbound.api.routers.metric_router import router as metric_router

api_router = APIRouter(prefix="/api")
api_router.include_router(host_router)
api_router.include_router(container_router)
api_router.include_router(metric_router)
