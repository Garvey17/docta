"""User Dashboard and Macro Analytics API Endpoints using Supabase."""

from datetime import datetime, timezone, date, time
from typing import Optional, List
from fastapi import APIRouter, Depends

from ..supabase_client import get_supabase_client
from ..schemas.auth import UserResponse
from ..schemas.dashboard import (
    DashboardStatsResponse,
    DailyMacroSummary,
    MacroTarget,
)
from ..schemas.meal import MealDetailResponse, MealItemResponse
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Analytics"])


@router.get("/summary", response_model=DashboardStatsResponse, summary="Get today's macro summary")
@router.get("", response_model=DashboardStatsResponse, summary="Get today's macro summary (alias)")
async def get_dashboard_summary(
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve today's nutritional intake summary and progress toward dietary targets."""
    supabase = get_supabase_client()
    user_id = current_user.id

    today = date.today()
    start_of_day = datetime.combine(today, time.min).replace(tzinfo=timezone.utc).isoformat()
    end_of_day = datetime.combine(today, time.max).replace(tzinfo=timezone.utc).isoformat()

    # Query today's meals
    query = (
        supabase.from_("meals")
        .select("*")
        .gte("logged_at", start_of_day)
        .lte("logged_at", end_of_day)
        .eq("user_id", user_id)
    )

    res = query.execute()
    today_meals = res.data or []

    cal = sum(float(m.get("total_calories_kcal", 0.0)) for m in today_meals)
    pro = sum(float(m.get("total_protein_g", 0.0)) for m in today_meals)
    fat = sum(float(m.get("total_fat_g", 0.0)) for m in today_meals)
    carb = sum(float(m.get("total_carbs_g", 0.0)) for m in today_meals)
    fib = sum(float(m.get("total_fiber_g", 0.0)) for m in today_meals)
    sod = sum(float(m.get("total_sodium_mg", 0.0)) for m in today_meals)
    calc = sum(float(m.get("total_calcium_mg", 0.0)) for m in today_meals)
    iron = sum(float(m.get("total_iron_mg", 0.0)) for m in today_meals)

    today_summary = DailyMacroSummary(
        summary_date=today,
        meal_count=len(today_meals),
        total_calories_kcal=round(cal, 1),
        total_protein_g=round(pro, 1),
        total_fat_g=round(fat, 1),
        total_carbs_g=round(carb, 1),
        total_fiber_g=round(fib, 1),
        total_sodium_mg=round(sod, 1),
        total_calcium_mg=round(calc, 1),
        total_iron_mg=round(iron, 1),
    )

    # User's targets
    target_cal = float(current_user.dailyCalorieTarget) if current_user else 2200.0
    target_pro = float(current_user.dailyProteinTargetG) if current_user else 110.0
    target_carb = float(current_user.dailyCarbsTargetG) if current_user else 250.0
    target_fat = float(current_user.dailyFatTargetG) if current_user else 65.0
    target_fib = float(current_user.dailyFiberTargetG) if current_user else 30.0

    targets = MacroTarget(
        target_calories_kcal=target_cal,
        target_protein_g=target_pro,
        target_fat_g=target_fat,
        target_carbs_g=target_carb,
        target_fiber_g=target_fib,
    )

    cal_pct = round((cal / target_cal) * 100, 1) if target_cal > 0 else 0.0
    pro_pct = round((pro / target_pro) * 100, 1) if target_pro > 0 else 0.0
    carb_pct = round((carb / target_carb) * 100, 1) if target_carb > 0 else 0.0
    fat_pct = round((fat / target_fat) * 100, 1) if target_fat > 0 else 0.0

    # Recent meals (last 5)
    recent_res = (
        supabase.from_("meals")
        .select("*")
        .eq("user_id", user_id)
        .order("logged_at", desc=True)
        .limit(5)
        .execute()
    )
    recent_raw = recent_res.data or []

    recent_meals: List[MealDetailResponse] = []
    for m in recent_raw:
        m_id = str(m["id"])
        items_res = supabase.from_("meal_items").select("*").eq("meal_id", m_id).execute()
        item_rows = [MealItemResponse(**i) for i in (items_res.data or [])]
        recent_meals.append(
            MealDetailResponse(
                id=m_id,
                meal_id=m_id,
                user_id=str(m.get("user_id")),
                image_url=m.get("image_url"),
                meal_type=m.get("meal_type", "lunch"),
                notes=m.get("notes"),
                logged_at=m.get("logged_at"),
                created_at=m.get("created_at"),
                total_calories_kcal=float(m.get("total_calories_kcal", 0.0)),
                total_protein_g=float(m.get("total_protein_g", 0.0)),
                total_fat_g=float(m.get("total_fat_g", 0.0)),
                total_carbs_g=float(m.get("total_carbs_g", 0.0)),
                total_fiber_g=float(m.get("total_fiber_g", 0.0)),
                total_sodium_mg=float(m.get("total_sodium_mg", 0.0)),
                total_calcium_mg=float(m.get("total_calcium_mg", 0.0)),
                total_iron_mg=float(m.get("total_iron_mg", 0.0)),
                items=item_rows,
                items_logged=len(item_rows),
            )
        )

    return DashboardStatsResponse(
        today=today_summary,
        targets=targets,
        calorie_progress_pct=cal_pct,
        protein_progress_pct=pro_pct,
        carbs_progress_pct=carb_pct,
        fat_progress_pct=fat_pct,
        recent_meals=recent_meals,
    )
