"""Computer Vision client for the configured live inference service."""

from typing import List, Dict, Any, Optional
import httpx

from ..config import get_settings

from abc import ABC, abstractmethod

class BaseCVProvider(ABC):
    """Abstract interface defining the strict contract for Computer Vision models.
    
    CRITICAL ARCHITECTURAL BOUNDARY:
    CV providers MUST only output food identification (dish_id, display_name, confidence, bounding_box).
    CV providers MUST NEVER calculate or estimate nutrition, calories, or gram weights.
    Authoritative nutrition and portion units belong strictly to RAGService.
    """

    @abstractmethod
    async def detect_dishes(
        self,
        image_bytes: Optional[bytes] = None,
        image_url: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Detect dishes in an image.
        
        Returns:
            List of dicts, each containing:
            - item_id (str)
            - predicted_dish_id (str)
            - display_name (str)
            - confidence (float 0.0 - 1.0)
            - bounding_box (List[float] [ymin, xmin, ymax, xmax])
        """
        pass


class CVClient(BaseCVProvider):
    """Client for the configured live Computer Vision service."""

    def __init__(self):
        settings = get_settings()
        self.service_url = settings.cv_service_url
        self.use_mock = settings.use_mock_ai

    async def detect_dishes(
        self,
        image_bytes: Optional[bytes] = None,
        image_url: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Call live inference and propagate missing configuration or service errors."""
        if self.use_mock:
            raise RuntimeError("Mock AI is disabled for this application. Set USE_MOCK_AI=false.")
        if not self.service_url:
            raise RuntimeError("CV_SERVICE_URL is required when mock AI is disabled.")

        async with httpx.AsyncClient(timeout=30.0) as client:
            if image_bytes:
                resp = await client.post(
                    f"{self.service_url.rstrip('/')}/detect",
                    files={"file": ("image.jpg", image_bytes, "image/jpeg")},
                    data={"prompt": prompt} if prompt else None,
                )
            else:
                resp = await client.post(
                    f"{self.service_url.rstrip('/')}/detect",
                    json={"image_url": image_url, "prompt": prompt},
                )
            resp.raise_for_status()
            payload = resp.json()
            return payload["detected_items"]


_cv_client: Optional[CVClient] = None


def get_cv_client() -> CVClient:
    global _cv_client
    if _cv_client is None:
        _cv_client = CVClient()
    return _cv_client
