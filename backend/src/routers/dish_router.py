"""Dish Resolution and Nutrition Reference Router."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.analyze import (
    DishDetailsResponse,
    PortionUnitInfo,
    NutrientProfile100g,
)
from ..services.rag_client import get_rag_client, RAGClient

router = APIRouter(prefix="/api/v1", tags=["Dishes & Nutrition Reference"])


@router.get(
    "/dishes/{dish_id}",
    response_model=DishDetailsResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve dish details, portion units, and 100g WAFCT nutrition profile",
)
async def get_dish_details(
    dish_id: str,
    rag_client: RAGClient = Depends(get_rag_client),
):
    """Resolve a dish ID or alias via authoritative RAG pipeline.
    
    Returns canonical dish_id, display_name, conventional portion units,
    and authoritative per-100g WAFCT nutrition.
    """
    clean_id = dish_id.lower().strip().replace(" ", "_")

    # Resolve the requested ID or alias through the configured RAG service.
    resolved_id = clean_id
    # Preserve natural-language spacing for semantic search. The normalized
    # underscore form remains useful as the fallback canonical ID.
    item = rag_client.rag_service.get_dish_nutrition(dish_id.strip(), weight_g=100.0)
    if item and item.dish_id:
        resolved_id = item.dish_id

    portion_data = rag_client.get_dish_portion_units(resolved_id)
    nutrient_data = rag_client.get_dish_base_nutrients(resolved_id)

    if not portion_data and not nutrient_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dish '{dish_id}' not found in canonical reference databases.",
        )

    units = [
        PortionUnitInfo(
            unit_id=u["unit_id"],
            unit_name=u["unit_name"],
            gram_weight=float(u["gram_weight"]),
            description=u.get("description", ""),
        )
        for u in portion_data.get("units", [])
    ]

    default_unit_id = portion_data.get("default_unit_id", "standard_serving")
    default_qty = float(portion_data.get("default_quantity", 1.0))
    default_unit_g = next((u.gram_weight for u in units if u.unit_id == default_unit_id), 100.0)

    n100 = nutrient_data.get("nutrients_per_100g", {})
    nutrients = NutrientProfile100g(
        calories_kcal=float(n100.get("calories_kcal", 0.0)),
        protein_g=float(n100.get("protein_g", 0.0)),
        fat_g=float(n100.get("fat_g", 0.0)),
        carbs_g=float(n100.get("carbs_g", 0.0)),
        fiber_g=float(n100.get("fiber_g", 0.0)),
        sodium_mg=float(n100.get("sodium_mg", 0.0)),
        calcium_mg=float(n100.get("calcium_mg", 0.0)),
        iron_mg=float(n100.get("iron_mg", 0.0)),
    )

    display_name = portion_data.get("dish_name") or nutrient_data.get("display_name") or resolved_id.replace("_", " ").title()

    return DishDetailsResponse(
        dish_id=resolved_id,
        display_name=display_name,
        default_unit_id=default_unit_id,
        default_quantity=default_qty,
        default_weight_g=round(default_unit_g * default_qty, 1),
        available_portion_units=units,
        nutrients_per_100g=nutrients,
        wafct_code=nutrient_data.get("wafct_code", "00_COMPOSITE"),
    )
