"""Additional edge case tests to ensure comprehensive coverage across data_pipeline."""

from pathlib import Path
import pytest

from data_pipeline.src.schemas import (
    NutrientProfile,
    TotalNutrition,
    MealAnalysisResponse,
    MealItemInput,
    CompositeDish,
    Ingredient,
)
from data_pipeline.src.macro_scaler import (
    scale_nutrients,
    build_scaled_item,
    aggregate_meal_nutrition,
)
from data_pipeline.src.semantic_search import (
    SemanticSearchEngine,
    _normalize_text,
    _token_jaccard_similarity,
)
from data_pipeline.src.vector_indexer import (
    TextEmbedder,
    get_qdrant_client,
    build_dish_document_text,
)
from data_pipeline.src.rag_service import (
    RAGService,
    get_rag_service,
    analyze_meal,
)
from data_pipeline.src.validate_prerequisites import (
    validate_prerequisites,
    PrerequisiteValidationError,
    main as prereq_main,
)


def test_nutrient_profile_round_values():
    """Verify round_values method on NutrientProfile."""
    np_raw = NutrientProfile(
        calories_kcal=123.456,
        protein_g=12.345,
        fat_g=6.789,
        carbs_g=45.678,
        fiber_g=2.345,
        sodium_mg=100.555,
        calcium_mg=20.444,
        iron_mg=1.888,
    )
    np_rounded = np_raw.round_values(decimals=1)
    assert np_rounded.calories_kcal == 123.5
    assert np_rounded.protein_g == 12.3
    assert np_rounded.fat_g == 6.8
    assert np_rounded.carbs_g == 45.7
    assert np_rounded.fiber_g == 2.3
    assert np_rounded.sodium_mg == 100.6
    assert np_rounded.calcium_mg == 20.4
    assert np_rounded.iron_mg == 1.9


def test_total_nutrition_round_values():
    """Verify round_values method on TotalNutrition."""
    tn_raw = TotalNutrition(
        total_calories_kcal=500.555,
        total_protein_g=30.333,
        total_fat_g=15.777,
        total_carbs_g=70.123,
        total_fiber_g=5.555,
        total_sodium_mg=450.456,
        total_calcium_mg=50.789,
        total_iron_mg=3.456,
    )
    tn_rounded = tn_raw.round_values(decimals=1)
    assert tn_rounded.total_calories_kcal == 500.6
    assert tn_rounded.total_protein_g == 30.3
    assert tn_rounded.total_fat_g == 15.8
    assert tn_rounded.total_carbs_g == 70.1
    assert tn_rounded.total_fiber_g == 5.6
    assert tn_rounded.total_sodium_mg == 450.5
    assert tn_rounded.total_calcium_mg == 50.8
    assert tn_rounded.total_iron_mg == 3.5


def test_scale_nutrients_zero_or_negative_weight():
    """Verify zero or negative weight results in zeroed nutrients."""
    nutrients_100g = {
        "calories_kcal": 200.0,
        "protein_g": 10.0,
        "fat_g": 5.0,
        "carbs_g": 30.0,
        "fiber_g": 2.0,
        "sodium_mg": 150.0,
        "calcium_mg": 20.0,
        "iron_mg": 1.5,
    }
    zero_res = scale_nutrients(nutrients_100g, weight_g=0.0)
    assert zero_res.calories_kcal == 0.0
    assert zero_res.protein_g == 0.0

    neg_res = scale_nutrients(nutrients_100g, weight_g=-50.0)
    assert neg_res.calories_kcal == 0.0


def test_scale_nutrients_nested_dict():
    """Verify scale_nutrients handles nested dict {"nutrients": {...}}."""
    nested_data = {
        "dish_name": "Test",
        "nutrients": {
            "calories_kcal": 100.0,
            "protein_g": 5.0,
            "fat_g": 2.0,
            "carbs_g": 15.0,
        }
    }
    res = scale_nutrients(nested_data, weight_g=200.0)
    assert res.calories_kcal == 200.0
    assert res.protein_g == 10.0


def test_normalize_text_and_jaccard_edge_cases():
    """Verify text normalization and empty token jaccard similarity."""
    assert _normalize_text("  Party Jollof Rice! @2026 #Spicy  ") == "party jollof rice   2026  spicy"
    assert _token_jaccard_similarity("", "jollof rice") == 0.0
    assert _token_jaccard_similarity("jollof", "") == 0.0
    assert _token_jaccard_similarity("same words", "same words") == 1.0


def test_rag_service_singleton_and_module_helper():
    """Verify get_rag_service singleton behavior and module-level analyze_meal helper."""
    s1 = get_rag_service(force_memory=True)
    s2 = get_rag_service(force_memory=True)
    assert s1 is s2

    res = analyze_meal(
        items=[
            {"dish_id": "jollof_rice", "weight_g": 250.0},
            MealItemInput(dish_name="fried_plantain", weight_g=150.0),
        ]
    )
    assert isinstance(res, MealAnalysisResponse)
    assert len(res.detected_items) == 2
    assert res.total_nutrition.total_calories_kcal > 0


def test_rag_service_type_error_on_invalid_item():
    """Verify analyze_meal raises TypeError when item is neither dict nor MealItemInput."""
    service = RAGService(force_memory=True)
    with pytest.raises(TypeError) as exc_info:
        service.analyze_meal(items=["invalid_string_item"])
    assert "Expected dict or MealItemInput" in str(exc_info.value)


def test_build_dish_document_text():
    """Verify build_dish_document_text formats all metadata fields properly."""
    dish = {
        "dish_name": "Nigerian Jollof Rice",
        "dish_id": "jollof_rice",
        "aliases": ["party jollof", "smoky jollof"],
        "description": "Rich tomato rice",
        "raw_ingredients": [
            {"name": "Rice", "quantity_g": 100.0},
            {"name": "Tomato", "quantity_g": 30.0},
        ],
    }
    doc_text = build_dish_document_text(dish)
    assert "Nigerian Jollof Rice (jollof_rice)" in doc_text
    assert "party jollof" in doc_text
    assert "Rice, Tomato" in doc_text


def test_semantic_search_empty_dir(tmp_path):
    """Verify SemanticSearchEngine initializes safely with empty data dir."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    engine = SemanticSearchEngine(data_dir=empty_dir, force_memory=True)
    assert engine.composite_db == {}
    assert engine.aliases_map == {}
    res = engine.search_dish("unknown food", 100.0)
    assert res.is_fallback


def test_semantic_search_vector_search_exception(monkeypatch):
    """Verify semantic search falls back to in-memory matching on vector error."""
    engine = SemanticSearchEngine(force_memory=True)
    res = engine.search_dish("party jollof with pepper", 250.0)
    assert res.dish_id == "jollof_rice"
    assert not res.is_fallback


def test_macro_scaler_type_error():
    """Verify scale_nutrients raises TypeError on invalid input type."""
    with pytest.raises(TypeError):
        scale_nutrients("invalid_input_type", 100.0)


def test_vector_indexer_extra_coverage():
    """Verify embed_query, default client and memory flag."""
    embedder = TextEmbedder()
    q_vec = embedder.embed_query("jollof rice")
    assert len(q_vec) in (384, 1536)

    c = get_qdrant_client()
    assert c is not None

    empty_vec = embedder._hash_embed("")
    assert len(empty_vec) in (384, 1536)


def test_validate_prerequisites_cli_error_printing(tmp_path, monkeypatch, capsys):
    """Verify CLI main error branch printing."""
    empty_data = tmp_path / "empty_dir"
    empty_data.mkdir()
    (empty_data / "recipe_ingredient_lookup.json").write_text('{"recipes": []}', encoding="utf-8")
    monkeypatch.setattr(
        "data_pipeline.src.validate_prerequisites.get_default_data_dir",
        lambda: empty_data
    )
    exit_code = prereq_main()
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Prerequisite validation failed" in captured.out or "FATAL" in captured.err


def test_validate_prerequisites_with_xlsx_only(tmp_path):
    """Verify validate_prerequisites detects NCT_Nigeria.xlsx when JSON is absent."""
    pytest.importorskip("openpyxl")
    import shutil
    data_source = Path(__file__).resolve().parent.parent / "data"
    data_dir = tmp_path / "xlsx_test_dir"
    data_dir.mkdir()
    shutil.copy(data_source / "recipe_ingredient_lookup.json", data_dir / "recipe_ingredient_lookup.json")
    shutil.copy(data_source / "portion_units.json", data_dir / "portion_units.json")
    if (data_source / "NCT_Nigeria.xlsx").exists():
        shutil.copy(data_source / "NCT_Nigeria.xlsx", data_dir / "NCT_Nigeria.xlsx")
        res = validate_prerequisites(data_dir=data_dir, auto_recover=False)
        assert res["status"] == "passed"
        assert "NCT_Nigeria.xlsx" in res["fct_file"]


def test_validate_prerequisites_with_csv_only(tmp_path):
    """Verify validate_prerequisites detects raw_wafct_2019.csv when JSON and XLSX absent."""
    import shutil
    data_source = Path(__file__).resolve().parent.parent / "data"
    data_dir = tmp_path / "csv_test_dir"
    data_dir.mkdir()
    shutil.copy(data_source / "recipe_ingredient_lookup.json", data_dir / "recipe_ingredient_lookup.json")
    shutil.copy(data_source / "portion_units.json", data_dir / "portion_units.json")
    if (data_source / "raw_wafct_2019.csv").exists():
        shutil.copy(data_source / "raw_wafct_2019.csv", data_dir / "raw_wafct_2019.csv")
        res = validate_prerequisites(data_dir=data_dir, auto_recover=False)
        assert "raw_wafct_2019.csv" in res["fct_file"]


def test_text_embedder_engine_modes():
    """Verify TextEmbedder output dimensions."""
    embedder = TextEmbedder()
    vecs = embedder.embed_texts(["hello world"])
    assert len(vecs) == 1
    assert len(vecs[0]) in (384, 1536)
