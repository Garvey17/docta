# Data & RAG Directive: RIQ Lookup, Conventional Portion Units & Nutrition Scaling

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Data & RAG Autonomous Agent, you must operate exclusively within `/data_pipeline/`. Do not modify files in other directories. All data models, lookup tables, and scaling services must conform strictly to `/PROJECT_ORCHESTRATION.md`.

---

## 2. Mandatory Pre-Execution Gate: 3 Required Inputs

> [!CAUTION]
> **Agent Pre-Execution Prerequisite Check**:
> The nutritional composition data obtained from raw food composition tables (e.g. FAO WAFCT 2019) represents **individual raw/prepared ingredients** (e.g. raw parboiled rice, tomato puree, palm oil, melon seeds, crayfish, yam flour) rather than finished composite dishes.
> 
> Furthermore, portion sizing relies on **Conventional Units of Measurement** (e.g. *Serving Spoons*, *Wraps*, *Pieces*, *Slices*) rather than CV-based automated volumetric estimation.
>
> **The agent MUST verify the presence of all 3 required artifacts before proceeding with execution:**
> 1. **Target 5 Dishes Scope**: The 5 specific Nigerian dishes to be considered (`jollof_rice`, `egusi_soup`, `amala`, `fried_plantain`, `moi_moi`).
> 2. **Food Composition Table (FCT)**: Raw ingredient-level nutrient dataset (`data/raw_wafct_2019.csv` or `data/food_composition_table.json`).
> 3. **Recipe-Ingredient-Quantity (RIQ) & Portion Units Lookup Table**: Standardized recipe table (`data/recipe_ingredient_lookup.json`) AND conventional portion units table (`data/portion_units.json`).
>
> If any of these are missing or invalid, the agent must halt execution, load the bundled fallback fixtures, or prompt the user before indexing.

---

## 3. Directory Structure Tree

```
data_pipeline/
├── data/
│   ├── raw_wafct_2019.csv             # Raw FAO/INFOODS ingredient composition table
│   ├── food_composition_table.json    # Normalized per-100g raw ingredient database
│   ├── recipe_ingredient_lookup.json  # [PREREQUISITE] 5-Dish Recipe-Ingredient-Quantity table
│   ├── portion_units.json             # [PREREQUISITE] Conventional portion units registry & gram mappings
│   ├── composite_dishes_db.json       # Compiled finished dish profiles (RIQ + FCT)
│   ├── dummy_wafct.json               # Seed dummy database for standalone offline testing
│   ├── aliases_map.json               # Dialect & colloquial name mapping dictionary
│   └── fallback_defaults.json        # Baseline profiles for unmapped items
├── src/
│   ├── __init__.py
│   ├── validate_prerequisites.py      # Pre-execution validator checking the 3 required inputs
│   ├── ingest_wafct.py                # Raw ingredient FCT parser & unit normalizer
│   ├── composite_dish_builder.py      # RIQ compiler: computes weighted dish nutrition
│   ├── portion_service.py             # Portion unit resolver & conventional gram calculator
│   ├── vector_indexer.py              # Qdrant collection creator & sentence-transformer embedder
│   ├── semantic_search.py             # Hybrid vector lookup with portion unit attachment
│   ├── macro_scaler.py                # Linear nutrition calculator (Unit Grams * Quantity)
│   ├── rag_service.py                 # Unified RAG & portion service interface
│   └── schemas.py                     # Pydantic v2 data models
├── tests/
│   ├── __init__.py
│   ├── test_prerequisites.py
│   ├── test_composite_builder.py
│   ├── test_portion_service.py
│   ├── test_semantic_search.py
│   ├── test_macro_scaler.py
│   └── test_rag_service.py
├── scripts/
│   ├── init_qdrant.py                 # CLI to bootstrap Qdrant collection
│   └── benchmark_retrieval.py         # Latency benchmark suite (<200ms SLA)
├── requirements.txt
└── INSTRUCTION.md
```

---

## 4. Conventional Portion Units Registry (`data/portion_units.json`)

Each of the 5 focus dishes is mapped to culturally standard portion units:

```json
{
  "portion_units": {
    "jollof_rice": {
      "dish_name": "Nigerian Jollof Rice",
      "default_unit_id": "serving_spoon",
      "default_quantity": 2.0,
      "units": [
        { "unit_id": "serving_spoon", "unit_name": "Serving Spoon", "gram_weight": 120.0, "description": "Standard catering/cooking spoon (~120g)" },
        { "unit_id": "mound_cup", "unit_name": "Mound / Cup", "gram_weight": 250.0, "description": "Standard dining plate mound (~250g)" },
        { "unit_id": "takeaway_pack", "unit_name": "Takeaway Pack", "gram_weight": 500.0, "description": "Full standard plastic pack (~500g)" }
      ]
    },
    "egusi_soup": {
      "dish_name": "Egusi Melon Seed Soup",
      "default_unit_id": "serving_spoon",
      "default_quantity": 2.0,
      "units": [
        { "unit_id": "serving_spoon", "unit_name": "Serving Spoon", "gram_weight": 100.0, "description": "Standard cooking soup spoon (~100g)" },
        { "unit_id": "small_bowl", "unit_name": "Small Soup Bowl", "gram_weight": 200.0, "description": "Side soup bowl (~200g)" },
        { "unit_id": "large_bowl", "unit_name": "Large Soup Bowl", "gram_weight": 350.0, "description": "Main soup bowl (~350g)" }
      ]
    },
    "amala": {
      "dish_name": "Amala (Yam Flour Swallow)",
      "default_unit_id": "medium_wrap",
      "default_quantity": 1.0,
      "units": [
        { "unit_id": "small_wrap", "unit_name": "Small Wrap", "gram_weight": 150.0, "description": "Light portion wrap (~150g)" },
        { "unit_id": "medium_wrap", "unit_name": "Medium Wrap", "gram_weight": 250.0, "description": "Standard restaurant wrap (~250g)" },
        { "unit_id": "large_wrap", "unit_name": "Large Wrap", "gram_weight": 400.0, "description": "Heavy swallow portion (~400g)" }
      ]
    },
    "fried_plantain": {
      "dish_name": "Fried Ripe Plantain (Dodo)",
      "default_unit_id": "portion_6_slices",
      "default_quantity": 1.0,
      "units": [
        { "unit_id": "single_slice", "unit_name": "Single Slice / Piece", "gram_weight": 25.0, "description": "One slice (~25g)" },
        { "unit_id": "portion_6_slices", "unit_name": "Small Portion (6 slices)", "gram_weight": 150.0, "description": "Standard side portion (~150g)" },
        { "unit_id": "large_portion", "unit_name": "Large Portion (12 slices)", "gram_weight": 300.0, "description": "Double side portion (~300g)" }
      ]
    },
    "moi_moi": {
      "dish_name": "Steamed Bean Cake (Moi Moi)",
      "default_unit_id": "single_wrap",
      "default_quantity": 1.0,
      "units": [
        { "unit_id": "single_wrap", "unit_name": "Single Wrap / Cup", "gram_weight": 150.0, "description": "Standard leaf or foil wrap (~150g)" },
        { "unit_id": "large_wrap", "unit_name": "Large Wrap", "gram_weight": 250.0, "description": "Large portion wrap (~250g)" }
      ]
    }
  }
}
```

---

## 5. Nutrition Calculation from User Portion Selection

When the user selects a portion unit and quantity for each recognized food:

1. **Calculate Total Gram Weight**:
   $$W_{\text{gram}} = \text{Unit Gram Weight} \times \text{Selected Quantity}$$
   *(e.g., $2 \times \text{Serving Spoon (120g)} = 240\text{g}$)*

2. **Scale Composite Nutrients**:
   $$\text{Nutrient}_{\text{item}} = \left( \frac{\text{Nutrient}_{\text{cooked 100g}}}{100.0} \right) \times W_{\text{gram}}$$

3. **Aggregate Multi-Food Meal Total**:
   $$\text{Meal Total} = \sum_{i=1}^{M} \text{Nutrient}_{\text{item } i}$$

---

## 6. Execution Commands & Prerequisite Validation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Validate the 3 required inputs (Target 5 Dishes, FCT, RIQ & Portion Units)
python src/validate_prerequisites.py

# 3. Ingest raw FCT table
python src/ingest_wafct.py --input data/raw_wafct_2019.csv --output data/food_composition_table.json

# 4. Compile composite dishes using RIQ lookup
python src/composite_dish_builder.py --riq data/recipe_ingredient_lookup.json --fct data/food_composition_table.json --output data/composite_dishes_db.json

# 5. Bootstrap Qdrant vector index
python scripts/init_qdrant.py --host localhost --port 6333 --data data/composite_dishes_db.json

# 6. Run test suite
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 7. Definition of Done (DoD) Checklist

- [ ] `validate_prerequisites.py` verifies the presence of 5 target dishes, FCT table, RIQ lookup, and portion units before execution.
- [ ] `portion_units.json` provides culturally accurate conventional units and gram mappings for all 5 dishes.
- [ ] `portion_service.py` calculates correct gram mass and macro scaling ($< 200\text{ms}$ SLA).
- [ ] In-memory offline fallback works without Qdrant container.
- [ ] Test coverage $\ge 90\%$ in `tests/`.