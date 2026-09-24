"""Tests for the /api/v1/analyze endpoint (CV Identification + Portion Units attachment)."""

import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_meal_multipart_upload(client: AsyncClient):
    # Prepare dummy image file bytes
    file_content = b"fake-jpeg-image-bytes-for-testing"
    files = {"file": ("test_lunch.jpg", file_content, "image/jpeg")}
    data = {"prompt": "Plate of Nigerian food"}

    response = await client.post("/api/v1/analyze", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["status"] == "success"
    assert "analysis_id" in res_data
    assert "image_url" in res_data
    assert res_data["processing_duration_ms"] > 0
    assert len(res_data["detected_items"]) >= 2

    # Check Jollof Rice item
    jollof_item = next((i for i in res_data["detected_items"] if i["predicted_dish_id"] == "jollof_rice"), None)
    assert jollof_item is not None
    assert jollof_item["confidence"] >= 0.8
    assert jollof_item["bounding_box"] is not None

    # Check portion units attachment
    portion_units = jollof_item["available_portion_units"]
    assert len(portion_units) >= 2
    unit_ids = [u["unit_id"] for u in portion_units]
    assert "serving_spoon" in unit_ids or "mound_cup" in unit_ids

    # Check 100g nutrients
    n100 = jollof_item["nutrients_per_100g"]
    assert n100["calories_kcal"] > 0
    assert n100["carbs_g"] > 0


@pytest.mark.asyncio
async def test_analyze_meal_json_url(client: AsyncClient):
    payload = {
        "image_url": "https://storage.docta.ng/meals/test_amala.jpg",
        "prompt": "I had amala with egusi soup",
    }
    response = await client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["status"] == "success"
    assert len(res_data["detected_items"]) >= 1

    dish_ids = [i["predicted_dish_id"] for i in res_data["detected_items"]]
    assert "amala" in dish_ids or "egusi_soup" in dish_ids
