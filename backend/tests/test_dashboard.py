"""Tests for user dashboard summary and target progress analytics."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_summary_empty(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "today" in data
    assert "targets" in data
    assert data["today"]["total_calories_kcal"] == 0.0


@pytest.mark.asyncio
async def test_dashboard_summary_with_meals(client: AsyncClient, auth_headers: dict):
    # Log a meal today
    payload = {
        "meal_type": "lunch",
        "items": [
            {
                "food_name": "Nigerian Jollof Rice",
                "predicted_dish_id": "jollof_rice",
                "final_dish_id": "jollof_rice",
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
            }
        ],
    }
    await client.post("/api/v1/meals/log", json=payload, headers=auth_headers)

    response = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["today"]["meal_count"] == 1
    assert data["today"]["total_calories_kcal"] == 336.0
    assert data["calorie_progress_pct"] > 0
    assert len(data["recent_meals"]) == 1
