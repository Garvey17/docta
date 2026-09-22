# Sub-Team 3 Directive: Core API, Database & MLOps Engine

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Sub-Team 3 Autonomous Agent, you must operate exclusively within `/subteam-3-backend-mlops/`. All inter-module orchestrations must be executed through clean client interfaces or published modules conforming to `/PROJECT_ORCHESTRATION.md`.

---

## 2. Directory Structure Tree

```
subteam-3-backend-mlops/
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
│   │   └── meal_item.py
│   ├── schemas/                       # Pydantic v2 request/response validation schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── analyze.py
│   │   ├── meal.py
│   │   └── dashboard.py
│   ├── services/                      # Business logic & external microservice clients
│   │   ├── __init__.py
│   │   ├── auth_service.py            # Password hashing (bcrypt) & JWT issuance
│   │   ├── storage_service.py         # Local / S3 / Supabase image uploader
│   │   ├── cv_client.py               # Sub-team 1 Vision Pipeline bridge
│   │   ├── rag_client.py              # Sub-team 2 RAG Engine bridge
│   │   └── orchestrator_service.py    # Pipeline coordinator (<2.0s SLA)
│   └── routers/                       # FastAPI endpoint route controllers
│       ├── __init__.py
│       ├── auth_router.py             # /api/v1/auth
│       ├── analyze_router.py          # /api/v1/analyze
│       ├── meal_router.py             # /api/v1/meals
│       ├── dashboard_router.py        # /api/v1/dashboard
│       └── health_router.py           # /healthz & /ready
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_analyze_flow.py
│   ├── test_meals.py
│   └── test_dashboard.py
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml                 # Orchestration for FastAPI, Postgres & Qdrant
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## 3. Detailed Functional Requirements

### 3.1. Relational Database Schema (SQLAlchemy 2.0 / PostgreSQL)

#### 1. `users` Table
* `id` (UUID, Primary Key, default=uuid4)
* `email` (String, Unique, Index, Nullable=False)
* `hashed_password` (String, Nullable=False)
* `daily_calorie_target` (Integer, default=2000)
* `target_protein_g` (Float, default=100.0)
* `target_fat_g` (Float, default=60.0)
* `target_carbs_g` (Float, default=250.0)
* `created_at` (DateTime with timezone, default=utcnow)
* `updated_at` (DateTime with timezone, onupdate=utcnow)

#### 2. `meals` Table
* `id` (UUID, Primary Key, default=uuid4)
* `user_id` (UUID, ForeignKey("users.id", ondelete="CASCADE"), Index, Nullable=False)
* `image_url` (String, Nullable=True)
* `raw_text_prompt` (Text, Nullable=True)
* `meal_type` (Enum: `"breakfast"`, `"lunch"`, `"dinner"`, `"snack"`, default=`"lunch"`)
* `total_calories_kcal` (Float, Nullable=False)
* `total_protein_g` (Float, Nullable=False)
* `total_fat_g` (Float, Nullable=False)
* `total_carbs_g` (Float, Nullable=False)
* `total_fiber_g` (Float, default=0.0)
* `total_sodium_mg` (Float, default=0.0)
* `logged_at` (DateTime with timezone, Index, Nullable=False)
* `created_at` (DateTime with timezone, default=utcnow)

#### 3. `meal_items` Table
* `id` (UUID, Primary Key, default=uuid4)
* `meal_id` (UUID, ForeignKey("meals.id", ondelete="CASCADE"), Index, Nullable=False)
* `food_name` (String, Nullable=False)
* `wafct_code` (String, Nullable=True)
* `gram_weight` (Float, Nullable=False)
* `calories_kcal` (Float, Nullable=False)
* `protein_g` (Float, Nullable=False)
* `fat_g` (Float, Nullable=False)
* `carbs_g` (Float, Nullable=False)
* `fiber_g` (Float, default=0.0)
* `sodium_mg` (Float, default=0.0)
* `calcium_mg` (Float, default=0.0)
* `iron_mg` (Float, default=0.0)
* `bounding_box` (JSONB / Array of 4 floats `[x_min, y_min, x_max, y_max]`, Nullable=True)

---

### 3.2. Core API Endpoints

#### 1. Authentication (`/api/v1/auth`)
* `POST /api/v1/auth/signup`: Accepts `email`, `password`. Creates user, returns JWT access token.
* `POST /api/v1/auth/login`: Validates credentials, returns JWT bearer token (`access_token`, `token_type: "bearer"`).

#### 2. Multimodal Analysis Orchestration (`/api/v1/analyze`)
* `POST /api/v1/analyze`:
  * Accepts `image: UploadFile` (JPEG/PNG $\le 10\text{MB}$) and optional `text_prompt: Optional[str]`.
  * Asynchronously coordinates:
    1. Uploads image to storage service $\rightarrow$ generates URL.
    2. Invokes CV/Multimodal engine (`Sub-team 1`) with image and user text prompt.
    3. Transforms detected item labels into RAG queries for nutrition scaling (`Sub-team 2`).
    4. Merges nutrition data with bounding box coordinates.
  * **SLA Constraint**: Must return completed payload in **$< 2.0\text{ seconds}$**.

#### 3. Meal Logging (`/api/v1/meals/log`)
* `POST /api/v1/meals/log`:
  * Saves finalized user-approved meal items and nutrition aggregates to PostgreSQL within a single atomic database transaction.

#### 4. Dashboard Analytics (`/api/v1/dashboard/summary`)
* `GET /api/v1/dashboard/summary?date=YYYY-MM-DD`:
  * Aggregates all meals logged by current authenticated user for target date.
  * Calculates consumed vs. target calories and macronutrients, remaining allowances, and historical meal breakdown.

---

### 3.3. Middleware & Security
* **CORS**: Configure `CORSMiddleware` permitting frontend origins (`http://localhost:3000`, production domain).
* **JWT Guard**: Dependency `get_current_user` enforcing bearer token verification on all protected endpoints.
* **Request ID & Timing**: Middleware adding `X-Request-ID` and `X-Response-Time-Ms` headers for observability.

---

## 4. Testing & Validation Commands

```bash
# 1. Install Sub-team 3 dependencies
pip install -r requirements.txt

# 2. Start PostgreSQL and Qdrant services
docker-compose up -d postgres qdrant

# 3. Apply database migrations
alembic upgrade head

# 4. Start FastAPI server locally
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Run test suite
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 5. Docker Infrastructure Configuration

The `docker-compose.yml` must orchestrate:
1. `postgres`: PostgreSQL 16 on port `5432` with healthcheck.
2. `qdrant`: Qdrant Vector DB on port `6333`.
3. `api`: FastAPI application on port `8000` with hot-reloading in development.

---

## 6. Definition of Done (DoD) Checklist

- [ ] Database models and Alembic migration scripts generate valid schemas on PostgreSQL.
- [ ] JWT authentication lifecycle (signup, login, token refresh, route protection) verified.
- [ ] `POST /api/v1/analyze` coordinates CV and RAG services, returning normalized responses in $< 2.0\text{s}$.
- [ ] `POST /api/v1/meals/log` commits atomic transactions for meal and itemized child rows.
- [ ] `GET /api/v1/dashboard/summary` computes accurate macro sums and remaining targets.
- [ ] `docker-compose up` spins up healthy containers across FastAPI, Postgres, and Qdrant.
- [ ] Unit and integration test coverage $\ge 85\%$.
