"""Supabase client integration with an explicit in-memory test fixture.

Provides a unified interface for database and auth operations using Supabase:
- Uses the real supabase-py client in application runtime.
- In-memory behavior is available only when explicitly initialized by tests.
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from .config import get_settings

logger = logging.getLogger(__name__)


class MockPostgrestResponse:
    def __init__(self, data: Any, count: Optional[int] = None):
        self.data = data
        self.count = count if count is not None else (len(data) if isinstance(data, list) else 1)


class InMemoryQueryBuilder:
    """Simulates PostgREST query builder on in-memory table store."""

    def __init__(self, table_name: str, table_data: List[Dict[str, Any]]):
        self.table_name = table_name
        self.table_data = table_data
        self._action = "select"
        self._insert_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
        self._update_data: Optional[Dict[str, Any]] = None
        self._filters = []
        self._order_by = None
        self._order_desc = False
        self._limit_count: Optional[int] = None
        self._offset_count: int = 0
        self._single = False

    def select(self, columns: str = "*", count: Optional[str] = None):
        self._action = "select"
        return self

    def eq(self, column: str, value: Any):
        self._filters.append(lambda r: str(r.get(column)) == str(value))
        return self

    def neq(self, column: str, value: Any):
        self._filters.append(lambda r: str(r.get(column)) != str(value))
        return self

    def gte(self, column: str, value: Any):
        def _filter(r):
            v = r.get(column)
            if v is None:
                return False
            val = value.isoformat() if hasattr(value, "isoformat") else str(value)
            v_str = v.isoformat() if hasattr(v, "isoformat") else str(v)
            return v_str >= val
        self._filters.append(_filter)
        return self

    def lte(self, column: str, value: Any):
        def _filter(r):
            v = r.get(column)
            if v is None:
                return False
            val = value.isoformat() if hasattr(value, "isoformat") else str(value)
            v_str = v.isoformat() if hasattr(v, "isoformat") else str(v)
            return v_str <= val
        self._filters.append(_filter)
        return self

    def is_(self, column: str, value: Any):
        self._filters.append(lambda r: r.get(column) is value)
        return self

    def or_(self, expr: str):
        # basic OR parser for expressions like "predicted_dish_id.eq.val,final_dish_id.eq.val"
        parts = [p.strip() for p in expr.split(",") if p.strip()]
        sub_filters = []
        for p in parts:
            chunks = p.split(".eq.")
            if len(chunks) == 2:
                col, val = chunks[0], chunks[1]
                sub_filters.append(lambda r, c=col, v=val: str(r.get(c)) == str(v))

        if sub_filters:
            self._filters.append(lambda r: any(sf(r) for sf in sub_filters))
        return self

    def order(self, column: str, desc: bool = False):
        self._order_by = column
        self._order_desc = desc
        return self

    def range(self, start: int, end: int):
        self._offset_count = start
        self._limit_count = end - start + 1
        return self

    def limit(self, count: int):
        self._limit_count = count
        return self

    def single(self):
        self._single = True
        return self

    def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]):
        self._action = "insert"
        self._insert_data = data
        return self

    def update(self, data: Dict[str, Any]):
        self._action = "update"
        self._update_data = data
        return self

    def delete(self):
        self._action = "delete"
        return self

    def execute(self) -> MockPostgrestResponse:
        if self._action == "insert":
            items = self._insert_data if isinstance(self._insert_data, list) else [self._insert_data]
            inserted = []
            for item in items:
                record = dict(item)
                if "id" not in record or not record["id"]:
                    record["id"] = str(uuid.uuid4())
                if "created_at" not in record:
                    record["created_at"] = datetime.now(timezone.utc).isoformat()
                self.table_data.append(record)
                inserted.append(record)
            res_data = inserted[0] if (self._single or not isinstance(self._insert_data, list)) else inserted
            return MockPostgrestResponse(data=res_data)

        # Apply filters for select / update / delete
        filtered = [r for r in self.table_data if all(f(r) for f in self._filters)]

        if self._action == "update":
            for r in filtered:
                r.update(self._update_data)
                r["updated_at"] = datetime.now(timezone.utc).isoformat()
            return MockPostgrestResponse(data=filtered)

        if self._action == "delete":
            for r in filtered:
                if r in self.table_data:
                    self.table_data.remove(r)
            return MockPostgrestResponse(data=filtered)

        # Select action
        if self._order_by:
            filtered.sort(
                key=lambda x: (x.get(self._order_by) is not None, x.get(self._order_by)),
                reverse=self._order_desc,
            )

        total_count = len(filtered)
        if self._offset_count:
            filtered = filtered[self._offset_count:]
        if self._limit_count is not None:
            filtered = filtered[:self._limit_count]

        if self._single:
            data = filtered[0] if filtered else None
        else:
            data = filtered

        return MockPostgrestResponse(data=data, count=total_count)


class InMemoryAuth:
    """Simulates Supabase Auth service in-memory."""

    def __init__(self, users_table: List[Dict[str, Any]]):
        self.users = users_table
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def sign_up(self, credentials: Dict[str, Any]):
        email = credentials.get("email")
        password = credentials.get("password")
        options = credentials.get("options", {})
        data = options.get("data", {})
        name = data.get("name") or data.get("full_name") or email.split("@")[0]

        for u in self.users:
            if u["email"].lower() == email.lower():
                raise Exception("User already registered")

        user_id = str(uuid.uuid4())
        user_record = {
            "id": user_id,
            "email": email,
            "name": name,
            "password": password,
            "dailyCalorieTarget": 2200,
            "dailyProteinTargetG": 110,
            "dailyCarbsTargetG": 250,
            "dailyFatTargetG": 65,
            "dailyFiberTargetG": 30,
            "dailySodiumTargetMg": 2300,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.users.append(user_record)

        access_token = f"sb_token_{uuid.uuid4().hex}"
        refresh_token = f"sb_ref_{uuid.uuid4().hex}"
        session_info = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_record,
        }
        self.active_sessions[access_token] = session_info

        class MockAuthResponse:
            def __init__(self, u, token, ref_token):
                self.user = type("MockUser", (), u)
                self.session = type("MockSession", (), {"access_token": token, "refresh_token": ref_token})

        return MockAuthResponse(user_record, access_token, refresh_token)

    def sign_in_with_password(self, credentials: Dict[str, Any]):
        email = credentials.get("email")
        password = credentials.get("password")

        user = next((u for u in self.users if u["email"].lower() == email.lower()), None)
        if not user or user.get("password") != password:
            raise Exception("Invalid login credentials")

        access_token = f"sb_token_{uuid.uuid4().hex}"
        refresh_token = f"sb_ref_{uuid.uuid4().hex}"
        session_info = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }
        self.active_sessions[access_token] = session_info

        class MockAuthResponse:
            def __init__(self, u, token, ref_token):
                self.user = type("MockUser", (), u)
                self.session = type("MockSession", (), {"access_token": token, "refresh_token": ref_token})

        return MockAuthResponse(user, access_token, refresh_token)

    def sign_out(self, jwt_token: Optional[str] = None):
        if jwt_token and jwt_token in self.active_sessions:
            del self.active_sessions[jwt_token]
        return True

    def get_user(self, jwt_token: str):
        session = self.active_sessions.get(jwt_token)
        if session:
            class MockUserWrapper:
                def __init__(self, u):
                    self.user = type("MockUser", (), u)
            return MockUserWrapper(session["user"])
        return None


class InMemoryStorage:
    """Simulates Supabase Storage service."""

    def __init__(self):
        self.buckets: Dict[str, Dict[str, bytes]] = {"meals": {}}

    def from_(self, bucket_name: str):
        class BucketManager:
            def __init__(self, b_name, b_store):
                self.b_name = b_name
                self.b_store = b_store

            def upload(self, path: str, file_bytes: bytes, file_options: Optional[dict] = None):
                self.b_store.setdefault(self.b_name, {})[path] = file_bytes
                return {"path": path}

            def get_public_url(self, path: str):
                return f"https://mock-supabase.storage.co/{self.b_name}/{path}"

        return BucketManager(bucket_name, self.buckets)


class InMemorySupabaseClient:
    """High-fidelity In-Memory Supabase Client for offline testing & dev."""

    def __init__(self):
        self.tables: Dict[str, List[Dict[str, Any]]] = {
            "users": [],
            "user_profiles": [],
            "meals": [],
            "meal_items": [],
            "meal_item_feedback_logs": [],
        }
        self.auth = InMemoryAuth(self.tables["users"])
        self.storage = InMemoryStorage()
        self._init_demo_data()

    def _init_demo_data(self):
        demo_user = {
            "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "email": "balkisu@docta.ng",
            "name": "Balkisu Habib",
            "password": "demo1234",
            "dailyCalorieTarget": 2200,
            "dailyProteinTargetG": 110,
            "dailyCarbsTargetG": 250,
            "dailyFatTargetG": 65,
            "dailyFiberTargetG": 30,
            "dailySodiumTargetMg": 2300,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.tables["users"].append(demo_user)
        self.tables["user_profiles"].append(dict(demo_user))

    def table(self, table_name: str) -> InMemoryQueryBuilder:
        return self.from_(table_name)

    def from_(self, table_name: str) -> InMemoryQueryBuilder:
        if table_name not in self.tables:
            self.tables[table_name] = []
        return InMemoryQueryBuilder(table_name, self.tables[table_name])

    def reset(self):
        """Clears test tables and re-seeds default user."""
        for t in self.tables:
            self.tables[t].clear()
        self.auth.active_sessions.clear()
        self._init_demo_data()


# Global Supabase client instance
_supabase_client = None
_supabase_storage_client = None
_supabase_auth_client = None


def _is_placeholder_credential(value: Optional[str]) -> bool:
    """Treat example/docs values as unset so they cannot mask a real key."""
    if value is None:
        return True
    text = value.strip().lower()
    if not text:
        return True
    return (
        text.startswith("https://your-project")
        or text.startswith("http://placeholder")
        or "your-supabase" in text
        or text.startswith("your-")
        or text.endswith("-key")
        and "your-" in text
    )


def get_supabase_client():
    """Retrieve the server-side database client or fail clearly.

    This client may use the service-role key and must not be used to sign users
    in. Auth sessions are mutable client state, so authentication uses its own
    isolated client below.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    settings = get_settings()
    url = settings.supabase_url
    service_role = settings.supabase_service_role_key
    anon_or_secret = settings.supabase_key
    key = None
    if service_role and not _is_placeholder_credential(service_role):
        key = service_role
    elif anon_or_secret and not _is_placeholder_credential(anon_or_secret):
        key = anon_or_secret

    if not url or _is_placeholder_credential(url):
        raise RuntimeError("SUPABASE_URL must point to the live Supabase project.")
    if not key:
        raise RuntimeError("SUPABASE_KEY or SUPABASE_SERVICE_ROLE_KEY is required for live Supabase.")

    from supabase import create_client
    _supabase_client = create_client(url, key)
    logger.info("Initialized live Supabase client.")
    return _supabase_client


def get_supabase_auth_client():
    """Return an isolated Supabase client for Auth API operations only."""
    global _supabase_auth_client
    if isinstance(_supabase_client, InMemorySupabaseClient):
        return _supabase_client
    if _supabase_auth_client is not None:
        return _supabase_auth_client

    settings = get_settings()
    url = settings.supabase_url
    # Prefer the public/anon key for Auth API requests. Falling back to the
    # configured server key preserves deployments that only define one key.
    key = settings.supabase_key
    if not key or _is_placeholder_credential(key):
        key = settings.supabase_service_role_key

    if not url or _is_placeholder_credential(url):
        raise RuntimeError("SUPABASE_URL must point to the live Supabase project.")
    if not key or _is_placeholder_credential(key):
        raise RuntimeError("SUPABASE_KEY or SUPABASE_SERVICE_ROLE_KEY is required for live Supabase Auth.")

    from supabase import create_client
    _supabase_auth_client = create_client(url, key)
    logger.info("Initialized isolated Supabase Auth client.")
    return _supabase_auth_client


def get_supabase_storage_client():
    """Return an isolated privileged client for server-side Storage operations.

    Keep upload operations on a separate client that is never used for user
    authentication or ordinary database requests.
    """
    global _supabase_storage_client
    if isinstance(_supabase_client, InMemorySupabaseClient):
        return _supabase_client
    if _supabase_storage_client is not None:
        return _supabase_storage_client

    settings = get_settings()
    url = settings.supabase_url
    key = settings.supabase_service_role_key
    if not url or _is_placeholder_credential(url):
        raise RuntimeError("SUPABASE_URL must point to the live Supabase project.")
    if not key or _is_placeholder_credential(key):
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY is required for server-side Storage uploads."
        )

    from supabase import create_client
    _supabase_storage_client = create_client(url, key)
    logger.info("Initialized isolated Supabase Storage client.")
    return _supabase_storage_client


def reset_in_memory_supabase():
    """Explicitly initialize/reset the in-memory store for test fixtures only."""
    global _supabase_client, _supabase_storage_client, _supabase_auth_client
    _supabase_storage_client = None
    _supabase_auth_client = None
    if isinstance(_supabase_client, InMemorySupabaseClient):
        _supabase_client.reset()
    else:
        _supabase_client = InMemorySupabaseClient()
