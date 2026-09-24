"""FastAPI Application Entrypoint for docta Backend Gateway.

Engineered for:
- Food Identification + Conventional Portion Units
- 'Log Everything' Active Learning Telemetry
- AWS ECS / Fargate Container Deployment
- PostgreSQL Async Database Integration
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db
from .routers import (
    health_router,
    auth_router,
    analyze_router,
    meal_router,
    telemetry_router,
    dashboard_router,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycles."""
    # Ensure tables are initialized on startup (helpful for local dev and testing)
    await init_db()

    # Ensure uploads directory exists
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "docta Core Backend Gateway providing African & Nigerian dietary nutrition intelligence, "
        "multimodal food identification, conventional portion unit resolution, and 'Log Everything' active learning telemetry."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if isinstance(settings.cors_origins, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for local image uploads
uploads_dir = Path(settings.upload_dir)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Mount API Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(meal_router)
app.include_router(telemetry_router)
app.include_router(dashboard_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to docta Nutrition Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
