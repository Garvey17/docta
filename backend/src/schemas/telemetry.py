"""Pydantic v2 schemas for Active Learning Telemetry and ML dataset export."""

import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict


class TelemetryRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    meal_id: Optional[uuid.UUID] = None
    meal_item_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None
    predicted_dish_id: str
    predicted_confidence: float
    bounding_box: Optional[List[float]] = None
    final_dish_id: str
    label_modified: bool
    selected_unit_id: str
    selected_quantity: float
    calculated_gram_weight: float
    custom_weight_entered_g: Optional[float] = None
    logged_at: datetime


class TelemetryExportResponse(BaseModel):
    total_records: int
    exported_at: datetime
    records: List[TelemetryRecord]


class TelemetryStatsResponse(BaseModel):
    total_decisions_logged: int
    total_label_modifications: int
    modification_rate: float
    top_predicted_dishes: Dict[str, int]
    top_final_dishes: Dict[str, int]
    top_portion_units: Dict[str, int]
