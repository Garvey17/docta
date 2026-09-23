"""Composite Dish Nutritional Builder.

Calculates composite dish nutrition using Recipe-Ingredient-Quantity (RIQ) lookup
and Food Composition Table (FCT) ingredient profiles according to Section 4.3 formulas:
1. Total Batch Raw Mass: M_raw = sum(m_k)
2. Ingredient Mass Fraction: w_k = m_k / M_raw
3. Raw Concentration: Nutrient_raw_100g = sum(w_k * Nutrient_k_100g)
4. Cooked Yield Adjustment: Nutrient_cooked_100g = Nutrient_raw_100g / cooking_yield_factor
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from .schemas import (
        RecipeIngredientLookup,
        Recipe,
        FoodItemFCT,
        NutrientProfile,
        CompositeDish,
    )
except ImportError:
    from schemas import (
        RecipeIngredientLookup,
        Recipe,
        FoodItemFCT,
        NutrientProfile,
        CompositeDish,
    )


NUTRIENT_FIELDS = [
    "calories_kcal",
    "protein_g",
    "fat_g",
    "carbs_g",
    "fiber_g",
    "sodium_mg",
    "calcium_mg",
    "iron_mg",
]


WAFCT_CODE_MAPPING = {
    "jollof_rice": "01_042",
    "egusi_soup": "03_015",
    "amala": "02_005",
    "fried_plantain": "02_018",
    "moi_moi": "04_021",
}


def compute_composite_profile(
    recipe: Recipe,
    fct_database: Dict[str, Dict[str, Any]],
    aliases: Optional[List[str]] = None,
) -> CompositeDish:
    """Compute weighted composite nutritional profile for a single recipe."""
    if recipe.cooking_yield_factor <= 0:
        raise ValueError(f"Dish '{recipe.dish_id}' has invalid cooking_yield_factor <= 0")

    total_batch_raw_mass = sum(ing.quantity_g for ing in recipe.ingredients)
    if total_batch_raw_mass <= 0:
        raise ValueError(f"Dish '{recipe.dish_id}' has total raw mass <= 0")

    raw_100g_accum = {field: 0.0 for field in NUTRIENT_FIELDS}

    for ing in recipe.ingredients:
        weight_fraction = ing.quantity_g / total_batch_raw_mass
        fct_entry = fct_database.get(ing.ingredient_code)
        if not fct_entry:
            raise KeyError(
                f"Missing FCT profile for ingredient '{ing.name}' ({ing.ingredient_code}) in dish '{recipe.dish_id}'"
            )
        
        # Handle both flat dict and nested 'nutrients' dict
        ing_nutrients = fct_entry.get("nutrients", fct_entry)

        for field in NUTRIENT_FIELDS:
            val = float(ing_nutrients.get(field, 0.0) or 0.0)
            raw_100g_accum[field] += weight_fraction * val

    # Cooked adjustment: divide raw 100g by cooking_yield_factor
    yield_factor = recipe.cooking_yield_factor
    cooked_100g_accum = {
        field: raw_100g_accum[field] / yield_factor
        for field in NUTRIENT_FIELDS
    }

    raw_profile = NutrientProfile(**raw_100g_accum).round_values(decimals=2)
    cooked_profile = NutrientProfile(**cooked_100g_accum).round_values(decimals=2)

    # Build descriptive text for vector indexing
    ing_names = ", ".join(ing.name for ing in recipe.ingredients)
    description = (
        f"{recipe.dish_name}. Standard portion: {recipe.standard_serving_g}g. "
        f"Constituent ingredients: {ing_names}. Cooked yield factor: {yield_factor}."
    )

    wafct_code = WAFCT_CODE_MAPPING.get(recipe.dish_id, f"WAFCT_{recipe.dish_id.upper()}")

    return CompositeDish(
        dish_id=recipe.dish_id,
        dish_name=recipe.dish_name,
        standard_serving_g=recipe.standard_serving_g,
        cooking_yield_factor=recipe.cooking_yield_factor,
        raw_batch_mass_g=round(total_batch_raw_mass, 2),
        raw_ingredients=recipe.ingredients,
        nutrients_raw_100g=raw_profile,
        nutrients_cooked_100g=cooked_profile,
        wafct_code=wafct_code,
        description=description,
        aliases=aliases or [],
    )


def compile_composite_dishes(
    riq_path: Path,
    fct_path: Path,
    aliases_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    """Compile all recipes in RIQ into composite dish profiles."""
    with open(riq_path, "r", encoding="utf-8") as f:
        riq_raw = json.load(f)
    riq = RecipeIngredientLookup(**riq_raw)

    with open(fct_path, "r", encoding="utf-8") as f:
        fct_db = json.load(f)

    # Invert aliases_map: dish_id -> list of aliases
    dish_aliases: Dict[str, List[str]] = {r.dish_id: [] for r in riq.recipes}
    if aliases_path and Path(aliases_path).exists():
        with open(aliases_path, "r", encoding="utf-8") as f:
            aliases_map = json.load(f)
        for alias_name, dish_id in aliases_map.items():
            if dish_id in dish_aliases and alias_name not in dish_aliases[dish_id]:
                dish_aliases[dish_id].append(alias_name)

    compiled: Dict[str, Dict[str, Any]] = {}
    for recipe in riq.recipes:
        aliases = dish_aliases.get(recipe.dish_id, [])
        comp_dish = compute_composite_profile(recipe, fct_db, aliases=aliases)
        compiled[recipe.dish_id] = comp_dish.model_dump()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(compiled, f, indent=2)

    return compiled


def main() -> int:
    """CLI handler matching Section 7 instructions."""
    parser = argparse.ArgumentParser(description="Compile composite dish nutrition profiles.")
    parser.add_argument("--riq", default="data/recipe_ingredient_lookup.json", help="Path to RIQ table")
    parser.add_argument("--fct", default="data/food_composition_table.json", help="Path to FCT database")
    parser.add_argument("--aliases", default="data/aliases_map.json", help="Path to dialect aliases map")
    parser.add_argument("--output", default="data/composite_dishes_db.json", help="Output path for composite dishes")
    args = parser.parse_args()

    try:
        compiled = compile_composite_dishes(
            Path(args.riq),
            Path(args.fct),
            Path(args.aliases) if Path(args.aliases).exists() else None,
            Path(args.output),
        )
        print(f"[SUCCESS] Compiled {len(compiled)} composite dishes into '{args.output}'.")
        for dish_id, dish in compiled.items():
            cooked = dish["nutrients_cooked_100g"]
            print(f"  * {dish['dish_name']} (100g cooked): {cooked['calories_kcal']} kcal, {cooked['protein_g']}g P, {cooked['carbs_g']}g C, {cooked['fat_g']}g F")
        return 0
    except Exception as e:
        print(f"[FATAL] Compilation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
