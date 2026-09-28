"""Tests for user signup, registration, Supabase login, and profile retrieval."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_user_success(client: AsyncClient):
    payload = {
        "email": "newuser@docta.ng",
        "password": "securepassword123",
        "name": "Dr. Chioma Adebayo",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "newuser@docta.ng"
    assert data["user"]["name"] == "Dr. Chioma Adebayo"
    assert data["user"]["is_active"] is True
    assert "id" in data["user"]


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    payload = {
        "email": "registeruser@docta.ng",
        "password": "securepassword123",
        "full_name": "Emeka Okafor",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "registeruser@docta.ng"
    assert data["full_name"] == "Emeka Okafor"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "anotherpassword",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_json_success(client: AsyncClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "demo1234",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "wrongpassword",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient, auth_headers: dict, test_user):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert "dailyCalorieTarget" in data


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_user(client: AsyncClient):
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert "Logged out successfully" in response.json()["message"]


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, auth_headers: dict):
    response = await client.post("/api/v1/auth/refresh", headers=auth_headers)
    assert response.status_code == 200
    assert "access_token" in response.json()
