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


@pytest.mark.asyncio
async def test_user_a_and_user_b_distinct_uuid_and_isolation(client: AsyncClient):
    import uuid

    # 1. User A signup & login
    res_a = await client.post(
        "/api/v1/auth/signup",
        json={"email": "usera@docta.ng", "password": "passwordA123", "name": "User Alpha"},
    )
    assert res_a.status_code == 201
    token_a = res_a.json()["access_token"]
    user_a = res_a.json()["user"]

    # Verify UUID format
    uuid_a = uuid.UUID(user_a["id"])
    assert str(uuid_a) == user_a["id"]

    # 2. User B signup & login
    res_b = await client.post(
        "/api/v1/auth/signup",
        json={"email": "userb@docta.ng", "password": "passwordB123", "name": "User Beta"},
    )
    assert res_b.status_code == 201
    token_b = res_b.json()["access_token"]
    user_b = res_b.json()["user"]

    # Verify UUID format
    uuid_b = uuid.UUID(user_b["id"])
    assert str(uuid_b) == user_b["id"]

    # Assert user IDs are completely distinct
    assert user_a["id"] != user_b["id"]
    assert user_a["email"] != user_b["email"]

    # 3. Access /auth/me for User A
    me_a = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert me_a.status_code == 200
    assert me_a.json()["id"] == user_a["id"]
    assert me_a.json()["email"] == "usera@docta.ng"

    # 4. Access /auth/me for User B
    me_b = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_b}"})
    assert me_b.status_code == 200
    assert me_b.json()["id"] == user_b["id"]
    assert me_b.json()["email"] == "userb@docta.ng"


@pytest.mark.asyncio
async def test_invalid_token_returns_401(client: AsyncClient):
    # Arbitrary fake token with prefix must NOT fall back to demo user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer sb_token_nonexistent_fake_token_123"},
    )
    assert response.status_code == 401
    assert "invalid or expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_real_logout_invalidates_token(client: AsyncClient):
    # Signup & obtain session
    signup_res = await client.post(
        "/api/v1/auth/signup",
        json={"email": "logout_test@docta.ng", "password": "password123", "name": "Logout Test"},
    )
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify token works
    me_res1 = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res1.status_code == 200

    # Logout
    logout_res = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200

    # Token must now be rejected
    me_res2 = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res2.status_code == 401

