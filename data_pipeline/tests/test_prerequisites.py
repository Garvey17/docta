"""Tests for validate_prerequisites.py module."""

import json
from pathlib import Path
import pytest

from data_pipeline.src.validate_prerequisites import (
    validate_prerequisites,
    PrerequisiteValidationError,
    TARGET_5_DISHES,
    main as cli_main,
)


def test_validate_prerequisites_success():
    """Verify that current data directory passes all 3 prerequisite checks."""
    result = validate_prerequisites(auto_recover=True)
    assert result["status"] == "passed"
    assert set(result["dishes_found"]) >= TARGET_5_DISHES
    assert result["fct_file"] is not None
    assert result["riq_file"] is not None
    assert len(result["errors"]) == 0


def test_validate_prerequisites_cli(capsys):
    """Verify CLI entrypoint returns exit code 0 on valid fixtures."""
    exit_code = cli_main()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[SUCCESS] All 3 prerequisites verified" in captured.out


def test_validate_prerequisites_missing_riq(tmp_path):
    """Verify that missing RIQ file raises PrerequisiteValidationError."""
    empty_dir = tmp_path / "empty_data"
    empty_dir.mkdir()
    with pytest.raises(PrerequisiteValidationError) as exc_info:
        validate_prerequisites(data_dir=empty_dir, auto_recover=False)
    assert "Missing required RIQ lookup file" in str(exc_info.value)


def test_validate_prerequisites_missing_dish(tmp_path):
    """Verify that missing one of the 5 target dishes fails validation."""
    custom_dir = tmp_path / "custom_data"
    custom_dir.mkdir()
    # Write RIQ with only 2 dishes
    riq_data = {
        "recipes": [
            {
                "dish_id": "jollof_rice",
                "dish_name": "Jollof Rice",
                "standard_serving_g": 250.0,
                "cooking_yield_factor": 0.88,
                "ingredients": [{"ingredient_code": "ING_001", "name": "Rice", "quantity_g": 100.0}]
            }
        ]
    }
    (custom_dir / "recipe_ingredient_lookup.json").write_text(json.dumps(riq_data), encoding="utf-8")
    (custom_dir / "raw_wafct_2019.csv").write_text("code,food_name,energy_kcal\nING_001,Rice,360\n", encoding="utf-8")

    with pytest.raises(PrerequisiteValidationError) as exc_info:
        validate_prerequisites(data_dir=custom_dir, auto_recover=False)
    assert "RIQ table is missing target dishes" in str(exc_info.value)


def test_validate_prerequisites_invalid_recipe_fields(tmp_path):
    """Verify that negative serving sizes or missing ingredients are detected."""
    custom_dir = tmp_path / "custom_data"
    custom_dir.mkdir()
    riq_data = {
        "recipes": [
            {
                "dish_id": "jollof_rice",
                "dish_name": "Jollof Rice",
                "standard_serving_g": -50.0,
                "cooking_yield_factor": 0.0,
                "ingredients": []
            }
        ]
    }
    (custom_dir / "recipe_ingredient_lookup.json").write_text(json.dumps(riq_data), encoding="utf-8")
    with pytest.raises(PrerequisiteValidationError):
        validate_prerequisites(data_dir=custom_dir, auto_recover=False)


def test_validate_prerequisites_missing_ingredients(tmp_path):
    """Verify that ingredients in RIQ missing from FCT are detected."""
    custom_dir = tmp_path / "custom_data"
    custom_dir.mkdir()
    riq_data = {
        "recipes": [
            {
                "dish_id": "jollof_rice",
                "dish_name": "Jollof Rice",
                "standard_serving_g": 250.0,
                "cooking_yield_factor": 0.88,
                "ingredients": [
                    {"ingredient_code": "ING_MISSING_123", "name": "Secret", "quantity_g": 10.0}
                ]
            }
        ]
    }
    (custom_dir / "recipe_ingredient_lookup.json").write_text(json.dumps(riq_data), encoding="utf-8")
    (custom_dir / "food_composition_table.json").write_text("{}", encoding="utf-8")

    with pytest.raises(PrerequisiteValidationError) as exc:
        validate_prerequisites(data_dir=custom_dir, auto_recover=False)
    assert "missing" in str(exc.value).lower()


def test_validate_prerequisites_cli_failure(tmp_path, monkeypatch):
    """Verify CLI main returns 1 when validation fails."""
    monkeypatch.setattr(
        "data_pipeline.src.validate_prerequisites.get_default_data_dir",
        lambda: tmp_path / "non_existent_dir"
    )
    exit_code = cli_main()
    assert exit_code == 1
