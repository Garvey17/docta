"""Pydantic v2 schemas for User Dashboard and Analytics."""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from .meal import MealDetailResponse


class MacroTarget(BaseModel):
    target_calories_kcal: float = 2200.0
    target_protein_g: float = 75.0
    target_fat_g: float = 70.0
    target_carbs_g: float = 300.0
    target_fiber_g: float = 30.0


class DailyMacroSummary(BaseModel):
    summary_date: date
    meal_count: int
    total_calories_kcal: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    total_fiber_g: float
    total_sodium_mg: float
    total_calcium_mg: float
    total_iron_mg: float


class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    today: DailyMacroSummary
    targets: MacroTarget
    calorie_progress_pct: float
    protein_progress_pct: float
    carbs_progress_pct: float
    fat_progress_pct: float
    recent_meals: List[MealDetailResponse] = []
