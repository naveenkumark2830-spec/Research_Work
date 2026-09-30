from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import BaseAppException
from app.simulation.common.exceptions import HDFSBaseException
from app.db.database import init_db
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.api.sessions import router as sessions_router
from app.api.events import router as events_router
from app.api.hdfs_simulation import router as hdfs_router
from app.api.ai import router as ai_router
from app.api.jarvis import router as jarvis_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Assisted Interactive Hadoop Execution & Learning Simulator Backend API",
    version="4.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BaseAppException)
async def custom_app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.exception_handler(HDFSBaseException)
async def hdfs_exception_handler(request: Request, exc: HDFSBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


# API v1 routers
app.include_router(
    health_router,
    prefix=settings.API_V1_STR,
    tags=["health"],
)

app.include_router(
    users_router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"],
)

app.include_router(
    sessions_router,
    prefix=f"{settings.API_V1_STR}/sessions",
    tags=["sessions"],
)

app.include_router(
    events_router,
    prefix=f"{settings.API_V1_STR}/sessions",
    tags=["events"],
)

app.include_router(
    hdfs_router,
    prefix=f"{settings.API_V1_STR}/simulation/hdfs",
    tags=["hdfs-simulation"],
)

app.include_router(
    ai_router,
    prefix=f"{settings.API_V1_STR}/ai",
    tags=["ai"],
)

app.include_router(jarvis_router)


@app.get("/", summary="Root Endpoint")
async def root() -> dict[str, str]:
    """Root endpoint returning service identity."""
    return {
        "service": settings.SERVICE_NAME,
        "status": "running",
        "docs": "/docs",
    }
