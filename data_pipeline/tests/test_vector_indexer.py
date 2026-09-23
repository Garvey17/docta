"""Tests for vector_indexer.py."""

import json
from pathlib import Path
import numpy as np
import pytest

from data_pipeline.src.vector_indexer import (
    TextEmbedder,
    get_qdrant_client,
    build_dish_document_text,
    index_composite_dishes,
    COLLECTION_NAME,
    VECTOR_DIMENSION,
)


def test_text_embedder_dimension_and_norm():
    """Verify embedder outputs 384-d unit vectors."""
    embedder = TextEmbedder()
    vec = embedder.embed_query("Nigerian Jollof Rice with chicken")
    assert len(vec) == VECTOR_DIMENSION
    norm = np.linalg.norm(vec)
    assert np.isclose(norm, 1.0, atol=1e-3)


def test_hash_embedder_fallback():
    """Verify deterministic hash fallback produces reproducible normalized vectors."""
    embedder = TextEmbedder()
    vec1 = embedder._hash_embed("amala and egusi soup")
    vec2 = embedder._hash_embed("amala and egusi soup")
    assert len(vec1) == VECTOR_DIMENSION
    assert vec1 == vec2
    norm = np.linalg.norm(vec1)
    assert np.isclose(norm, 1.0, atol=1e-3)


def test_build_dish_document_text():
    """Verify document formatting combines dish name, aliases, ingredients, and description."""
    sample_dish = {
        "dish_name": "Nigerian Jollof Rice",
        "dish_id": "jollof_rice",
        "aliases": ["party jollof", "smoky jollof"],
        "description": "Rich tomato rice dish.",
        "raw_ingredients": [
            {"name": "Long Grain White Rice"},
            {"name": "Tomato Paste"},
        ],
    }
    doc = build_dish_document_text(sample_dish)
    assert "Nigerian Jollof Rice" in doc
    assert "party jollof" in doc
    assert "Tomato Paste" in doc


def test_index_composite_dishes_in_memory():
    """Verify end-to-end collection creation and vector upsert in in-memory Qdrant."""
    client = get_qdrant_client(use_memory=True)
    sample_db = {
        "jollof_rice": {
            "dish_id": "jollof_rice",
            "dish_name": "Nigerian Jollof Rice",
            "aliases": ["party jollof"],
            "raw_ingredients": [{"name": "Rice"}],
            "description": "Party rice",
            "nutrients_cooked_100g": {"calories_kcal": 304.7},
        },
        "fried_plantain": {
            "dish_id": "fried_plantain",
            "dish_name": "Fried Ripe Plantain",
            "aliases": ["dodo"],
            "raw_ingredients": [{"name": "Plantain"}],
            "description": "Sweet fried dodo",
            "nutrients_cooked_100g": {"calories_kcal": 219.6},
        },
    }

    count = index_composite_dishes(client, sample_db, collection_name="test_dishes")
    assert count == 2

    # Verify points stored in collection
    collection_info = client.get_collection("test_dishes")
    assert collection_info.points_count == 2


def test_qdrant_client_path(tmp_path):
    """Verify local on-disk storage initialization."""
    db_path = tmp_path / "qdrant_storage"
    client = get_qdrant_client(path=str(db_path))
    assert client is not None


def test_init_qdrant_cli_main(monkeypatch):
    """Verify scripts/init_qdrant.py CLI execution."""
    from data_pipeline.scripts.init_qdrant import main as init_qdrant_main
    monkeypatch.setattr("sys.argv", ["init_qdrant.py", "--memory"])
    exit_code = init_qdrant_main()
    assert exit_code == 0


def test_qdrant_client_host_fallback():
    """Verify get_qdrant_client falls back to memory when host is unreachable."""
    client = get_qdrant_client(host="invalid_dummy_host_999", port=6333)
    assert client is not None


def test_init_qdrant_cli_missing_file(monkeypatch):
    """Verify init_qdrant CLI returns 1 on non-existent file."""
    from data_pipeline.scripts.init_qdrant import main as init_qdrant_main
    monkeypatch.setattr("sys.argv", ["init_qdrant.py", "--data", "non_existent_file.json"])
    exit_code = init_qdrant_main()
    assert exit_code == 1
