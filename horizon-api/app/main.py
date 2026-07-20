from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.inbound.api.exception_handlers import api_exception_handler
from app.adapters.inbound.api.routers import api_router
from app.domain.exceptions import APIException
from app.infrastructure.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Horizon API", lifespan=lifespan)

# Exception Handlers
app.add_exception_handler(APIException, api_exception_handler)

# Routers
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
