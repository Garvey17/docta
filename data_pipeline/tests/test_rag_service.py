"""Tests for rag_service.py."""

import pytest
from data_pipeline.src.rag_service import RAGService, analyze_meal
from data_pipeline.src.schemas import MealItemInput, MealAnalysisResponse


@pytest.fixture(scope="module")
def rag_service():
    """Instantiate RAGService with in-memory Qdrant."""
    return RAGService(force_memory=True)


def test_analyze_meal_canonical_contract(rag_service):
    """Verify analyze_meal returns contract matching PROJECT_ORCHESTRATION.md Section 6.2 B."""
    items = [
        {
            "dish_id": "jollof_rice",
            "weight_g": 272.0,
            "confidence": 0.93,
            "bounding_box": [0.125, 0.240, 0.550, 0.780],
        },
        {
            "dish_id": "fried_plantain",
            "weight_g": 150.0,
            "confidence": 0.89,
            "bounding_box": [0.580, 0.310, 0.890, 0.650],
        },
    ]

    response = rag_service.analyze_meal(
        items=items,
        analysis_id="anlz_test_123",
        image_url="https://storage.docta.ng/meals/temp_test.jpg",
    )

    assert isinstance(response, MealAnalysisResponse)
    assert response.analysis_id == "anlz_test_123"
    assert response.status == "success"
    assert response.image_url == "https://storage.docta.ng/meals/temp_test.jpg"
    assert len(response.detected_items) == 2

    # Check item 1
    item1 = response.detected_items[0]
    assert item1.dish_id == "jollof_rice"
    assert item1.weight_g == 272.0
    assert item1.confidence == 0.93
    assert item1.bounding_box == [0.125, 0.240, 0.550, 0.780]
    assert item1.wafct_code == "01_042"
    assert not item1.is_fallback
    assert item1.nutrients.calories_kcal > 0

    # Check item 2
    item2 = response.detected_items[1]
    assert item2.dish_id == "fried_plantain"
    assert item2.weight_g == 150.0
    assert item2.confidence == 0.89
    assert item2.wafct_code == "02_018"

    # Check total nutrition aggregation
    total = response.total_nutrition
    expected_kcal = round(item1.nutrients.calories_kcal + item2.nutrients.calories_kcal, 1)
    assert total.total_calories_kcal == expected_kcal
    assert total.total_protein_g == round(item1.nutrients.protein_g + item2.nutrients.protein_g, 1)
    assert total.total_fat_g == round(item1.nutrients.fat_g + item2.nutrients.fat_g, 1)
    assert total.total_carbs_g == round(item1.nutrients.carbs_g + item2.nutrients.carbs_g, 1)

    # SLA check
    assert response.processing_duration_ms < 200.0


def test_analyze_meal_pydantic_inputs(rag_service):
    """Verify analyze_meal handles MealItemInput schema instances."""
    items = [
        MealItemInput(query="egusi soup", weight_g=200.0, confidence=0.91),
        MealItemInput(query="amala", weight_g=300.0, confidence=0.95),
    ]

    response = rag_service.analyze_meal(items=items)
    assert response.status == "success"
    assert len(response.detected_items) == 2
    assert response.detected_items[0].dish_id == "egusi_soup"
    assert response.detected_items[1].dish_id == "amala"
    assert response.total_nutrition.total_calories_kcal > 0


def test_get_dish_nutrition(rag_service):
    """Verify single dish nutrition retrieval."""
    item = rag_service.get_dish_nutrition("moi_moi", weight_g=200.0)
    assert item.dish_id == "moi_moi"
    assert item.weight_g == 200.0
    assert not item.is_fallback
    assert item.nutrients.protein_g > 0


def test_module_level_analyze_meal():
    """Verify module-level analyze_meal helper function."""
    res = analyze_meal([{"dish_id": "jollof_rice", "weight_g": 200.0}])
    assert res.status == "success"
    assert len(res.detected_items) == 1
    assert res.detected_items[0].dish_id == "jollof_rice"


def test_analyze_meal_invalid_type(rag_service):
    """Verify TypeError raised when item is neither dict nor MealItemInput."""
    with pytest.raises(TypeError):
        rag_service.analyze_meal(["invalid_string_item"])
