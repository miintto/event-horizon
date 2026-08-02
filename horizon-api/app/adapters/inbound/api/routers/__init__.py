from fastapi import APIRouter, Depends

from app.adapters.inbound.api.auth import verify_user
from app.adapters.inbound.api.routers.auth_router import router as auth_router
from app.adapters.inbound.api.routers.container_router import router as container_router
from app.adapters.inbound.api.routers.host_router import router as host_router
from app.adapters.inbound.api.routers.metric_router import router as metric_router
from app.adapters.inbound.api.routers.workload_router import router as workload_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(metric_router)

protected_router = APIRouter(dependencies=[Depends(verify_user)])
protected_router.include_router(container_router)
protected_router.include_router(host_router)
protected_router.include_router(workload_router)
api_router.include_router(protected_router)
