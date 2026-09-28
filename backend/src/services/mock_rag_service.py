"""Deterministic Mock RAG Service.

Supplies culturally conventional African portion units (spoons, wraps, slices, cups)
and 100g WAFCT base nutrition without requiring external vector databases or LLMs.
"""

from typing import Dict, Any

MOCK_PORTION_UNITS_REGISTRY: Dict[str, Any] = {
    "jollof_rice": {
        "dish_id": "jollof_rice",
        "dish_name": "Nigerian Jollof Rice",
        "default_unit_id": "serving_spoon",
        "default_quantity": 2.0,
        "units": [
            {
                "unit_id": "serving_spoon",
                "unit_name": "Serving Spoon",
                "gram_weight": 120.0,
                "description": "Standard catering/cooking spoon (~120g)",
            },
            {
                "unit_id": "mound_cup",
                "unit_name": "Mound / Cup",
                "gram_weight": 250.0,
                "description": "Standard dining plate mound (~250g)",
            },
            {
                "unit_id": "takeaway_pack",
                "unit_name": "Takeaway Pack",
                "gram_weight": 500.0,
                "description": "Full standard plastic takeaway pack (~500g)",
            },
        ],
    },
    "fried_plantain": {
        "dish_id": "fried_plantain",
        "dish_name": "Fried Ripe Plantain (Dodo)",
        "default_unit_id": "portion_6_slices",
        "default_quantity": 1.0,
        "units": [
            {
                "unit_id": "single_slice",
                "unit_name": "Single Slice / Piece",
                "gram_weight": 25.0,
                "description": "One slice (~25g)",
            },
            {
                "unit_id": "portion_6_slices",
                "unit_name": "Small Portion (6 slices)",
                "gram_weight": 150.0,
                "description": "Standard side portion (~150g)",
            },
            {
                "unit_id": "large_portion",
                "unit_name": "Large Portion (12 slices)",
                "gram_weight": 300.0,
                "description": "Double side portion (~300g)",
            },
        ],
    },
    "amala": {
        "dish_id": "amala",
        "dish_name": "Àmàlà (Yam Flour Swallow)",
        "default_unit_id": "medium_wrap",
        "default_quantity": 1.0,
        "units": [
            {
                "unit_id": "small_wrap",
                "unit_name": "Small Wrap",
                "gram_weight": 150.0,
                "description": "Light portion (~150g)",
            },
            {
                "unit_id": "medium_wrap",
                "unit_name": "Medium Wrap",
                "gram_weight": 250.0,
                "description": "Standard restaurant wrap (~250g)",
            },
            {
                "unit_id": "large_wrap",
                "unit_name": "Large Wrap",
                "gram_weight": 400.0,
                "description": "Heavy portion (~400g)",
            },
        ],
    },
    "egusi_soup": {
        "dish_id": "egusi_soup",
        "dish_name": "Egusi Melon Seed Soup",
        "default_unit_id": "serving_spoon",
        "default_quantity": 2.0,
        "units": [
            {
                "unit_id": "serving_spoon",
                "unit_name": "Serving Spoon",
                "gram_weight": 100.0,
                "description": "Standard soup spoon (~100g)",
            },
            {
                "unit_id": "small_bowl",
                "unit_name": "Small Soup Bowl",
                "gram_weight": 200.0,
                "description": "Side soup bowl (~200g)",
            },
            {
                "unit_id": "large_bowl",
                "unit_name": "Large Soup Bowl",
                "gram_weight": 350.0,
                "description": "Main soup bowl (~350g)",
            },
        ],
    },
    "moi_moi": {
        "dish_id": "moi_moi",
        "dish_name": "Moi Moi (Steamed Bean Pudding)",
        "default_unit_id": "single_wrap",
        "default_quantity": 1.0,
        "units": [
            {
                "unit_id": "single_wrap",
                "unit_name": "Single Wrap",
                "gram_weight": 150.0,
                "description": "One standard leaf or tin wrap (~150g)",
            },
            {
                "unit_id": "double_wrap",
                "unit_name": "Double Wrap",
                "gram_weight": 300.0,
                "description": "Two wraps (~300g)",
            },
        ],
    },
}

MOCK_NUTRITION_PROFILES: Dict[str, Any] = {
    "jollof_rice": {
        "nutrients_per_100g": {
            "calories_kcal": 140.0,
            "protein_g": 2.7,
            "fat_g": 4.0,
            "carbs_g": 23.0,
            "fiber_g": 1.0,
            "sodium_mg": 180.0,
            "calcium_mg": 8.0,
            "iron_mg": 0.7,
        },
        "display_name": "Nigerian Jollof Rice",
        "wafct_code": "01_JOLLOF",
    },
    "fried_plantain": {
        "nutrients_per_100g": {
            "calories_kcal": 208.0,
            "protein_g": 1.2,
            "fat_g": 9.4,
            "carbs_g": 32.0,
            "fiber_g": 2.4,
            "sodium_mg": 4.0,
            "calcium_mg": 10.0,
            "iron_mg": 0.6,
        },
        "display_name": "Fried Ripe Plantain (Dodo)",
        "wafct_code": "02_DODO",
    },
    "amala": {
        "nutrients_per_100g": {
            "calories_kcal": 110.0,
            "protein_g": 1.5,
            "fat_g": 0.3,
            "carbs_g": 25.4,
            "fiber_g": 3.2,
            "sodium_mg": 12.0,
            "calcium_mg": 14.0,
            "iron_mg": 1.1,
        },
        "display_name": "Àmàlà (Yam Flour Swallow)",
        "wafct_code": "03_AMALA",
    },
    "egusi_soup": {
        "nutrients_per_100g": {
            "calories_kcal": 220.0,
            "protein_g": 8.5,
            "fat_g": 17.0,
            "carbs_g": 8.2,
            "fiber_g": 3.8,
            "sodium_mg": 340.0,
            "calcium_mg": 45.0,
            "iron_mg": 2.8,
        },
        "display_name": "Egusi Melon Seed Soup",
        "wafct_code": "04_EGUSI",
    },
    "moi_moi": {
        "nutrients_per_100g": {
            "calories_kcal": 128.0,
            "protein_g": 7.2,
            "fat_g": 4.5,
            "carbs_g": 14.8,
            "fiber_g": 3.2,
            "sodium_mg": 210.0,
            "calcium_mg": 22.0,
            "iron_mg": 1.4,
        },
        "display_name": "Moi Moi (Steamed Bean Pudding)",
        "wafct_code": "05_MOIMOI",
    },
}


class MockRAGService:
    """Provides deterministic portion units and nutrient mappings."""

    @staticmethod
    def get_portion_units(dish_id: str) -> Dict[str, Any]:
        clean_id = dish_id.lower().strip().replace(" ", "_")
        if clean_id in MOCK_PORTION_UNITS_REGISTRY:
            return MOCK_PORTION_UNITS_REGISTRY[clean_id]

        return {
            "dish_id": clean_id,
            "dish_name": dish_id.replace("_", " ").title(),
            "default_unit_id": "standard_serving",
            "default_quantity": 1.0,
            "units": [
                {
                    "unit_id": "standard_serving",
                    "unit_name": "Standard Serving",
                    "gram_weight": 150.0,
                    "description": "Standard serving (~150g)",
                },
                {
                    "unit_id": "small_portion",
                    "unit_name": "Small Portion",
                    "gram_weight": 75.0,
                    "description": "Small portion (~75g)",
                },
                {
                    "unit_id": "large_portion",
                    "unit_name": "Large Portion",
                    "gram_weight": 300.0,
                    "description": "Large portion (~300g)",
                },
            ],
        }

    @staticmethod
    def get_nutrients(dish_id: str) -> Dict[str, Any]:
        clean_id = dish_id.lower().strip().replace(" ", "_")
        if clean_id in MOCK_NUTRITION_PROFILES:
            return MOCK_NUTRITION_PROFILES[clean_id]

        return {
            "nutrients_per_100g": {
                "calories_kcal": 150.0,
                "protein_g": 3.5,
                "fat_g": 4.5,
                "carbs_g": 22.0,
                "fiber_g": 1.5,
                "sodium_mg": 120.0,
                "calcium_mg": 15.0,
                "iron_mg": 1.0,
            },
            "display_name": dish_id.replace("_", " ").title(),
            "wafct_code": "00_COMPOSITE",
        }
