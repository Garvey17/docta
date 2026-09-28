"""Health and Diagnostics Routers for ECS/Fargate and Load Balancers."""

import time
from fastapi import APIRouter, status, Response

from ..config import get_settings
from ..supabase_client import get_supabase_client

router = APIRouter(tags=["Health & Diagnostics"])
settings = get_settings()

_start_time = time.time()


@router.get("/health", status_code=status.HTTP_200_OK)
@router.get("/api/v1/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe for container orchestrator and gateways."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "uptime_seconds": round(time.time() - _start_time, 2),
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check(response: Response):
    """Readiness probe checking Supabase connectivity and mock flags."""
    db_status = "connected"
    try:
        supabase = get_supabase_client()
        supabase.from_("meals").select("id").limit(1).execute()
    except Exception as e:
        db_status = f"unconnected: {str(e)}"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if "connected" in db_status else "unready",
        "database": db_status,
        "mock_ai": settings.use_mock_ai,
        "mock_rag": settings.use_mock_rag,
    }
