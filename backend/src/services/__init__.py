"""Services registry for docta backend."""

from .auth_service import AuthService
from .storage_service import StorageService, get_storage_service, save_uploaded_image
from .cv_client import CVClient, get_cv_client
from .rag_client import RAGClient, get_rag_client
from .telemetry_service import TelemetryService
from .orchestrator_service import OrchestratorService, get_orchestrator_service

__all__ = [
    "AuthService",
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
