# Sub-Team 2 Directive: Nutrition Data & RAG Engine

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Sub-Team 2 Autonomous Agent, you must operate exclusively within `/subteam-2-data-rag/`. Do not modify files outside this folder. Ensure all exported functions and schemas align with the canonical project architecture in `/PROJECT_ORCHESTRATION.md`.

---

## 2. Directory Structure Tree

```
subteam-2-data-rag/
├── data/
│   ├── raw_wafct_2019.csv             # Raw FAO/INFOODS WAFCT 2019 source table
│   ├── wafct_db.json                  # Cleaned & normalized per-100g nutrition database
│   ├── aliases_map.json               # Nigerian dialect & colloquial name mapping dictionary
│   └── fallback_defaults.json        # Baseline macro profiles for unmatched items
├── src/
│   ├── __init__.py
│   ├── ingest_wafct.py                # Data parser, unit normalizer, and validator
│   ├── vector_indexer.py              # Qdrant client collection creator & embedding generator
│   ├── semantic_search.py             # Hybrid vector lookup with threshold fallback
│   ├── macro_scaler.py                # Linear nutrition calculator & aggregator
│   ├── rag_service.py                 # Unified RAG engine service interface
│   └── schemas.py                     # Pydantic v2 data models
├── tests/
│   ├── __init__.py
│   ├── test_ingest.py
│   ├── test_vector_indexer.py
│   ├── test_semantic_search.py
│   ├── test_macro_scaler.py
│   └── test_rag_service.py
├── scripts/
│   ├── init_qdrant.py                 # CLI to bootstrap Qdrant collection
│   └── benchmark_retrieval.py         # Latency and recall benchmark suite (<200ms SLA)
├── requirements.txt
└── README.md
```

---

## 3. Detailed Functional Requirements

### 3.1. FAO WAFCT 2019 Data Ingestion & Normalization
* Parse the Western Africa Food Composition Table (WAFCT 2019) from `data/raw_wafct_2019.csv`.
* Filter and normalize each food item to a strict **per-100g edible portion** schema:
  * `food_code` (str, e.g., `"01_042"`)
  * `food_name_en` (str, e.g., `"Rice, jollof, prepared with tomato paste and oil"`)
  * `local_names` (List[str], e.g., `["Nigerian Jollof", "Jollof Rice", "Party Jollof"]`)
  * `category` (str, e.g., `"Cereals and cereal products"`)
  * `calories_kcal` (float, Energy per 100g)
  * `protein_g` (float, Total Protein per 100g)
  * `fat_g` (float, Total Lipid/Fat per 100g)
  * `carbs_g` (float, Available Carbohydrate per 100g)
  * `fiber_g` (float, Dietary Fiber per 100g)
  * `sodium_mg` (float, Sodium per 100g)
  * `calcium_mg` (float, Calcium per 100g)
  * `iron_mg` (float, Iron per 100g)
* Save normalized records to `data/wafct_db.json`.

---

### 3.2. Qdrant Vector Indexing
* **Vector Store**: Qdrant Vector Database (collection name: `wafct_nutrition`).
* **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (dimension: $384$, metric: `Cosine`).
* **Document Text Representation**: Construct a rich composite text string for embedding:
  ```
  "{food_name_en}. Also known as: {local_names_comma_separated}. Category: {category}. Ingredients: {key_ingredients}"
  ```
* **Payload Storage**: Store the full normalized per-100g nutrient profile directly inside the Qdrant point payload for zero-overhead retrieval.

---

### 3.3. Semantic Search & Fallback Threshold Logic
* Query Qdrant with candidate dish names (e.g., `"amala with egusi"`, `"fried dodo"`).
* Query Resolution Rules:
  1. Check exact match in `aliases_map.json`.
  2. Perform vector search over `wafct_nutrition` collection using `all-MiniLM-L6-v2`.
  3. **Similarity Threshold Evaluation**:
     * If $\text{Cosine Similarity} \ge 0.75$: Select best matching WAFCT item.
     * If $\text{Cosine Similarity} < 0.75$: Flag item as `is_fallback: true` and match to generic category default in `data/fallback_defaults.json`.

---

### 3.4. Macronutrient Scaling Engine
Given detected or user-adjusted gram weight $W_{\text{gram}}$, calculate scaled nutrients:

$$\text{Nutrient}_{\text{total}} = \left( \frac{\text{Nutrient}_{\text{WAFCT per 100g}}}{100.0} \right) \times W_{\text{gram}}$$

Total meal nutrition is computed by summing across all itemized components:

$$\text{Meal Total} = \sum_{i=1}^{N} \text{Nutrient}_{\text{item } i}$$

* Enforce a hard execution SLA: Retrieval + Scaling calculation must execute in **$< 200\text{ ms}$**.

---

## 4. Input & Output Contracts

### 4.1. Request Model to RAG Service
```python
from pydantic import BaseModel
from typing import List, Optional

class ItemQuery(BaseModel):
    item_id: str
    query_text: str  # e.g., "jollof_rice", "fried plantain", "amala"
    weight_g: float  # e.g., 250.0

class RAGMealRequest(BaseModel):
    items: List[ItemQuery]
```

### 4.2. Response Model from RAG Service
```python
class NutrientsProfile(BaseModel):
    calories_kcal: float
    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: float
    sodium_mg: float
    calcium_mg: float
    iron_mg: float

class ScaledItemBreakdown(BaseModel):
    item_id: str
    query_text: str
    matched_food_name: str
    wafct_code: str
    similarity_score: float
    is_fallback: bool
    weight_g: float
    nutrients: NutrientsProfile

class TotalMealNutrition(BaseModel):
    total_calories_kcal: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    total_fiber_g: float
    total_sodium_mg: float
    total_calcium_mg: float
    total_iron_mg: float

class RAGMealResponse(BaseModel):
    itemized_breakdown: List[ScaledItemBreakdown]
    total_meal_nutrition: TotalMealNutrition
    retrieval_duration_ms: float
```

---

## 5. Testing & Validation Commands

```bash
# 1. Install Sub-team 2 dependencies
pip install -r requirements.txt

# 2. Ingest & normalize raw WAFCT table
python src/ingest_wafct.py --input data/raw_wafct_2019.csv --output data/wafct_db.json

# 3. Bootstrap & Index Qdrant collection
python scripts/init_qdrant.py --host localhost --port 6333 --data data/wafct_db.json

# 4. Run retrieval and latency benchmark
python scripts/benchmark_retrieval.py

# 5. Run test suite
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 6. Definition of Done (DoD) Checklist

- [ ] `data/wafct_db.json` successfully generated with 100% normalized nutrient fields.
- [ ] `wafct_nutrition` collection created in Qdrant with 384-dim Cosine vectors.
- [ ] Semantic search achieves $\ge 95\%$ top-1 accuracy on standard Nigerian food alias benchmark.
- [ ] Similarity threshold ($0.75$) accurately triggers fallback defaults when tested with ambiguous or out-of-distribution queries.
- [ ] Macro scaling formulas verify exact arithmetic scaling with zero rounding drifts ($< 0.01\text{g}$).
- [ ] Total RAG query latency executes within the $< 200\text{ms}$ SLA limit.
- [ ] Test coverage exceeds $90\%$ across all modules in `tests/`.
