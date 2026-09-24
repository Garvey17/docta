"""Health and Readiness Routers for AWS ECS / Fargate and Load Balancers."""

import time
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..database import get_db

router = APIRouter(tags=["Health & Diagnostics"])
settings = get_settings()

_start_time = time.time()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe for container orchestrator (AWS Fargate / ECS)."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "uptime_seconds": round(time.time() - _start_time, 2),
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check(response: Response, db: AsyncSession = Depends(get_db)):
    """Readiness probe checking database connectivity and core services."""
    db_status = "unknown"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if db_status == "connected" else "unready",
        "database": db_status,
        "mock_ai": settings.use_mock_ai,
        "mock_rag": settings.use_mock_rag,
    }
