"""User Dashboard and Macro Analytics API Endpoints."""

from datetime import datetime, timezone, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.user import User
from ..models.meal import Meal
from ..schemas.dashboard import (
    DashboardStatsResponse,
    DailyMacroSummary,
    MacroTarget,
)
from ..schemas.meal import MealDetailResponse
from ..services.auth_service import get_current_user_optional

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Analytics"])


@router.get("/summary", response_model=DashboardStatsResponse)
async def get_dashboard_summary(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve today's nutritional intake summary and progress toward dietary targets."""
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)

    query = select(Meal).where(
        Meal.logged_at >= start_of_day,
        Meal.logged_at <= end_of_day,
    ).options(selectinload(Meal.items))

    if current_user:
        query = query.where(Meal.user_id == current_user.id)

    res = await db.execute(query)
    today_meals = res.scalars().all()

    cal = sum(m.total_calories_kcal for m in today_meals)
    pro = sum(m.total_protein_g for m in today_meals)
    fat = sum(m.total_fat_g for m in today_meals)
    carb = sum(m.total_carbs_g for m in today_meals)
    fib = sum(m.total_fiber_g for m in today_meals)
    sod = sum(m.total_sodium_mg for m in today_meals)
    calc = sum(m.total_calcium_mg for m in today_meals)
    iron = sum(m.total_iron_mg for m in today_meals)

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

    targets = MacroTarget()

    cal_pct = round((cal / targets.target_calories_kcal) * 100, 1) if targets.target_calories_kcal > 0 else 0.0
    pro_pct = round((pro / targets.target_protein_g) * 100, 1) if targets.target_protein_g > 0 else 0.0
    carb_pct = round((carb / targets.target_carbs_g) * 100, 1) if targets.target_carbs_g > 0 else 0.0
    fat_pct = round((fat / targets.target_fat_g) * 100, 1) if targets.target_fat_g > 0 else 0.0

    # Recent meals (last 5)
    recent_q = select(Meal).options(selectinload(Meal.items))
    if current_user:
        recent_q = recent_q.where(Meal.user_id == current_user.id)
    recent_q = recent_q.order_by(desc(Meal.logged_at)).limit(5)
    recent_res = await db.execute(recent_q)
    recent_meals = [MealDetailResponse.model_validate(m) for m in recent_res.scalars().all()]

    return DashboardStatsResponse(
        today=today_summary,
        targets=targets,
        calorie_progress_pct=cal_pct,
        protein_progress_pct=pro_pct,
        carbs_progress_pct=carb_pct,
        fat_progress_pct=fat_pct,
        recent_meals=recent_meals,
    )
