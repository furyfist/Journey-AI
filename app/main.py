from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.http_client import build_async_client
from app.common.logger import get_logger
from app.core.config import settings
from app.core.database import create_db_client
from app.core.exception_handlers import register_exception_handlers
from app.health.router import router as health_router
from app.trips.router import router as trips_router

logger = get_logger(__name__)

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Journey AI backend [env=%s]", settings.app_env)
    app.state.db = await create_db_client()
    app.state.http = build_async_client()
    yield
    logger.info("Shutting down Journey AI backend")
    await app.state.http.aclose()


app = FastAPI(
    title="Journey AI",
    description="Multi-agent AI travel planner — research, plan, stream, conflict-detect.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health_router, prefix=API_PREFIX)
app.include_router(trips_router, prefix=API_PREFIX)
