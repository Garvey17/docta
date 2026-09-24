"""Tests for Meal Logging and 'Log Everything' Active Learning Telemetry."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.meal import Meal
from src.models.meal_item import MealItem
from src.models.meal_item_feedback_log import MealItemFeedbackLog


@pytest.mark.asyncio
async def test_log_meal_atomic_transaction_and_telemetry(
    client: AsyncClient,
    auth_headers: dict,
    test_user,
    db_session: AsyncSession,
):
    """
    Verify POST /api/v1/meals/log creates:
    1. A parent Meal record.
    2. Child MealItem records.
    3. Dedicated MealItemFeedbackLog records for active learning telemetry.
    """
    payload = {
        "analysis_id": "anlz_test123",
        "image_url": "https://storage.docta.ng/meals/jollof_lunch.jpg",
        "meal_type": "lunch",
        "notes": "Sunday special lunch",
        "items": [
            {
                "item_id": "item_1",
                "food_name": "Nigerian Jollof Rice",
                "predicted_dish_id": "jollof_rice",
                "final_dish_id": "jollof_rice",
                "label_modified": False,
                "confidence": 0.94,
                "bounding_box": [0.125, 0.240, 0.550, 0.780],
                "selected_unit_id": "serving_spoon",
                "selected_quantity": 2.0,
                "gram_weight": 240.0,
                "calories_kcal": 336.0,
                "protein_g": 6.48,
                "fat_g": 9.6,
                "carbs_g": 55.2,
                "fiber_g": 2.4,
                "sodium_mg": 432.0,
                "calcium_mg": 19.2,
                "iron_mg": 1.68,
            },
            {
                "item_id": "item_2",
                "food_name": "Fried Ripe Plantain (Dodo)",
                "predicted_dish_id": "fried_rice",  # Intentionally simulated misclassification corrected by user
                "final_dish_id": "fried_plantain",
                "label_modified": True,
                "confidence": 0.65,
                "bounding_box": [0.580, 0.310, 0.890, 0.650],
                "selected_unit_id": "portion_6_slices",
                "selected_quantity": 1.0,
                "gram_weight": 150.0,
                "calories_kcal": 312.0,
                "protein_g": 1.8,
                "fat_g": 14.1,
                "carbs_g": 48.0,
                "fiber_g": 3.6,
                "sodium_mg": 6.0,
                "calcium_mg": 15.0,
                "iron_mg": 0.9,
            },
        ],
    }

    response = await client.post("/api/v1/meals/log", json=payload, headers=auth_headers)
    assert response.status_code == 201
    meal_data = response.json()

    assert "id" in meal_data
    assert meal_data["user_id"] == str(test_user.id)
    assert meal_data["meal_type"] == "lunch"
    assert len(meal_data["items"]) == 2

    # Check aggregated totals (336 + 312 = 648 kcal)
    assert meal_data["total_calories_kcal"] == 648.0
    assert meal_data["total_protein_g"] == round(6.48 + 1.8, 2)

    saved_meal_id = uuid.UUID(meal_data["id"])

    # 1. Verify Meal record in DB
    db_meal = (await db_session.execute(select(Meal).where(Meal.id == saved_meal_id))).scalar_one_or_none()
    assert db_meal is not None
    assert db_meal.total_calories_kcal == 648.0

    # 2. Verify Meal Items in DB
    db_items = (await db_session.execute(select(MealItem).where(MealItem.meal_id == saved_meal_id))).scalars().all()
    assert len(db_items) == 2

    # 3. Verify "Log Everything" Telemetry in DB
    db_logs = (
        await db_session.execute(select(MealItemFeedbackLog).where(MealItemFeedbackLog.meal_id == saved_meal_id))
    ).scalars().all()
    assert len(db_logs) == 2

    # Find the corrected item in telemetry
    corrected_log = next((l for l in db_logs if l.label_modified is True), None)
    assert corrected_log is not None
    assert corrected_log.predicted_dish_id == "fried_rice"
    assert corrected_log.final_dish_id == "fried_plantain"
    assert corrected_log.selected_unit_id == "portion_6_slices"
    assert corrected_log.selected_quantity == 1.0
    assert corrected_log.calculated_gram_weight == 150.0

    # Find the uncorrected item in telemetry
    normal_log = next((l for l in db_logs if l.label_modified is False), None)
    assert normal_log is not None
    assert normal_log.predicted_dish_id == "jollof_rice"
    assert normal_log.final_dish_id == "jollof_rice"
    assert normal_log.selected_unit_id == "serving_spoon"
    assert normal_log.selected_quantity == 2.0
    assert normal_log.calculated_gram_weight == 240.0


@pytest.mark.asyncio
async def test_get_and_delete_meal(client: AsyncClient, auth_headers: dict):
    # Log a simple meal first
    payload = {
        "meal_type": "dinner",
        "items": [
            {
                "food_name": "Egusi Soup",
                "predicted_dish_id": "egusi_soup",
                "final_dish_id": "egusi_soup",
                "label_modified": False,
                "confidence": 0.95,
                "selected_unit_id": "small_bowl",
                "selected_quantity": 1.0,
                "gram_weight": 200.0,
                "calories_kcal": 370.0,
                "protein_g": 13.6,
                "fat_g": 28.4,
                "carbs_g": 15.0,
                "fiber_g": 4.2,
                "sodium_mg": 580.0,
                "calcium_mg": 90.0,
                "iron_mg": 3.6,
            }
        ],
    }
    create_resp = await client.post("/api/v1/meals/log", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    meal_id = create_resp.json()["id"]

    # Retrieve single meal
    get_resp = await client.get(f"/api/v1/meals/{meal_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["total_calories_kcal"] == 370.0

    # List meals
    list_resp = await client.get("/api/v1/meals", headers=auth_headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["total_count"] >= 1

    # Delete meal
    del_resp = await client.delete(f"/api/v1/meals/{meal_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    # Verify not found after delete
    get_after_del = await client.get(f"/api/v1/meals/{meal_id}", headers=auth_headers)
    assert get_after_del.status_code == 404
