"""Qdrant Vector Indexer using LangChain and OpenAI Embeddings for Qdrant Cloud.

Handles embedding composite Nigerian dishes and indexing them into Qdrant Cloud
using LangChain's QdrantVectorStore with graceful offline fallback.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

try:
    from langchain_core.documents import Document
except ImportError:
    Document = None

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    QdrantClient = None
    qmodels = None

try:
    from langchain_qdrant import QdrantVectorStore
except ImportError:
    QdrantVectorStore = None

try:
    from .config import Settings, get_settings
    from .schemas import CompositeDish
except ImportError:
    from config import Settings, get_settings
    from schemas import CompositeDish

logger = logging.getLogger(__name__)

COLLECTION_NAME = "composite_dishes"
VECTOR_DIMENSION = 1536  # Default OpenAI text-embedding-3-small dimension


class TextEmbedder:
    """Embedder wrapper supporting OpenAI, FastEmbed, and deterministic fallback."""

    def __init__(self, model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._openai_model = None
        if self.api_key and OpenAIEmbeddings is not None:
            try:
                self._openai_model = OpenAIEmbeddings(api_key=self.api_key, model=self.model_name)
            except Exception:
                self._openai_model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of strings into normalized vectors."""
        if self._openai_model is not None:
            try:
                return self._openai_model.embed_documents(texts)
            except Exception as e:
                logger.debug(f"OpenAI embedding failed: {e}. Falling back to deterministic vector.")

        return [self._hash_embed(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query text."""
        if self._openai_model is not None:
            try:
                return self._openai_model.embed_query(query)
            except Exception as e:
                logger.debug(f"OpenAI query embedding failed: {e}. Falling back.")
        return self._hash_embed(query)

    def _hash_embed(self, text: str, dimension: int = VECTOR_DIMENSION) -> List[float]:
        """Deterministic normalized dense vector fallback."""
        vec = np.zeros(dimension, dtype=np.float32)
        words = text.lower().strip().split()
        if not words:
            vec[0] = 1.0
            return vec.tolist()

        for word in words:
            for i in range(len(word) - 1):
                gram = word[i : i + 3]
                h = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
                idx = h % dimension
                val = 1.0 if (h // dimension) % 2 == 0 else -1.0
                vec[idx] += val

            h_word = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx_w = h_word % dimension
            vec[idx_w] += 2.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


def get_embeddings(settings: Optional[Settings] = None):
    """Initialize LangChain OpenAI Embeddings."""
    cfg = settings or get_settings()
    if not cfg.openai_api_key or OpenAIEmbeddings is None:
        return None
    return OpenAIEmbeddings(
        api_key=cfg.openai_api_key,
        model=cfg.embedding_model,
    )


def get_qdrant_client(
    settings: Optional[Settings] = None,
    host: Optional[str] = None,
    port: int = 6333,
    use_memory: bool = False,
    path: Optional[str] = None,
) -> Any:
    """Initialize Qdrant client for Qdrant Cloud or local in-memory instance."""
    if QdrantClient is None:
        raise ImportError("qdrant-client is required. Please install requirements.txt")

    if path is not None:
        return QdrantClient(path=path)

    if use_memory or os.getenv("USE_IN_MEMORY_FALLBACK", "false").lower() == "true":
        return QdrantClient(":memory:")

    cfg = settings or get_settings()

    # If Qdrant Cloud credentials are provided, connect to Cloud
    if cfg.qdrant_url and not host:
        try:
            client = QdrantClient(
                url=cfg.qdrant_url,
                api_key=cfg.qdrant_api_key,
                timeout=30.0,
            )
            client.get_collections()
            return client
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant Cloud at {cfg.qdrant_url}: {e}. Falling back to in-memory mode.")

    if host:
        try:
            return QdrantClient(host=host, port=port, timeout=2.0)
        except Exception:
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


def create_dish_documents(dishes: Dict[str, Any]) -> List[Document]:
    """Convert composite dishes to LangChain Document objects with metadata."""
    docs: List[Document] = []
    for dish_id, dish in dishes.items():
        name = dish.get("dish_name", dish_id)
        page_content = build_dish_document_text(dish)
        
        doc = Document(
            page_content=page_content,
            metadata={
                "dish_id": dish.get("dish_id", dish_id),
                "dish_name": name,
                "wafct_code": dish.get("wafct_code", "00_COMPOSITE"),
                "nutrients_cooked_100g": json.dumps(dish.get("nutrients_cooked_100g", {})),
                "aliases": json.dumps(dish.get("aliases", [])),
            }
        )
        docs.append(doc)
    return docs


def index_composite_dishes(
    client: Any = None,
    dishes_db: Optional[Dict[str, Any]] = None,
    collection_name: Optional[str] = None,
    settings: Optional[Settings] = None,
    embedder: Optional[Any] = None,
) -> int:
    """Index composite dishes into Qdrant Cloud using LangChain."""
    cfg = settings or get_settings()
    
    # Handle single or multi-argument call
    if isinstance(client, dict) and dishes_db is None:
        dishes_db = client
        client = None

    if dishes_db is None:
        dishes_db = {}

    target_client = client or get_qdrant_client(cfg)
    target_coll = collection_name or cfg.qdrant_collection_name
    embeddings = get_embeddings(cfg)

    docs = create_dish_documents(dishes_db)
    if not docs:
        return 0

    collections = [c.name for c in target_client.get_collections().collections]
    vector_size = VECTOR_DIMENSION
    
    if target_coll not in collections:
        target_client.create_collection(
            collection_name=target_coll,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        )

    # Use QdrantVectorStore if embeddings are configured
    if embeddings is not None and QdrantVectorStore is not None:
        try:
            vector_store = QdrantVectorStore(
                client=target_client,
                collection_name=target_coll,
                embedding=embeddings,
            )
            vector_store.add_documents(docs)
            logger.info(f"Indexed {len(docs)} dish documents into Qdrant Cloud via LangChain.")
            return len(docs)
        except Exception as e:
            logger.warning(f"Error indexing via LangChain QdrantVectorStore: {e}")

    # Fallback direct insertion
    fallback_embedder = embedder or TextEmbedder()
    texts = [d.page_content for d in docs]
    vectors = fallback_embedder.embed_texts(texts)
    
    points = []
    for idx, (doc, vector) in enumerate(zip(docs, vectors)):
        point = qmodels.PointStruct(
            id=idx + 1,
            vector=vector,
            payload=doc.metadata,
        )
        points.append(point)

    target_client.upsert(
        collection_name=target_coll,
        points=points,
    )
    return len(points)
