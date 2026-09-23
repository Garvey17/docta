"""Tests for semantic_search.py."""

import time
import pytest
from data_pipeline.src.semantic_search import SemanticSearchEngine


@pytest.fixture(scope="module")
def search_engine():
    """Instantiate SearchEngine with in-memory Qdrant."""
    return SemanticSearchEngine(force_memory=True)


def test_exact_riq_dish_lookup(search_engine):
    """Verify exact match for the 5 target dishes."""
    dishes = ["jollof_rice", "egusi_soup", "amala", "fried_plantain", "moi_moi"]
    for dish_id in dishes:
        res = search_engine.search_dish(query=dish_id, weight_g=200.0)
        assert res.dish_id == dish_id
        assert res.similarity_score == 1.0
        assert not res.is_fallback
        assert res.weight_g == 200.0
        assert res.nutrients.calories_kcal > 0


def test_alias_resolution(search_engine):
    """Verify colloquial dialect aliases map to canonical dish IDs."""
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


def test_semantic_vector_modified_queries(search_engine):
    """Verify modified queries are matched accurately."""
    res = search_engine.search_dish("spicy party jollof with extra stock", weight_g=250.0)
    assert res.dish_id == "jollof_rice"
    assert not res.is_fallback
    assert res.similarity_score >= 0.35


def test_unmapped_food_fallback(search_engine):
    """Verify unmapped exotic food triggers baseline fallback defaults."""
    res = search_engine.search_dish("extraterrestrial moon cheese stew", weight_g=100.0)
    assert res.is_fallback
    assert res.nutrients.calories_kcal > 0
    assert "Estimated" in res.display_name or "Generic" in res.display_name


def test_generic_category_fallbacks(search_engine):
    """Verify category heuristics for unknown foods (rice, soup, swallow)."""
    res_rice = search_engine._resolve_fallback_default("foreign wild rice")
    assert res_rice["dish_id"] == "generic_rice"

    res_soup = search_engine._resolve_fallback_default("wild mushroom broth soup")
    assert res_soup["dish_id"] == "generic_soup"

    res_swallow = search_engine._resolve_fallback_default("cassava flour fufu swallow")
    assert res_swallow["dish_id"] == "generic_swallow"


def test_search_latency_sla(search_engine):
    """Verify search response time is strictly under 200ms SLA."""
    start = time.perf_counter()
    search_engine.search_dish("jollof_rice", weight_g=250.0)
    duration_ms = (time.perf_counter() - start) * 1000.0
    assert duration_ms < 200.0, f"Latency {duration_ms}ms exceeded 200ms SLA"
