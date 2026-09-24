"""Multimodal Analysis Orchestrator Service (<2.0s SLA)."""

import time
import uuid
import logging
from typing import Optional, List
from fastapi import UploadFile

from ..schemas.analyze import (
    AnalyzeMealResponse,
    DetectedItemNutrition,
    PortionUnitInfo,
    NutrientProfile100g,
)
from .cv_client import get_cv_client
from .rag_client import get_rag_client
from .storage_service import save_uploaded_image

logger = logging.getLogger(__name__)


class OrchestratorService:
    """Orchestrates CV food detection and RAG portion unit & macro resolution."""

    def __init__(self):
        self.cv_client = get_cv_client()
        self.rag_client = get_rag_client()

    async def analyze(
        self,
        file: Optional[UploadFile] = None,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> AnalyzeMealResponse:
        """Process meal image (file upload or URL/base64) and attach portion units."""
        start_time = time.perf_counter()
        analysis_id = f"anlz_{uuid.uuid4().hex[:8]}"

        image_bytes = None
        effective_image_url = image_url

        if file is not None and file.filename:
            image_bytes = await file.read()
            await file.seek(0)
            effective_image_url = await save_uploaded_image(file, prefix=analysis_id)

        # 1. Computer Vision Detection
        cv_items = await self.cv_client.detect_dishes(
            image_bytes=image_bytes,
            image_url=effective_image_url,
            prompt=prompt,
        )

        # 2. Enrich with conventional portion units and WAFCT macros
        detected_items: List[DetectedItemNutrition] = []
        for idx, item in enumerate(cv_items):
            dish_id = item.get("predicted_dish_id") or item.get("dish_id") or "jollof_rice"
            item_id = item.get("item_id") or f"item_{idx + 1}"
            confidence = float(item.get("confidence", 0.90))
            bbox = item.get("bounding_box")

            portion_data = self.rag_client.get_dish_portion_units(dish_id)
            nutrient_data = self.rag_client.get_dish_base_nutrients(dish_id)

            display_name = item.get("display_name") or portion_data.get("dish_name") or dish_id.replace("_", " ").title()
            default_unit_id = portion_data.get("default_unit_id", "serving_spoon")
            default_qty = float(portion_data.get("default_quantity", 1.0))

            units = [
                PortionUnitInfo(
                    unit_id=u["unit_id"],
                    unit_name=u["unit_name"],
                    gram_weight=float(u["gram_weight"]),
                    description=u.get("description", ""),
                )
                for u in portion_data.get("units", [])
            ]

            default_unit_g = next((u.gram_weight for u in units if u.unit_id == default_unit_id), 100.0)

            n100 = nutrient_data.get("nutrients_per_100g", {})
            nutrients = NutrientProfile100g(
                calories_kcal=float(n100.get("calories_kcal", 0.0)),
                protein_g=float(n100.get("protein_g", 0.0)),
                fat_g=float(n100.get("fat_g", 0.0)),
                carbs_g=float(n100.get("carbs_g", 0.0)),
                fiber_g=float(n100.get("fiber_g", 0.0)),
                sodium_mg=float(n100.get("sodium_mg", 0.0)),
                calcium_mg=float(n100.get("calcium_mg", 0.0)),
                iron_mg=float(n100.get("iron_mg", 0.0)),
            )

            detected_items.append(
                DetectedItemNutrition(
                    item_id=item_id,
                    predicted_dish_id=dish_id,
                    display_name=display_name,
                    confidence=confidence,
                    bounding_box=bbox,
                    default_unit_id=default_unit_id,
                    default_quantity=default_qty,
                    default_weight_g=round(default_unit_g * default_qty, 1),
                    available_portion_units=units,
                    nutrients_per_100g=nutrients,
                    wafct_code=nutrient_data.get("wafct_code", "00_COMPOSITE"),
                )
            )

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 1)

        return AnalyzeMealResponse(
            analysis_id=analysis_id,
            status="success",
            processing_duration_ms=duration_ms,
            image_url=effective_image_url,
            detected_items=detected_items,
        )

    # Aliases for backward compatibility
    async def analyze_image_file(self, file: UploadFile, prompt: Optional[str] = None):
        return await self.analyze(file=file, prompt=prompt)

    async def analyze_image_url(self, image_url: Optional[str] = None, image_base64: Optional[str] = None, prompt: Optional[str] = None):
        return await self.analyze(image_url=image_url, image_base64=image_base64, prompt=prompt)


_orchestrator: Optional[OrchestratorService] = None


def get_orchestrator_service() -> OrchestratorService:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorService()
    return _orchestrator
