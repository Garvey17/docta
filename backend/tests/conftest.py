"""Pytest fixtures for docta backend test suite with Supabase in-memory store."""

import sys
import uuid
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.main import app
from src.supabase_client import get_supabase_client, reset_in_memory_supabase
from src.schemas.auth import UserResponse


@pytest.fixture(autouse=True)
def clean_supabase_db():
    """Reset the in-memory Supabase store before each test run."""
    reset_in_memory_supabase()
    yield
    reset_in_memory_supabase()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Provide httpx AsyncClient pointing to FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user():
    """Default test user."""
    return UserResponse(
        id="f47ac10b-58cc-4372-a567-0e02b2c3d479",
        email="balkisu@docta.ng",
        name="Balkisu Habib",
        full_name="Balkisu Habib",
        is_active=True,
        is_admin=True,
        dailyCalorieTarget=2200,
        dailyProteinTargetG=110.0,
        dailyCarbsTargetG=250.0,
        dailyFatTargetG=65.0,
        dailyFiberTargetG=30.0,
        dailySodiumTargetMg=2300.0,
    )


@pytest.fixture
def auth_headers(test_user):
    """Authorization headers for test user."""
    token = f"sb_token_{test_user.id}"
    # Ensure active session in mock auth
    client_instance = get_supabase_client()
    if hasattr(client_instance, "auth") and hasattr(client_instance.auth, "active_sessions"):
        client_instance.auth.active_sessions[token] = {
            "access_token": token,
            "user": {
                "id": test_user.id,
                "email": test_user.email,
                "name": test_user.name,
                "is_admin": test_user.is_admin,
            },
        }
    return {"Authorization": f"Bearer {token}"}
