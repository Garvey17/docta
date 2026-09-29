# Docta — End-to-End Application Integration

You are the implementation agent for the Docta nutrition logging application.

Your job is to take the existing repository and connect the frontend, FastAPI backend, data/RAG pipeline, Supabase database/storage, authentication, telemetry, and the future CV layer into one working application.

## IMPORTANT: Current Repository State

Before doing anything, inspect the repository. Do not assume the previous integration plan is still completely accurate.

The application currently consists of:

* `frontend/` — Vite + React + Tailwind
* `backend/` — FastAPI backend
* `backend/src/data_pipeline/` — the data pipeline has now been moved inside the backend
* Supabase — real project credentials have been configured
* Supabase schema SQL — already executed successfully
* Supabase database — confirmed live and reachable
* FastAPI backend — already running successfully
* CV model — NOT READY YET

The previous integration plan described the architecture as:

```text
Frontend
   ↓
FastAPI
   ↓
Orchestrator
   ├── CV
   └── Data/RAG
         ↓
      Supabase
```

This remains the target architecture.

However, the repository has changed since that plan was generated. Therefore:

### DO NOT blindly follow old file paths.

First inspect the current repository and adapt all implementation to the actual current structure.

---

# PRIMARY OBJECTIVE

Get the application to this development state:

```text
Real React/Vite frontend
        ↓
Real FastAPI backend
        ↓
Real authentication
        ↓
Real Supabase
        ↓
Real data/RAG pipeline
        ↓
Mock CV
        ↓
Real nutrition/portion calculation
        ↓
Real meal persistence
        ↓
Real history
        ↓
Real dashboard/statistics
        ↓
Real telemetry
```

The CV model must remain replaceable.

When the real CV model is eventually ready, the intended change should be approximately:

```text
USE_MOCK_AI=true
        ↓
USE_MOCK_AI=false
```

or the equivalent provider configuration.

The rest of the application should NOT need to be redesigned.

---

# CRITICAL ARCHITECTURAL PRINCIPLE

Separate responsibilities strictly:

```text
CV = WHAT FOOD IS THIS?
RAG/Data Pipeline = WHAT ARE THE NUTRITIONAL PROPERTIES?
User = HOW MUCH DID THEY EAT?
Supabase = PERSISTENCE
FastAPI = APPLICATION/API/ORCHESTRATION
Frontend = UI/interaction/state presentation
```

The CV layer must NOT calculate:

* calories
* protein
* carbohydrates
* fat
* fiber
* portion weight
* serving sizes

The CV output should only identify food and provide relevant detection information such as:

```text
dish_id
display_name
confidence
bounding_box
```

The existing RAG/data pipeline must remain the authoritative source for nutrition and portion information.

Do not duplicate authoritative nutrition data into the frontend or backend.

---

# DEVELOPMENT MODE

Until the real CV model is ready, the application must operate in:

```text
Frontend mock mode: OFF
Backend mock AI: ON
Backend mock RAG: OFF
Supabase: REAL
```

Conceptually:

```env
VITE_USE_MOCK=false
USE_MOCK_AI=true
USE_MOCK_RAG=false
```

Use the actual environment variable names found in the current repository if they differ.

The mock CV exists only to unblock the rest of the application.

---

# EXECUTION RULES

You MUST execute the work sequentially.

Do not attempt to implement everything in one uncontrolled change.

For each phase:

1. Inspect the relevant existing code.
2. Explain briefly what you found.
3. Implement the phase.
4. Run the relevant tests/checks.
5. Fix failures caused by your changes.
6. Verify the phase manually where possible.
7. Report exactly what changed.
8. Report the tests/checks that passed.
9. Only then move to the next phase.

Do NOT move forward while the current phase is knowingly broken.

---

# SAFETY RULES

## 1. Do not overwrite working architecture unnecessarily

Prefer modifying existing services/routes/components over rewriting the application.

## 2. Do not delete useful mock infrastructure

Keep mock implementations, but make them explicitly selectable.

## 3. Do not silently fall back to fake data in live mode

This is extremely important.

Bad:

```text
API failure → fake successful response
```

Correct:

```text
API failure → real error → frontend displays error
```

Mocks should only be used when explicitly enabled.

## 4. Never expose secrets

Do not hardcode:

* Supabase secret keys
* service-role keys
* passwords
* API keys
* JWT secrets

Never put privileged Supabase credentials in frontend code.

## 5. Do not modify the authoritative nutrition JSON files unless absolutely necessary

Consume them through the data pipeline.

Do not create duplicate nutrition tables.

## 6. Do not implement the real CV model

The real model is not ready.

Only create the adapter/interface necessary for plugging it in later.

## 7. Do not fabricate successful tests

If something cannot be tested, clearly state that.

---

# PHASE 0 — RECONNAISSANCE

Before modifying code:

Inspect:

```text
frontend/
backend/
backend/src/
backend/src/data_pipeline/
```

Inspect:

* frontend API layer
* frontend authentication state
* meal flow
* review flow
* dashboard
* history
* telemetry
* backend routers
* authentication dependencies
* Supabase client
* orchestrator
* CV service
* RAG service
* data pipeline
* schemas
* environment/configuration
* tests

Determine the CURRENT actual architecture.

Pay particular attention to the fact that:

```text
data_pipeline
```

has already been moved inside:

```text
backend/src/
```

Do not recreate the old external `data_pipeline/` structure.

Before making changes, produce a concise current architecture map.

Then begin Phase 1.

---

# PHASE 1 — FRONTEND → FASTAPI

Goal:

Make the real frontend actually depend on the running FastAPI backend.

Inspect:

```text
frontend/src/api/
frontend/src/store/
frontend/src/App.jsx
frontend/src/components/
frontend/.env*
```

Implement:

### 1. Disable live-mode mocks

Set the appropriate default so:

```text
VITE_USE_MOCK=false
```

in development integration mode.

### 2. Remove silent API fallbacks

Review:

* `authApi`
* `mealApi`
* other API clients

When live mode is enabled:

```text
HTTP error
→ throw/return real error
→ UI handles error
```

Do NOT return hardcoded successful data.

### 3. Fix API client behavior

Ensure:

* correct API base URL
* Authorization header when authenticated
* correct JSON handling
* useful error messages
* 401 handling
* non-JSON responses handled safely where necessary

### 4. Verify

Start:

```text
Frontend
FastAPI
```

Test a real frontend request.

Then temporarily stop FastAPI and verify the frontend displays an actual connection error rather than fake application data.

Do not proceed until this works.

---

# PHASE 2 — REAL AUTHENTICATION

Goal:

Replace fake/demo authentication behavior with real Supabase-backed authentication.

Implement:

```text
Signup
Login
Current user
Logout
Protected requests
Unauthorized state
```

The frontend must NOT consider the user authenticated when there is no valid token.

Expected flow:

```text
Signup/Login
      ↓
FastAPI
      ↓
Supabase Auth
      ↓
access token
      ↓
Frontend stores token
      ↓
Authorization: Bearer <token>
```

On application startup:

```text
stored token exists?
      ↓
GET /api/v1/auth/me
      ↓
valid → authenticated
invalid → clear token → login
```

Remove production reliance on:

```text
MOCK_USER
dummy JWTs
demo user IDs
usr_4a89fb21
```

Use the real Supabase `auth.users.id` UUID.

Implement real logout.

Ensure backend protected routes obtain the authenticated user from the validated token.

Test:

### User A

* signup
* login
* access `/auth/me`

### User B

* signup
* login
* access `/auth/me`

Confirm the IDs are different.

Do not proceed until authentication is genuinely working.

---

# PHASE 3 — AUTHORIZATION AND USER ISOLATION

Make the following user-specific routes require a real authenticated user:

```text
POST /api/v1/analyze
POST /api/v1/meals/log

GET /api/v1/meals/history
GET /api/v1/meals
GET /api/v1/meals/{id}
DELETE /api/v1/meals/{id}

GET /api/v1/dashboard

GET /api/v1/profile
PATCH /api/v1/profile
```

Health endpoints should remain public.

Remove anonymous/demo user fallbacks.

Every database query must be scoped to the authenticated user's UUID where appropriate.

Test:

```text
User A logs meal
User B logs meal

User A sees A's meal
User B sees B's meal
User A cannot access B's meal
User B cannot access A's meal
```

Do not proceed until user isolation works.

---

# PHASE 4 — CONNECT BACKEND TO THE REAL DATA PIPELINE

The data pipeline is now inside:

```text
backend/src/data_pipeline/
```

Integrate the backend with the actual `RAGService`.

The backend should NOT independently duplicate the data pipeline's JSON-reading logic.

Target:

```text
FastAPI
   ↓
orchestrator_service
   ↓
RAG service
   ↓
data_pipeline
   ↓
authoritative nutrition/portion data
```

Inspect the actual package structure and create clean imports.

Use the existing RAG functionality:

* portion configuration
* nutrition lookup
* nutrient scaling
* aliases
* semantic search where available

If a small batch helper is necessary, add it to the data pipeline rather than duplicating its logic in the backend.

Ensure the backend's `USE_MOCK_RAG=false` means the real data pipeline is used.

`USE_MOCK_RAG=true` may remain available for isolated testing.

### IMPORTANT

There must be ONE authoritative source of nutrition information.

Do not duplicate:

```text
calories
protein
carbs
fat
fiber
portion units
```

into the frontend as production truth.

Verify that:

```text
mock CV → real RAG
```

returns real nutrition data.

---

# PHASE 5 — COMPLETE ANALYZE FLOW USING MOCK CV

This is the most important integration milestone.

The complete flow must work:

```text
Frontend
   ↓
POST /api/v1/analyze
   ↓
FastAPI
   ↓
Mock CV
   ↓
detected foods
   ↓
RAG
   ↓
portion information
   ↓
nutrition information
   ↓
AnalyzeResponse
   ↓
ReviewScreen
```

The mock CV should return realistic detection objects:

```text
dish_id
display_name
confidence
bounding_box
```

It must NOT return nutrition or gram estimates.

Ensure the orchestrator converts CV results into the frontend's expected analyze response.

Test with multiple detected foods.

Verify the frontend renders:

* food name
* confidence
* bounding box
* portion options
* nutrition

Do not proceed until this complete flow works.

---

# PHASE 6 — FOOD CORRECTION / DISH RESOLUTION

Implement a backend endpoint such as:

```text
GET /api/v1/dishes/{dish_id}
```

It must resolve the dish through the real RAG/data pipeline.

Return the relevant:

```text
dish_id
display_name
portion units
nutrition per 100g
```

Add frontend API support.

When the user changes the detected food:

```text
Old food
   ↓
User selects new food
   ↓
Frontend requests new dish
   ↓
Backend → RAG
   ↓
New nutrition + portions
   ↓
Review UI updates
```

Do not use dummy frontend macros after correction.

Test several food corrections.

---

# PHASE 7 — PORTIONS AND NUTRITION SCALING

Connect the portion selector to real RAG data.

Expected flow:

```text
Dish
 ↓
available portion units
 ↓
user selects unit
 ↓
quantity
 ↓
gram weight
 ↓
scaled nutrition
```

Ensure the final meal draft contains enough information to accurately log:

```text
selected_unit_id
selected_quantity
gram_weight
calories_kcal
protein_g
fat_g
carbs_g
fiber_g
sodium_mg
calcium_mg
iron_mg
```

If custom gram entry is already supported by the backend/data pipeline but missing from the frontend, add it cleanly.

Do not create a second nutrition calculation system.

---

# PHASE 8 — IMAGE STORAGE

Connect meal images to persistent storage.

Preferred flow:

```text
Image
 ↓
FastAPI
 ↓
Supabase Storage
 ↓
persistent image URL
```

Do not persist:

```text
blob:http://...
```

as the meal's permanent image URL.

Ensure the analyze response exposes the real image URL.

Ensure meal logging uses the persistent URL.

Test:

1. Upload image.
2. Analyze.
3. Log meal.
4. Refresh browser.
5. Load history.
6. Confirm image still loads.

---

# PHASE 9 — MEAL LOGGING → SUPABASE

Connect the Review → Confirm flow completely.

Expected:

```text
ReviewScreen
     ↓
Confirm meal
     ↓
POST /api/v1/meals/log
     ↓
FastAPI
     ↓
Supabase
```

Persist:

```text
meal
meal_items
feedback telemetry
```

with the authenticated user's UUID.

Ensure:

```text
predicted_dish_id
```

and:

```text
final_dish_id
```

remain distinct.

If atomic persistence is already practical with the current Supabase schema, implement it. Otherwise use safe compensation/error handling and document the limitation.

Test by checking the actual Supabase tables.

---

# PHASE 10 — REAL HISTORY

Connect:

```text
GET /api/v1/meals/history
```

to the frontend.

Remove logic where an empty live response causes mock history to remain visible.

Correct behavior:

```text
[] 
```

means:

```text
No meals logged yet
```

not:

```text
Show fake meals
```

After logging:

```text
POST /meals/log
      ↓
GET /meals/history
      ↓
real Supabase data
```

Refresh the browser and verify the meal remains.

---

# PHASE 11 — REAL DASHBOARD

Connect dashboard metrics to:

```text
GET /api/v1/dashboard
```

Remove hardcoded production nutrition metrics.

The dashboard should calculate/display real values based on persisted meals.

At minimum connect:

* today's calories
* today's macros
* recent meals
* relevant nutrition progress

Do not invent values when the database contains no data.

Test:

```text
No meals → zero/empty state
Log meal → dashboard changes
Refresh → dashboard remains correct
```

---

# PHASE 12 — REAL STATISTICS

Connect weekly/period statistics to real backend data.

Remove hardcoded values such as fake weekly calorie numbers.

Make:

```text
WeeklyCalorieBarChart
MealProgressCard
```

consume real API data.

Test with several meals across dates if the existing schema supports this.

---

# PHASE 13 — TELEMETRY

Ensure telemetry records:

```text
analysis_id
predicted_dish_id
final_dish_id
label_modified
confidence
bounding_box
selected_unit_id
selected_quantity
gram_weight
nutrients
```

where supported by the existing schema.

The purpose is to preserve the difference between:

```text
What CV predicted
```

and:

```text
What the user ultimately confirmed
```

Verify telemetry records in Supabase.

---

# PHASE 14 — TELEMETRY EXPORT

Secure telemetry export appropriately.

Do not leave sensitive telemetry export publicly accessible.

Fix the frontend so it can correctly process:

```text
application/json
text/csv
```

rather than assuming every response is JSON.

Test the export flow.

---

# PHASE 15 — CV PROVIDER ABSTRACTION

Now make the CV layer explicitly pluggable.

Create/use an interface or protocol equivalent to:

```python
class FoodIdentificationProvider:
    def detect(self, image_bytes, prompt=None):
        ...
```

Create:

```text
MockCVProvider
```

as the current implementation.

The orchestrator should depend on the provider contract, not a specific YOLO implementation.

Target:

```text
                 ┌── MockCVProvider
Orchestrator ────┤
                 └── RealCVProvider (future)
```

The mock provider must remain functional.

Do NOT implement the real CV model.

---

# PHASE 16 — END-TO-END TEST

Create or update an integration test covering:

```text
Create user
   ↓
Login
   ↓
Upload image
   ↓
Analyze
   ↓
Mock CV
   ↓
Real RAG
   ↓
Review
   ↓
Correct food
   ↓
Select portion
   ↓
Log meal
   ↓
Supabase
   ↓
History
   ↓
Dashboard
   ↓
Telemetry
```

The test must verify actual data contracts between each layer.

Where practical, test against a controlled test database/project rather than destructive production data.

---

# PHASE 17 — FINAL CLEANUP

After all functional phases pass:

Search for remaining:

```text
MOCK_USER
demo user
usr_4a89fb21
dummy JWT
hardcoded calories
hardcoded macros
MOCK_MEAL_HISTORY
silent API fallback
blob:http
fake successful response
```

Determine whether each occurrence is:

```text
legitimate explicit mock/test infrastructure
```

or:

```text
production integration bug
```

Remove the latter.

Do NOT remove legitimate mock infrastructure that is required for development/testing.

---

# FINAL ACCEPTANCE CRITERIA

The implementation is complete only when all of these are true:

## Authentication

* Signup works.
* Login works.
* Logout works.
* `/auth/me` works.
* Invalid/expired tokens result in unauthenticated state.
* No automatic mock authentication exists in live mode.
* User IDs are real Supabase UUIDs.

## Frontend

* `VITE_USE_MOCK=false`.
* API errors are visible.
* No silent fake success.
* Frontend communicates with FastAPI.

## CV

* Mock CV works.
* CV returns only identification/detection information.
* CV is replaceable through a provider interface.
* Real CV can be plugged in later without redesigning the application.

## RAG

* Backend calls the real data pipeline.
* Nutrition comes from one authoritative source.
* Portion information comes from the data pipeline.
* Food correction uses the backend/RAG.
* No production nutrition duplication in frontend.

## Supabase

* Real authentication works.
* Real meals are persisted.
* Real meal items are persisted.
* Telemetry is persisted.
* Images are persistently stored.
* User data is isolated.

## Frontend data

* Analyze uses real backend results.
* Review uses real RAG information.
* Portion selection uses real data.
* Meal history uses Supabase-backed API results.
* Dashboard uses real persisted data.
* Statistics use real persisted data.
* Empty states are real empty states.

## Errors

* Backend failures are not silently converted into fake success.
* CV failures are visible.
* RAG failures are visible.
* Supabase failures are visible.
* Authentication failures are visible.

## Testing

At minimum, the complete:

```text
Auth
→ Analyze
→ Mock CV
→ RAG
→ Review
→ Log
→ Supabase
→ History
→ Dashboard
→ Telemetry
```

flow must be verified.

---

# FINAL REPORT

When all phases are complete, provide:

## 1. Architecture

Show the final architecture as a simple diagram.

## 2. Files changed

Group by:

```text
Frontend
Backend
Data Pipeline
Tests
Configuration
```

## 3. What is now connected

Explicitly list:

```text
Frontend → Backend
Auth → Supabase
Backend → RAG
Backend → CV mock
Meals → Supabase
Storage → Supabase
History → Supabase
Dashboard → Supabase
Telemetry → Supabase
```

## 4. Tests performed

List every test/check and whether it passed.

## 5. Remaining limitations

Only list genuine remaining limitations.

## 6. Future CV integration

Explain exactly:

* which interface the future CV model must implement
* what input it receives
* what output it must return
* which environment/configuration needs to change
* what existing code should NOT need modification

Do not claim the application is complete unless the acceptance criteria above have actually been verified.
