"""Lookup-Before-Retrieval semantic search engine with Qdrant and offline fallback.

Flow:
1. Exact & Alias RIQ Match (< 1ms)
2. Semantic Vector Search via Qdrant Collection (< 15ms)
3. In-memory Token & String Similarity Fallback (when Qdrant offline)
4. Baseline Generic Defaults (for completely unmapped foods)
SLA Target: < 200ms
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from .schemas import ScaledItemNutrition, CompositeDish, NutrientProfile
    from .macro_scaler import build_scaled_item
    from .vector_indexer import (
        TextEmbedder,
        get_qdrant_client,
        COLLECTION_NAME,
        index_composite_dishes,
    )
except ImportError:
    from schemas import ScaledItemNutrition, CompositeDish, NutrientProfile
    from macro_scaler import build_scaled_item
    from vector_indexer import (
        TextEmbedder,
        get_qdrant_client,
        COLLECTION_NAME,
        index_composite_dishes,
    )

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    """Normalize text by lowercasing and stripping punctuation."""
    t = text.lower().strip()
    return re.sub(r"[^\w\s]", " ", t)


def _token_jaccard_similarity(query: str, target: str) -> float:
    """Compute token Jaccard similarity for in-memory matching."""
    q_tokens = set(_normalize_text(query).split())
    t_tokens = set(_normalize_text(target).split())
    if not q_tokens or not t_tokens:
        return 0.0
    intersection = q_tokens.intersection(t_tokens)
    union = q_tokens.union(t_tokens)
    return len(intersection) / len(union)


class SemanticSearchEngine:
    """Hybrid semantic search engine providing fast dish lookup with fallback."""

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        qdrant_host: Optional[str] = None,
        qdrant_port: int = 6333,
        force_memory: bool = False,
    ):
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)

        self._load_fixtures()

        self.embedder = TextEmbedder()
        self.qdrant_client = None
        self._is_qdrant_ready = False

        # Check offline env flag
        use_fallback = (
            force_memory or os.getenv("USE_IN_MEMORY_FALLBACK", "false").lower() == "true"
        )

        try:
            self.qdrant_client = get_qdrant_client(
                host=qdrant_host if not use_fallback else None,
                port=qdrant_port,
                use_memory=use_fallback,
            )
            # Ensure collection exists; if not, bootstrap from composite_dishes_db
            collections = [c.name for c in self.qdrant_client.get_collections().collections]
            if COLLECTION_NAME not in collections:
                index_composite_dishes(
                    self.qdrant_client,
                    self.composite_db,
                    collection_name=COLLECTION_NAME,
                    embedder=self.embedder,
                )
            self._is_qdrant_ready = True
        except Exception as e:
            logger.warning(
                f"Qdrant vector search unavailable: {e}. Running with in-memory lookup fallback."
            )
            self._is_qdrant_ready = False

    def _load_fixtures(self) -> None:
        """Load RIQ lookup, composite dishes, aliases, and fallbacks."""
        # 1. Composite dishes db
        comp_path = self.data_dir / "composite_dishes_db.json"
        if comp_path.exists():
            with open(comp_path, "r", encoding="utf-8") as f:
                self.composite_db = json.load(f)
        else:
            self.composite_db = {}

        # 2. Aliases map
        alias_path = self.data_dir / "aliases_map.json"
        if alias_path.exists():
            with open(alias_path, "r", encoding="utf-8") as f:
                self.aliases_map = json.load(f)
        else:
            self.aliases_map = {}

        # 3. Fallback defaults
        fallback_path = self.data_dir / "fallback_defaults.json"
        if fallback_path.exists():
            with open(fallback_path, "r", encoding="utf-8") as f:
                self.fallback_defaults = json.load(f)
        else:
            self.fallback_defaults = {}

        # Precompute normalized exact keys
        self.exact_dish_map: Dict[str, str] = {}
        for dish_id, dish in self.composite_db.items():
            self.exact_dish_map[dish_id.lower()] = dish_id
            self.exact_dish_map[dish_id.lower().replace("_", " ")] = dish_id
            name_clean = dish.get("dish_name", "").lower()
            if name_clean:
                self.exact_dish_map[name_clean] = dish_id

        for alias, dish_id in self.aliases_map.items():
            self.exact_dish_map[alias.lower()] = dish_id

    def search_dish(
        self,
        query: str,
        weight_g: float = 100.0,
        confidence: float = 1.0,
        item_id: Optional[str] = None,
        bounding_box: Optional[List[float]] = None,
    ) -> ScaledItemNutrition:
        """Execute lookup-before-retrieval flow for a dish query and target weight.
        
        SLA: < 200ms.
        """
        start_t = time.perf_counter()
        clean_q = _normalize_text(query).strip()

        # Step 1: Direct RIQ & Alias exact lookup (< 1ms)
        matched_dish_id = self.exact_dish_map.get(clean_q)
        if not matched_dish_id:
            # Check with underscores
            matched_dish_id = self.exact_dish_map.get(clean_q.replace(" ", "_"))

        if matched_dish_id and matched_dish_id in self.composite_db:
            dish = self.composite_db[matched_dish_id]
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            return build_scaled_item(
                dish_id=dish["dish_id"],
                display_name=dish["dish_name"],
                weight_g=weight_g,
                cooked_100g=dish["nutrients_cooked_100g"],
                wafct_code=dish.get("wafct_code", "00_COMPOSITE"),
                similarity_score=1.0,
                is_fallback=False,
                confidence=confidence,
                item_id=item_id,
                bounding_box=bounding_box,
            )

        # Step 2: Semantic vector search via Qdrant (< 25ms)
        if self._is_qdrant_ready and self.qdrant_client is not None:
            try:
                query_vector = self.embedder.embed_query(query)
                search_results = self.qdrant_client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=query_vector,
                    limit=1,
                )
                if search_results and search_results.points:
                    top_point = search_results.points[0]
                    score = float(top_point.score)
                    if score >= 0.30:  # Valid semantic match
                        payload = top_point.payload
                        return build_scaled_item(
                            dish_id=payload["dish_id"],
                            display_name=payload["dish_name"],
                            weight_g=weight_g,
                            cooked_100g=payload["nutrients_cooked_100g"],
                            wafct_code=payload.get("wafct_code", "00_COMPOSITE"),
                            similarity_score=round(score, 3),
                            is_fallback=False,
                            confidence=confidence,
                            item_id=item_id,
                            bounding_box=bounding_box,
                        )
            except Exception as e:
                logger.warning(f"Vector search failed ({e}). Proceeding to in-memory fallback.")

        # Step 3: In-memory Token Similarity Fallback
        best_id, best_score = self._in_memory_fuzzy_match(query)
        if best_id and best_score >= 0.30 and best_id in self.composite_db:
            dish = self.composite_db[best_id]
            return build_scaled_item(
                dish_id=dish["dish_id"],
                display_name=dish["dish_name"],
                weight_g=weight_g,
                cooked_100g=dish["nutrients_cooked_100g"],
                wafct_code=dish.get("wafct_code", "00_COMPOSITE"),
                similarity_score=round(best_score, 3),
                is_fallback=False,
                confidence=confidence,
                item_id=item_id,
                bounding_box=bounding_box,
            )

        # Step 4: Baseline fallback defaults for unmapped queries
        fallback = self._resolve_fallback_default(query)
        return build_scaled_item(
            dish_id=fallback["dish_id"],
            display_name=f"{query.capitalize()} (Estimated)",
            weight_g=weight_g,
            cooked_100g=fallback["nutrients_cooked_100g"],
            wafct_code=fallback.get("wafct_code", "00_DEFAULT"),
            similarity_score=0.25,
            is_fallback=True,
            confidence=confidence,
            item_id=item_id,
            bounding_box=bounding_box,
        )

    def _in_memory_fuzzy_match(self, query: str) -> Tuple[Optional[str], float]:
        """Perform token Jaccard similarity across composite dishes and aliases."""
        best_id: Optional[str] = None
        best_score = 0.0

        for key, dish_id in self.exact_dish_map.items():
            sim = _token_jaccard_similarity(query, key)
            if sim > best_score:
                best_score = sim
                best_id = dish_id

        # Also check dish descriptions and ingredient lists
        for dish_id, dish in self.composite_db.items():
            for ing in dish.get("raw_ingredients", []):
                sim = _token_jaccard_similarity(query, ing.get("name", "")) * 0.75
                if sim > best_score:
                    best_score = sim
                    best_id = dish_id

        return best_id, best_score

    def _resolve_fallback_default(self, query: str) -> Dict[str, Any]:
        """Choose appropriate baseline profile from fallback_defaults.json."""
        q = query.lower()
        if "rice" in q:
            return self.fallback_defaults.get("generic_rice", self.fallback_defaults["default"])
        if "soup" in q or "stew" in q:
            return self.fallback_defaults.get("generic_soup", self.fallback_defaults["default"])
        if "swallow" in q or "fufu" in q or "garri" in q:
            return self.fallback_defaults.get("generic_swallow", self.fallback_defaults["default"])
        return self.fallback_defaults.get("default", {
            "dish_id": "default_meal",
            "dish_name": "Mixed West African Meal",
            "wafct_code": "00_DEFAULT",
            "nutrients_cooked_100g": {
                "calories_kcal": 185.0,
                "protein_g": 5.5,
                "fat_g": 7.0,
                "carbs_g": 25.0,
                "fiber_g": 2.5,
                "sodium_mg": 250.0,
                "calcium_mg": 25.0,
                "iron_mg": 1.5,
            }
        })
