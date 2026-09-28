"""User Profile and Settings API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from ..supabase_client import get_supabase_client
from ..schemas.auth import UserResponse
from ..schemas.profile import ProfileResponse, ProfileUpdateRequest
from ..dependencies.auth import get_current_user_optional, get_current_user

router = APIRouter(prefix="/api/v1/profile", tags=["Profile & Settings"])


@router.get("", response_model=ProfileResponse, summary="Get user profile and dietary targets")
async def get_profile(
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Retrieve authenticated user's profile and nutritional targets."""
    if not current_user:
        return ProfileResponse(
            id="usr_4a89fb21",
            email="balkisu@docta.ng",
            name="Balkisu Habib",
            dailyCalorieTarget=2200,
            dailyProteinTargetG=110.0,
            dailyCarbsTargetG=250.0,
            dailyFatTargetG=65.0,
            dailyFiberTargetG=30.0,
            dailySodiumTargetMg=2300.0,
        )

    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        dailyCalorieTarget=current_user.dailyCalorieTarget,
        dailyProteinTargetG=current_user.dailyProteinTargetG,
        dailyCarbsTargetG=current_user.dailyCarbsTargetG,
        dailyFatTargetG=current_user.dailyFatTargetG,
        dailyFiberTargetG=current_user.dailyFiberTargetG,
        dailySodiumTargetMg=current_user.dailySodiumTargetMg,
    )


@router.patch("", response_model=ProfileResponse, summary="Update user profile and targets")
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Update user's profile fields and macro targets in Supabase."""
    supabase = get_supabase_client()
    update_data = {}

    if payload.name is not None:
        update_data["name"] = payload.name
    if payload.dailyCalorieTarget is not None:
        update_data["daily_calorie_target"] = payload.dailyCalorieTarget
    if payload.dailyProteinTargetG is not None:
        update_data["daily_protein_target_g"] = payload.dailyProteinTargetG
    if payload.dailyCarbsTargetG is not None:
        update_data["daily_carbs_target_g"] = payload.dailyCarbsTargetG
    if payload.dailyFatTargetG is not None:
        update_data["daily_fat_target_g"] = payload.dailyFatTargetG
    if payload.dailyFiberTargetG is not None:
        update_data["daily_fiber_target_g"] = payload.dailyFiberTargetG
    if payload.dailySodiumTargetMg is not None:
        update_data["daily_sodium_target_mg"] = payload.dailySodiumTargetMg

    if update_data:
        try:
            supabase.from_("user_profiles").update(update_data).eq("id", current_user.id).execute()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed updating profile: {str(e)}",
            )

    # Re-fetch profile
    res = supabase.from_("user_profiles").select("*").eq("id", current_user.id).execute()
    data = res.data[0] if (res.data and isinstance(res.data, list)) else (res.data or {})

    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        name=data.get("name") or payload.name or current_user.name,
        dailyCalorieTarget=data.get("daily_calorie_target") or payload.dailyCalorieTarget or current_user.dailyCalorieTarget,
        dailyProteinTargetG=float(data.get("daily_protein_target_g") or payload.dailyProteinTargetG or current_user.dailyProteinTargetG),
        dailyCarbsTargetG=float(data.get("daily_carbs_target_g") or payload.dailyCarbsTargetG or current_user.dailyCarbsTargetG),
        dailyFatTargetG=float(data.get("daily_fat_target_g") or payload.dailyFatTargetG or current_user.dailyFatTargetG),
        dailyFiberTargetG=float(data.get("daily_fiber_target_g") or payload.dailyFiberTargetG or current_user.dailyFiberTargetG),
        dailySodiumTargetMg=float(data.get("daily_sodium_target_mg") or payload.dailySodiumTargetMg or current_user.dailySodiumTargetMg),
    )
