from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check() -> dict[str, str]:
    """Returns application health status."""
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
    }
