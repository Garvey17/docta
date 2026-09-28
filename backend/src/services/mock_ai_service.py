"""Deterministic Mock AI / Computer Vision Service.

Provides realistic food identification, bounding boxes, and confidence scores
without requiring external GPU/YOLO/Gemini services.
"""

from typing import List, Dict, Any, Optional

DEFAULT_MOCK_DETECTIONS: List[Dict[str, Any]] = [
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


class MockAIService:
    """Deterministic CV prediction provider."""

    @staticmethod
    def detect(prompt: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return deterministic detections tailored to optional user prompt."""
        if prompt:
            p_lower = prompt.lower()
            if "amala" in p_lower:
                return [
                    {
                        "item_id": "item_1",
                        "predicted_dish_id": "amala",
                        "display_name": "Àmàlà (Yam Flour)",
                        "confidence": 0.95,
                        "bounding_box": [0.15, 0.25, 0.55, 0.80],
                    },
                    {
                        "item_id": "item_2",
                        "predicted_dish_id": "egusi_soup",
                        "display_name": "Egusi Soup",
                        "confidence": 0.92,
                        "bounding_box": [0.55, 0.30, 0.90, 0.70],
                    },
                ]
            if "egusi" in p_lower:
                return [
                    {
                        "item_id": "item_1",
                        "predicted_dish_id": "egusi_soup",
                        "display_name": "Egusi Soup",
                        "confidence": 0.96,
                        "bounding_box": [0.10, 0.20, 0.50, 0.75],
                    }
                ]
            if "moi" in p_lower or "bean" in p_lower:
                return [
                    {
                        "item_id": "item_1",
                        "predicted_dish_id": "moi_moi",
                        "display_name": "Moi Moi (Steamed Bean Pudding)",
                        "confidence": 0.93,
                        "bounding_box": [0.20, 0.20, 0.80, 0.80],
                    }
                ]

        return [dict(d) for d in DEFAULT_MOCK_DETECTIONS]
