"""
Liveness/readiness endpoint.

Split into two concerns on purpose:
- liveness: "is the process up" — never touches the DB, always fast.
- readiness: "can it actually serve traffic" — checks DB + Redis connectivity,
  used by Railway's health check to decide whether to route traffic to this
  instance during deploys.
"""
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def liveness():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    checks = {"database": "unknown", "redis": "unknown"}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001 - reported in response, not raised
        checks["database"] = f"error: {exc}"

    try:
        redis_client = Redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.aclose()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"error: {exc}"

    overall_ok = all(v == "ok" for v in checks.values())
    return {"status": "ok" if overall_ok else "degraded", "checks": checks}
