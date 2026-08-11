from fastapi import APIRouter, Depends

from app.adapters.inbound.api.auth import verify_user
from app.adapters.inbound.api.routers.agent_router import router as agent_router
from app.adapters.inbound.api.routers.auth_router import router as auth_router
from app.adapters.inbound.api.routers.container_router import router as container_router
from app.adapters.inbound.api.routers.deployment_router import (
    router as deployment_router,
)
from app.adapters.inbound.api.routers.host_router import router as host_router
from app.adapters.inbound.api.routers.metric_router import router as metric_router
from app.adapters.inbound.api.routers.network_router import router as network_router
from app.adapters.inbound.api.routers.secret_router import router as secret_router
from app.adapters.inbound.api.routers.user_router import router as user_router
from app.adapters.inbound.api.routers.workload_router import router as workload_router

api_router = APIRouter(prefix="/api")
api_router.include_router(agent_router)
api_router.include_router(auth_router)
api_router.include_router(metric_router)

protected_router = APIRouter(dependencies=[Depends(verify_user)])
protected_router.include_router(container_router)
protected_router.include_router(deployment_router)
protected_router.include_router(host_router)
protected_router.include_router(network_router)
protected_router.include_router(secret_router)
protected_router.include_router(user_router)
protected_router.include_router(workload_router)
api_router.include_router(protected_router)
