"""Unified RAG Engine Service Interface for docta backend and orchestrator.

Adheres strictly to PROJECT_ORCHESTRATION.md Section 6.2 B contracts:
- analyze_meal(items: List[Dict[str, Any]]) -> MealAnalysisResponse
- get_dish_nutrition(query: str, weight_g: float) -> ScaledItemNutrition
Guaranteed SLA: < 200ms
"""

import time
import uuid
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

try:
    from .schemas import (
        ScaledItemNutrition,
        TotalNutrition,
        MealAnalysisResponse,
        MealItemInput,
    )
    from .semantic_search import SemanticSearchEngine
    from .macro_scaler import aggregate_meal_nutrition
except ImportError:
    from schemas import (
        ScaledItemNutrition,
        TotalNutrition,
        MealAnalysisResponse,
        MealItemInput,
    )
    from semantic_search import SemanticSearchEngine
    from macro_scaler import aggregate_meal_nutrition


class RAGService:
    """High-throughput RAG engine for meal nutrient resolution and portion scaling."""

    def __init__(
        self,
        search_engine: Optional[SemanticSearchEngine] = None,
        data_dir: Optional[Path] = None,
        force_memory: bool = False,
    ):
        if search_engine is not None:
            self.search_engine = search_engine
        else:
            self.search_engine = SemanticSearchEngine(
                data_dir=data_dir,
                force_memory=force_memory,
            )

    def get_dish_nutrition(
        self,
        query: str,
        weight_g: float = 100.0,
        confidence: float = 1.0,
        item_id: Optional[str] = None,
        bounding_box: Optional[List[float]] = None,
    ) -> ScaledItemNutrition:
        """Resolve a single dish name/query and scale to target weight."""
        return self.search_engine.search_dish(
            query=query,
            weight_g=weight_g,
            confidence=confidence,
            item_id=item_id,
            bounding_box=bounding_box,
        )

    def analyze_meal(
        self,
        items: List[Union[Dict[str, Any], MealItemInput]],
        analysis_id: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> MealAnalysisResponse:
        """Analyze a multi-item meal detected by vision or inputted by user.
        
        SLA: < 200ms total processing time.
        """
        start_time = time.perf_counter()
        if analysis_id is None:
            analysis_id = f"anlz_{uuid.uuid4().hex[:8]}"

        scaled_items: List[ScaledItemNutrition] = []

        for idx, item in enumerate(items):
            if isinstance(item, MealItemInput):
                item_dict = item.model_dump()
            elif isinstance(item, dict):
                item_dict = item
            else:
                raise TypeError(f"Expected dict or MealItemInput, got {type(item)}")

            dish_query = (
                item_dict.get("dish_id")
                or item_dict.get("dish_name")
                or item_dict.get("query")
                or item_dict.get("display_name")
                or "default_meal"
            )
            weight = float(item_dict.get("weight_g") or item_dict.get("estimated_weight_g") or 100.0)
            conf = float(item_dict.get("confidence", 1.0))
            bbox = item_dict.get("bounding_box")
            item_id = item_dict.get("item_id") or f"item_{idx + 1}"

            scaled_dish = self.search_engine.search_dish(
                query=dish_query,
                weight_g=weight,
                confidence=conf,
                item_id=item_id,
                bounding_box=bbox,
            )
            scaled_items.append(scaled_dish)

        total_nutrients = aggregate_meal_nutrition(scaled_items)
        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 1)

        return MealAnalysisResponse(
            analysis_id=analysis_id,
            status="success",
            processing_duration_ms=duration_ms,
            image_url=image_url,
            detected_items=scaled_items,
            total_nutrition=total_nutrients,
        )


# Global singleton instance for easy import by backend
_default_service: Optional[RAGService] = None


def get_rag_service(force_memory: bool = False) -> RAGService:
    """Retrieve or initialize default RAGService singleton."""
    global _default_service
    if _default_service is None:
        _default_service = RAGService(force_memory=force_memory)
    return _default_service


def analyze_meal(
    items: List[Union[Dict[str, Any], MealItemInput]],
    analysis_id: Optional[str] = None,
    image_url: Optional[str] = None,
) -> MealAnalysisResponse:
    """Module-level helper to execute meal analysis with default service."""
    service = get_rag_service()
    return service.analyze_meal(items=items, analysis_id=analysis_id, image_url=image_url)
