"""Tests for portion_service.py module."""

import pytest
from pathlib import Path
from data_pipeline.src.portion_service import PortionService
from data_pipeline.src.schemas import PortionUnit, DishPortionConfig


@pytest.fixture
def portion_service():
    return PortionService()


def test_portion_service_load_5_dishes(portion_service):
    """Verify all 5 target dishes have registered portion units."""
    target_dishes = ["jollof_rice", "egusi_soup", "amala", "fried_plantain", "moi_moi"]
    for dish_id in target_dishes:
        config = portion_service.get_portion_config(dish_id)
        assert config.dish_id == dish_id
        assert len(config.units) >= 2
        assert config.default_unit_id is not None
        assert config.default_quantity > 0


def test_portion_service_jollof_serving_spoon(portion_service):
    """Verify Jollof Rice 2 serving spoons = 240g."""
    weight, unit, qty = portion_service.calculate_portion_grams(
        dish_id="jollof_rice",
        unit_id="serving_spoon",
        quantity=2.0,
    )
    assert weight == 240.0
    assert unit == "serving_spoon"
    assert qty == 2.0


def test_portion_service_amala_medium_wrap(portion_service):
    """Verify Amala 1 medium wrap = 250g, 2 wraps = 500g."""
    weight1, unit1, qty1 = portion_service.calculate_portion_grams(
        dish_id="amala",
        unit_id="medium_wrap",
        quantity=1.0,
    )
    assert weight1 == 250.0

    weight2, unit2, qty2 = portion_service.calculate_portion_grams(
        dish_id="amala",
        unit_id="medium_wrap",
        quantity=2.0,
    )
    assert weight2 == 500.0


def test_portion_service_custom_weight_override(portion_service):
    """Verify custom gram override bypasses unit calculation."""
    weight, unit, qty = portion_service.calculate_portion_grams(
        dish_id="jollof_rice",
        unit_id="serving_spoon",
        quantity=2.0,
        custom_weight_g=385.5,
    )
    assert weight == 385.5
    assert unit == "custom_grams"


def test_portion_service_unmapped_dish_fallback(portion_service):
    """Verify unmapped dish falls back to generic standard serving."""
    config = portion_service.get_portion_config("unknown_dish_xyz")
    assert config.default_unit_id == "standard_serving"
    weight, unit, qty = portion_service.calculate_portion_grams(
        dish_id="unknown_dish_xyz",
        quantity=1.0,
    )
    assert weight == 150.0
