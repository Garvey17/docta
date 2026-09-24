"""Routers registry for docta backend."""

from .health_router import router as health_router
from .auth_router import router as auth_router
from .analyze_router import router as analyze_router
from .meal_router import router as meal_router
from .telemetry_router import router as telemetry_router
from .dashboard_router import router as dashboard_router

__all__ = [
    "health_router",
    "auth_router",
    "analyze_router",
    "meal_router",
    "telemetry_router",
    "dashboard_router",
]
