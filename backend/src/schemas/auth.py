"""Authentication and User Pydantic Schemas."""

import uuid
from typing import Optional, Union, Any, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


class UserRegister(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: str
    password: str = Field(..., min_length=6)
    name: Optional[str] = None
    full_name: Optional[str] = None

    @model_validator(mode="after")
    def unify_names(self):
        if not self.name and self.full_name:
            self.name = self.full_name
        if not self.full_name and self.name:
            self.full_name = self.name
        return self


class UserLogin(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: str
    email: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

    # Nutritional Targets (CamelCase to match frontend expectations)
    dailyCalorieTarget: int = 2200
    dailyProteinTargetG: float = 110.0
    dailyCarbsTargetG: float = 250.0
    dailyFatTargetG: float = 65.0
    dailyFiberTargetG: float = 30.0
    dailySodiumTargetMg: float = 2300.0

    @model_validator(mode="before")
    @classmethod
    def map_fields(cls, data: Any):
        if isinstance(data, dict):
            mapped = dict(data)
            if "full_name" in mapped and not mapped.get("name"):
                mapped["name"] = mapped["full_name"]
            if "name" in mapped and not mapped.get("full_name"):
                mapped["full_name"] = mapped["name"]
            if "id" in mapped:
                mapped["id"] = str(mapped["id"])
            return mapped
        return data


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 604800
    refresh_token: Optional[str] = None
    user: Optional[UserResponse] = None


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    is_admin: bool = False
