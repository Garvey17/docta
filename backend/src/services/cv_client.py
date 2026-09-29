"""Computer Vision Client with clean mock fallback."""

import logging
from typing import List, Dict, Any, Optional
import httpx

from ..config import get_settings
from .mock_ai_service import MockAIService

from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


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
    """Client for Computer Vision inference with automatic mock fallback."""

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
        """Call live AI microservice or return deterministic mock detections."""
        if not self.use_mock and self.service_url:
            try:
                async with httpx.AsyncClient(timeout=2.5) as client:
                    if image_bytes:
                        resp = await client.post(
                            f"{self.service_url}/detect",
                            files={"file": ("image.jpg", image_bytes, "image/jpeg")},
                            data={"prompt": prompt} if prompt else None,
                        )
                    else:
                        resp = await client.post(
                            f"{self.service_url}/detect",
                            json={"image_url": image_url, "prompt": prompt},
                        )
                    if resp.status_code == 200:
                        return resp.json().get("detected_items", [])
            except Exception as e:
                logger.warning("Live CV service call failed: %s. Using MockAIService fallback.", e)

        return MockAIService.detect(prompt=prompt)


_cv_client: Optional[CVClient] = None


def get_cv_client() -> CVClient:
    global _cv_client
    if _cv_client is None:
        _cv_client = CVClient()
    return _cv_client
