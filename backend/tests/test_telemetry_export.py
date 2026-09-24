"""Tests for active learning dataset export and telemetry statistics."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_telemetry_export_json_and_csv(client: AsyncClient, auth_headers: dict):
    # Log a meal with telemetry first
    payload = {
        "meal_type": "breakfast",
        "items": [
            {
                "food_name": "Moi Moi",
                "predicted_dish_id": "moi_moi",
                "final_dish_id": "moi_moi",
                "label_modified": False,
                "confidence": 0.95,
                "selected_unit_id": "single_wrap",
                "selected_quantity": 1.0,
                "gram_weight": 150.0,
                "calories_kcal": 192.0,
                "protein_g": 10.8,
                "fat_g": 6.75,
                "carbs_g": 22.2,
                "fiber_g": 4.8,
                "sodium_mg": 315.0,
                "calcium_mg": 33.0,
                "iron_mg": 2.1,
            }
        ],
    }
    await client.post("/api/v1/meals/log", json=payload, headers=auth_headers)

    # 1. Test JSON Export
    json_resp = await client.get("/api/v1/telemetry/export?format=json")
    assert json_resp.status_code == 200
    export_data = json_resp.json()
    assert export_data["total_records"] >= 1
    assert len(export_data["records"]) >= 1
    rec = export_data["records"][0]
    assert "predicted_dish_id" in rec
    assert "selected_unit_id" in rec
    assert "calculated_gram_weight" in rec

    # 2. Test CSV Export
    csv_resp = await client.get("/api/v1/telemetry/export?format=csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "predicted_dish_id" in csv_resp.text
    assert "moi_moi" in csv_resp.text

    # 3. Test Telemetry Stats
    stats_resp = await client.get("/api/v1/telemetry/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_decisions_logged"] >= 1
    assert "moi_moi" in stats["top_predicted_dishes"]
