"""Pydantic v2 schemas for Meal Logging, History, and Retrieval."""

import uuid
from datetime import datetime
from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, ConfigDict, model_validator


class LogMealItemInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    item_id: Optional[str] = None
    food_name: str
    predicted_dish_id: str
    final_dish_id: str
    label_modified: bool = False
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bounding_box: Optional[List[float]] = None

    selected_unit_id: str
    selected_quantity: float = Field(default=1.0, gt=0.0)
    gram_weight: float = Field(..., gt=0.0)
    custom_weight_entered_g: Optional[float] = None

    calories_kcal: float = 0.0
    protein_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0
    fiber_g: float = 0.0
    sodium_mg: float = 0.0
    calcium_mg: float = 0.0
    iron_mg: float = 0.0


class LogMealRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    analysis_id: Optional[str] = None
    image_url: Optional[str] = None
    meal_type: str = Field(default="lunch", description="breakfast, lunch, dinner, snack")
    notes: Optional[str] = None
    logged_at: Optional[Union[datetime, str]] = None
    items: List[LogMealItemInput] = Field(..., min_length=1)


class MealItemResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: Optional[str] = None
    meal_id: Optional[str] = None
    item_id: Optional[str] = None
    food_name: str
    predicted_dish_id: str
    final_dish_id: str
    label_modified: bool = False
    confidence: float = 1.0
    bounding_box: Optional[List[float]] = None
    selected_unit_id: Optional[str] = None
    selected_quantity: Optional[float] = None
    gram_weight: float
    calories_kcal: float = 0.0
    protein_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0
    fiber_g: float = 0.0
    sodium_mg: float = 0.0
    calcium_mg: float = 0.0
    iron_mg: float = 0.0

    @model_validator(mode="before")
    @classmethod
    def serialize_ids(cls, data: Any):
        if isinstance(data, dict):
            mapped = dict(data)
            if "id" in mapped and mapped["id"] is not None:
                mapped["id"] = str(mapped["id"])
            if "meal_id" in mapped and mapped["meal_id"] is not None:
                mapped["meal_id"] = str(mapped["meal_id"])
            return mapped
        return data


class MealDetailResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: str
    meal_id: Optional[str] = None
    user_id: Optional[str] = None
    image_url: Optional[str] = None
    meal_type: str = "lunch"
    notes: Optional[str] = None
    logged_at: Union[datetime, str]
    created_at: Optional[Union[datetime, str]] = None

    total_calories_kcal: float = 0.0
    total_protein_g: float = 0.0
    total_fat_g: float = 0.0
    total_carbs_g: float = 0.0
    total_fiber_g: float = 0.0
    total_sodium_mg: float = 0.0
    total_calcium_mg: float = 0.0
    total_iron_mg: float = 0.0

    items: List[MealItemResponse] = Field(default_factory=list)

    # Response metadata for frontend compatibility
    status: str = "success"
    items_logged: Optional[int] = None
    feedback_telemetry_recorded: bool = True
    message: str = "Meal and decision telemetry successfully recorded."

    @model_validator(mode="before")
    @classmethod
    def ensure_meal_id(cls, data: Any):
        if isinstance(data, dict):
            mapped = dict(data)
            if "id" in mapped and mapped["id"] is not None:
                mapped["id"] = str(mapped["id"])
                if not mapped.get("meal_id"):
                    mapped["meal_id"] = mapped["id"]
            if "user_id" in mapped and mapped["user_id"] is not None:
                mapped["user_id"] = str(mapped["user_id"])
            if "items" in mapped and mapped.get("items_logged") is None:
                mapped["items_logged"] = len(mapped["items"])
            return mapped
        return data


class HistoryItemDetail(BaseModel):
    food_name: str
    unit_name: Optional[str] = "Standard Portion"
    quantity: float = 1.0
    gram_weight: float = 100.0
    calories_kcal: float = 0.0


class MealHistoryItemResponse(BaseModel):
    meal_id: str
    meal_type: str = "lunch"
    logged_at: str
    total_calories_kcal: float = 0.0
    total_protein_g: float = 0.0
    total_carbs_g: float = 0.0
    total_fat_g: float = 0.0
    items: List[HistoryItemDetail] = Field(default_factory=list)


class MealSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: str
    meal_type: str = "lunch"
    logged_at: Union[datetime, str]
    image_url: Optional[str] = None
    item_count: int = 0
    total_calories_kcal: float = 0.0
    total_protein_g: float = 0.0
    total_fat_g: float = 0.0
    total_carbs_g: float = 0.0


class MealListResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    meals: List[MealDetailResponse]

