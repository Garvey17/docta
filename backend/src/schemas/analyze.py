"""Pydantic v2 schemas for Vision + RAG Analysis Endpoint."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PortionUnitInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    unit_id: str
    unit_name: str
    gram_weight: float
    description: str = ""


class NutrientProfile100g(BaseModel):
    model_config = ConfigDict(extra="ignore")

    calories_kcal: float = 0.0
    protein_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0
    fiber_g: float = 0.0
    sodium_mg: float = 0.0
    calcium_mg: float = 0.0
    iron_mg: float = 0.0


class DetectedItemNutrition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    item_id: str
    predicted_dish_id: str
    display_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bounding_box: Optional[List[float]] = None  # [x_min, y_min, x_max, y_max] normalized 0-1
    default_unit_id: str
    default_quantity: float = 1.0
    default_weight_g: float = 100.0
    available_portion_units: List[PortionUnitInfo] = Field(default_factory=list)
    nutrients_per_100g: NutrientProfile100g = Field(default_factory=NutrientProfile100g)
    wafct_code: Optional[str] = "00_COMPOSITE"


class AnalyzeImageURLRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    prompt: Optional[str] = None


class AnalyzeMealResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    analysis_id: str
    status: str = "success"
    processing_duration_ms: float
    image_url: Optional[str] = None
    detected_items: List[DetectedItemNutrition] = Field(default_factory=list)
