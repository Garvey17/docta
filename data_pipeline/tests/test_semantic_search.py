"""Tests for semantic_search.py module."""

import pytest
from data_pipeline.src.semantic_search import SemanticSearchEngine


@pytest.fixture(scope="module")
def search_engine():
    """Shared SemanticSearchEngine initialized with in-memory mode."""
    return SemanticSearchEngine(force_memory=True)


def test_exact_riq_dish_lookup(search_engine):
    """Verify exact dish IDs resolve instantly."""
    target_dishes = ["jollof_rice", "egusi_soup", "amala", "fried_plantain", "moi_moi"]
    for dish_id in target_dishes:
        res = search_engine.search_dish(query=dish_id, weight_g=200.0)
        assert res.dish_id == dish_id
        assert not res.is_fallback
        assert res.similarity_score == 1.0
        assert res.nutrients.calories_kcal > 0
        assert len(res.available_portion_units) > 0
        assert res.default_unit_id is not None


def test_alias_mapping_lookup(search_engine):
    """Verify colloquial Nigerian aliases resolve to canonical dish IDs."""
    test_cases = [
        ("dodo", "fried_plantain"),
        ("party jollof", "jollof_rice"),
        ("elubo", "amala"),
        ("melon soup", "egusi_soup"),
        ("moimoi", "moi_moi"),
    ]
    for alias, expected_dish in test_cases:
        res = search_engine.search_dish(query=alias, weight_g=150.0)
        assert res.dish_id == expected_dish
        assert not res.is_fallback
        assert len(res.available_portion_units) > 0


def test_semantic_vector_modified_queries(search_engine):
    """Verify modified queries are matched accurately."""
    res = search_engine.search_dish("spicy party jollof with extra stock", weight_g=250.0)
    assert res.dish_id == "jollof_rice"
    assert not res.is_fallback
    assert res.similarity_score >= 0.25
    assert len(res.available_portion_units) > 0


def test_unmapped_food_fallback(search_engine):
    """Verify unmapped exotic food triggers baseline fallback defaults."""
    res = search_engine.search_dish("extraterrestrial moon cheese stew", weight_g=100.0)
    assert res.is_fallback
    assert res.nutrients.calories_kcal > 0
    assert "Standard" in res.display_name or "Generic" in res.display_name or "Estimated" in res.display_name
    assert len(res.available_portion_units) > 0


def test_portion_unit_search_selection(search_engine):
    """Verify searching a dish with unit_id and quantity scales correctly."""
    res = search_engine.search_dish(
        query="jollof_rice",
        selected_unit_id="serving_spoon",
        selected_quantity=2.0
    )
    assert res.dish_id == "jollof_rice"
    assert res.weight_g == 240.0  # 2 x 120g
    assert res.selected_unit_id == "serving_spoon"
    assert res.selected_quantity == 2.0
