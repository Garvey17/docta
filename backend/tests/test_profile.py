"""Tests for User Profile retrieval and target updates."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient, auth_headers: dict, test_user):
    response = await client.get("/api/v1/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["dailyCalorieTarget"] == 2200


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_headers: dict):
    payload = {
        "name": "Balkisu H. Updated",
        "dailyCalorieTarget": 2400,
        "dailyProteinTargetG": 125.0,
    }
    response = await client.patch("/api/v1/profile", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Balkisu H. Updated"
    assert data["dailyCalorieTarget"] == 2400
    assert data["dailyProteinTargetG"] == 125.0

    # Verify persisted in get
    get_res = await client.get("/api/v1/profile", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["dailyCalorieTarget"] == 2400
