# Backend Directive: Complete API, Supabase Database & "Log Everything" Telemetry Engine

## 1. Mission

You are the backend implementation agent for an AI + Computer Vision nutrition logging application.

Your objective is to **finish the backend inside `/backend/` so that the remaining work is primarily configuration of external API keys/services**.

The backend must:

* Use **FastAPI**.
* Use **Supabase as the database/backend infrastructure**.
* Remove the previous SQLAlchemy/Alembic/PostgreSQL-local-database architecture.
* Provide authentication and authorization.
* Implement every backend API route required by the existing frontend.
* Implement the AI/CV nutrition-analysis pipeline with mock fallbacks.
* Implement meal logging and nutrition persistence.
* Implement "Log Everything" telemetry for future ML training.
* Implement dashboard/history/profile functionality required by the frontend.
* Be testable without external AI/CV API keys by using mock services.
* Follow the existing `/PROJECT_ORCHESTRATION.md`.
* Keep implementation simple and avoid unnecessary abstractions.
* Work as autonomously as possible.

**Do not stop after implementing only the routes explicitly listed in this prompt.**

Before coding, inspect the frontend structure and existing backend implementation to determine the complete API contract required by the application.

---

# 2. STRICT DIRECTORY BOUNDARY

You must operate strictly within:

```text
/backend/
```

Do not modify the frontend application.

Do not modify files outside `/backend/`.

You may **read** the frontend and project documentation to understand the required API contract, routes, request payloads, response shapes, authentication expectations, and application flow.

The frontend is the source of truth for identifying missing backend functionality.

---

# 3. FIRST: RECONNAISSANCE BEFORE CODING

Before making implementation changes:

1. Read `/PROJECT_ORCHESTRATION.md`.
2. Inspect the complete `/backend/` directory.
3. Inspect the frontend directory structure.
4. Search the frontend for:

   * `fetch(`
   * `axios`
   * API client utilities
   * `/api/`
   * `/api/v1/`
   * authentication calls
   * login/register/logout flows
   * meal logging
   * meal history
   * dashboard
   * profile
   * image upload
   * food analysis
   * nutrition data
   * saved meals
   * settings
   * delete/update operations
   * any other backend-dependent functionality.
5. Identify every API endpoint the frontend expects.
6. Compare those endpoints against the existing backend.
7. Create an internal checklist of:

   * existing routes that work,
   * existing routes that are incomplete,
   * missing routes,
   * expected request schemas,
   * expected response schemas,
   * authentication requirements,
   * database entities required.

**Do not blindly implement the route list in this document if the frontend requires additional routes.**

The final backend should satisfy the frontend's existing API expectations without requiring frontend changes.

---

# 4. TARGET ARCHITECTURE

Use the following simplified architecture:

```text
Frontend
   |
   | HTTP
   v
FastAPI Backend
   |
   +---- Authentication
   |
   +---- Meal / Nutrition API
   |
   +---- CV / AI orchestration
   |
   +---- Telemetry
   |
   +---- Dashboard / History
   |
   v
Supabase
   |
   +---- PostgreSQL database
   +---- Auth
   +---- Storage (where appropriate)
```

The FastAPI backend remains responsible for application/business logic.

Supabase provides:

* PostgreSQL database
* Authentication
* Storage where useful

External AI/CV/RAG services remain separate services.

---

# 5. DATABASE ARCHITECTURE — SUPABASE

## IMPORTANT

The previous architecture used:

```text
SQLAlchemy
Alembic
asyncpg
local PostgreSQL
Docker PostgreSQL
```

**Remove this architecture.**

Do NOT introduce SQLAlchemy.

Do NOT create an Alembic migration system.

Do NOT require a locally running PostgreSQL container.

Do NOT require `docker-compose up -d postgres`.

Use the Supabase client instead.

The purpose of this change is specifically to make the backend simpler.

---

# 6. SUPABASE DATABASE ACCESS

Use the official Supabase Python client.

Create a simple database client module, for example:

```text
src/supabase_client.py
```

or an equivalent structure if the existing architecture has a better location.

Use environment variables:

```env
SUPABASE_URL=
SUPABASE_KEY=
```

Use the appropriate Supabase key for backend/server-side operations.

Do not hardcode credentials.

Centralize Supabase client initialization.

Avoid creating multiple unnecessary clients.

---

# 7. SUPABASE DATABASE SCHEMA

The database should support at minimum:

```text
users / profiles
meals
meal_items
meal_item_feedback_logs
```

Inspect the frontend and existing backend to determine whether additional tables are required.

Likely additional entities may include:

```text
user_profiles
saved_meals
nutrition_preferences
```

but **do not create unnecessary tables simply because they are listed here**.

Create only what is required by the actual application.

Use UUID primary keys where appropriate.

---

# 8. AUTHENTICATION

Implement the complete authentication API required by the frontend.

At minimum, inspect whether the frontend requires:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/me
POST /api/v1/auth/refresh
```

Implement whichever endpoints the frontend actually requires.

If Supabase Auth is used, leverage Supabase Auth rather than implementing a custom password hashing/JWT system unnecessarily.

The backend should be able to:

1. Register users.
2. Log users in.
3. Log users out.
4. Retrieve the current authenticated user.
5. Validate authenticated requests.
6. Obtain the authenticated user's Supabase identity.
7. Prevent users from accessing another user's meals/profile/data.

Authentication must be enforced on all user-private routes.

Do not trust `user_id` supplied by the frontend when the authenticated identity is available.

Example:

```text
Authenticated user
        |
        v
Supabase access token
        |
        v
FastAPI authentication dependency
        |
        v
authenticated_user.id
        |
        v
database queries filtered by that ID
```

---

# 9. AUTHENTICATION SECURITY

Never:

* accept arbitrary user IDs for authorization,
* allow one user to retrieve another user's meals,
* expose service-role credentials to the frontend,
* store passwords directly,
* hardcode JWT secrets,
* trust frontend-provided authentication claims.

The backend must derive the authenticated user from the Supabase authentication context.

Use Supabase's server-side capabilities appropriately.

---

# 10. COMPLETE ROUTE DISCOVERY

The following routes are required if applicable, but the frontend inspection must determine the final route inventory.

## Authentication

```text
/api/v1/auth/register
/api/v1/auth/login
/api/v1/auth/logout
/api/v1/auth/me
/api/v1/auth/refresh
```

## Health

```text
GET /api/v1/health
```

## AI / CV Analysis

```text
POST /api/v1/analyze
```

## Meals

```text
POST   /api/v1/meals/log
GET    /api/v1/meals
GET    /api/v1/meals/{meal_id}
DELETE /api/v1/meals/{meal_id}
```

Add update endpoints if the frontend requires them.

## Dashboard

Implement whatever dashboard endpoints the frontend requires.

Potential examples:

```text
GET /api/v1/dashboard
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/nutrition
GET /api/v1/dashboard/recent-meals
```

Do not create duplicate endpoints if a single existing endpoint can satisfy the frontend.

## Profile

If required by the frontend:

```text
GET   /api/v1/profile
PATCH /api/v1/profile
```

## Storage

If images are uploaded through the backend, implement the required upload flow.

Use Supabase Storage where appropriate.

Inspect the frontend first to determine whether it uploads:

* directly to Supabase Storage,
* through FastAPI,
* or through another service.

Do not create unnecessary proxy endpoints.

## Telemetry

```text
GET /api/v1/telemetry/export
```

Restrict this endpoint to the appropriate admin/ML authorization level.

---

# 11. `POST /api/v1/analyze`

This is the primary AI/CV pipeline endpoint.

Flow:

```text
Frontend
   |
   | image
   v
FastAPI
   |
   +--> CV service
   |
   +--> RAG/Nutrition service
   |
   v
Composite nutrition response
```

The endpoint must:

1. Receive the image/input expected by the frontend.
2. Send it to the CV service.
3. Receive detected food items.
4. Receive bounding boxes.
5. Receive confidence values.
6. Send detected foods to the nutrition/RAG service.
7. Attach nutrition information.
8. Attach available portion units.
9. Return a frontend-compatible response.

Each detected food should support information equivalent to:

```json
{
  "dish_id": "jollof_rice",
  "name": "Jollof Rice",
  "confidence": 0.94,
  "bounding_box": [0.1, 0.2, 0.5, 0.7],
  "nutrition_per_100g": {
    "calories": 180,
    "protein": 4.5,
    "carbohydrates": 28,
    "fat": 6
  },
  "available_portion_units": [
    {
      "unit_id": "serving_spoon",
      "name": "Serving Spoon",
      "grams_per_unit": 120
    }
  ]
}
```

Adapt this to the actual frontend contract.

---

# 12. MOCK AI / RAG MODE

The backend must remain fully runnable without external AI API keys.

Environment variables:

```env
USE_MOCK_AI=true
USE_MOCK_RAG=true
```

When enabled:

```text
mock_ai_service.py
```

should return deterministic mock detections.

For example:

```text
Jollof Rice
Plantain
```

with realistic:

* confidence
* bounding box
* dish ID

The mock RAG service should provide:

* nutrition information
* available portion units
* grams-per-unit
* relevant nutrition fields.

This allows the entire frontend → backend → database workflow to be tested before external services are connected.

---

# 13. LIVE SERVICE CLIENTS

Keep external integrations behind clean interfaces.

For example:

```text
cv_client.py
rag_client.py
```

The orchestrator should decide whether to use:

```text
mock_ai_service
```

or:

```text
cv_client
```

based on configuration.

Do the same for RAG/nutrition.

Do not scatter external API calls throughout routers.

---

# 14. MEAL LOGGING

Implement:

```text
POST /api/v1/meals/log
```

This endpoint must save a complete meal.

The operation should conceptually be:

```text
Authenticated user
       |
       v
Validate meal payload
       |
       +--> Create meal
       |
       +--> Create meal_items
       |
       +--> Create telemetry records
       |
       v
Return meal summary
```

Because Supabase is being used instead of SQLAlchemy transactions, implement the safest practical atomic strategy supported by the chosen Supabase architecture.

Prefer a database-side RPC/function for genuinely atomic multi-table insertion if necessary.

The goal is:

> Either the complete meal + meal items + telemetry are persisted, or the operation fails without leaving inconsistent partial data.

Do not fake transactionality by simply making multiple unrelated requests and assuming they will succeed.

---

# 15. DATABASE TABLE: `meal_item_feedback_logs`

This table is critical.

It is the "Log Everything" dataset used for future ML training.

Required fields:

```text
id
user_id
meal_id
meal_item_id
image_url
predicted_dish_id
predicted_confidence
bounding_box
final_dish_id
label_modified
selected_unit_id
selected_quantity
calculated_gram_weight
custom_weight_entered_g
logged_at
```

Recommended types:

```text
id                       UUID
user_id                  UUID
meal_id                  UUID
meal_item_id             UUID
image_url                TEXT
predicted_dish_id        TEXT
predicted_confidence     FLOAT
bounding_box              JSONB
final_dish_id             TEXT
label_modified            BOOLEAN
selected_unit_id          TEXT
selected_quantity         FLOAT
calculated_gram_weight   FLOAT
custom_weight_entered_g  FLOAT NULL
logged_at                 TIMESTAMPTZ
```

Add indexes for:

```text
user_id
meal_id
meal_item_id
logged_at
```

Use foreign keys where appropriate.

---

# 16. TELEMETRY REQUIREMENTS

Every saved meal item must produce a telemetry record.

Telemetry must preserve the difference between:

```text
AI prediction
```

and:

```text
user-confirmed/final decision
```

For example:

```text
predicted_dish_id = "jollof_rice"

final_dish_id = "fried_rice"

label_modified = true
```

The telemetry must also capture portion decisions:

```text
selected_unit_id
selected_quantity
calculated_gram_weight
custom_weight_entered_g
```

This data should make it possible to construct a future supervised dataset for:

* food classification correction,
* portion estimation,
* portion-unit preference analysis,
* food frequency analysis.

---

# 17. TELEMETRY EXPORT

Implement:

```text
GET /api/v1/telemetry/export
```

It must support exporting the telemetry dataset in a format useful for ML development.

At minimum support:

```text
JSON
CSV
```

Use a query parameter if appropriate:

```text
?format=json
?format=csv
```

Restrict this endpoint to authorized admin/ML users.

Do not expose all users' telemetry to ordinary users.

Do not include unnecessary sensitive user information in the export.

---

# 18. MEAL HISTORY

Inspect the frontend and implement the complete meal-history functionality it requires.

The backend should support:

* listing the authenticated user's meals,
* pagination if needed,
* retrieving a specific meal,
* nutrition summaries,
* meal item details,
* timestamps,
* deletion if supported by the frontend.

Every query must be scoped to the authenticated user.

For example:

```text
GET /api/v1/meals
```

must never return another user's meals.

---

# 19. DASHBOARD

Inspect the frontend dashboard carefully.

Implement every backend data source required for:

* calories
* macros
* meal counts
* recent meals
* daily/weekly summaries
* nutrition trends
* any other metrics displayed by the frontend.

Prefer computing these from the persisted meal data rather than duplicating information unnecessarily.

If an endpoint can return the dashboard data efficiently in one response, prefer that over creating many unnecessary endpoints.

---

# 20. PROFILE / USER DATA

If the frontend contains a profile/settings page, implement its backend requirements.

Support only fields actually used by the application.

Examples might include:

```text
name
age
weight
height
gender
activity level
nutrition goal
daily calorie target
```

Do not invent fields unless the frontend or project specification requires them.

---

# 21. STORAGE

Inspect how the frontend handles meal images.

If the frontend expects backend-managed uploads:

```text
POST /api/v1/storage/upload
```

may be implemented.

If the frontend already uploads directly to Supabase Storage, do not create an unnecessary FastAPI upload proxy.

Use Supabase Storage for persistent meal images where appropriate.

The backend should store the resulting image URL/path with the relevant meal/meal item/telemetry data.

---

# 22. PYDANTIC SCHEMAS

Use Pydantic v2.

Maintain a clean separation:

```text
Request schemas
Response schemas
Database/domain structures
```

Do not duplicate schemas unnecessarily.

Ensure all API responses match what the frontend expects.

Use validation for:

* quantities
* gram weights
* IDs
* confidence values
* portion units
* meal items
* image references.

---

# 23. PROJECT STRUCTURE

The final structure should be approximately:

```text
backend/

├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── supabase_client.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── analyze.py
│   │   ├── meal.py
│   │   ├── telemetry.py
│   │   ├── dashboard.py
│   │   └── profile.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── storage_service.py
│   │   ├── mock_ai_service.py
│   │   ├── mock_rag_service.py
│   │   ├── cv_client.py
│   │   ├── rag_client.py
│   │   ├── telemetry_service.py
│   │   └── orchestrator_service.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth_router.py
│   │   ├── analyze_router.py
│   │   ├── meal_router.py
│   │   ├── telemetry_router.py
│   │   ├── dashboard_router.py
│   │   ├── profile_router.py
│   │   └── health_router.py
│   │
│   └── dependencies/
│       ├── __init__.py
│       └── auth.py
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_analyze_flow.py
│   ├── test_meals_and_telemetry.py
│   ├── test_dashboard.py
│   └── test_profile.py
│
├── requirements.txt
├── .env.example
└── INSTRUCTION.md
```

Adapt the structure to the existing repository instead of unnecessarily restructuring working code.

---

# 24. REMOVE OBSOLETE DATABASE INFRASTRUCTURE

Because Supabase replaces the local PostgreSQL/SQLAlchemy architecture, remove obsolete components where they are no longer needed:

```text
alembic/
alembic.ini
database.py
SQLAlchemy models
asyncpg dependency
docker-compose PostgreSQL service
PostgreSQL-specific local setup instructions
```

Do not blindly delete files.

First determine whether anything still depends on them.

Then remove or replace them cleanly.

The final project should not require:

```bash
docker-compose up -d postgres
```

or:

```bash
alembic upgrade head
```

to operate.

---

# 25. ENVIRONMENT VARIABLES

Create/update `.env.example`.

At minimum:

```env
SUPABASE_URL=
SUPABASE_KEY=

USE_MOCK_AI=true
USE_MOCK_RAG=true

CV_SERVICE_URL=
RAG_SERVICE_URL=

ENVIRONMENT=development
```

Add only environment variables actually required by the implementation.

Never commit real secrets.

---

# 26. DEPENDENCIES

Update:

```text
requirements.txt
```

Remove dependencies that are no longer needed.

Add the Supabase Python client.

Keep dependencies minimal.

Do not add a library merely because it is convenient if the functionality can easily be implemented with existing dependencies.

---

# 27. ERROR HANDLING

Implement consistent API errors.

Examples:

```text
400 - invalid request
401 - unauthenticated
403 - unauthorized
404 - resource not found
422 - validation error
500 - internal server error
503 - external AI/RAG service unavailable
```

Do not leak:

* database credentials,
* service-role keys,
* stack traces,
* internal secrets,
* unnecessary implementation details.

---

# 28. CORS

Inspect the frontend configuration and configure CORS appropriately.

Use an environment variable for allowed frontend origins where practical.

Example:

```env
FRONTEND_URL=http://localhost:3000
```

Do not use unrestricted CORS in production unless explicitly required.

---

# 29. TESTING STRATEGY

The backend must be testable without real external AI services.

Use:

```env
USE_MOCK_AI=true
USE_MOCK_RAG=true
```

for automated tests.

Test at minimum:

### Authentication

* registration
* login
* logout
* current-user retrieval
* unauthorized access
* cross-user access prevention

### Analyze

* valid analysis request
* mock CV result
* mock RAG result
* portion units
* nutrition information
* validation errors

### Meals

* create meal
* create meal items
* retrieve meals
* retrieve individual meal
* prevent cross-user access
* delete if supported

### Telemetry

Verify that creating a meal creates telemetry for **every meal item**.

Verify:

```text
predicted_dish_id
final_dish_id
label_modified
selected_unit_id
selected_quantity
calculated_gram_weight
```

are persisted correctly.

### Dashboard

Test the calculations against known meal data.

### Profile

Test retrieval/update if applicable.

---

# 30. TEST COVERAGE

Target:

```text
>= 85%
```

Do not artificially inflate coverage with meaningless tests.

Prioritize testing business logic, authentication, database interactions, route authorization, meal logging, and telemetry.

---

# 31. API DOCUMENTATION

FastAPI's generated documentation should accurately expose the API.

Ensure:

```text
/docs
/redoc
```

work correctly.

Use clear:

* endpoint descriptions,
* request models,
* response models,
* authentication requirements,
* status codes.

---

# 32. PERFORMANCE

The analysis pipeline has an intended target of approximately:

```text
< 2 seconds
```

when external services permit it.

Do not add unnecessary sequential operations.

Where appropriate:

* parallelize independent external calls,
* avoid unnecessary database queries,
* avoid repeatedly fetching the same data,
* keep payloads reasonable.

Do not sacrifice correctness or simplicity for premature optimization.

---

# 33. CODE QUALITY

Follow these principles:

### Prefer simple code.

Do not create elaborate abstractions for a small application.

### Keep responsibilities separated.

Routers should primarily:

```text
receive request
validate request
authenticate user
call service
return response
```

Business logic belongs in services.

### Avoid duplication.

### Use type hints.

### Use async where it genuinely helps.

### Keep external integrations isolated.

### Do not over-engineer.

The goal is a backend that is:

```text
simple
maintainable
testable
extensible
```

---

# 34. FRONTEND CONTRACT IS AUTHORITATIVE

This is extremely important.

If the frontend currently expects:

```text
GET /api/v1/something
```

with a particular request/response structure, implement that contract rather than inventing a different API and requiring frontend modifications.

Inspect the frontend to determine:

* endpoint paths
* HTTP methods
* request bodies
* query parameters
* authentication headers
* response fields
* error expectations.

If the frontend contains an API client abstraction, inspect that first.

---

# 35. DO NOT MODIFY FRONTEND

The backend agent may inspect frontend files.

It must **not modify them**.

If a frontend/backend mismatch is discovered:

1. Determine whether the backend can accommodate the existing frontend contract.
2. Prefer compatibility in the backend.
3. Only report an unavoidable incompatibility in the final summary.

Do not silently modify frontend code.

---

# 36. EXECUTION STRATEGY — TOKEN EFFICIENT

Work in the following order:

```text
PHASE 1
Repository reconnaissance
        ↓
PHASE 2
Frontend API contract discovery
        ↓
PHASE 3
Supabase architecture migration
        ↓
PHASE 4
Authentication
        ↓
PHASE 5
Core analysis pipeline
        ↓
PHASE 6
Meals + telemetry
        ↓
PHASE 7
Dashboard/history/profile/storage
        ↓
PHASE 8
Tests
        ↓
PHASE 9
Final integration validation
```

Do not repeatedly reread large files unnecessarily.

Use targeted searches to discover:

* route usage,
* API calls,
* environment variables,
* database references,
* TODOs,
* unimplemented functions.

Prioritize implementation over lengthy explanations.

Do not ask for confirmation for ordinary implementation decisions.

Make reasonable engineering decisions autonomously.

---

# 37. EXTERNAL SERVICE KEYS

The final backend should be capable of running in mock mode without external AI/CV/RAG keys.

The intended final state is:

```text
Supabase credentials
        +
optional external service credentials
        |
        v
Complete application
```

The following should be the only remaining configuration-dependent work where possible:

```text
SUPABASE_URL
SUPABASE_KEY
CV/API keys
RAG/LLM API keys
other genuinely external credentials
```

Do not leave core application routes as TODOs merely because external services are unavailable.

Use mocks/interfaces so the routes are complete.

---

# 38. FINAL VALIDATION

Before declaring the task complete:

1. Run the test suite.
2. Fix all failures.
3. Verify imports.
4. Verify FastAPI startup.
5. Verify route registration.
6. Verify `/docs`.
7. Verify authentication dependencies.
8. Verify Supabase connection initialization.
9. Verify meal persistence.
10. Verify telemetry persistence.
11. Verify user isolation.
12. Verify mock AI analysis.
13. Verify mock RAG nutrition data.
14. Verify frontend-required routes exist.
15. Search the frontend one final time for API calls and confirm each has a backend implementation.
16. Search the backend for:

* TODO
* FIXME
* `pass`
* `NotImplemented`
* placeholder responses
* mock implementations accidentally being used when live mode is configured.

17. Remove obsolete SQLAlchemy/Alembic/local-Postgres dependencies.
18. Ensure `.env.example` contains every required configuration variable.

Run appropriate commands such as:

```bash
pip install -r requirements.txt

pytest tests/ -v --cov=src --cov-report=term-missing

uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Do not require Docker PostgreSQL or Alembic.

---

# 39. DEFINITION OF DONE

The backend is complete only when all applicable items below are satisfied.

## Architecture

* [ ] FastAPI backend works.
* [ ] Supabase is the database/backend infrastructure.
* [ ] SQLAlchemy is completely removed.
* [ ] Alembic is completely removed.
* [ ] Local PostgreSQL is no longer required.
* [ ] Database configuration is centralized.
* [ ] Secrets are environment-based.

## Authentication

* [ ] Required auth routes exist.
* [ ] Supabase authentication is integrated.
* [ ] Authenticated user identity is available to protected routes.
* [ ] Users cannot access another user's private data.
* [ ] Logout/session behavior works as required by the frontend.

## Frontend integration

* [ ] Frontend structure was inspected.
* [ ] All frontend API calls were identified.
* [ ] Every required backend route exists.
* [ ] Request schemas match frontend usage.
* [ ] Response schemas match frontend usage.
* [ ] No frontend files were modified.

## AI/CV

* [ ] `/api/v1/analyze` exists.
* [ ] CV integration interface exists.
* [ ] RAG/nutrition integration interface exists.
* [ ] Mock CV mode works.
* [ ] Mock RAG mode works.
* [ ] Detected foods contain confidence/bounding boxes.
* [ ] Nutrition information is attached.
* [ ] `available_portion_units` is returned.

## Meals

* [ ] `/api/v1/meals/log` exists.
* [ ] Meals are persisted.
* [ ] Meal items are persisted.
* [ ] User ownership is enforced.
* [ ] Meal retrieval works.
* [ ] Required update/delete functionality exists.

## Telemetry

* [ ] `meal_item_feedback_logs` exists.
* [ ] Every logged meal item produces a telemetry record.
* [ ] `predicted_dish_id` is captured.
* [ ] `final_dish_id` is captured.
* [ ] `label_modified` is captured.
* [ ] `selected_unit_id` is captured.
* [ ] `selected_quantity` is captured.
* [ ] `calculated_gram_weight` is captured.
* [ ] `custom_weight_entered_g` is captured.
* [ ] `/api/v1/telemetry/export` exists.
* [ ] JSON export works.
* [ ] CSV export works.
* [ ] Export access is restricted.

## Dashboard / user functionality

* [ ] All frontend-required dashboard endpoints exist.
* [ ] Meal history works.
* [ ] Profile functionality works if required.
* [ ] Storage functionality works if required.

## Testing

* [ ] Tests pass.
* [ ] Coverage is >= 85% where reasonably achievable.
* [ ] Authentication is tested.
* [ ] Authorization is tested.
* [ ] Analyze flow is tested.
* [ ] Meal logging is tested.
* [ ] Telemetry is tested.
* [ ] Dashboard is tested.
* [ ] Cross-user access is tested.

## Final state

The backend should be runnable with:

```env
USE_MOCK_AI=true
USE_MOCK_RAG=true
SUPABASE_URL=<supabase project url>
SUPABASE_KEY=<supabase backend key>
```

and should provide a complete working backend without requiring external AI/CV/RAG credentials.

When external API keys are later supplied, switching from mock implementations to live integrations should require configuration changes rather than rewriting the API layer.

---

# 40. FINAL REPORT

At the end, provide a concise implementation report containing:

```text
1. What was implemented
2. Routes discovered from the frontend
3. Routes added
4. Supabase schema/tables created or expected
5. Authentication implementation
6. AI/CV integration status
7. Telemetry implementation
8. Tests run + results
9. Coverage
10. Remaining external credentials/configuration required
11. Any genuine blockers
```

Do not provide a long narrative.

If everything is complete, explicitly state:

```text
BACKEND IMPLEMENTATION COMPLETE
```

and list only the remaining configuration items.
