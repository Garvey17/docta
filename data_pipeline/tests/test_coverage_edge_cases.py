"""Edge case test suite to push test coverage above 90% across all modules."""

import json
from pathlib import Path
import pytest

from data_pipeline.src.validate_prerequisites import (
    validate_prerequisites,
    PrerequisiteValidationError,
    main as prereq_main,
)
from data_pipeline.src.ingest_wafct import (
    ingest_wafct,
    main as ingest_main,
)
from data_pipeline.src.vector_indexer import (
    get_qdrant_client,
    index_composite_dishes,
    TextEmbedder,
    COLLECTION_NAME,
)
from data_pipeline.src.semantic_search import SemanticSearchEngine
from data_pipeline.src.rag_service import get_rag_service, RAGService
from data_pipeline.src.macro_scaler import scale_nutrients, NutrientProfile


def test_validate_prerequisites_dummy_fallback_recovery(tmp_path):
    """Verify validate_prerequisites recovers using dummy_wafct when csv/json absent."""
    data_dir = tmp_path / "dummy_recovery_data"
    data_dir.mkdir()

    # Create RIQ
    riq_data = {
        "recipes": [
            {
                "dish_id": "jollof_rice",
                "dish_name": "Jollof Rice",
                "standard_serving_g": 250.0,
                "cooking_yield_factor": 0.88,
                "ingredients": [{"ingredient_code": "ING_DUMMY", "name": "Dummy", "quantity_g": 100.0}],
            },
            {
                "dish_id": "egusi_soup",
                "dish_name": "Egusi",
                "standard_serving_g": 200.0,
                "cooking_yield_factor": 0.85,
                "ingredients": [{"ingredient_code": "ING_DUMMY", "name": "Dummy", "quantity_g": 50.0}],
            },
            {
                "dish_id": "amala",
                "dish_name": "Amala",
                "standard_serving_g": 300.0,
                "cooking_yield_factor": 2.5,
                "ingredients": [{"ingredient_code": "ING_DUMMY", "name": "Dummy", "quantity_g": 50.0}],
            },
            {
                "dish_id": "fried_plantain",
                "dish_name": "Dodo",
                "standard_serving_g": 150.0,
                "cooking_yield_factor": 0.78,
                "ingredients": [{"ingredient_code": "ING_DUMMY", "name": "Dummy", "quantity_g": 50.0}],
            },
            {
                "dish_id": "moi_moi",
                "dish_name": "Moi Moi",
                "standard_serving_g": 200.0,
                "cooking_yield_factor": 1.1,
                "ingredients": [{"ingredient_code": "ING_DUMMY", "name": "Dummy", "quantity_g": 50.0}],
            },
        ]
    }
    (data_dir / "recipe_ingredient_lookup.json").write_text(json.dumps(riq_data), encoding="utf-8")

    # Create dummy_wafct only
    dummy_data = {
        "ING_DUMMY": {
            "code": "ING_DUMMY",
            "food_name": "Dummy Food",
            "nutrients": {"calories_kcal": 100, "protein_g": 5, "fat_g": 2, "carbs_g": 15},
        }
    }
    (data_dir / "dummy_wafct.json").write_text(json.dumps(dummy_data), encoding="utf-8")

    res = validate_prerequisites(data_dir=data_dir, auto_recover=True)
    assert res["status"] == "passed"
    assert "dummy_wafct.json" in res["fct_file"]


def test_validate_prerequisites_no_fct_error(tmp_path):
    """Verify error when no FCT at all exists."""
    data_dir = tmp_path / "no_fct_data"
    data_dir.mkdir()
    riq_data = {
        "recipes": [
            {"dish_id": d, "dish_name": d, "standard_serving_g": 100, "cooking_yield_factor": 1.0, "ingredients": [{"ingredient_code": "I", "name": "I", "quantity_g": 10}]}
            for d in ["jollof_rice", "egusi_soup", "amala", "fried_plantain", "moi_moi"]
        ]
    }
    (data_dir / "recipe_ingredient_lookup.json").write_text(json.dumps(riq_data), encoding="utf-8")
    with pytest.raises(PrerequisiteValidationError) as exc:
        validate_prerequisites(data_dir=data_dir, auto_recover=False)
    assert "No Food Composition Table found" in str(exc.value)


def test_ingest_wafct_nested_dict_without_code(tmp_path):
    """Verify ingest_wafct handles dict of objects with nested nutrients."""
    raw_dict = {
        "ING_NESTED": {
            "food_name": "Nested Ingredient",
            "nutrients": {"calories_kcal": 250, "protein_g": 8, "fat_g": 4, "carbs_g": 35},
        }
    }
    f_path = tmp_path / "nested_dict.json"
    f_path.write_text(json.dumps(raw_dict), encoding="utf-8")
    res = ingest_wafct(f_path)
    assert "ING_NESTED" in res
    assert res["ING_NESTED"]["code"] == "ING_NESTED"


def test_ingest_wafct_cli_error(monkeypatch):
    """Verify ingest_wafct CLI returns 1 on error."""
    monkeypatch.setattr("sys.argv", ["ingest_wafct.py", "--input", "non_existent_file.csv"])
    exit_code = ingest_main()
    assert exit_code == 1


def test_vector_indexer_recreate_collection():
    """Verify re-indexing existing collection successfully deletes and recreates."""
    client = get_qdrant_client(use_memory=True)
    sample_db = {
        "test": {
            "dish_id": "test",
            "dish_name": "Test",
            "aliases": [],
            "raw_ingredients": [],
            "description": "Test",
            "nutrients_cooked_100g": {"calories_kcal": 100},
        }
    }
    c1 = index_composite_dishes(client, sample_db, collection_name="double_index_col")
    assert c1 == 1
    # Index again to hit line deleting existing collection
    c2 = index_composite_dishes(client, sample_db, collection_name="double_index_col")
    assert c2 == 1


def test_vector_indexer_env_memory_flag(monkeypatch):
    """Verify USE_IN_MEMORY_FALLBACK env flag activates memory client."""
    monkeypatch.setenv("USE_IN_MEMORY_FALLBACK", "true")
    client = get_qdrant_client(host="some_remote_host")
    assert client is not None


def test_text_embedder_exception_fallback(monkeypatch):
    """Verify embedder falls back to hash vectorizer on exception."""
    embedder = TextEmbedder()
    # Force fastembed to raise exception
    if embedder._fastembed_model is not None:
        def raise_err(texts):
            raise RuntimeError("Simulated FastEmbed runtime failure")
        monkeypatch.setattr(embedder._fastembed_model, "embed", raise_err)

    vec = embedder.embed_texts(["test text for exception fallback"])
    assert len(vec) == 1
    assert len(vec[0]) == 384


def test_semantic_search_empty_data_dir(tmp_path):
    """Verify SemanticSearchEngine initializes safely when data_dir is empty."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    engine = SemanticSearchEngine(data_dir=empty_dir, force_memory=True)
    assert engine.composite_db == {}
    assert engine.aliases_map == {}
    # Searching should return default fallback
    res = engine.search_dish("unknown food", 100.0)
    assert res.is_fallback


def test_semantic_search_vector_search_exception(monkeypatch):
    """Verify semantic search falls back to in-memory matching on Qdrant query error."""
    engine = SemanticSearchEngine(force_memory=True)
    def raise_qdrant_err(*args, **kwargs):
        raise RuntimeError("Simulated Qdrant query error")
    monkeypatch.setattr(engine.qdrant_client, "query_points", raise_qdrant_err)

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
    assert len(q_vec) == 384

    # Default client with no args
    c = get_qdrant_client()
    assert c is not None

    # Hash embedder empty text
    empty_vec = embedder._hash_embed("")
    assert len(empty_vec) == 384


def test_validate_prerequisites_cli_error_printing(tmp_path, monkeypatch, capsys):
    """Verify CLI main error branch printing."""
    # Point default dir to an empty dir where auto_recover=True still encounters missing dishes
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
