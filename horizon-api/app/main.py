from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.adapters.inbound.api.exception_handlers import api_exception_handler
from app.adapters.inbound.api.middlewares.logging_middleware import LoggingMiddleware
from app.adapters.inbound.api.routers import api_router
from app.domain.exceptions import APIException
from app.infrastructure.config import settings
from app.infrastructure.database import engine
from app.infrastructure.logging import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Horizon API", lifespan=lifespan)

# Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(APIException, api_exception_handler)

# Routers
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
