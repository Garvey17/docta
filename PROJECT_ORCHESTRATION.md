# docta: Master Project Orchestration Blueprint

## 1. Executive Summary & System Vision
**docta** is an edge-optimized, multimodal, and localized nutrition intelligence platform engineered specifically for African and Nigerian dietary compositions. It bridges the critical accuracy gap in mainstream global diet-tracking applications by integrating:
1. Custom-trained Computer Vision (YOLOv8/v11) specialized on complex, mixed, and stew-heavy West African dishes.
2. Geometric volumetric portion estimation coupled with localized food density tables.
3. Multimodal Large Language Model (Gemini Flash) vision-text reasoning for conversational disambiguation and portion overrides.
4. High-performance Retrieval-Augmented Generation (RAG) powered by Qdrant Vector Search over the FAO/INFOODS West African Food Composition Table (WAFCT 2019).
5. Asynchronous, high-throughput microservices architecture delivering end-to-end meal analysis in under 2.0 seconds.

---

## 2. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph Client Layer [Sub-team 4: Frontend PWA]
        User([User / Client Device]) -->|1. Capture Image & Text| CameraUI[Camera & Text Input Feed]
        CameraUI -->|2. Multipart POST| API_Gateway[FastAPI Gateway /api/v1/analyze]
        BBoxOverlay[Bounding Box Canvas Overlay] <---|8. Render Boxes & Macros| API_Gateway
        PortionSlider[Interactive Portion Adjuster] -->|9. Approve Log /api/v1/meals/log| API_Gateway
    end

    subgraph Service Layer [Sub-team 3: Backend & MLOps]
        API_Gateway -->|3. Orchestrate Payload| Orchestrator[Analysis Orchestrator Service]
        Orchestrator -->|7. Persist Meal & Items| Postgres[(PostgreSQL / Supabase)]
    end

    subgraph AI Inference Layer [Sub-team 1: CV & Multimodal AI]
        Orchestrator -->|4a. Image Tensor (640x640)| YOLO[YOLOv8/v11 Object Detection]
        YOLO -->|BBoxes & Visual Classes| VolumetricEngine[Volumetric Pixel-to-Gram Estimator]
        VolumetricEngine -->|Visual Weights & Boxes| GeminiFusion[Gemini Flash Multimodal Fusion]
        Orchestrator -->|4b. Text Prompt + Image + Boxes| GeminiFusion
        GeminiFusion -->|5. Fused Dish Classes & Gram Weights| Orchestrator
    end

    subgraph Knowledge Layer [Sub-team 2: Nutrition Data & RAG]
        Orchestrator -->|6. Query Dish Names & Grams| RAGEngine[Qdrant Semantic RAG Engine]
        RAGEngine -->|Vector Lookup: all-MiniLM-L6-v2| QdrantDB[(Qdrant Vector DB / WAFCT 2019)]
        QdrantDB -->|Matched Per-100g Nutrition| ScalingEngine[Macronutrient Scaling Calculator]
        ScalingEngine -->|Scaled Total & Itemized Nutrients| Orchestrator
    end
```

---

## 3. System Dataflow & Latency SLA Breakdown

The maximum permissible end-to-end latency budget for `/api/v1/analyze` is **$2000\text{ ms}$ ($2.0\text{ s}$)**.

| Sequence Stage | Source $\rightarrow$ Destination | Payload Description | SLA Target |
| :--- | :--- | :--- | :--- |
| **1. Ingestion** | Frontend $\rightarrow$ Backend | `multipart/form-data` (JPEG image $\le 5\text{MB}$, optional `text_prompt`) | $< 150\text{ ms}$ |
| **2. CV Detection** | Backend $\rightarrow$ YOLO Inference | $640\times 640$ Preprocessed Tensor $\rightarrow$ Bounding boxes, class labels, visual confidence | $< 180\text{ ms}$ |
| **3. Volume & Fusion** | YOLO + Text $\rightarrow$ Gemini Flash | BBoxes + Area-to-Volume Heuristic + User prompt $\rightarrow$ LLM Structured Output | $< 800\text{ ms}$ |
| **4. Vector Retrieval** | Fusion $\rightarrow$ Qdrant RAG | Embedding search (`all-MiniLM-L6-v2`) over FAO WAFCT collections | $< 120\text{ ms}$ |
| **5. Macro Scaling** | RAG $\rightarrow$ Scaling Engine | Arithmetic multiplication: $\text{Nutrient} = (\text{WAFCT}_{100g} / 100) \times \text{Weight}$ | $< 20\text{ ms}$ |
| **6. Persistence** | Backend $\rightarrow$ PostgreSQL | Insert records into `meals` and `meal_items` tables | $< 80\text{ ms}$ |
| **7. Serialization** | Backend $\rightarrow$ Frontend | Return `AnalyzeMealResponse` JSON to Client UI | $< 50\text{ ms}$ |
| **Total Target** | **End-to-End Budget** | **User Capture $\rightarrow$ Interactive Review Screen** | **$< 1400\text{ ms}$** (Buffer: $600\text{ ms}$) |

---

## 4. Canonical Shared API Contracts & Data Types

All sub-teams must strictly align with these unified JSON schemas and data types.

### 4.1. Coordinate System for Bounding Boxes
All bounding box coordinates are normalized floats in the interval $[0.0, 1.0]$ structured as:
$$\text{bbox} = [x_{\min}, y_{\min}, x_{\max}, y_{\max}]$$
Where:
* $x_{\min}, x_{\max}$: Horizontal offsets relative to image width ($0.0 = \text{leftmost}, 1.0 = \text{rightmost}$).
* $y_{\min}, y_{\max}$: Vertical offsets relative to image height ($0.0 = \text{topmost}, 1.0 = \text{bottommost}$).

### 4.2. Core JSON Data Schemas

#### A. Intermediate CV Detection Payload (Sub-team 1 $\rightarrow$ Sub-team 3)
```json
{
  "detected_items": [
    {
      "dish_id": "jollof_rice",
      "display_name": "Jollof Rice",
      "confidence": 0.93,
      "bounding_box": [0.125, 0.240, 0.550, 0.780],
      "estimated_volume_cm3": 320.5,
      "density_g_cm3": 0.85,
      "estimated_weight_g": 272.4,
      "text_override_applied": false,
      "reasoning": "Standard single scoop portion detected via bounding box area ratio."
    },
    {
      "dish_id": "fried_plantain",
      "display_name": "Fried Plantain (Dodo)",
      "confidence": 0.89,
      "bounding_box": [0.580, 0.310, 0.890, 0.650],
      "estimated_volume_cm3": 140.0,
      "density_g_cm3": 0.78,
      "estimated_weight_g": 150.0,
      "text_override_applied": true,
      "reasoning": "User prompt specified '4 slices of dodo', overriding visual estimate of 109g to 150g."
    }
  ],
  "raw_prompt": "Jollof with 4 slices of dodo",
  "processing_time_ms": 780.5
}
```

#### B. Full Analyze Meal Response (Sub-team 3 API $\rightarrow$ Sub-team 4 Frontend)
`POST /api/v1/analyze`
```json
{
  "analysis_id": "anlz_8f92c10b",
  "status": "success",
  "processing_duration_ms": 1140.2,
  "image_url": "https://storage.docta.ng/meals/temp_8f92c10b.jpg",
  "detected_items": [
    {
      "item_id": "item_1",
      "dish_id": "jollof_rice",
      "display_name": "Nigerian Jollof Rice",
      "confidence": 0.93,
      "bounding_box": [0.125, 0.240, 0.550, 0.780],
      "weight_g": 272.0,
      "wafct_code": "01_042",
      "similarity_score": 0.942,
      "is_fallback": false,
      "nutrients": {
        "calories_kcal": 380.8,
        "protein_g": 7.3,
        "fat_g": 10.9,
        "carbs_g": 62.6,
        "fiber_g": 2.7,
        "sodium_mg": 489.6,
        "calcium_mg": 21.8,
        "iron_mg": 1.9
      }
    },
    {
      "item_id": "item_2",
      "dish_id": "fried_plantain",
      "display_name": "Fried Ripe Plantain (Dodo)",
      "confidence": 0.89,
      "bounding_box": [0.580, 0.310, 0.890, 0.650],
      "weight_g": 150.0,
      "wafct_code": "02_018",
      "similarity_score": 0.961,
      "is_fallback": false,
      "nutrients": {
        "calories_kcal": 312.0,
        "protein_g": 1.8,
        "fat_g": 14.1,
        "carbs_g": 48.0,
        "fiber_g": 3.6,
        "sodium_mg": 6.0,
        "calcium_mg": 15.0,
        "iron_mg": 0.9
      }
    }
  ],
  "total_nutrition": {
    "total_calories_kcal": 692.8,
    "total_protein_g": 9.1,
    "total_fat_g": 25.0,
    "total_carbs_g": 110.6,
    "total_fiber_g": 6.3,
    "total_sodium_mg": 495.6,
    "total_calcium_mg": 36.8,
    "total_iron_mg": 2.8
  }
}
```

#### C. Log Approved Meal Request (Sub-team 4 Frontend $\rightarrow$ Sub-team 3 API)
`POST /api/v1/meals/log`
```json
{
  "analysis_id": "anlz_8f92c10b",
  "image_url": "https://storage.docta.ng/meals/temp_8f92c10b.jpg",
  "meal_type": "lunch",
  "logged_at": "2026-09-22T13:45:00Z",
  "items": [
    {
      "food_name": "Nigerian Jollof Rice",
      "wafct_code": "01_042",
      "gram_weight": 250.0,
      "calories_kcal": 350.0,
      "protein_g": 6.7,
      "fat_g": 10.0,
      "carbs_g": 57.5,
      "fiber_g": 2.5,
      "sodium_mg": 450.0,
      "calcium_mg": 20.0,
      "iron_mg": 1.75
    },
    {
      "food_name": "Fried Ripe Plantain (Dodo)",
      "wafct_code": "02_018",
      "gram_weight": 150.0,
      "calories_kcal": 312.0,
      "protein_g": 1.8,
      "fat_g": 14.1,
      "carbs_g": 48.0,
      "fiber_g": 3.6,
      "sodium_mg": 6.0,
      "calcium_mg": 15.0,
      "iron_mg": 0.9
    }
  ]
}
```

#### D. Dashboard Daily Summary (Sub-team 3 API $\rightarrow$ Sub-team 4 Frontend)
`GET /api/v1/dashboard/summary?date=2026-09-22`
```json
{
  "date": "2026-09-22",
  "user_id": "usr_99a812ef",
  "calorie_target_kcal": 2200,
  "calorie_consumed_kcal": 1450.5,
  "remaining_calories_kcal": 749.5,
  "target_macros": {
    "protein_target_g": 120.0,
    "fat_target_g": 65.0,
    "carbs_target_g": 275.0
  },
  "consumed_macros": {
    "protein_consumed_g": 78.4,
    "fat_consumed_g": 49.2,
    "carbs_consumed_g": 182.1,
    "fiber_consumed_g": 16.8,
    "sodium_consumed_mg": 1320.0
  },
  "meals_logged": [
    {
      "meal_id": "meal_412",
      "meal_type": "breakfast",
      "logged_at": "2026-09-22T08:15:00Z",
      "calories_kcal": 420.0,
      "thumbnail_url": "https://storage.docta.ng/meals/thumb_412.jpg",
      "summary_text": "Moi Moi (200g), Boiled Egg (50g)"
    },
    {
      "meal_id": "meal_413",
      "meal_type": "lunch",
      "logged_at": "2026-09-22T13:45:00Z",
      "calories_kcal": 1030.5,
      "thumbnail_url": "https://storage.docta.ng/meals/thumb_413.jpg",
      "summary_text": "Jollof Rice (250g), Dodo (150g), Suya (120g)"
    }
  ]
}
```

---

## 5. Directory Scope & Ownership Matrix

| Directory Path | Sub-Team Identifier | Primary Responsibilities |
| :--- | :--- | :--- |
| `/subteam-1-cv-multimodal` | **CV & Multimodal AI** | YOLOv8/v11 training, Albumentations pipeline, volumetric heuristics, Gemini Flash multimodal vision-text fusion. |
| `/subteam-2-data-rag` | **Nutrition Data & RAG** | FAO WAFCT 2019 data normalization, Qdrant vector indexing, hybrid semantic search, macro scaling engine. |
| `/subteam-3-backend-mlops` | **Backend & MLOps** | FastAPI gateway, PostgreSQL schemas & SQLAlchemy ORM, authentication, service orchestration, Docker Compose. |
| `/subteam-4-frontend-ux` | **Frontend & UX** | Next.js 14 App Router, WebRTC camera capture, Canvas bounding box overlay, interactive meal editor, dashboard. |

---

## 6. Cross-Module Integration Rules & Contract Governance

1. **Strict Directory Encapsulation**: Each subagent must strictly limit write operations to its assigned directory. Cross-module imports are prohibited unless interfacing via standard REST endpoints or published package libraries.
2. **Mock-First Contract Verification**: Before downstream dependencies (e.g. Sub-team 1 model or Sub-team 2 Qdrant index) are completed, Sub-team 3 and Sub-team 4 must utilize mock data compliant with Section 4 schemas to ensure unblocked parallel development.
3. **Pydantic Validation**: All inter-service communications must be validated via Pydantic v2 schemas at runtime. Any field missing or mismatching in typing will trigger a standardized `422 Unprocessable Entity` response.
4. **Environment Configuration**: Secrets and endpoints are configured strictly via standard `.env` variables (e.g. `GEMINI_API_KEY`, `QDRANT_HOST`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL`).
5. **Continuous Quality Gates**: Each module contains independent test suites (`pytest`, `jest`) that must achieve $\ge 80\%$ unit test coverage before merging.
