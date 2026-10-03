"""Tests for Insight Chatbot, Agentic RAG nutrition retrieval, and scope restrictions."""

import pytest
from httpx import AsyncClient
from src.supabase_client import get_supabase_client
from src.services.insight_service import InsightService, _build_user_tools


@pytest.mark.asyncio
async def test_insight_database_tools_retrieval(test_user):
    """Verify user-scoped tools retrieve profile targets and meals correctly."""
    supabase = get_supabase_client()
    user_id = test_user.id

    # Seed a meal for this user
    meal_data = {
        "id": "11111111-1111-1111-1111-111111111111",
        "user_id": user_id,
        "meal_type": "lunch",
        "notes": "Test Lunch",
        "logged_at": "2026-10-03T12:00:00Z",
        "total_calories_kcal": 450.0,
        "total_protein_g": 25.0,
        "total_carbs_g": 55.0,
        "total_fat_g": 12.0,
        "total_fiber_g": 6.0,
        "total_sodium_mg": 400.0,
    }
    supabase.from_("meals").insert(meal_data).execute()

    item_data = {
        "id": "22222222-2222-2222-2222-222222222222",
        "meal_id": "11111111-1111-1111-1111-111111111111",
        "food_name": "Jollof Rice",
        "selected_unit_id": "cup",
        "selected_quantity": 1.5,
        "calories_kcal": 450.0,
        "protein_g": 25.0,
        "fat_g": 12.0,
        "carbs_g": 55.0,
        "fiber_g": 6.0,
        "sodium_mg": 400.0,
    }
    supabase.from_("meal_items").insert(item_data).execute()

    tools = _build_user_tools(user_id)
    history_tool = next(t for t in tools if t.name == "get_user_nutrition_history")
    targets_tool = next(t for t in tools if t.name == "get_user_nutrition_targets")

    # Test targets tool
    targets_result = targets_tool.invoke({})
    assert "Daily Calories" in targets_result or "Daily Targets" in targets_result
    assert "2200" in targets_result

    # Test history tool
    history_result = history_tool.invoke({"days": 7})
    assert "Jollof Rice" in history_result
    assert "450" in history_result
    assert "25" in history_result


@pytest.mark.asyncio
async def test_insight_chat_endpoint_authenticated(client: AsyncClient, auth_headers):
    """Test the POST /api/v1/insights/chat endpoint with auth."""
    payload = {
        "message": "Hello, how can you help me as my nutritionist?",
        "history": [],
    }
    response = await client.post("/api/v1/insights/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "reply" in data
    assert len(data["reply"]) > 0


@pytest.mark.asyncio
async def test_insight_chat_scope_restriction(client: AsyncClient, auth_headers):
    """Test that the chatbot declines off-topic non-nutrition queries."""
    payload = {
        "message": "Can you write Python code to implement binary search?",
        "history": [],
    }
    response = await client.post("/api/v1/insights/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"].lower()
    # Should politely decline and mention nutrition/diet
    assert any(term in reply for term in ["nutrition", "diet", "meal", "food", "cannot", "only", "sorry", "decline"])
