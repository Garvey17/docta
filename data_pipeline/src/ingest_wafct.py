"""Raw ingredient Food Composition Table (WAFCT) parser & unit normalizer.

Parses raw FAO/INFOODS WAFCT 2019 tables (CSV or JSON) and normalizes per-100g
nutritional values into the canonical FoodItemFCT schema.
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from .schemas import FoodItemFCT, NutrientProfile
except ImportError:
    from schemas import FoodItemFCT, NutrientProfile


# Synonyms for FAO/INFOODS tag names & common CSV headers
COLUMN_MAPPING = {
    "code": ["code", "id", "food_id", "food_code", "fdc_id", "wafct_code"],
    "food_name": ["food_name", "name", "food_desc", "item_name", "description"],
    "calories_kcal": ["energy_kcal", "calories_kcal", "enerc_kcal", "energy", "enerc", "calories"],
    "protein_g": ["protein_g", "protein", "procnt_g", "procnt"],
    "fat_g": ["fat_g", "fat", "fatce_g", "total_fat", "fatce"],
    "carbs_g": ["carbs_g", "carbohydrates", "carbohydrate_g", "choavl_g", "choavldf_g", "choavldf"],
    "fiber_g": ["fiber_g", "dietary_fiber", "fibtg_g", "fiber", "fibtg"],
    "sodium_mg": ["sodium_mg", "sodium", "na_mg", "na"],
    "calcium_mg": ["calcium_mg", "calcium", "ca_mg", "ca"],
    "iron_mg": ["iron_mg", "iron", "fe_mg", "fe"],
}


def _clean_numeric_value(raw_val: Any) -> float:
    """Parse numeric nutrient value, handling FAO WAFCT notations like '[T]', '-', or 'tr'."""
    if raw_val is None:
        return 0.0
    if isinstance(raw_val, (int, float)):
        return float(raw_val)
    val_str = str(raw_val).strip()
    if not val_str or val_str in ("-", "[]", "NA", "N/A", "nd", "tr", "trace", "[T]"):
        return 0.0
    # Strip brackets or text like '[12.4]' -> '12.4'
    cleaned = re.sub(r"[^\d\.-]", "", val_str)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _match_column(header: str, synonyms: list) -> bool:
    h = header.strip().lower()
    return h in synonyms or h.replace(" ", "_") in synonyms


def normalize_fct_row(row: Dict[str, Any]) -> FoodItemFCT:
    """Normalize a raw dictionary row into a validated FoodItemFCT."""
    mapped: Dict[str, Any] = {}
    row_normalized = {k.strip().lower(): v for k, v in row.items()}

    for target_field, synonyms in COLUMN_MAPPING.items():
        found_val = None
        for syn in synonyms:
            if syn in row_normalized:
                found_val = row_normalized[syn]
                break
        mapped[target_field] = found_val

    code = str(mapped["code"] or "UNKNOWN").strip()
    food_name = str(mapped["food_name"] or code).strip()

    profile = NutrientProfile(
        calories_kcal=_clean_numeric_value(mapped.get("calories_kcal")),
        protein_g=_clean_numeric_value(mapped.get("protein_g")),
        fat_g=_clean_numeric_value(mapped.get("fat_g")),
        carbs_g=_clean_numeric_value(mapped.get("carbs_g")),
        fiber_g=_clean_numeric_value(mapped.get("fiber_g")),
        sodium_mg=_clean_numeric_value(mapped.get("sodium_mg")),
        calcium_mg=_clean_numeric_value(mapped.get("calcium_mg")),
        iron_mg=_clean_numeric_value(mapped.get("iron_mg")),
    )

    return FoodItemFCT(
        code=code,
        food_name=food_name,
        nutrients=profile,
    )


def ingest_wafct(
    input_path: Path,
    output_path: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    """Parse raw FAO WAFCT dataset (CSV or JSON) and output normalized table.
    
    Args:
        input_path: Path to raw CSV or JSON file.
        output_path: Path to write normalized food_composition_table.json.
        
    Returns:
        Dictionary mapping ingredient code to FoodItemFCT dict.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    normalized_records: Dict[str, Dict[str, Any]] = {}

    if input_path.suffix.lower() == ".csv":
        with open(input_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = normalize_fct_row(row)
                normalized_records[item.code] = item.model_dump()
    elif input_path.suffix.lower() == ".json":
        with open(input_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        if isinstance(raw_data, list):
            for row in raw_data:
                item = normalize_fct_row(row)
                normalized_records[item.code] = item.model_dump()
        elif isinstance(raw_data, dict):
            for code, row in raw_data.items():
                if not isinstance(row, dict):
                    continue
                if "code" not in row:
                    row["code"] = code
                if "nutrients" in row and isinstance(row["nutrients"], dict):
                    # Flat merge for normalization
                    flat_row = {"code": row.get("code", code), "food_name": row.get("food_name", code)}
                    flat_row.update(row["nutrients"])
                    item = normalize_fct_row(flat_row)
                else:
                    item = normalize_fct_row(row)
                normalized_records[item.code] = item.model_dump()
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}. Expected .csv or .json")

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(normalized_records, f, indent=2)

    return normalized_records


def main() -> int:
    """CLI handler matching Section 7 instructions."""
    parser = argparse.ArgumentParser(description="Ingest FAO WAFCT 2019 ingredient composition data.")
    parser.add_argument("--input", default="data/raw_wafct_2019.csv", help="Path to raw FCT dataset")
    parser.add_argument("--output", default="data/food_composition_table.json", help="Path for normalized output")
    args = parser.parse_args()

    try:
        records = ingest_wafct(Path(args.input), Path(args.output))
        print(f"[SUCCESS] Successfully ingested {len(records)} ingredients from '{args.input}' into '{args.output}'.")
        return 0
    except Exception as e:
        print(f"[FATAL] Ingestion failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
