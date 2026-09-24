"""Configuration and Environment Settings for docta Backend."""

import os
from functools import lru_cache
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable management."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server & Environment
    app_name: str = "docta Backend API"
    environment: str = "development"
    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"

    # Database
    # Standard: postgresql+asyncpg://postgres:postgres@localhost:5432/docta_db
    # Or SQLite fallback for local test execution: sqlite+aiosqlite:///./docta.db
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/docta_db",
        alias="DATABASE_URL",
    )

    # Authentication & Security
    secret_key: str = Field(
        default="docta-secret-key-for-dev-change-in-production-0987654321",
        alias="SECRET_KEY",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS
    cors_origins: Union[List[str], str] = ["*"]

    # Storage & Uploads (AWS Fargate / S3 / Local allowances)
    upload_dir: str = "uploads"
    aws_region: str = "eu-central-1"
    s3_bucket_name: Union[str, None] = None

    # Service Bridges & Mocking
    use_mock_ai: bool = Field(default=True, alias="USE_MOCK_AI")
    use_mock_rag: bool = Field(default=False, alias="USE_MOCK_RAG")
    ai_service_url: Union[str, None] = Field(default=None, alias="AI_SERVICE_URL")

    # Qdrant / OpenAI passthrough if needed
    openai_api_key: Union[str, None] = Field(default=None, alias="OPENAI_API_KEY")
    qdrant_url: Union[str, None] = Field(default=None, alias="QDRANT_URL")
    qdrant_api_key: Union[str, None] = Field(default=None, alias="QDRANT_API_KEY")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if not v:
            return "sqlite+aiosqlite:///./docta.db"
        # If user provides standard postgres:// or postgresql://, adapt to postgresql+asyncpg://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("sqlite://") and not v.startswith("sqlite+aiosqlite://"):
            return v.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return v

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
