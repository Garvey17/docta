"""Semantic Search Engine powered by LangChain, OpenAI, and Qdrant Cloud.

Implements Lookup-Before-Retrieval flow:
1. Fast Direct Recipe & Alias exact match (< 1ms)
2. LangChain Qdrant Vector Store similarity search with OpenAI Embeddings
3. In-memory string & token similarity fallback
4. Standard baseline defaults for unmapped items
5. Automatic attachment of conventional portion units
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from langchain_qdrant import QdrantVectorStore
except ImportError:
    QdrantVectorStore = None

try:
    from .config import Settings, get_settings
    from .schemas import ScaledItemNutrition, CompositeDish, NutrientProfile, PortionUnit
    from .macro_scaler import build_scaled_item
    from .portion_service import PortionService
    from .vector_indexer import get_qdrant_client, get_embeddings
except ImportError:
    from config import Settings, get_settings
    from schemas import ScaledItemNutrition, CompositeDish, NutrientProfile, PortionUnit
    from macro_scaler import build_scaled_item
    from portion_service import PortionService
    from vector_indexer import get_qdrant_client, get_embeddings

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """Normalize text by lowercasing and stripping special characters."""
    t = text.lower().strip()
    return re.sub(r"[^\w\s]", " ", t)


_normalize_text = _clean_text


def _token_similarity(query: str, target: str) -> float:
    """Compute token Jaccard similarity for in-memory fallback matching."""
    q_tokens = set(_clean_text(query).split())
    t_tokens = set(_clean_text(target).split())
    if not q_tokens or not t_tokens:
        return 0.0
    return len(q_tokens.intersection(t_tokens)) / len(q_tokens.union(t_tokens))


_token_jaccard_similarity = _token_similarity


class SemanticSearchEngine:
    """Simplified LangChain + Qdrant Cloud Semantic Search Engine."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        data_dir: Optional[Path] = None,
        force_memory: bool = False,
    ):
        self.settings = settings or get_settings()
        if data_dir is not None:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = self.settings.data_dir

        self._load_local_data()

        self.portion_service = PortionService(data_dir=self.data_dir)
        self.embeddings = get_embeddings(self.settings) if not force_memory else None
        self.qdrant_client = get_qdrant_client(self.settings, use_memory=force_memory)
        
        # Initialize LangChain Qdrant Vector Store if available
        self.vector_store = None
        if self.embeddings is not None and QdrantVectorStore is not None and not force_memory:
            try:
                self.vector_store = QdrantVectorStore(
                    client=self.qdrant_client,
                    collection_name=self.settings.qdrant_collection_name,
                    embedding=self.embeddings,
                )
            except Exception as e:
                logger.debug(f"LangChain QdrantVectorStore not initialized: {e}. Using local lookup fallback.")

    def _load_local_data(self) -> None:
        """Load composite dishes, aliases, and fallback profiles."""
        comp_file = self.data_dir / "composite_dishes_db.json"
        if comp_file.exists():
            with open(comp_file, "r", encoding="utf-8") as f:
                self.composite_db = json.load(f)
        else:
            self.composite_db = {}

        alias_file = self.data_dir / "aliases_map.json"
        if alias_file.exists():
            with open(alias_file, "r", encoding="utf-8") as f:
                self.aliases_map = json.load(f)
        else:
            self.aliases_map = {}

        fallback_file = self.data_dir / "fallback_defaults.json"
        if fallback_file.exists():
            with open(fallback_file, "r", encoding="utf-8") as f:
                self.fallback_defaults = json.load(f)
        else:
            self.fallback_defaults = {}

        # Exact match dictionary
        self.exact_map: Dict[str, str] = {}
        for dish_id, dish in self.composite_db.items():
            self.exact_map[dish_id.lower()] = dish_id
            self.exact_map[dish_id.lower().replace("_", " ")] = dish_id
            name = dish.get("dish_name", "").lower()
            if name:
                self.exact_map[name] = dish_id

        for alias, dish_id in self.aliases_map.items():
            self.exact_map[alias.lower()] = dish_id

    def search_dish(
        self,
        query: str,
        weight_g: float = 100.0,
        confidence: float = 1.0,
        item_id: Optional[str] = None,
        bounding_box: Optional[List[float]] = None,
        selected_unit_id: Optional[str] = None,
        selected_quantity: Optional[float] = None,
    ) -> ScaledItemNutrition:
        """Execute lookup-before-retrieval search for a dish query and target portion."""
        clean_q = _clean_text(query).strip()

        # 1. Exact Recipe & Alias Match (< 1ms)
        matched_id = self.exact_map.get(clean_q) or self.exact_map.get(clean_q.replace(" ", "_"))
        if matched_id and matched_id in self.composite_db:
            dish = self.composite_db[matched_id]
            return self._build_item(
                dish_id=dish["dish_id"],
                display_name=dish["dish_name"],
                cooked_nutrients=dish["nutrients_cooked_100g"],
                weight_g=weight_g,
                wafct_code=dish.get("wafct_code", "00_COMPOSITE"),
                confidence=confidence,
                item_id=item_id,
                bounding_box=bounding_box,
                similarity_score=1.0,
                is_fallback=False,
                selected_unit_id=selected_unit_id,
                selected_quantity=selected_quantity,
            )

        # 2. LangChain Vector Store Similarity Search via Qdrant Cloud
        if self.vector_store is not None:
            try:
                results = self.vector_store.similarity_search_with_score(query, k=1)
                if results:
                    doc, score = results[0]
                    dish_id = doc.metadata.get("dish_id")
                    if dish_id and dish_id in self.composite_db:
                        dish = self.composite_db[dish_id]
                        return self._build_item(
                            dish_id=dish["dish_id"],
                            display_name=dish["dish_name"],
                            cooked_nutrients=dish["nutrients_cooked_100g"],
                            weight_g=weight_g,
                            wafct_code=dish.get("wafct_code", "00_COMPOSITE"),
                            confidence=confidence,
                            item_id=item_id,
                            bounding_box=bounding_box,
                            similarity_score=float(score),
                            is_fallback=False,
                            selected_unit_id=selected_unit_id,
                            selected_quantity=selected_quantity,
                        )
            except Exception as e:
                logger.debug(f"LangChain vector similarity search failed: {e}. Falling back to in-memory matching.")

        # 3. In-Memory Token Similarity Fallback
        best_dish = None
        best_score = 0.0
        for dish_id, dish in self.composite_db.items():
            candidates = [dish.get("dish_name", ""), dish_id] + dish.get("aliases", [])
            for c in candidates:
                sim = _token_similarity(query, c)
                if sim > best_score:
                    best_score = sim
                    best_dish = dish

        if best_dish is not None and best_score >= 0.20:
            return self._build_item(
                dish_id=best_dish["dish_id"],
                display_name=best_dish["dish_name"],
                cooked_nutrients=best_dish["nutrients_cooked_100g"],
                weight_g=weight_g,
                wafct_code=best_dish.get("wafct_code", "00_COMPOSITE"),
                confidence=confidence,
                item_id=item_id,
                bounding_box=bounding_box,
                similarity_score=best_score,
                is_fallback=False,
                selected_unit_id=selected_unit_id,
                selected_quantity=selected_quantity,
            )

        # 4. Standard Generic Fallback
        fallback_profile = self.fallback_defaults.get("generic_cooked_meal", {})
        fallback_nutrients = fallback_profile.get("nutrients") or {
            "calories_kcal": 150.0,
            "protein_g": 5.0,
            "fat_g": 5.0,
            "carbs_g": 20.0,
            "fiber_g": 1.5,
            "sodium_mg": 100.0,
            "calcium_mg": 15.0,
            "iron_mg": 1.0,
        }
        return self._build_item(
            dish_id="unmapped_dish",
            display_name=f"Standard Meal ({query})",
            cooked_nutrients=fallback_nutrients,
            weight_g=weight_g,
            wafct_code="FALLBACK_DEFAULT",
            confidence=confidence,
            item_id=item_id,
            bounding_box=bounding_box,
            similarity_score=0.0,
            is_fallback=True,
            selected_unit_id=selected_unit_id,
            selected_quantity=selected_quantity,
        )

    def _build_item(
        self,
        dish_id: str,
        display_name: str,
        cooked_nutrients: Dict[str, Any],
        weight_g: float,
        wafct_code: str = "WAFCT_COMPOSITE",
        confidence: float = 1.0,
        item_id: Optional[str] = None,
        bounding_box: Optional[List[float]] = None,
        similarity_score: float = 1.0,
        is_fallback: bool = False,
        selected_unit_id: Optional[str] = None,
        selected_quantity: Optional[float] = None,
    ) -> ScaledItemNutrition:
        """Helper to construct scaled item and attach portion units."""
        portion_conf = self.portion_service.get_portion_config(dish_id)
        
        # Recalculate weight from units if selected
        if selected_unit_id or selected_quantity is not None:
            calc_w, unit_used, qty_used = self.portion_service.calculate_portion_grams(
                dish_id=dish_id,
                unit_id=selected_unit_id,
                quantity=selected_quantity,
            )
            final_weight = calc_w
        else:
            final_weight = weight_g
            unit_used = portion_conf.default_unit_id
            qty_used = portion_conf.default_quantity

        return build_scaled_item(
            dish_id=dish_id,
            display_name=display_name,
            weight_g=final_weight,
            cooked_100g=cooked_nutrients,
            wafct_code=wafct_code,
            similarity_score=similarity_score,
            is_fallback=is_fallback,
            confidence=confidence,
            item_id=item_id,
            bounding_box=bounding_box,
            available_portion_units=portion_conf.units,
            default_unit_id=portion_conf.default_unit_id,
            default_quantity=portion_conf.default_quantity,
            selected_unit_id=unit_used,
            selected_quantity=qty_used,
        )
