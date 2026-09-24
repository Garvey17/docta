"""Pydantic v2 schemas for Meal Logging and Retrieval."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


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
    logged_at: Optional[datetime] = None
    items: List[LogMealItemInput] = Field(..., min_length=1)


class MealItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    item_id: Optional[str] = None
    food_name: str
    predicted_dish_id: str
    final_dish_id: str
    label_modified: bool
    confidence: float
    bounding_box: Optional[List[float]] = None
    selected_unit_id: Optional[str] = None
    selected_quantity: Optional[float] = None
    gram_weight: float
    calories_kcal: float
    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: float
    sodium_mg: float
    calcium_mg: float
    iron_mg: float


class MealDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    image_url: Optional[str] = None
    meal_type: str
    notes: Optional[str] = None
    logged_at: datetime
    created_at: datetime

    total_calories_kcal: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    total_fiber_g: float
    total_sodium_mg: float
    total_calcium_mg: float
    total_iron_mg: float

    items: List[MealItemResponse] = Field(default_factory=list)


class MealSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meal_type: str
    logged_at: datetime
    image_url: Optional[str] = None
    item_count: int
    total_calories_kcal: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float


class MealListResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    meals: List[MealDetailResponse]
