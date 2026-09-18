from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text

from app.database import get_db
from app.services.rate_limiter import get_redis
from app.config import get_settings

settings = get_settings()
router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: DBSession = Depends(get_db)):
    """
    Returns the health status of all system components.
    Used by Nginx for upstream health checks.
    """
    checks: dict = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "components": {},
    }

    # MySQL check
    try:
        db.execute(text("SELECT 1"))
        checks["components"]["mysql"] = "healthy"
    except Exception as e:
        checks["components"]["mysql"] = f"unhealthy: {str(e)}"
        checks["status"] = "degraded"

    # Redis check
    try:
        r = get_redis()
        r.ping()
        checks["components"]["redis"] = "healthy"
    except Exception as e:
        checks["components"]["redis"] = f"unhealthy: {str(e)}"
        checks["status"] = "degraded"

    return checks
