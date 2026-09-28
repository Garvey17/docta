"""Pydantic v2 schemas for Active Learning Telemetry and ML dataset export."""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, ConfigDict, model_validator


class TelemetryRecord(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: str
    user_id: Optional[str] = None
    meal_id: Optional[str] = None
    meal_item_id: Optional[str] = None
    image_url: Optional[str] = None
    predicted_dish_id: str
    predicted_confidence: float = 1.0
    bounding_box: Optional[List[float]] = None
    final_dish_id: str
    label_modified: bool = False
    selected_unit_id: str
    selected_quantity: float = 1.0
    calculated_gram_weight: float
    custom_weight_entered_g: Optional[float] = None
    logged_at: Union[datetime, str]

    @model_validator(mode="before")
    @classmethod
    def serialize_fields(cls, data: Any):
        if isinstance(data, dict):
            mapped = dict(data)
            for k in ["id", "user_id", "meal_id", "meal_item_id"]:
                if k in mapped and mapped[k] is not None:
                    mapped[k] = str(mapped[k])
            return mapped
        return data


class TelemetryExportResponse(BaseModel):
    total_records: int
    exported_at: Union[datetime, str]
    records: List[TelemetryRecord]


class TelemetryStatsResponse(BaseModel):
    total_decisions_logged: int
    total_label_modifications: int
    modification_rate: float
    top_predicted_dishes: Dict[str, int]
    top_final_dishes: Dict[str, int]
    top_portion_units: Dict[str, int]
