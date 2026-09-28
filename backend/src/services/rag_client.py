"""RAG & Portion Units Client providing conventional portion units and WAFCT nutrition."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import get_settings
from .mock_rag_service import MockRAGService

logger = logging.getLogger(__name__)

# Optional path to canonical data files if present in workspace
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data_pipeline" / "data"


class RAGClient:
    """Provides portion units and composite nutrition with mock fallback."""

    def __init__(self):
        settings = get_settings()
        self.use_mock = settings.use_mock_rag
        self._portion_cache: Dict[str, Any] = {}
        self._dishes_cache: Dict[str, Any] = {}
        if not self.use_mock:
            self._load_local_data()

    def _load_local_data(self):
        portion_file = DATA_DIR / "portion_units.json"
        if portion_file.exists():
            try:
                with open(portion_file, "r", encoding="utf-8") as f:
                    self._portion_cache = json.load(f).get("portion_units", {})
            except Exception as e:
                logger.warning("Failed loading portion_units.json: %s", e)

        dishes_file = DATA_DIR / "composite_dishes_db.json"
        if dishes_file.exists():
            try:
                with open(dishes_file, "r", encoding="utf-8") as f:
                    self._dishes_cache = json.load(f)
            except Exception as e:
                logger.warning("Failed loading composite_dishes_db.json: %s", e)

    def get_dish_portion_units(self, dish_id: str) -> Dict[str, Any]:
        """Fetch available conventional units for a dish."""
        clean_id = dish_id.lower().strip().replace(" ", "_")
        if self._portion_cache and clean_id in self._portion_cache:
            return self._portion_cache[clean_id]
        return MockRAGService.get_portion_units(clean_id)

    def get_dish_base_nutrients(self, dish_id: str) -> Dict[str, Any]:
        """Fetch per-100g base cooked nutrients."""
        clean_id = dish_id.lower().strip().replace(" ", "_")
        if self._dishes_cache and clean_id in self._dishes_cache:
            dish = self._dishes_cache[clean_id]
            return {
                "nutrients_per_100g": dish.get("nutrients_cooked_100g", {}),
                "display_name": dish.get("dish_name", dish_id.title()),
                "wafct_code": dish.get("wafct_code", "00_COMPOSITE"),
            }
        return MockRAGService.get_nutrients(clean_id)


_rag_client: Optional[RAGClient] = None


def get_rag_client() -> RAGClient:
    global _rag_client
    if _rag_client is None:
        _rag_client = RAGClient()
    return _rag_client
