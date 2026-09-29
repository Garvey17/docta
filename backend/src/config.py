"""Configuration and Environment Settings for docta Backend."""

import os
from pathlib import Path
from functools import lru_cache
from typing import List, Union, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable management."""

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server & Environment
    app_name: str = "docta Backend API"
    environment: str = "development"
    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"

    # Supabase Infrastructure
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, alias="SUPABASE_KEY")
    supabase_service_role_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")

    # Authentication & Security
    secret_key: str = Field(
        default="docta-secret-key-for-dev-change-in-production-0987654321",
        alias="SECRET_KEY",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    cors_origins: Union[List[str], str] = ["*"]

    # Storage & Uploads
    upload_dir: str = "uploads"
    supabase_storage_bucket: str = "meals"

    # Service Bridges & Mocking
    use_mock_ai: bool = Field(default=True, alias="USE_MOCK_AI")
    use_mock_rag: bool = Field(default=True, alias="USE_MOCK_RAG")
    cv_service_url: Optional[str] = Field(default=None, alias="CV_SERVICE_URL")
    rag_service_url: Optional[str] = Field(default=None, alias="RAG_SERVICE_URL")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Singleton getter for application settings."""
    return Settings()
