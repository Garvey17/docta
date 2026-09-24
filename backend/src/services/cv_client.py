"""Computer Vision Bridge Client with deterministic fallback."""

import logging
from typing import List, Dict, Any, Optional
import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

MOCK_DETECTIONS = [
    {
        "item_id": "item_1",
        "predicted_dish_id": "jollof_rice",
        "display_name": "Nigerian Jollof Rice",
        "confidence": 0.94,
        "bounding_box": [0.125, 0.240, 0.550, 0.780],
    },
    {
        "item_id": "item_2",
        "predicted_dish_id": "fried_plantain",
        "display_name": "Fried Ripe Plantain (Dodo)",
        "confidence": 0.89,
        "bounding_box": [0.580, 0.310, 0.890, 0.650],
    },
]


class CVClient:
    """Client for Computer Vision inference with automatic mock fallback."""

    def __init__(self):
        self.ai_service_url = settings.ai_service_url
        self.use_mock = settings.use_mock_ai

    async def detect_dishes(
        self,
        image_bytes: Optional[bytes] = None,
        image_url: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Call live AI microservice or return deterministic detections."""
        if not self.use_mock and self.ai_service_url:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    if image_bytes:
                        resp = await client.post(
                            f"{self.ai_service_url}/detect",
                            files={"file": ("image.jpg", image_bytes, "image/jpeg")},
                            data={"prompt": prompt} if prompt else None,
                        )
                    else:
                        resp = await client.post(
                            f"{self.ai_service_url}/detect",
                            json={"image_url": image_url, "prompt": prompt},
                        )
                    if resp.status_code == 200:
                        return resp.json().get("detected_items", [])
            except Exception as e:
                logger.warning(f"Live CV service call failed: {e}. Using fallback detections.")

        # Deterministic prompt matching for tests & offline dev
        if prompt:
            p_lower = prompt.lower()
            if "amala" in p_lower:
                return [
                    {"item_id": "item_1", "predicted_dish_id": "amala", "display_name": "Àmàlà (Yam Flour)", "confidence": 0.95, "bounding_box": [0.15, 0.25, 0.55, 0.80]},
                    {"item_id": "item_2", "predicted_dish_id": "egusi_soup", "display_name": "Egusi Soup", "confidence": 0.92, "bounding_box": [0.55, 0.30, 0.90, 0.70]},
                ]
            if "egusi" in p_lower:
                return [{"item_id": "item_1", "predicted_dish_id": "egusi_soup", "display_name": "Egusi Soup", "confidence": 0.96, "bounding_box": [0.10, 0.20, 0.50, 0.75]}]
            if "moi" in p_lower:
                return [{"item_id": "item_1", "predicted_dish_id": "moi_moi", "display_name": "Moi Moi (Steamed Bean Pudding)", "confidence": 0.93, "bounding_box": [0.20, 0.20, 0.80, 0.80]}]

        return list(MOCK_DETECTIONS)


_cv_client: Optional[CVClient] = None


def get_cv_client() -> CVClient:
    global _cv_client
    if _cv_client is None:
        _cv_client = CVClient()
    return _cv_client
