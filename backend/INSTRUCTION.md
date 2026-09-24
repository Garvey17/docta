# Backend Directive: Core API, Database & "Log Everything" Telemetry Engine

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Backend Agent, you must operate strictly within `/backend/`. All database schemas, API routes, and telemetry loggers must strictly conform to `/PROJECT_ORCHESTRATION.md`.

---

## 2. Directory Structure Tree

```
backend/
├── alembic/                           # Database migration scripts
│   ├── versions/
│   └── env.py
├── src/
│   ├── __init__.py
│   ├── main.py                        # FastAPI application entrypoint & middleware
│   ├── config.py                      # Pydantic BaseSettings environment manager
│   ├── database.py                    # Async SQLAlchemy 2.0 engine & session maker
│   ├── models/                        # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── meal.py
│   │   ├── meal_item.py
│   │   └── meal_item_feedback_log.py  # [NEW] "Log Everything" active learning telemetry
│   ├── schemas/                       # Pydantic v2 validation schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── analyze.py                 # Schemas including available_portion_units
│   │   ├── meal.py                    # Schemas with portion units & decision flags
│   │   ├── telemetry.py               # Schemas for ML dataset export
│   │   └── dashboard.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── storage_service.py
│   │   ├── mock_ai_service.py         # Injects mock detections + portion units
│   │   ├── mock_rag_service.py        # Injects mock RIQ nutrition
│   │   ├── cv_client.py               # Live bridge to ai_services/
│   │   ├── rag_client.py              # Live bridge to data_pipeline/
│   │   ├── telemetry_service.py       # Decision logger service for ML dataset
│   │   └── orchestrator_service.py    # Pipeline coordinator (<2.0s SLA)
│   └── routers/
│       ├── __init__.py
│       ├── auth_router.py
│       ├── analyze_router.py          # /api/v1/analyze (returns foods + portion units)
│       ├── meal_router.py             # /api/v1/meals (saves meal + logs decisions)
│       ├── telemetry_router.py        # /api/v1/telemetry/export (ML dataset export)
│       ├── dashboard_router.py
│       └── health_router.py
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_analyze_flow.py
│   ├── test_meals_and_telemetry.py    # Verifies decision logging on meal creation
│   └── test_dashboard.py
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── INSTRUCTION.md
```

---

## 3. "Log Everything" Telemetry Architecture

Every time a user saves a meal via `POST /api/v1/meals/log`, the backend must write to `meal_item_feedback_logs` to build the ground-truth training dataset for future portion-size models and track real-world food frequency.

### 3.1. Database Schema (`models/meal_item_feedback_log.py`)
* `id` (UUID, Primary Key, default=uuid4)
* `user_id` (UUID, ForeignKey("users.id", ondelete="SET NULL"), Index)
* `meal_id` (UUID, ForeignKey("meals.id", ondelete="CASCADE"), Index)
* `meal_item_id` (UUID, ForeignKey("meal_items.id", ondelete="CASCADE"))
* `image_url` (String, Not Null)
* `predicted_dish_id` (String, Not Null) - e.g., `"jollof_rice"`
* `predicted_confidence` (Float, Not Null) - e.g., `0.94`
* `bounding_box` (JSONB) - `[x_min, y_min, x_max, y_max]`
* `final_dish_id` (String, Not Null) - e.g., `"jollof_rice"` or corrected to `"fried_rice"`
* `label_modified` (Boolean, Not Null) - `true` if user corrected the prediction
* `selected_unit_id` (String, Not Null) - e.g., `"serving_spoon"`, `"medium_wrap"`
* `selected_quantity` (Float, Not Null) - e.g., `2.0`
* `calculated_gram_weight` (Float, Not Null) - e.g., `240.0`
* `custom_weight_entered_g` (Float, Nullable)
* `logged_at` (DateTime with timezone, default=utcnow, Index)

---

## 4. Core Endpoint Flow & Schemas

### 4.1. `POST /api/v1/analyze`
1. Calls CV service (`ai_services/` or `mock_ai_service.py`) $\rightarrow$ retrieves detected dishes and bounding boxes.
2. Calls Data/RAG service (`data_pipeline/` or `mock_rag_service.py`) $\rightarrow$ attaches `available_portion_units` and base per-100g nutrition for each detected dish.
3. Returns composite payload with available units for user selection.

### 4.2. `POST /api/v1/meals/log`
1. Within a single atomic database transaction:
   * Inserts row into `meals`.
   * Inserts child rows into `meal_items`.
   * Inserts telemetry rows into `meal_item_feedback_logs` for every item.
2. Returns success response and meal summary.

### 4.3. `GET /api/v1/telemetry/export` (Admin / ML Team)
* Supports exporting logged user decisions as JSON/CSV for the ML team to train future portion-size models.

---

## 5. Independent Development & Mock Mode

```env
USE_MOCK_AI=true     # Injects mock food items (Jollof Rice, Plantain)
USE_MOCK_RAG=true    # Injects mock portion units and WAFCT macros
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/docta_db
```

---

## 6. Testing & Validation Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run unit & integration test suite (verifying decision logging)
pytest tests/ -v --cov=src --cov-report=term-missing

# 3. Start DB and run migrations
docker-compose up -d postgres
alembic upgrade head

# 4. Start FastAPI server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 7. Definition of Done (DoD) Checklist

- [ ] `/api/v1/analyze` attaches `available_portion_units` to each detected food item.
- [ ] `/api/v1/meals/log` saves meal records AND writes decision records to `meal_item_feedback_logs`.
- [ ] Telemetry captures `predicted_dish_id`, `final_dish_id`, `label_modified`, `selected_unit_id`, `selected_quantity`, and `calculated_gram_weight`.
- [ ] `/api/v1/telemetry/export` returns formatted dataset for the ML team.
- [ ] Test coverage $\ge 85\%$ in `tests/`.