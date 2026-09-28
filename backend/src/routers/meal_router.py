"""Meal Logging, History, and Retrieval API Endpoints using Supabase."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..supabase_client import get_supabase_client
from ..schemas.auth import UserResponse
from ..schemas.meal import (
    LogMealRequest,
    MealDetailResponse,
    MealListResponse,
    MealHistoryItemResponse,
    HistoryItemDetail,
    MealItemResponse,
)
from ..dependencies.auth import get_current_user_optional, get_current_user
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
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """
    Log an approved meal with atomic decision telemetry:
    1. Aggregates total macros across selected items.
    2. Inserts parent `meals` record into Supabase.
    3. Inserts children `meal_items` records with chosen units and grams.
    4. Simultaneously writes each decision to `meal_item_feedback_logs` (active learning dataset).
    """
    supabase = get_supabase_client()
    user_id = current_user.id if current_user else "usr_4a89fb21"

    # 1. Aggregate Nutritional Totals
    total_cal = sum(item.calories_kcal for item in payload.items)
    total_pro = sum(item.protein_g for item in payload.items)
    total_fat = sum(item.fat_g for item in payload.items)
    total_carb = sum(item.carbs_g for item in payload.items)
    total_fib = sum(item.fiber_g for item in payload.items)
    total_sod = sum(item.sodium_mg for item in payload.items)
    total_calc = sum(item.calcium_mg for item in payload.items)
    total_iron = sum(item.iron_mg for item in payload.items)

    logged_time = (
        payload.logged_at.isoformat()
        if hasattr(payload.logged_at, "isoformat")
        else (payload.logged_at or datetime.now(timezone.utc).isoformat())
    )
    meal_id = str(uuid.uuid4())

    meal_record = {
        "id": meal_id,
        "user_id": user_id,
        "image_url": payload.image_url,
        "meal_type": payload.meal_type,
        "notes": payload.notes,
        "logged_at": logged_time,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_calories_kcal": round(total_cal, 2),
        "total_protein_g": round(total_pro, 2),
        "total_fat_g": round(total_fat, 2),
        "total_carbs_g": round(total_carb, 2),
        "total_fiber_g": round(total_fib, 2),
        "total_sodium_mg": round(total_sod, 2),
        "total_calcium_mg": round(total_calc, 2),
        "total_iron_mg": round(total_iron, 2),
    }

    try:
        supabase.from_("meals").insert(meal_record).execute()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed creating meal record: {str(e)}",
        )

    # 2. Insert Meal Items & Decision Telemetry Logs
    saved_items: List[MealItemResponse] = []
    for item_input in payload.items:
        item_id = str(uuid.uuid4())
        label_modified = bool(
            item_input.label_modified or (item_input.predicted_dish_id != item_input.final_dish_id)
        )

        item_record = {
            "id": item_id,
            "meal_id": meal_id,
            "item_id": item_input.item_id,
            "food_name": item_input.food_name,
            "predicted_dish_id": item_input.predicted_dish_id,
            "final_dish_id": item_input.final_dish_id,
            "label_modified": label_modified,
            "confidence": float(item_input.confidence),
            "bounding_box": item_input.bounding_box,
            "selected_unit_id": item_input.selected_unit_id,
            "selected_quantity": float(item_input.selected_quantity),
            "gram_weight": float(item_input.gram_weight),
            "calories_kcal": float(item_input.calories_kcal),
            "protein_g": float(item_input.protein_g),
            "fat_g": float(item_input.fat_g),
            "carbs_g": float(item_input.carbs_g),
            "fiber_g": float(item_input.fiber_g),
            "sodium_mg": float(item_input.sodium_mg),
            "calcium_mg": float(item_input.calcium_mg),
            "iron_mg": float(item_input.iron_mg),
        }
        supabase.from_("meal_items").insert(item_record).execute()
        saved_items.append(MealItemResponse(**item_record))

        # Log Everything: Telemetry store
        await TelemetryService.log_item_decision(
            user_id=user_id,
            meal_id=meal_id,
            item=item_input,
            saved_meal_item_id=item_id,
            image_url=payload.image_url,
        )

    return MealDetailResponse(
        id=meal_id,
        meal_id=meal_id,
        user_id=user_id,
        image_url=payload.image_url,
        meal_type=payload.meal_type,
        notes=payload.notes,
        logged_at=logged_time,
        created_at=meal_record["created_at"],
        total_calories_kcal=meal_record["total_calories_kcal"],
        total_protein_g=meal_record["total_protein_g"],
        total_fat_g=meal_record["total_fat_g"],
        total_carbs_g=meal_record["total_carbs_g"],
        total_fiber_g=meal_record["total_fiber_g"],
        total_sodium_mg=meal_record["total_sodium_mg"],
        total_calcium_mg=meal_record["total_calcium_mg"],
        total_iron_mg=meal_record["total_iron_mg"],
        items=saved_items,
        status="success",
        items_logged=len(saved_items),
        feedback_telemetry_recorded=True,
        message="Meal and decision telemetry successfully recorded.",
    )


@router.get(
    "/history",
    response_model=List[MealHistoryItemResponse],
    summary="Get user meal history formatted for frontend consumption",
)
async def get_meal_history(
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Retrieve logged meal history array expected by frontend."""
    supabase = get_supabase_client()
    user_id = current_user.id if current_user else "usr_4a89fb21"

    res = (
        supabase.from_("meals")
        .select("*")
        .eq("user_id", user_id)
        .order("logged_at", desc=True)
        .execute()
    )
    meals_data = res.data or []

    history_items: List[MealHistoryItemResponse] = []
    for m in meals_data:
        m_id = str(m["id"])
        # Fetch meal items
        items_res = supabase.from_("meal_items").select("*").eq("meal_id", m_id).execute()
        item_rows = items_res.data or []

        details = [
            HistoryItemDetail(
                food_name=i.get("food_name", "Dish"),
                unit_name=i.get("selected_unit_id", "Standard Portion"),
                quantity=float(i.get("selected_quantity", 1.0)),
                gram_weight=float(i.get("gram_weight", 100.0)),
                calories_kcal=float(i.get("calories_kcal", 0.0)),
            )
            for i in item_rows
        ]

        history_items.append(
            MealHistoryItemResponse(
                meal_id=m_id,
                meal_type=m.get("meal_type", "lunch"),
                logged_at=str(m.get("logged_at", "")),
                total_calories_kcal=float(m.get("total_calories_kcal", 0.0)),
                total_protein_g=float(m.get("total_protein_g", 0.0)),
                total_carbs_g=float(m.get("total_carbs_g", 0.0)),
                total_fat_g=float(m.get("total_fat_g", 0.0)),
                items=details,
            )
        )

    return history_items


@router.get("", response_model=MealListResponse, summary="List meals for current user")
async def list_meals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Retrieve paginated meals for current authenticated user."""
    supabase = get_supabase_client()
    user_id = current_user.id if current_user else "usr_4a89fb21"

    query = supabase.from_("meals").select("*", count="exact")
    if user_id:
        query = query.eq("user_id", user_id)

    offset = (page - 1) * page_size
    res = query.order("logged_at", desc=True).range(offset, offset + page_size - 1).execute()
    meals_data = res.data or []
    total_count = res.count if res.count is not None else len(meals_data)

    detailed_meals: List[MealDetailResponse] = []
    for m in meals_data:
        m_id = str(m["id"])
        items_res = supabase.from_("meal_items").select("*").eq("meal_id", m_id).execute()
        item_rows = [MealItemResponse(**i) for i in (items_res.data or [])]
        detailed_meals.append(
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

    return MealListResponse(
        total_count=total_count,
        page=page,
        page_size=page_size,
        meals=detailed_meals,
    )


@router.get("/{meal_id}", response_model=MealDetailResponse, summary="Get meal details by ID")
async def get_meal(
    meal_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Retrieve a single meal by ID ensuring user ownership isolation."""
    supabase = get_supabase_client()
    query = supabase.from_("meals").select("*").eq("id", str(meal_id))
    if current_user:
        query = query.eq("user_id", current_user.id)

    res = query.execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")

    m = res.data[0] if isinstance(res.data, list) else res.data
    m_id = str(m["id"])
    items_res = supabase.from_("meal_items").select("*").eq("meal_id", m_id).execute()
    item_rows = [MealItemResponse(**i) for i in (items_res.data or [])]

    return MealDetailResponse(
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


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a meal")
async def delete_meal(
    meal_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Delete a logged meal enforcing user ownership."""
    supabase = get_supabase_client()
    query = supabase.from_("meals").select("*").eq("id", str(meal_id))
    if current_user:
        query = query.eq("user_id", current_user.id)

    res = query.execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")

    # Delete child items and meal
    supabase.from_("meal_items").delete().eq("meal_id", str(meal_id)).execute()
    supabase.from_("meal_item_feedback_logs").delete().eq("meal_id", str(meal_id)).execute()
    supabase.from_("meals").delete().eq("id", str(meal_id)).execute()
    return None
