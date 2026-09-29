"""Comprehensive End-to-End Integration Test for Docta Architecture (Phase 16).

Verifies the complete flow across all layers:
1. User registration & authentication (Supabase auth contract)
2. Image upload & analysis (Mock CV detection + Real RAG nutrition/portion attachment)
3. Dish correction / alias resolution (/api/v1/dishes/{dish_id})
4. Portion selection & nutrient scaling
5. Meal persistence to Supabase (/api/v1/meals/log)
6. Meal history retrieval (/api/v1/meals/history) & meal detail (/api/v1/meals/{id})
7. Real dashboard calculation (/api/v1/dashboard/summary)
8. Telemetry persistence & export (/api/v1/telemetry/export)
9. User isolation boundary verification
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_complete_end_to_end_flow(client: AsyncClient):
    # -------------------------------------------------------------
    # 1. USER SIGNUP & LOGIN
    # -------------------------------------------------------------
    signup_payload = {
        "email": "dr_fatima@docta.ng",
        "password": "Password123!",
        "name": "Dr. Fatima Bello",
    }
    signup_res = await client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201
    signup_data = signup_res.json()
    assert "access_token" in signup_data
    token = signup_data["access_token"]
    user_id = signup_data["user"]["id"]
    assert user_id is not None
    assert "-" in user_id  # Valid UUID format

    headers = {"Authorization": f"Bearer {token}"}

    # Verify /auth/me returns the registered user
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "dr_fatima@docta.ng"

    # -------------------------------------------------------------
    # 2. UPLOAD & ANALYZE IMAGE (CV Identification + RAG Nutrition)
    # -------------------------------------------------------------
    dummy_image = b"fake-jpeg-raw-bytes-for-meal-analysis"
    files = {"image": ("sunday_lunch.jpg", dummy_image, "image/jpeg")}
    data = {"prompt": "Plate with jollof rice and fried fish"}

    analyze_res = await client.post("/api/v1/analyze", files=files, data=data, headers=headers)
    assert analyze_res.status_code == 200
    analysis = analyze_res.json()
    assert analysis["status"] == "success"
    analysis_id = analysis["analysis_id"]
    image_url = analysis["image_url"]
    assert analysis_id is not None
    assert image_url.startswith("http")
    assert not image_url.startswith("blob:")  # Never blob: URL in backend

    detected_items = analysis["detected_items"]
    assert len(detected_items) >= 2

    # Check Jollof Rice item
    jollof_item = next((i for i in detected_items if i["predicted_dish_id"] == "jollof_rice"), None)
    assert jollof_item is not None
    assert jollof_item["confidence"] >= 0.8
    assert jollof_item["bounding_box"] is not None
    assert "nutrients_per_100g" in jollof_item
    assert jollof_item["nutrients_per_100g"]["calories_kcal"] > 0
    assert len(jollof_item["available_portion_units"]) >= 1

    # -------------------------------------------------------------
    # 3. FOOD CORRECTION / DISH RESOLUTION
    # -------------------------------------------------------------
    # User corrects second item to Nigerian alias "dodo"
    dish_res = await client.get("/api/v1/dishes/dodo", headers=headers)
    assert dish_res.status_code == 200
    dodo_details = dish_res.json()
    assert dodo_details["dish_id"] == "fried_plantain"
    assert "Plantain" in dodo_details["display_name"]
    assert dodo_details["nutrients_per_100g"]["calories_kcal"] > 0
    assert len(dodo_details["available_portion_units"]) >= 1

    # -------------------------------------------------------------
    # 4. PORTION SELECTION & SCALING
    # -------------------------------------------------------------
    # Jollof Rice: 2 serving spoons = 240g
    jollof_unit = next(
        (u for u in jollof_item["available_portion_units"] if u["unit_id"] == "serving_spoon"),
        jollof_item["available_portion_units"][0],
    )
    jollof_grams = jollof_unit["gram_weight"] * 2
    factor_jollof = jollof_grams / 100.0
    jollof_cals = round(jollof_item["nutrients_per_100g"]["calories_kcal"] * factor_jollof, 1)
    jollof_prot = round(jollof_item["nutrients_per_100g"]["protein_g"] * factor_jollof, 1)
    jollof_carbs = round(jollof_item["nutrients_per_100g"]["carbs_g"] * factor_jollof, 1)
    jollof_fat = round(jollof_item["nutrients_per_100g"]["fat_g"] * factor_jollof, 1)

    # Fried Plantain: custom 100g portion
    plantain_grams = 100.0
    plantain_cals = dodo_details["nutrients_per_100g"]["calories_kcal"]
    plantain_prot = dodo_details["nutrients_per_100g"]["protein_g"]
    plantain_carbs = dodo_details["nutrients_per_100g"]["carbs_g"]
    plantain_fat = dodo_details["nutrients_per_100g"]["fat_g"]

    total_cals = round(jollof_cals + plantain_cals, 1)
    total_prot = round(jollof_prot + plantain_prot, 1)
    total_carbs = round(jollof_carbs + plantain_carbs, 1)
    total_fat = round(jollof_fat + plantain_fat, 1)

    # -------------------------------------------------------------
    # 5. PERSIST MEAL & ACTIVE LEARNING TELEMETRY
    # -------------------------------------------------------------
    second_detected = [i for i in detected_items if i["predicted_dish_id"] != "jollof_rice"][0]

    meal_payload = {
        "analysis_id": analysis_id,
        "image_url": image_url,
        "meal_type": "lunch",
        "total_calories": total_cals,
        "total_protein_g": total_prot,
        "total_carbs_g": total_carbs,
        "total_fat_g": total_fat,
        "total_fiber_g": 6.5,
        "items": [
            {
                "item_id": "item_1",
                "food_name": "Jollof Rice",
                "predicted_dish_id": "jollof_rice",
                "final_dish_id": "jollof_rice",
                "label_modified": False,
                "confidence": jollof_item["confidence"],
                "bounding_box": jollof_item["bounding_box"],
                "selected_unit_id": jollof_unit["unit_id"],
                "selected_quantity": 2.0,
                "gram_weight": jollof_grams,
                "calories_kcal": jollof_cals,
                "protein_g": jollof_prot,
                "carbs_g": jollof_carbs,
                "fat_g": jollof_fat,
                "fiber_g": 3.5,
            },
            {
                "item_id": "item_2",
                "food_name": "Fried Plantain (Dodo)",
                "predicted_dish_id": second_detected["predicted_dish_id"],
                "final_dish_id": "fried_plantain",
                "label_modified": True,
                "confidence": second_detected["confidence"],
                "bounding_box": second_detected["bounding_box"],
                "selected_unit_id": "custom_grams",
                "selected_quantity": 1.0,
                "gram_weight": plantain_grams,
                "custom_weight_entered_g": plantain_grams,
                "calories_kcal": plantain_cals,
                "protein_g": plantain_prot,
                "carbs_g": plantain_carbs,
                "fat_g": plantain_fat,
                "fiber_g": 3.0,
            },
        ],
    }

    log_res = await client.post("/api/v1/meals/log", json=meal_payload, headers=headers)
    assert log_res.status_code == 201
    meal_data = log_res.json()
    assert "id" in meal_data
    meal_id = meal_data["id"]
    assert meal_data["user_id"] == user_id
    assert round(meal_data["total_calories_kcal"], 1) == round(total_cals, 1)

    # -------------------------------------------------------------
    # 6. MEAL HISTORY & MEAL DETAIL
    # -------------------------------------------------------------
    history_res = await client.get("/api/v1/meals/history", headers=headers)
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 1
    recent = history[0]
    assert recent["meal_id"] == meal_id
    assert round(recent["total_calories_kcal"], 1) == round(total_cals, 1)
    assert len(recent["items"]) == 2

    # Fetch meal by ID
    single_res = await client.get(f"/api/v1/meals/{meal_id}", headers=headers)
    assert single_res.status_code == 200
    assert single_res.json()["id"] == meal_id

    # -------------------------------------------------------------
    # 7. REAL DASHBOARD CALCULATION
    # -------------------------------------------------------------
    dash_res = await client.get("/api/v1/dashboard/summary", headers=headers)
    assert dash_res.status_code == 200
    dashboard = dash_res.json()
    assert round(dashboard["today"]["total_calories_kcal"], 1) == round(total_cals, 1)
    assert dashboard["today"]["meal_count"] >= 1
    assert dashboard["calorie_progress_pct"] > 0
    assert len(dashboard["recent_meals"]) >= 1

    # -------------------------------------------------------------
    # 8. TELEMETRY RECORDING & EXPORT
    # -------------------------------------------------------------
    telemetry_json_res = await client.get("/api/v1/telemetry/export?format=json", headers=headers)
    assert telemetry_json_res.status_code == 200
    telemetry_data = telemetry_json_res.json()
    assert telemetry_data["total_records"] >= 2
    records = telemetry_data["records"]

    # Verify the corrected item logged telemetry
    plantain_log = next((t for t in records if t["final_dish_id"] == "fried_plantain"), None)
    assert plantain_log is not None
    assert plantain_log["meal_id"] == meal_id
    assert plantain_log["label_modified"] is True
    assert plantain_log["selected_unit_id"] == "custom_grams"
    assert plantain_log["calculated_gram_weight"] == 100.0

    # Test CSV export format
    telemetry_csv_res = await client.get("/api/v1/telemetry/export?format=csv", headers=headers)
    assert telemetry_csv_res.status_code == 200
    assert "text/csv" in telemetry_csv_res.headers.get("content-type", "")
    assert "predicted_dish_id" in telemetry_csv_res.text
    assert "fried_plantain" in telemetry_csv_res.text

    # -------------------------------------------------------------
    # 9. USER ISOLATION
    # -------------------------------------------------------------
    # Register second user
    user2_signup = {
        "email": "user2@docta.ng",
        "password": "Password123!",
        "name": "User Two",
    }
    user2_res = await client.post("/api/v1/auth/signup", json=user2_signup)
    assert user2_res.status_code == 201
    user2_headers = {"Authorization": f"Bearer {user2_res.json()['access_token']}"}

    # User 2 sees empty history
    user2_history = await client.get("/api/v1/meals/history", headers=user2_headers)
    assert user2_history.status_code == 200
    assert len(user2_history.json()) == 0

    # User 2 sees 0 calories on dashboard
    user2_dash = await client.get("/api/v1/dashboard/summary", headers=user2_headers)
    assert user2_dash.status_code == 200
    assert user2_dash.json()["today"]["total_calories_kcal"] == 0.0

    # User 2 cannot access User 1's meal
    user2_meal_res = await client.get(f"/api/v1/meals/{meal_id}", headers=user2_headers)
    assert user2_meal_res.status_code in [403, 404]
