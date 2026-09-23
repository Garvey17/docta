"""Tests for composite_dish_builder.py."""

import json
from pathlib import Path
import pytest

from data_pipeline.src.composite_dish_builder import (
    compute_composite_profile,
    compile_composite_dishes,
    main as cli_main,
)
from data_pipeline.src.schemas import Recipe, Ingredient


@pytest.fixture
def sample_fct():
    return {
        "ING_RICE": {
            "code": "ING_RICE",
            "food_name": "Rice",
            "nutrients": {
                "calories_kcal": 360.0,
                "protein_g": 7.0,
                "fat_g": 0.6,
                "carbs_g": 79.0,
                "fiber_g": 1.3,
                "sodium_mg": 1.0,
                "calcium_mg": 10.0,
                "iron_mg": 1.2,
            }
        },
        "ING_OIL": {
            "code": "ING_OIL",
            "food_name": "Oil",
            "nutrients": {
                "calories_kcal": 884.0,
                "protein_g": 0.0,
                "fat_g": 100.0,
                "carbs_g": 0.0,
                "fiber_g": 0.0,
                "sodium_mg": 0.0,
                "calcium_mg": 0.0,
                "iron_mg": 0.0,
            }
        }
    }


def test_compute_composite_profile_stoichiometry(sample_fct):
    """Verify Section 4.3 formulas for raw concentration and cooked yield adjustment."""
    # 80g Rice + 20g Oil = 100g raw total
    # Raw kcal = (0.8 * 360) + (0.2 * 884) = 288 + 176.8 = 464.8 kcal per 100g raw
    # Yield factor = 0.8 -> cooked = 464.8 / 0.8 = 581.0 kcal per 100g cooked
    recipe = Recipe(
        dish_id="test_rice",
        dish_name="Test Rice",
        standard_serving_g=200.0,
        cooking_yield_factor=0.8,
        ingredients=[
            Ingredient(ingredient_code="ING_RICE", name="Rice", quantity_g=80.0),
            Ingredient(ingredient_code="ING_OIL", name="Oil", quantity_g=20.0),
        ]
    )

    comp = compute_composite_profile(recipe, sample_fct, aliases=["sample_rice"])
    assert comp.dish_id == "test_rice"
    assert comp.raw_batch_mass_g == 100.0
    assert comp.nutrients_raw_100g.calories_kcal == 464.8
    assert comp.nutrients_cooked_100g.calories_kcal == 581.0
    assert comp.aliases == ["sample_rice"]


def test_compute_composite_profile_missing_ingredient(sample_fct):
    """Verify error raised when recipe has ingredient not in FCT."""
    recipe = Recipe(
        dish_id="test_rice",
        dish_name="Test Rice",
        standard_serving_g=200.0,
        cooking_yield_factor=0.8,
        ingredients=[
            Ingredient(ingredient_code="ING_UNKNOWN", name="Mystery Spice", quantity_g=10.0),
        ]
    )
    with pytest.raises(KeyError) as exc_info:
        compute_composite_profile(recipe, sample_fct)
    assert "Missing FCT profile" in str(exc_info.value)


def test_compute_composite_profile_invalid_yield(sample_fct):
    """Verify error raised for non-positive cooking yield factor."""
    from pydantic import ValidationError
    with pytest.raises((ValueError, ValidationError)):
        Recipe(
            dish_id="test_rice",
            dish_name="Test Rice",
            standard_serving_g=200.0,
            cooking_yield_factor=0.0,
            ingredients=[
                Ingredient(ingredient_code="ING_RICE", name="Rice", quantity_g=80.0),
            ]
        )


def test_compile_composite_dishes_production_files():
    """Verify full compilation from real project data files."""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    riq_path = data_dir / "recipe_ingredient_lookup.json"
    fct_path = data_dir / "food_composition_table.json"
    aliases_path = data_dir / "aliases_map.json"

    assert riq_path.exists()
    assert fct_path.exists()

    compiled = compile_composite_dishes(riq_path, fct_path, aliases_path=aliases_path)
    assert len(compiled) == 5
    for dish_id in ["jollof_rice", "egusi_soup", "amala", "fried_plantain", "moi_moi"]:
        assert dish_id in compiled
        entry = compiled[dish_id]
        assert entry["nutrients_cooked_100g"]["calories_kcal"] > 0
        assert entry["raw_batch_mass_g"] > 0


def test_composite_dish_builder_cli_main(tmp_path, monkeypatch):
    """Verify CLI main entrypoint of composite_dish_builder."""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    riq_path = data_dir / "recipe_ingredient_lookup.json"
    fct_path = data_dir / "food_composition_table.json"
    out_path = tmp_path / "compiled_out.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "composite_dish_builder.py",
            "--riq", str(riq_path),
            "--fct", str(fct_path),
            "--output", str(out_path),
        ]
    )
    exit_code = cli_main()
    assert exit_code == 0
    assert out_path.exists()
