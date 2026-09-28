"""Tests for Meal Logging, History, and 'Log Everything' Active Learning Telemetry."""

import pytest
from httpx import AsyncClient
from src.supabase_client import get_supabase_client


@pytest.mark.asyncio
async def test_log_meal_and_telemetry_persistence(client: AsyncClient, auth_headers: dict, test_user):
    """
    Verify POST /api/v1/meals/log creates:
    1. Parent meal in Supabase meals.
    2. Child meal items in Supabase meal_items.
    3. Dedicated telemetry logs in meal_item_feedback_logs for every item.
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
    assert "meal_id" in meal_data
    assert meal_data["status"] == "success"
    assert meal_data["user_id"] == str(test_user.id)
    assert meal_data["meal_type"] == "lunch"
    assert len(meal_data["items"]) == 2
    assert meal_data["total_calories_kcal"] == 648.0
    assert meal_data["total_protein_g"] == round(6.48 + 1.8, 2)
    assert meal_data["feedback_telemetry_recorded"] is True

    meal_id = meal_data["id"]
    supabase = get_supabase_client()

    # 1. Verify Meal record in Supabase
    db_meal = supabase.from_("meals").select("*").eq("id", meal_id).execute().data
    assert len(db_meal) == 1
    assert db_meal[0]["total_calories_kcal"] == 648.0

    # 2. Verify Meal Items in Supabase
    db_items = supabase.from_("meal_items").select("*").eq("meal_id", meal_id).execute().data
    assert len(db_items) == 2

    # 3. Verify 'Log Everything' Telemetry in Supabase
    db_logs = supabase.from_("meal_item_feedback_logs").select("*").eq("meal_id", meal_id).execute().data
    assert len(db_logs) == 2

    # Check the user-modified item in telemetry
    corrected = next((l for l in db_logs if l["label_modified"] is True), None)
    assert corrected is not None
    assert corrected["predicted_dish_id"] == "fried_rice"
    assert corrected["final_dish_id"] == "fried_plantain"
    assert corrected["selected_unit_id"] == "portion_6_slices"
    assert corrected["selected_quantity"] == 1.0
    assert corrected["calculated_gram_weight"] == 150.0

    # Check uncorrected item in telemetry
    normal = next((l for l in db_logs if l["label_modified"] is False), None)
    assert normal is not None
    assert normal["predicted_dish_id"] == "jollof_rice"
    assert normal["final_dish_id"] == "jollof_rice"
    assert normal["selected_unit_id"] == "serving_spoon"
    assert normal["selected_quantity"] == 2.0
    assert normal["calculated_gram_weight"] == 240.0


@pytest.mark.asyncio
async def test_get_meal_history_frontend_format(client: AsyncClient, auth_headers: dict):
    # Log a meal
    payload = {
        "meal_type": "breakfast",
        "items": [
            {
                "food_name": "Moi Moi",
                "predicted_dish_id": "moi_moi",
                "final_dish_id": "moi_moi",
                "selected_unit_id": "single_wrap",
                "selected_quantity": 1.0,
                "gram_weight": 150.0,
                "calories_kcal": 215.0,
                "protein_g": 12.0,
                "fat_g": 5.0,
                "carbs_g": 20.0,
            }
        ],
    }
    await client.post("/api/v1/meals/log", json=payload, headers=auth_headers)

    response = await client.get("/api/v1/meals/history", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) >= 1
    assert history[0]["meal_type"] == "breakfast"
    assert history[0]["total_calories_kcal"] == 215.0
    assert len(history[0]["items"]) == 1
    assert history[0]["items"][0]["food_name"] == "Moi Moi"


@pytest.mark.asyncio
async def test_get_and_delete_meal(client: AsyncClient, auth_headers: dict):
    payload = {
        "meal_type": "dinner",
        "items": [
            {
                "food_name": "Egusi Soup",
                "predicted_dish_id": "egusi_soup",
                "final_dish_id": "egusi_soup",
                "selected_unit_id": "small_bowl",
                "selected_quantity": 1.0,
                "gram_weight": 200.0,
                "calories_kcal": 370.0,
                "protein_g": 13.6,
                "fat_g": 28.4,
                "carbs_g": 15.0,
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

    # Delete meal
    del_resp = await client.delete(f"/api/v1/meals/{meal_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    # Verify not found after delete
    get_after_del = await client.get(f"/api/v1/meals/{meal_id}", headers=auth_headers)
    assert get_after_del.status_code == 404


@pytest.mark.asyncio
async def test_cross_user_isolation(client: AsyncClient, auth_headers: dict):
    # Log meal with User 1
    payload = {
        "meal_type": "lunch",
        "items": [
            {
                "food_name": "Jollof Rice",
                "predicted_dish_id": "jollof_rice",
                "final_dish_id": "jollof_rice",
                "selected_unit_id": "serving_spoon",
                "selected_quantity": 1.0,
                "gram_weight": 120.0,
                "calories_kcal": 180.0,
            }
        ],
    }
    resp = await client.post("/api/v1/meals/log", json=payload, headers=auth_headers)
    meal_id = resp.json()["id"]

    # User 2 headers
    user2_token = "sb_token_user_2_another"
    supabase = get_supabase_client()
    if hasattr(supabase, "auth") and hasattr(supabase.auth, "active_sessions"):
        supabase.auth.active_sessions[user2_token] = {
            "access_token": user2_token,
            "user": {"id": "user_2_another", "email": "other@docta.ng", "name": "Other User"},
        }
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 cannot access User 1's meal
    user2_get = await client.get(f"/api/v1/meals/{meal_id}", headers=user2_headers)
    assert user2_get.status_code == 404

    # User 2 cannot delete User 1's meal
    user2_del = await client.delete(f"/api/v1/meals/{meal_id}", headers=user2_headers)
    assert user2_del.status_code == 404
