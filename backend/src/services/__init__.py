"""Services registry for docta backend."""

from .auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
    get_current_user_optional,
)
from .storage_service import StorageService, get_storage_service, save_uploaded_image
from .cv_client import CVClient, get_cv_client
from .rag_client import RAGClient, get_rag_client
from .telemetry_service import TelemetryService
from .orchestrator_service import OrchestratorService, get_orchestrator_service

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_current_user_optional",
    "StorageService",
    "get_storage_service",
    "save_uploaded_image",
    "CVClient",
    "get_cv_client",
    "RAGClient",
    "get_rag_client",
    "TelemetryService",
    "OrchestratorService",
    "get_orchestrator_service",
]
