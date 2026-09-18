"""
routers/health.py — GET /health
"""
from fastapi import APIRouter
from database import ping_db
from config import get_settings
from schemas.common import HealthResponse

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns "ok" if database is reachable, "degraded" otherwise.
    """
    db_ok = await ping_db()
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        environment=settings.environment,
        database="connected" if db_ok else "error",
    )

