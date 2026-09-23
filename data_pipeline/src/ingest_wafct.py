"""Raw ingredient Food Composition Table (WAFCT / NCT_Nigeria) parser & unit normalizer.

Parses official Nigerian Food Composition Table (NCT_Nigeria.xlsx),
FAO/INFOODS WAFCT datasets (CSV or JSON), and normalizes per-100g
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


COLUMN_MAPPING = {
    "code": ["code", "id", "food_id", "food_code", "fdc_id", "wafct_code"],
    "food_name": ["food_name", "name", "food_desc", "item_name", "description", "food item description in english"],
    "calories_kcal": ["energy_kcal", "calories_kcal", "enerc_kcal", "energy", "enerc", "calories", "energy (kcal)"],
    "protein_g": ["protein_g", "protein", "procnt_g", "procnt", "protein, total (g)"],
    "fat_g": ["fat_g", "fat", "fatce_g", "total_fat", "fatce", "fat (g)"],
    "carbs_g": ["carbs_g", "carbohydrates", "carbohydrate_g", "choavl_g", "choavldf_g", "choavldf", "carbohydrate, available, calculated by difference (g)"],
    "fiber_g": ["fiber_g", "dietary_fiber", "fibtg_g", "fiber", "fibtg", "total fiber (g)"],
    "sodium_mg": ["sodium_mg", "sodium", "na_mg", "na", "sodium (mg)"],
    "calcium_mg": ["calcium_mg", "calcium", "ca_mg", "ca", "calcium (mg)"],
    "iron_mg": ["iron_mg", "iron", "fe_mg", "fe", "iron (mg)"],
}


def _clean_numeric_value(raw_val: Any) -> float:
    """Parse numeric nutrient value, handling notations like '[T]', '-', or 'tr'."""
    if raw_val is None:
        return 0.0
    if isinstance(raw_val, (int, float)):
        import math
        return 0.0 if math.isnan(raw_val) else float(raw_val)
    val_str = str(raw_val).strip()
    if not val_str or val_str in ("-", "[]", "NA", "N/A", "nd", "tr", "trace", "[T]", "nan"):
        return 0.0
    cleaned = re.sub(r"[^\d\.-]", "", val_str)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def normalize_fct_row(row: Dict[str, Any]) -> FoodItemFCT:
    """Normalize a raw dictionary row into a validated FoodItemFCT."""
    mapped: Dict[str, Any] = {}
    row_normalized = {re.sub(r"\s+", " ", str(k)).strip().lower(): v for k, v in row.items()}

    for target_field, synonyms in COLUMN_MAPPING.items():
        found_val = None
        for syn in synonyms:
            if syn in row_normalized:
                found_val = row_normalized[syn]
                break
        mapped[target_field] = found_val

    raw_code = mapped.get("code")
    if raw_code is None or str(raw_code).strip() == "" or str(raw_code).lower() == "nan":
        code = "UNKNOWN"
    else:
        # Format numeric codes like 14.0 as clean strings
        try:
            val_f = float(raw_code)
            code = f"{int(val_f)}" if val_f.is_integer() else f"{val_f}"
        except (ValueError, TypeError):
            code = str(raw_code).strip()

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


def _blend_nutrients(
    items_weights: list,
    by_code: Dict[str, FoodItemFCT],
) -> NutrientProfile:
    """Compute weighted blend of nutrient profiles for compound ingredients."""
    total_w = sum(w for _, w in items_weights)
    accum = {
        "calories_kcal": 0.0,
        "protein_g": 0.0,
        "fat_g": 0.0,
        "carbs_g": 0.0,
        "fiber_g": 0.0,
        "sodium_mg": 0.0,
        "calcium_mg": 0.0,
        "iron_mg": 0.0,
    }
    for code, weight in items_weights:
        frac = weight / total_w
        item = by_code.get(code)
        if item is not None:
            n = item.nutrients
            accum["calories_kcal"] += frac * n.calories_kcal
            accum["protein_g"] += frac * n.protein_g
            accum["fat_g"] += frac * n.fat_g
            accum["carbs_g"] += frac * n.carbs_g
            accum["fiber_g"] += frac * n.fiber_g
            accum["sodium_mg"] += frac * n.sodium_mg
            accum["calcium_mg"] += frac * n.calcium_mg
            accum["iron_mg"] += frac * n.iron_mg
    return NutrientProfile(**accum).round_values(decimals=2)


def generate_riq_mappings_from_nct(
    nct_by_code: Dict[str, FoodItemFCT]
) -> Dict[str, FoodItemFCT]:
    """Map constituent ingredients ING_001..044 using authentic NCT Nigeria data."""
    generated: Dict[str, FoodItemFCT] = {}

    direct_mappings = {
        "ING_001": ("14", "Long Grain White Rice"),               # 14 = Rice - imported
        "ING_002": ("71", "Tomato Paste"),                         # 71 = Tomato puree (canned)
        "ING_003": ("76", "Red Bell Pepper & Scotch Bonnet Blend"),# 76 = Fresh Pepper
        "ING_004": ("532", "Vegetable Oil"),                      # 532 = Vegetable oil
        "ING_005": ("72", "Onion"),                               # 72 = Onions
        "ING_006": ("149", "Seasoning & Spices (Thyme Curry Stock)"), # 149 = Stock cube
        "ING_010": ("147", "Ground Egusi (Melon Seeds)"),          # 147 = Melon (ground)
        "ING_011": ("50", "Red Palm Oil"),                        # 50 = Palm oil
        "ING_012": ("7801", "Spinach / Ugwu Leaves"),             # 7801 = Fluted pumpkin leaves (ugu)
        "ING_013": ("1071", "Ground Dried Crayfish"),              # 1071 = Crayfish
        "ING_015": ("1031", "Smoked Fish / Stockfish"),           # 1031 = Stockfish (or 102 Fish smoked)
        "ING_020": ("17", "Yam Flour (Elubo)"),                   # 17 = Yam flour
        "ING_021": ("150", "Water"),                              # 150 = Bottled water
        "ING_030": ("35", "Ripe Plantain"),                       # 35 = Plantains
        "ING_031": ("532", "Vegetable Oil (Absorbed)"),           # 532 = Vegetable oil
        "ING_032": ("141", "Salt"),                               # 141 = Salt
        "ING_040": ("41", "Black-Eyed Peas (Peeled Beans)"),      # 41 = Brown beans
        "ING_042": ("532", "Vegetable Oil"),                      # 532 = Vegetable oil
        "ING_044": ("150", "Water"),                              # 150 = Bottled water
    }

    for ing_code, (nct_code, name) in direct_mappings.items():
        if nct_code in nct_by_code:
            base_item = nct_by_code[nct_code]
            generated[ing_code] = FoodItemFCT(
                code=ing_code,
                food_name=name,
                nutrients=base_item.nutrients,
            )

    # Compound blends
    # ING_014: Onion & Pepper Puree (50% Onions 72, 50% Fresh Pepper 76)
    if "72" in nct_by_code and "76" in nct_by_code:
        blended_puree = _blend_nutrients([("72", 50.0), ("76", 50.0)], nct_by_code)
        generated["ING_014"] = FoodItemFCT(
            code="ING_014",
            food_name="Onion & Pepper Puree",
            nutrients=blended_puree,
        )

    # ING_041: Red Bell Pepper & Onion Paste (50% Fresh Pepper 76, 50% Onions 72)
    if "76" in nct_by_code and "72" in nct_by_code:
        blended_paste = _blend_nutrients([("76", 50.0), ("72", 50.0)], nct_by_code)
        generated["ING_041"] = FoodItemFCT(
            code="ING_041",
            food_name="Red Bell Pepper & Onion Paste",
            nutrients=blended_paste,
        )

    # ING_043: Ground Crayfish & Seasoning (70% Crayfish 1071, 30% Stock cube 149)
    if "1071" in nct_by_code and "149" in nct_by_code:
        blended_seasoning = _blend_nutrients([("1071", 70.0), ("149", 30.0)], nct_by_code)
        generated["ING_043"] = FoodItemFCT(
            code="ING_043",
            food_name="Ground Crayfish & Seasoning",
            nutrients=blended_seasoning,
        )

    return generated


def ingest_wafct(
    input_path: Path,
    output_path: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    """Parse raw dataset (Excel .xlsx, CSV or JSON) and output normalized table.
    
    Args:
        input_path: Path to dataset (.xlsx, .csv, or .json).
        output_path: Path to write normalized food_composition_table.json.
        
    Returns:
        Dictionary mapping ingredient code to FoodItemFCT dict.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    normalized_records: Dict[str, Dict[str, Any]] = {}
    fct_items_by_code: Dict[str, FoodItemFCT] = {}

    if input_path.suffix.lower() == ".xlsx":
        import pandas as pd
        df = pd.read_excel(input_path, sheet_name=0)
        # Check if row 0 contains INFOODS tag names (e.g. FAPU, EDIBLE)
        start_row = 1 if df.iloc[0].astype(str).str.contains("EDIBLE|ENERC|FAPU").any() else 0
        
        for idx in range(start_row, len(df)):
            row = df.iloc[idx].to_dict()
            desc = row.get("Food item description in English")
            if pd.isna(desc) or not str(desc).strip():
                continue
            item = normalize_fct_row(row)
            if item.code != "UNKNOWN":
                fct_items_by_code[item.code] = item
                normalized_records[item.code] = item.model_dump()
                # Also store prefixed with NCT_
                normalized_records[f"NCT_{item.code}"] = item.model_dump()

        # Generate the 5-dish constituent ingredients using authentic NCT data
        generated_riq = generate_riq_mappings_from_nct(fct_items_by_code)
        for ing_code, item in generated_riq.items():
            normalized_records[ing_code] = item.model_dump()

    elif input_path.suffix.lower() == ".csv":
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
                    flat_row = {"code": row.get("code", code), "food_name": row.get("food_name", code)}
                    flat_row.update(row["nutrients"])
                    item = normalize_fct_row(flat_row)
                else:
                    item = normalize_fct_row(row)
                normalized_records[item.code] = item.model_dump()
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}. Expected .xlsx, .csv or .json")

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(normalized_records, f, indent=2)

    return normalized_records


def main() -> int:
    """CLI handler matching Section 7 instructions."""
    parser = argparse.ArgumentParser(description="Ingest Nigerian Food Composition Table (NCT / WAFCT).")
    # Default to NCT_Nigeria.xlsx if present, otherwise raw_wafct_2019.csv
    default_input = "data/NCT_Nigeria.xlsx" if Path("data/NCT_Nigeria.xlsx").exists() else "data/raw_wafct_2019.csv"
    parser.add_argument("--input", default=default_input, help="Path to raw FCT dataset (.xlsx, .csv, .json)")
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
