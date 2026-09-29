"""RAG & Portion Units Client providing conventional portion units and WAFCT nutrition."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import get_settings
from .mock_rag_service import MockRAGService

logger = logging.getLogger(__name__)

try:
    from ..data_pipeline.src.rag_service import RAGService
except ImportError:
    try:
        from backend.src.data_pipeline.src.rag_service import RAGService
    except ImportError:
        RAGService = None


class RAGClient:
    """Provides portion units and composite nutrition delegating to RAGService or mock fallback."""

    def __init__(self):
        settings = get_settings()
        self.use_mock = settings.use_mock_rag
        self.rag_service: Optional[Any] = None
        if not self.use_mock and RAGService is not None:
            try:
                self.rag_service = RAGService(force_memory=True)
            except Exception as e:
                logger.error("Failed to initialize RAGService: %s", e)
                self.rag_service = None

    def get_dish_portion_units(self, dish_id: str) -> Dict[str, Any]:
        """Fetch available conventional units for a dish."""
        clean_id = dish_id.lower().strip().replace(" ", "_")
        if not self.use_mock and self.rag_service is not None:
            try:
                cfg = self.rag_service.get_portion_config(clean_id)
                return {
                    "dish_id": cfg.dish_id or clean_id,
                    "dish_name": cfg.dish_name or clean_id.replace("_", " ").title(),
                    "default_unit_id": cfg.default_unit_id,
                    "default_quantity": cfg.default_quantity,
                    "units": [
                        {
                            "unit_id": u.unit_id,
                            "unit_name": u.unit_name,
                            "gram_weight": u.gram_weight,
                            "description": u.description,
                        }
                        for u in cfg.units
                    ],
                }
            except Exception as e:
                logger.warning("RAGService get_portion_config failed for %s: %s", clean_id, e)

        return MockRAGService.get_portion_units(clean_id)

    def get_dish_base_nutrients(self, dish_id: str) -> Dict[str, Any]:
        """Fetch per-100g base cooked nutrients."""
        clean_id = dish_id.lower().strip().replace(" ", "_")
        if not self.use_mock and self.rag_service is not None:
            try:
                item = self.rag_service.get_dish_nutrition(clean_id, weight_g=100.0)
                n_dict = (
                    item.nutrients_per_100g.model_dump()
                    if item.nutrients_per_100g
                    else item.nutrients.model_dump()
                )
                return {
                    "nutrients_per_100g": n_dict,
                    "display_name": item.display_name,
                    "wafct_code": item.wafct_code,
                }
            except Exception as e:
                logger.warning("RAGService get_dish_nutrition failed for %s: %s", clean_id, e)

        return MockRAGService.get_nutrients(clean_id)

    def get_dish_nutrition(
        self,
        query: str,
        weight_g: Optional[float] = None,
        unit_id: Optional[str] = None,
        quantity: Optional[float] = None,
        custom_weight_g: Optional[float] = None,
        confidence: float = 1.0,
    ) -> Any:
        """Resolve a dish and scale its nutrition through RAGService."""
        if not self.use_mock and self.rag_service is not None:
            return self.rag_service.get_dish_nutrition(
                query=query,
                weight_g=weight_g,
                unit_id=unit_id,
                quantity=quantity,
                custom_weight_g=custom_weight_g,
                confidence=confidence,
            )
        return None


_rag_client: Optional[RAGClient] = None


def get_rag_client() -> RAGClient:
    global _rag_client
    if _rag_client is None:
        _rag_client = RAGClient()
    return _rag_client
