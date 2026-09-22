# Backend Directive: Core API, Database & MLOps Engine

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Backend Agent, you must operate strictly within `/backend/`. All database schemas, API routes, and service clients must strictly conform to the canonical contracts defined in `/PROJECT_ORCHESTRATION.md`.

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
│   │   ├── mock_ai_service.py         # Dummy AI service for independent development
│   │   ├── mock_rag_service.py        # Dummy RAG service for independent development
│   │   ├── cv_client.py               # Live bridge to ai_services/
│   │   ├── rag_client.py              # Live bridge to data_pipeline/
│   │   └── orchestrator_service.py    # Pipeline coordinator with fallback switches (<2.0s SLA)
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
└── INSTRUCTION.md
```

---

## 3. Dummy / Mock Content Strategy for Independent Development

To allow Backend engineers and autonomous coding agents to develop, test, and deploy database models, authentication, and endpoint orchestration without waiting for the ML Team to complete training or Qdrant to be indexed:

### 3.1. Mock Configuration in `.env`
```env
# Backend Environment Flags
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/docta_db
JWT_SECRET=supersecretjwtkeydocta2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Independent Development Fallback Switches
USE_MOCK_AI=true     # Set to false once ML team finishes training in ai_services/
USE_MOCK_RAG=true    # Set to false once data_pipeline/ Qdrant index is live
```

### 3.2. Mock Service Behavior
* **`src/services/mock_ai_service.py`**: Injects simulated detection payloads containing Nigerian Jollof Rice ($272\text{g}$) and Fried Plantain ($150\text{g}$) with normalized bounding box coordinates and simulated latency ($\sim 50\text{ms}$).
* **`src/services/mock_rag_service.py`**: Computes accurate nutrition breakdowns from bundled static WAFCT profiles without network calls.
* **Seamless Live Switch**: When `USE_MOCK_AI=false`, `orchestrator_service.py` dynamically delegates calls to `src/services/cv_client.py` (`ai_services/src/pipeline.py`), requiring zero code refactoring.

---

## 4. Database Schema Specifications (SQLAlchemy 2.0 Async)

### 4.1. `users` Table
* `id`: UUID, Primary Key.
* `email`: String, Unique, Index, Not Null.
* `hashed_password`: String, Not Null.
* `daily_calorie_target`: Integer, default=2000.
* `target_protein_g`: Float, default=100.0.
* `target_fat_g`: Float, default=60.0.
* `target_carbs_g`: Float, default=250.0.
* `created_at`, `updated_at`: DateTime(timezone=True).

### 4.2. `meals` Table
* `id`: UUID, Primary Key.
* `user_id`: UUID, ForeignKey("users.id", ondelete="CASCADE"), Index, Not Null.
* `image_url`: String, Nullable.
* `raw_text_prompt`: Text, Nullable.
* `meal_type`: Enum (`"breakfast"`, `"lunch"`, `"dinner"`, `"snack"`), default=`"lunch"`.
* `total_calories_kcal`, `total_protein_g`, `total_fat_g`, `total_carbs_g`, `total_fiber_g`, `total_sodium_mg`: Float.
* `logged_at`: DateTime(timezone=True), Index, Not Null.

### 4.3. `meal_items` Table
* `id`: UUID, Primary Key.
* `meal_id`: UUID, ForeignKey("meals.id", ondelete="CASCADE"), Index, Not Null.
* `food_name`: String, Not Null.
* `wafct_code`: String, Nullable.
* `gram_weight`: Float, Not Null.
* `calories_kcal`, `protein_g`, `fat_g`, `carbs_g`, `fiber_g`, `sodium_mg`, `calcium_mg`, `iron_mg`: Float.
* `bounding_box`: JSONB / Array of 4 floats `[x_min, y_min, x_max, y_max]`.

---

## 5. API Endpoints & SLA Targets

1. **`POST /api/v1/auth/signup` & `POST /api/v1/auth/login`**: User registration and JWT token creation.
2. **`POST /api/v1/analyze`**: Accepts multipart `image` and optional `text_prompt`. Orchestrates CV/Vision detection and RAG nutrition scaling. Strict SLA: **$< 2.0\text{ seconds}$**.
3. **`POST /api/v1/meals/log`**: Saves approved meal items and totals atomically.
4. **`GET /api/v1/dashboard/summary?date=YYYY-MM-DD`**: Aggregates target vs consumed calories and macros for current user.

---

## 6. Testing & Validation Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run test suite in Mock Mode (zero external dependencies required)
pytest tests/ -v --cov=src --cov-report=term-missing

# 3. Start PostgreSQL container
docker-compose up -d postgres

# 4. Run database migrations
alembic upgrade head

# 5. Start FastAPI development server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 7. Definition of Done (DoD) Checklist

- [ ] Mock services allow full execution of `/api/v1/analyze` without external ML weights or vector databases.
- [ ] SQLAlchemy models and Alembic migrations execute cleanly against PostgreSQL.
- [ ] JWT authentication and route guard dependencies validated.
- [ ] `/api/v1/meals/log` commits atomic records with verified rollback on error.
- [ ] `/api/v1/dashboard/summary` correctly computes consumed sums and target deltas.
- [ ] Test coverage exceeds $85\%$ in `tests/`.


---

## Automated Task Completion & Submission Protocol

When all functional requirements are implemented and local unit tests pass, execute the following submission sequence in the terminal:

### Step 1: Pre-Submission Health Check
Run the local test suite for your module. Do NOT push if any test fails.
* `pytest` (or `npm run build` for Frontend)

### Step 2: Automated Commit, Push & PR Creation
Execute these exact bash commands:

```bash
# 1. Switch to (or create) the dedicated sub-team branch
git checkout -B docta-backend

# 2. Stage and commit changes
git add .
git commit -m "feat(docta-backend): completed subteam task deliverables"

# 3. Push branch to GitHub
git push origin docta-backend

# 4. Open Pull Request via GitHub CLI
gh pr create \
  --title "feat(docta-backend): Completed Backend Deliverables" \
  --body "Automated PR generated by Coding Agent upon completing INSTRUCTION.md tasks. All local tests passed." \
  --base main