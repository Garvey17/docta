"""Tests for macro_scaler.py."""

import pytest
from data_pipeline.src.macro_scaler import (
    scale_nutrients,
    build_scaled_item,
    aggregate_meal_nutrition,
)
from data_pipeline.src.schemas import NutrientProfile, ScaledItemNutrition


def test_scale_nutrients_basic():
    """Verify linear scaling for standard portions."""
    cooked_100g = {
        "calories_kcal": 200.0,
        "protein_g": 10.0,
        "fat_g": 5.0,
        "carbs_g": 30.0,
        "fiber_g": 2.0,
        "sodium_mg": 100.0,
        "calcium_mg": 50.0,
        "iron_mg": 2.0,
    }
    # 250g should be 2.5x of each nutrient
    scaled = scale_nutrients(cooked_100g, 250.0)
    assert scaled.calories_kcal == 500.0
    assert scaled.protein_g == 25.0
    assert scaled.fat_g == 12.5
    assert scaled.carbs_g == 75.0
    assert scaled.fiber_g == 5.0
    assert scaled.sodium_mg == 250.0
    assert scaled.calcium_mg == 125.0
    assert scaled.iron_mg == 5.0


def test_scale_nutrients_zero_and_negative():
    """Verify that zero or negative portion weight safely returns 0 without crashing."""
    cooked_100g = {"calories_kcal": 350.0, "protein_g": 8.0, "fat_g": 10.0, "carbs_g": 55.0}
    scaled_zero = scale_nutrients(cooked_100g, 0.0)
    assert scaled_zero.calories_kcal == 0.0
    assert scaled_zero.protein_g == 0.0

    scaled_neg = scale_nutrients(cooked_100g, -50.0)
    assert scaled_neg.calories_kcal == 0.0
    assert scaled_neg.protein_g == 0.0


def test_build_scaled_item_contract():
    """Verify build_scaled_item produces schema compliant with PROJECT_ORCHESTRATION.md."""
    cooked_100g = {
        "calories_kcal": 304.7,
        "protein_g": 5.3,
        "fat_g": 8.0,
        "carbs_g": 52.1,
        "fiber_g": 2.1,
        "sodium_mg": 400.0,
        "calcium_mg": 20.0,
        "iron_mg": 1.5,
    }
    item = build_scaled_item(
        dish_id="jollof_rice",
        display_name="Nigerian Jollof Rice",
        weight_g=250.0,
        cooked_100g=cooked_100g,
        wafct_code="01_042",
        similarity_score=0.985,
        is_fallback=False,
        confidence=0.95,
        item_id="item_1",
        bounding_box=[0.1, 0.2, 0.5, 0.8],
    )
    assert item.dish_id == "jollof_rice"
    assert item.item_id == "item_1"
    assert item.weight_g == 250.0
    assert item.wafct_code == "01_042"
    assert item.similarity_score == 0.985
    assert not item.is_fallback
    assert item.nutrients.calories_kcal == round(304.7 * 2.5, 1)


def test_aggregate_meal_nutrition():
    """Verify aggregation across multiple dishes."""
    item1 = build_scaled_item(
        dish_id="jollof_rice",
        display_name="Jollof Rice",
        weight_g=250.0,
        cooked_100g={"calories_kcal": 300.0, "protein_g": 5.0, "fat_g": 8.0, "carbs_g": 50.0, "fiber_g": 2.0, "sodium_mg": 400.0, "calcium_mg": 20.0, "iron_mg": 1.5},
    )
    item2 = build_scaled_item(
        dish_id="fried_plantain",
        display_name="Dodo",
        weight_g=150.0,
        cooked_100g={"calories_kcal": 220.0, "protein_g": 1.5, "fat_g": 9.0, "carbs_g": 35.0, "fiber_g": 2.5, "sodium_mg": 5.0, "calcium_mg": 10.0, "iron_mg": 0.8},
    )

    total = aggregate_meal_nutrition([item1, item2])
    # item1 kcal: 300 * 2.5 = 750
    # item2 kcal: 220 * 1.5 = 330
    assert total.total_calories_kcal == 1080.0
    assert total.total_protein_g == round(item1.nutrients.protein_g + item2.nutrients.protein_g, 1)
    assert total.total_carbs_g == round(item1.nutrients.carbs_g + item2.nutrients.carbs_g, 1)
