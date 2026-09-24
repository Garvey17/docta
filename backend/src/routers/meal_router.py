"""Meal Logging, Retrieval, and Active Learning Telemetry API Endpoints."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.user import User
from ..models.meal import Meal
from ..models.meal_item import MealItem
from ..models.meal_item_feedback_log import MealItemFeedbackLog
from ..schemas.meal import (
    LogMealRequest,
    MealDetailResponse,
    MealListResponse,
)
from ..services.auth_service import get_current_user, get_current_user_optional
from ..services.telemetry_service import TelemetryService

router = APIRouter(prefix="/api/v1/meals", tags=["Meals & Logging"])


@router.post(
    "/log",
    response_model=MealDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log approved meal and persist active learning telemetry",
)
async def log_meal(
    payload: LogMealRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Log an approved meal with atomic decision telemetry:
    1. Aggregates total macros across selected items.
    2. Inserts parent `Meal` record.
    3. Inserts children `MealItem` records with chosen units and grams.
    4. Simultaneously writes each decision to `meal_item_feedback_logs` (the ML portion-training dataset).
    """
    # 1. Determine user ID (use current_user if authenticated, or create / use anonymous user)
    user_id = current_user.id if current_user else None

    # If no authenticated user, find or create default demo user
    if user_id is None:
        demo_user_res = await db.execute(select(User).where(User.email == "guest@docta.ng"))
        demo_user = demo_user_res.scalar_one_or_none()
        if not demo_user:
            demo_user = User(
                id=uuid.uuid4(),
                email="guest@docta.ng",
                hashed_password="demo_guest_account",
                full_name="Guest User",
                is_active=True,
            )
            db.add(demo_user)
            await db.flush()
        user_id = demo_user.id

    # 2. Aggregate Nutritional Totals
    total_cal = sum(item.calories_kcal for item in payload.items)
    total_pro = sum(item.protein_g for item in payload.items)
    total_fat = sum(item.fat_g for item in payload.items)
    total_carb = sum(item.carbs_g for item in payload.items)
    total_fib = sum(item.fiber_g for item in payload.items)
    total_sod = sum(item.sodium_mg for item in payload.items)
    total_calc = sum(item.calcium_mg for item in payload.items)
    total_iron = sum(item.iron_mg for item in payload.items)

    logged_time = payload.logged_at or datetime.now(timezone.utc)

    # 3. Create Meal Record
    meal = Meal(
        id=uuid.uuid4(),
        user_id=user_id,
        image_url=payload.image_url,
        meal_type=payload.meal_type,
        notes=payload.notes,
        logged_at=logged_time,
        created_at=datetime.now(timezone.utc),
        total_calories_kcal=round(total_cal, 2),
        total_protein_g=round(total_pro, 2),
        total_fat_g=round(total_fat, 2),
        total_carbs_g=round(total_carb, 2),
        total_fiber_g=round(total_fib, 2),
        total_sodium_mg=round(total_sod, 2),
        total_calcium_mg=round(total_calc, 2),
        total_iron_mg=round(total_iron, 2),
    )
    db.add(meal)
    await db.flush()

    # 4. Insert Meal Items & Decision Telemetry Logs Atomically
    for item_input in payload.items:
        meal_item = MealItem(
            id=uuid.uuid4(),
            meal_id=meal.id,
            item_id=item_input.item_id,
            food_name=item_input.food_name,
            predicted_dish_id=item_input.predicted_dish_id,
            final_dish_id=item_input.final_dish_id,
            label_modified=item_input.label_modified or (item_input.predicted_dish_id != item_input.final_dish_id),
            confidence=item_input.confidence,
            bounding_box=item_input.bounding_box,
            selected_unit_id=item_input.selected_unit_id,
            selected_quantity=item_input.selected_quantity,
            gram_weight=item_input.gram_weight,
            calories_kcal=item_input.calories_kcal,
            protein_g=item_input.protein_g,
            fat_g=item_input.fat_g,
            carbs_g=item_input.carbs_g,
            fiber_g=item_input.fiber_g,
            sodium_mg=item_input.sodium_mg,
            calcium_mg=item_input.calcium_mg,
            iron_mg=item_input.iron_mg,
        )
        db.add(meal_item)
        await db.flush()

        # Telemetry: Log Everything
        await TelemetryService.log_item_decision(
            db=db,
            user_id=user_id,
            meal_id=meal.id,
            item=item_input,
            saved_meal_item_id=meal_item.id,
            image_url=payload.image_url,
        )

    # 5. Commit transaction atomically
    await db.commit()

    # 6. Reload meal with items for response
    result = await db.execute(
        select(Meal).where(Meal.id == meal.id).options(selectinload(Meal.items))
    )
    saved_meal = result.scalar_one()
    return saved_meal


@router.get("", response_model=MealListResponse)
async def list_meals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve logged meals for current user or all meals."""
    offset = (page - 1) * page_size
    query = select(Meal).options(selectinload(Meal.items))
    count_query = select(func.count(Meal.id))

    if current_user:
        query = query.where(Meal.user_id == current_user.id)
        count_query = count_query.where(Meal.user_id == current_user.id)

    total_res = await db.execute(count_query)
    total_count = total_res.scalar() or 0

    query = query.order_by(desc(Meal.logged_at)).offset(offset).limit(page_size)
    results = await db.execute(query)
    meals = results.scalars().all()

    return MealListResponse(
        total_count=total_count,
        page=page,
        page_size=page_size,
        meals=list(meals),
    )


@router.get("/{meal_id}", response_model=MealDetailResponse)
async def get_meal(
    meal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a single meal by ID with its constituent items."""
    result = await db.execute(
        select(Meal).where(Meal.id == meal_id).options(selectinload(Meal.items))
    )
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal(
    meal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a logged meal."""
    result = await db.execute(select(Meal).where(Meal.id == meal_id))
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")

    await db.delete(meal)
    await db.commit()
    return None
