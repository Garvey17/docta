"""Qdrant vector collection creator and dense embedder.

Supports Qdrant server connection (host:port), local on-disk storage,
or in-memory Qdrant instance (QdrantClient(":memory:")).
Uses FastEmbed / Sentence-Transformers with deterministic fallback.
"""

import hashlib
import json
import logging
import math
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import numpy as np

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    QdrantClient = None
    qmodels = None

logger = logging.getLogger(__name__)

COLLECTION_NAME = "composite_dishes"
VECTOR_DIMENSION = 384


class TextEmbedder:
    """Embedder interface supporting FastEmbed with fallback to deterministic hash vectorizer."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._fastembed_model = None
        self._st_model = None
        self._engine = "fallback"

        # Try FastEmbed
        try:
            from fastembed import TextEmbedding
            self._fastembed_model = TextEmbedding(model_name=model_name)
            self._engine = "fastembed"
            logger.info("Using FastEmbed for dense vector generation.")
        except Exception as e:
            logger.debug(f"FastEmbed init failed: {e}. Trying sentence-transformers.")
            # Try sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer(model_name)
                self._engine = "sentence_transformers"
                logger.info("Using sentence-transformers for vector generation.")
            except Exception as e2:
                logger.debug(f"sentence-transformers not available: {e2}. Using deterministic hash embedder.")
                self._engine = "hash_fallback"

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of strings into normalized 384-d vectors."""
        if self._engine == "fastembed" and self._fastembed_model is not None:
            try:
                embeddings = list(self._fastembed_model.embed(texts))
                return [e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings]
            except Exception as e:
                logger.warning(f"FastEmbed error during embedding: {e}. Falling back.")

        if self._engine == "sentence_transformers" and self._st_model is not None:
            try:
                embeddings = self._st_model.encode(texts, normalize_embeddings=True)
                return [e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings]
            except Exception as e:
                logger.warning(f"SentenceTransformer error during embedding: {e}. Falling back.")

        # Deterministic 384-d hash embedding fallback
        return [self._hash_embed(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query text."""
        return self.embed_texts([query])[0]

    def _hash_embed(self, text: str) -> List[float]:
        """Produce a normalized 384-dimensional vector from character ngrams."""
        vec = np.zeros(VECTOR_DIMENSION, dtype=np.float32)
        words = text.lower().strip().split()
        if not words:
            vec[0] = 1.0
            return vec.tolist()

        for word in words:
            # 3-gram hashing
            for i in range(len(word) - 1):
                gram = word[i : i + 3]
                h = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
                idx = h % VECTOR_DIMENSION
                val = 1.0 if (h // VECTOR_DIMENSION) % 2 == 0 else -1.0
                vec[idx] += val

            # Whole word hash
            h_word = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx_w = h_word % VECTOR_DIMENSION
            vec[idx_w] += 2.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


def get_qdrant_client(
    host: Optional[str] = None,
    port: int = 6333,
    use_memory: bool = False,
    path: Optional[str] = None,
) -> Any:
    """Initialize QdrantClient with fallback to in-memory mode."""
    if QdrantClient is None:
        raise ImportError("qdrant-client is not installed. Please install requirements.txt")

    if use_memory or os.getenv("USE_IN_MEMORY_FALLBACK", "false").lower() == "true":
        return QdrantClient(":memory:")

    if path is not None:
        return QdrantClient(path=path)

    if host:
        try:
            client = QdrantClient(host=host, port=port, timeout=2.0)
            # Health check
            client.get_collections()
            return client
        except Exception as e:
            logger.warning(
                f"Could not connect to Qdrant at {host}:{port} ({e}). Falling back to in-memory Qdrant."
            )
            return QdrantClient(":memory:")

    return QdrantClient(":memory:")


def build_dish_document_text(dish: Dict[str, Any]) -> str:
    """Generate search-optimized textual representation for a composite dish."""
    name = dish.get("dish_name", "")
    dish_id = dish.get("dish_id", "")
    aliases = ", ".join(dish.get("aliases", []))
    desc = dish.get("description", "")
    ingredients = ", ".join(
        ing.get("name", "") for ing in dish.get("raw_ingredients", [])
    )
    return (
        f"{name} ({dish_id}). "
        f"Colloquial aliases: {aliases}. "
        f"Ingredients: {ingredients}. "
        f"Description: {desc}"
    )


def index_composite_dishes(
    client: Any,
    dishes_db: Dict[str, Dict[str, Any]],
    collection_name: str = COLLECTION_NAME,
    embedder: Optional[TextEmbedder] = None,
) -> int:
    """Create collection and index composite dish documents into Qdrant."""
    if embedder is None:
        embedder = TextEmbedder()

    # Recreate collection
    collections = [c.name for c in client.get_collections().collections]
    if collection_name in collections:
        client.delete_collection(collection_name=collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(
            size=VECTOR_DIMENSION,
            distance=qmodels.Distance.COSINE,
        ),
    )

    dish_items = list(dishes_db.values())
    texts = [build_dish_document_text(dish) for dish in dish_items]
    embeddings = embedder.embed_texts(texts)

    points = []
    for idx, (dish, vector) in enumerate(zip(dish_items, embeddings)):
        point = qmodels.PointStruct(
            id=idx + 1,
            vector=vector,
            payload=dish,
        )
        points.append(point)

    client.upsert(
        collection_name=collection_name,
        points=points,
    )
    return len(points)
