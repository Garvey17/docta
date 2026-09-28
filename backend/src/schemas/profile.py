"""Pydantic schemas for User Profile and Dietary Target Settings."""

from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, model_validator


class ProfileResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: str
    email: str
    name: Optional[str] = None
    dailyCalorieTarget: int = 2200
    dailyProteinTargetG: float = 110.0
    dailyCarbsTargetG: float = 250.0
    dailyFatTargetG: float = 65.0
    dailyFiberTargetG: float = 30.0
    dailySodiumTargetMg: float = 2300.0

    @model_validator(mode="before")
    @classmethod
    def map_profile_fields(cls, data: Any):
        if isinstance(data, dict):
            mapped = dict(data)
            if "daily_calorie_target" in mapped and "dailyCalorieTarget" not in mapped:
                mapped["dailyCalorieTarget"] = mapped["daily_calorie_target"]
            if "daily_protein_target_g" in mapped and "dailyProteinTargetG" not in mapped:
                mapped["dailyProteinTargetG"] = float(mapped["daily_protein_target_g"])
            if "daily_carbs_target_g" in mapped and "dailyCarbsTargetG" not in mapped:
                mapped["dailyCarbsTargetG"] = float(mapped["daily_carbs_target_g"])
            if "daily_fat_target_g" in mapped and "dailyFatTargetG" not in mapped:
                mapped["dailyFatTargetG"] = float(mapped["daily_fat_target_g"])
            if "daily_fiber_target_g" in mapped and "dailyFiberTargetG" not in mapped:
                mapped["dailyFiberTargetG"] = float(mapped["daily_fiber_target_g"])
            if "daily_sodium_target_mg" in mapped and "dailySodiumTargetMg" not in mapped:
                mapped["dailySodiumTargetMg"] = float(mapped["daily_sodium_target_mg"])
            if "full_name" in mapped and not mapped.get("name"):
                mapped["name"] = mapped["full_name"]
            if "id" in mapped:
                mapped["id"] = str(mapped["id"])
            return mapped
        return data


class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = None
    dailyCalorieTarget: Optional[int] = None
    dailyProteinTargetG: Optional[float] = None
    dailyCarbsTargetG: Optional[float] = None
    dailyFatTargetG: Optional[float] = None
    dailyFiberTargetG: Optional[float] = None
    dailySodiumTargetMg: Optional[float] = None
