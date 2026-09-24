"""RAG & Portion Units Client connecting backend to data_pipeline without code duplication."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Path to canonical data files
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data_pipeline" / "data"


class RAGClient:
    """Provides fast lookup of portion units and composite nutrition."""

    def __init__(self):
        self._portion_cache: Dict[str, Any] = {}
        self._dishes_cache: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self):
        # Load portion units from canonical data_pipeline JSON
        portion_file = DATA_DIR / "portion_units.json"
        if portion_file.exists():
            try:
                with open(portion_file, "r", encoding="utf-8") as f:
                    self._portion_cache = json.load(f).get("portion_units", {})
            except Exception as e:
                logger.warning(f"Failed loading portion_units.json: {e}")

        # Load composite dishes database
        dishes_file = DATA_DIR / "composite_dishes_db.json"
        if dishes_file.exists():
            try:
                with open(dishes_file, "r", encoding="utf-8") as f:
                    self._dishes_cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed loading composite_dishes_db.json: {e}")

    def get_dish_portion_units(self, dish_id: str) -> Dict[str, Any]:
        """Fetch available conventional units for a dish."""
        clean_id = dish_id.lower().strip().replace(" ", "_")
        if clean_id in self._portion_cache:
            return self._portion_cache[clean_id]

        # Generic fallback if custom dish not in 5 initial dishes
        return {
            "dish_id": clean_id,
            "dish_name": dish_id.replace("_", " ").title(),
            "default_unit_id": "standard_serving",
            "default_quantity": 1.0,
            "units": [
                {"unit_id": "standard_serving", "unit_name": "Standard Serving", "gram_weight": 150.0, "description": "Standard serving (~150g)"},
                {"unit_id": "half_serving", "unit_name": "Half Serving", "gram_weight": 75.0, "description": "Half serving (~75g)"},
                {"unit_id": "double_serving", "unit_name": "Double Serving", "gram_weight": 300.0, "description": "Double serving (~300g)"},
            ],
        }

    def get_dish_base_nutrients(self, dish_id: str) -> Dict[str, Any]:
        """Fetch per-100g base cooked nutrients."""
        clean_id = dish_id.lower().strip().replace(" ", "_")
        if clean_id in self._dishes_cache:
            dish = self._dishes_cache[clean_id]
            return {
                "nutrients_per_100g": dish.get("nutrients_cooked_100g", {}),
                "display_name": dish.get("dish_name", dish_id.title()),
                "wafct_code": dish.get("wafct_code", "00_COMPOSITE"),
            }

        # Fallback average nutrients
        return {
            "nutrients_per_100g": {
                "calories_kcal": 150.0, "protein_g": 3.5, "fat_g": 4.5, "carbs_g": 22.0,
                "fiber_g": 1.5, "sodium_mg": 120.0, "calcium_mg": 15.0, "iron_mg": 1.0,
            },
            "display_name": dish_id.replace("_", " ").title(),
            "wafct_code": "00_COMPOSITE",
        }


_rag_client: Optional[RAGClient] = None


def get_rag_client() -> RAGClient:
    global _rag_client
    if _rag_client is None:
        _rag_client = RAGClient()
    return _rag_client
