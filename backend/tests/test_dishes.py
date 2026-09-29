"""Tests for GET /api/v1/dishes/{dish_id} endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_dish_details_canonical(client: AsyncClient):
    """Test retrieving details for canonical dishes."""
    response = await client.get("/api/v1/dishes/jollof_rice")
    assert response.status_code == 200
    data = response.json()

    assert data["dish_id"] == "jollof_rice"
    assert "Jollof" in data["display_name"]
    assert len(data["available_portion_units"]) >= 2
    assert data["nutrients_per_100g"]["calories_kcal"] > 0
    assert data["wafct_code"] == "01_042"


@pytest.mark.asyncio
async def test_get_dish_details_alias_resolution(client: AsyncClient):
    """Test that Nigerian colloquial aliases resolve to canonical dish data."""
    response = await client.get("/api/v1/dishes/dodo")
    assert response.status_code == 200
    data = response.json()

    assert data["dish_id"] == "fried_plantain"
    assert "Plantain" in data["display_name"] or "Dodo" in data["display_name"]
    assert len(data["available_portion_units"]) >= 2
    assert data["nutrients_per_100g"]["calories_kcal"] > 0


@pytest.mark.asyncio
async def test_get_dish_details_amala(client: AsyncClient):
    """Test retrieving details for Amala."""
    response = await client.get("/api/v1/dishes/amala")
    assert response.status_code == 200
    data = response.json()

    assert data["dish_id"] == "amala"
    assert len(data["available_portion_units"]) >= 2
    assert data["nutrients_per_100g"]["calories_kcal"] > 0
