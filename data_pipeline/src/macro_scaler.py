"""Linear nutrition calculator & portion scaler.

Implements linear scaling formula:
Nutrient_total = (Nutrient_cooked_100g / 100.0) * weight_g

Supports single items and meal aggregation aligned with PROJECT_ORCHESTRATION.md schemas.
"""

from typing import Dict, Any, List, Union, Optional

try:
    from .schemas import (
        NutrientProfile,
        PortionUnit,
        ScaledItemNutrition,
        TotalNutrition,
        MealAnalysisResponse,
    )
except ImportError:
    from schemas import (
        NutrientProfile,
        PortionUnit,
        ScaledItemNutrition,
        TotalNutrition,
        MealAnalysisResponse,
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


def scale_nutrients(
    cooked_100g: Union[NutrientProfile, Dict[str, Any]],
    weight_g: float,
    decimals: int = 1,
) -> NutrientProfile:
    """Scale per-100g cooked nutrient profile by the target portion weight.
    
    Args:
        cooked_100g: Per-100g cooked nutrient profile (NutrientProfile or dict).
        weight_g: Target portion weight in grams.
        decimals: Decimal precision for rounding.
        
    Returns:
        Scaled NutrientProfile object.
    """
    if isinstance(cooked_100g, NutrientProfile):
        profile_dict = cooked_100g.model_dump()
    elif isinstance(cooked_100g, dict):
        # Handle nested nutrients if passed
        profile_dict = cooked_100g.get("nutrients", cooked_100g)
    else:
        raise TypeError(f"Expected NutrientProfile or dict, got {type(cooked_100g)}")

    if weight_g <= 0:
        return NutrientProfile(
            calories_kcal=0.0,
            protein_g=0.0,
            fat_g=0.0,
            carbs_g=0.0,
            fiber_g=0.0,
            sodium_mg=0.0,
            calcium_mg=0.0,
            iron_mg=0.0,
        )

    scale_factor = max(0.0, weight_g) / 100.0
    scaled: Dict[str, float] = {}

    for field in NUTRIENT_FIELDS:
        raw_val = float(profile_dict.get(field, 0.0) or 0.0)
        scaled[field] = round(max(0.0, raw_val * scale_factor), decimals)

    return NutrientProfile(**scaled)


def build_scaled_item(
    dish_id: str,
    display_name: str,
    weight_g: float,
    cooked_100g: Union[NutrientProfile, Dict[str, Any]],
    wafct_code: str = "WAFCT_CUSTOM",
    similarity_score: float = 1.0,
    is_fallback: bool = False,
    confidence: float = 1.0,
    item_id: Optional[str] = None,
    bounding_box: Optional[List[float]] = None,
    available_portion_units: Optional[List[PortionUnit]] = None,
    default_unit_id: Optional[str] = None,
    default_quantity: float = 1.0,
    selected_unit_id: Optional[str] = None,
    selected_quantity: Optional[float] = None,
    nutrients_per_100g: Optional[NutrientProfile] = None,
) -> ScaledItemNutrition:
    """Build a validated ScaledItemNutrition model matching PROJECT_ORCHESTRATION.md."""
    scaled_nutrients = scale_nutrients(cooked_100g, weight_g, decimals=1)

    if nutrients_per_100g is None:
        if isinstance(cooked_100g, NutrientProfile):
            nutrients_per_100g = cooked_100g
        elif isinstance(cooked_100g, dict) and cooked_100g:
            raw_data = cooked_100g.get("nutrients", cooked_100g)
            nutrients_per_100g = NutrientProfile(
                calories_kcal=float(raw_data.get("calories_kcal", 0.0) or 0.0),
                protein_g=float(raw_data.get("protein_g", 0.0) or 0.0),
                fat_g=float(raw_data.get("fat_g", 0.0) or 0.0),
                carbs_g=float(raw_data.get("carbs_g", 0.0) or 0.0),
                fiber_g=float(raw_data.get("fiber_g", 0.0) or 0.0),
                sodium_mg=float(raw_data.get("sodium_mg", 0.0) or 0.0),
                calcium_mg=float(raw_data.get("calcium_mg", 0.0) or 0.0),
                iron_mg=float(raw_data.get("iron_mg", 0.0) or 0.0),
            )
        else:
            nutrients_per_100g = NutrientProfile(
                calories_kcal=0.0,
                protein_g=0.0,
                fat_g=0.0,
                carbs_g=0.0,
                fiber_g=0.0,
                sodium_mg=0.0,
                calcium_mg=0.0,
                iron_mg=0.0,
            )

    return ScaledItemNutrition(
        item_id=item_id,
        dish_id=dish_id,
        display_name=display_name,
        confidence=round(confidence, 2),
        bounding_box=bounding_box,
        weight_g=round(max(0.0, weight_g), 1),
        wafct_code=wafct_code,
        similarity_score=round(similarity_score, 3),
        is_fallback=is_fallback,
        nutrients=scaled_nutrients,
        available_portion_units=available_portion_units or [],
        default_unit_id=default_unit_id,
        default_quantity=default_quantity,
        selected_unit_id=selected_unit_id or default_unit_id,
        selected_quantity=selected_quantity if selected_quantity is not None else default_quantity,
        nutrients_per_100g=nutrients_per_100g,
    )


def aggregate_meal_nutrition(
    items: List[ScaledItemNutrition],
    decimals: int = 1,
) -> TotalNutrition:
    """Sum itemized nutrients into a TotalNutrition summary matching Section 6.2 B."""
    total_kcal = 0.0
    total_p = 0.0
    total_fat = 0.0
    total_carb = 0.0
    total_fib = 0.0
    total_na = 0.0
    total_ca = 0.0
    total_fe = 0.0

    for item in items:
        n = item.nutrients
        total_kcal += n.calories_kcal
        total_p += n.protein_g
        total_fat += n.fat_g
        total_carb += n.carbs_g
        total_fib += n.fiber_g
        total_na += n.sodium_mg
        total_ca += n.calcium_mg
        total_fe += n.iron_mg

    return TotalNutrition(
        total_calories_kcal=round(total_kcal, decimals),
        total_protein_g=round(total_p, decimals),
        total_fat_g=round(total_fat, decimals),
        total_carbs_g=round(total_carb, decimals),
        total_fiber_g=round(total_fib, decimals),
        total_sodium_mg=round(total_na, decimals),
        total_calcium_mg=round(total_ca, decimals),
        total_iron_mg=round(total_fe, decimals),
    )
