"""Portion Unit Resolution & Conventional Measurement Service.

Manages conventional cultural units of measurement (e.g. serving spoons, wraps, slices)
and computes mass in grams from user selections:
    Weight (g) = Unit Gram Weight * Selected Quantity
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from .schemas import (
        PortionUnit,
        DishPortionConfig,
        PortionUnitsRegistry,
        NutrientProfile,
        ScaledItemNutrition,
    )
except ImportError:
    from schemas import (
        PortionUnit,
        DishPortionConfig,
        PortionUnitsRegistry,
        NutrientProfile,
        ScaledItemNutrition,
    )

logger = logging.getLogger(__name__)

# Built-in fallback portion configurations
FALLBACK_PORTION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "jollof_rice": {
        "dish_id": "jollof_rice",
        "dish_name": "Nigerian Jollof Rice",
        "default_unit_id": "serving_spoon",
        "default_quantity": 2.0,
        "units": [
            {"unit_id": "serving_spoon", "unit_name": "Serving Spoon", "gram_weight": 120.0, "description": "Standard catering/cooking spoon (~120g)"},
            {"unit_id": "mound_cup", "unit_name": "Mound / Cup", "gram_weight": 250.0, "description": "Standard dining plate mound (~250g)"},
            {"unit_id": "takeaway_pack", "unit_name": "Takeaway Pack", "gram_weight": 500.0, "description": "Full standard plastic takeaway pack (~500g)"}
        ]
    },
    "egusi_soup": {
        "dish_id": "egusi_soup",
        "dish_name": "Egusi Melon Seed Soup",
        "default_unit_id": "serving_spoon",
        "default_quantity": 2.0,
        "units": [
            {"unit_id": "serving_spoon", "unit_name": "Serving Spoon", "gram_weight": 100.0, "description": "Standard cooking soup spoon (~100g)"},
            {"unit_id": "small_bowl", "unit_name": "Small Soup Bowl", "gram_weight": 200.0, "description": "Side soup bowl (~200g)"},
            {"unit_id": "large_bowl", "unit_name": "Large Soup Bowl", "gram_weight": 350.0, "description": "Main soup bowl (~350g)"}
        ]
    },
    "amala": {
        "dish_id": "amala",
        "dish_name": "Amala (Yam Flour Swallow)",
        "default_unit_id": "medium_wrap",
        "default_quantity": 1.0,
        "units": [
            {"unit_id": "small_wrap", "unit_name": "Small Wrap", "gram_weight": 150.0, "description": "Light portion wrap (~150g)"},
            {"unit_id": "medium_wrap", "unit_name": "Medium Wrap", "gram_weight": 250.0, "description": "Standard restaurant wrap (~250g)"},
            {"unit_id": "large_wrap", "unit_name": "Large Wrap", "gram_weight": 400.0, "description": "Heavy swallow portion (~400g)"}
        ]
    },
    "fried_plantain": {
        "dish_id": "fried_plantain",
        "dish_name": "Fried Ripe Plantain (Dodo)",
        "default_unit_id": "portion_6_slices",
        "default_quantity": 1.0,
        "units": [
            {"unit_id": "single_slice", "unit_name": "Single Slice / Piece", "gram_weight": 25.0, "description": "One slice (~25g)"},
            {"unit_id": "portion_6_slices", "unit_name": "Small Portion (6 slices)", "gram_weight": 150.0, "description": "Standard side portion (~150g)"},
            {"unit_id": "large_portion", "unit_name": "Large Portion (12 slices)", "gram_weight": 300.0, "description": "Double side portion (~300g)"}
        ]
    },
    "moi_moi": {
        "dish_id": "moi_moi",
        "dish_name": "Steamed Bean Cake (Moi Moi)",
        "default_unit_id": "single_wrap",
        "default_quantity": 1.0,
        "units": [
            {"unit_id": "single_wrap", "unit_name": "Single Wrap / Cup", "gram_weight": 150.0, "description": "Standard leaf or foil wrap (~150g)"},
            {"unit_id": "large_wrap", "unit_name": "Large Wrap", "gram_weight": 250.0, "description": "Large portion wrap (~250g)"}
        ]
    }
}

GENERIC_DEFAULT_PORTIONS = DishPortionConfig(
    dish_id="generic",
    dish_name="Generic Dish",
    default_unit_id="standard_serving",
    default_quantity=1.0,
    units=[
        PortionUnit(
            unit_id="standard_serving",
            unit_name="Standard Serving",
            gram_weight=150.0,
            description="Standard medium serving (~150g)"
        ),
        PortionUnit(
            unit_id="large_serving",
            unit_name="Large Serving",
            gram_weight=300.0,
            description="Large double serving (~300g)"
        ),
    ]
)


class PortionService:
    """Service providing portion unit lookup and unit-to-gram conversion."""

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)

        self.portion_configs: Dict[str, DishPortionConfig] = {}
        self.generic_config: DishPortionConfig = GENERIC_DEFAULT_PORTIONS
        self._load_registry()

    def _load_registry(self) -> None:
        """Load portion units from data/portion_units.json with fallback."""
        units_file = self.data_dir / "portion_units.json"
        if units_file.exists():
            try:
                with open(units_file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                
                portion_map = raw_data.get("portion_units", {})
                for dish_key, conf in portion_map.items():
                    units_list = [PortionUnit(**u) for u in conf.get("units", [])]
                    self.portion_configs[dish_key] = DishPortionConfig(
                        dish_id=conf.get("dish_id", dish_key),
                        dish_name=conf.get("dish_name", dish_key.replace("_", " ").title()),
                        default_unit_id=conf.get("default_unit_id", "serving_spoon"),
                        default_quantity=float(conf.get("default_quantity", 1.0)),
                        units=units_list,
                    )
                
                gen_data = raw_data.get("generic_default_units")
                if gen_data:
                    gen_units = [PortionUnit(**u) for u in gen_data.get("units", [])]
                    self.generic_config = DishPortionConfig(
                        dish_id="generic",
                        dish_name="Generic Serving",
                        default_unit_id=gen_data.get("default_unit_id", "standard_serving"),
                        default_quantity=float(gen_data.get("default_quantity", 1.0)),
                        units=gen_units,
                    )
                return
            except Exception as e:
                logger.warning(f"Error loading portion_units.json: {e}. Falling back to internal defaults.")

        # Fallback initialization
        for dish_key, conf in FALLBACK_PORTION_REGISTRY.items():
            units_list = [PortionUnit(**u) for u in conf["units"]]
            self.portion_configs[dish_key] = DishPortionConfig(
                dish_id=conf["dish_id"],
                dish_name=conf["dish_name"],
                default_unit_id=conf["default_unit_id"],
                default_quantity=float(conf["default_quantity"]),
                units=units_list,
            )

    def get_portion_config(self, dish_id: str) -> DishPortionConfig:
        """Retrieve portion unit configuration for a given dish."""
        normalized_id = dish_id.lower().strip().replace(" ", "_")
        if normalized_id in self.portion_configs:
            return self.portion_configs[normalized_id]
        return self.generic_config

    def calculate_portion_grams(
        self,
        dish_id: str,
        unit_id: Optional[str] = None,
        quantity: Optional[float] = None,
        custom_weight_g: Optional[float] = None,
    ) -> Tuple[float, str, float]:
        """Calculate mass in grams from conventional unit selection or direct grams.
        
        Returns:
            Tuple[gram_weight, used_unit_id, used_quantity]
        """
        config = self.get_portion_config(dish_id)

        # 1. Custom weight override takes highest precedence if valid
        if custom_weight_g is not None and custom_weight_g > 0:
            return (float(custom_weight_g), "custom_grams", 1.0)

        # 2. Determine target unit
        target_unit_id = unit_id or config.default_unit_id
        target_qty = quantity if (quantity is not None and quantity > 0) else config.default_quantity

        # 3. Find unit in config
        matched_unit = None
        for u in config.units:
            if u.unit_id == target_unit_id:
                matched_unit = u
                break

        if matched_unit is None and config.units:
            matched_unit = config.units[0]
            target_unit_id = matched_unit.unit_id

        if matched_unit is not None:
            total_grams = round(matched_unit.gram_weight * target_qty, 1)
            return (total_grams, target_unit_id, target_qty)

        # Ultimate fallback
        return (150.0, "standard_serving", 1.0)

    def attach_portion_metadata(
        self,
        item: ScaledItemNutrition,
        selected_unit_id: Optional[str] = None,
        selected_quantity: Optional[float] = None,
        per_100g: Optional[NutrientProfile] = None,
    ) -> ScaledItemNutrition:
        """Enrich a ScaledItemNutrition instance with available conventional units."""
        config = self.get_portion_config(item.dish_id)
        item.available_portion_units = list(config.units)
        item.default_unit_id = config.default_unit_id
        item.default_quantity = config.default_quantity
        item.selected_unit_id = selected_unit_id or config.default_unit_id
        item.selected_quantity = selected_quantity or config.default_quantity
        if per_100g is not None:
            item.nutrients_per_100g = per_100g
        return item
