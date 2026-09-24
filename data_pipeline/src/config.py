"""Configuration settings for Data & RAG pipeline using Pydantic Settings."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env if present
load_dotenv()


class Settings(BaseSettings):
    """Pipeline configuration loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # OpenAI Settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI Chat/Reasoning Model")
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI Embedding Model")

    # Qdrant Cloud Settings
    qdrant_url: Optional[str] = Field(default=None, description="Qdrant Cloud URL (e.g. https://xyz.qdrant.io)")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant Cloud API Key")
    qdrant_collection_name: str = Field(default="composite_dishes", description="Qdrant collection name")

    # Local Paths
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data")


def get_settings() -> Settings:
    """Retrieve settings singleton with environment fallback."""
    return Settings()
