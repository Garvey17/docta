"""Pydantic schemas registry."""

from .auth import UserRegister, UserLogin, Token, TokenData, UserResponse
from .analyze import (
    PortionUnitInfo,
    NutrientProfile100g,
    DetectedItemNutrition,
    AnalyzeImageURLRequest,
    AnalyzeMealResponse,
)
from .meal import (
    LogMealItemInput,
    LogMealRequest,
    MealItemResponse,
    MealDetailResponse,
    MealSummaryResponse,
    MealListResponse,
)
from .telemetry import (
    TelemetryRecord,
    TelemetryExportResponse,
    TelemetryStatsResponse,
)
from .dashboard import (
    MacroTarget,
    DailyMacroSummary,
    DashboardStatsResponse,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenData",
    "UserResponse",
    "PortionUnitInfo",
    "NutrientProfile100g",
    "DetectedItemNutrition",
    "AnalyzeImageURLRequest",
    "AnalyzeMealResponse",
    "LogMealItemInput",
    "LogMealRequest",
    "MealItemResponse",
    "MealDetailResponse",
    "MealSummaryResponse",
    "MealListResponse",
    "TelemetryRecord",
    "TelemetryExportResponse",
    "TelemetryStatsResponse",
    "MacroTarget",
    "DailyMacroSummary",
    "DashboardStatsResponse",
]
