"""Tests for ingest_wafct.py."""

import json
from pathlib import Path
import pytest

from data_pipeline.src.ingest_wafct import (
    _clean_numeric_value,
    normalize_fct_row,
    ingest_wafct,
    main as cli_main,
)
from data_pipeline.src.schemas import FoodItemFCT


def test_clean_numeric_value():
    """Verify numeric cleaning with various WAFCT notations."""
    assert _clean_numeric_value(10.5) == 10.5
    assert _clean_numeric_value("12.4") == 12.4
    assert _clean_numeric_value("[15.0]") == 15.0
    assert _clean_numeric_value("-") == 0.0
    assert _clean_numeric_value("NA") == 0.0
    assert _clean_numeric_value("[T]") == 0.0
    assert _clean_numeric_value("trace") == 0.0
    assert _clean_numeric_value(None) == 0.0
    assert _clean_numeric_value("invalid_str") == 0.0


def test_normalize_fct_row_synonyms():
    """Verify synonym column mapping for FAO INFOODS tag names."""
    raw_row = {
        "food_id": "TEST_001",
        "description": "Cooked Cassava",
        "enerc_kcal": "160.0",
        "procnt_g": "1.4",
        "fatce_g": "0.3",
        "choavldf_g": "38.1",
        "fibtg_g": "1.8",
        "na_mg": "14.0",
        "ca_mg": "16.0",
        "fe_mg": "0.27",
    }
    item = normalize_fct_row(raw_row)
    assert isinstance(item, FoodItemFCT)
    assert item.code == "TEST_001"
    assert item.food_name == "Cooked Cassava"
    assert item.nutrients.calories_kcal == 160.0
    assert item.nutrients.protein_g == 1.4
    assert item.nutrients.fat_g == 0.3
    assert item.nutrients.carbs_g == 38.1
    assert item.nutrients.fiber_g == 1.8
    assert item.nutrients.sodium_mg == 14.0
    assert item.nutrients.calcium_mg == 16.0
    assert item.nutrients.iron_mg == 0.27


def test_ingest_wafct_csv_and_json(tmp_path):
    """Verify ingestion from CSV and JSON file formats."""
    csv_file = tmp_path / "test_raw.csv"
    csv_file.write_text(
        "code,food_name,energy_kcal,protein_g,fat_g,carbs_g,fiber_g,sodium_mg,calcium_mg,iron_mg\n"
        "ING_X,Ingredient X,100,5,2,15,1,10,20,1.5\n",
        encoding="utf-8"
    )
    out_json = tmp_path / "out_fct.json"
    res = ingest_wafct(csv_file, output_path=out_json)
    assert "ING_X" in res
    assert res["ING_X"]["food_name"] == "Ingredient X"
    assert out_json.exists()

    # Now ingest from the generated JSON
    res_json = ingest_wafct(out_json)
    assert "ING_X" in res_json

    # Ingest from JSON list format
    list_json = tmp_path / "list.json"
    list_json.write_text(
        json.dumps([{"code": "ING_Y", "food_name": "Ingredient Y", "energy_kcal": 200, "protein_g": 10, "fat_g": 5, "carbs_g": 25, "fiber_g": 2, "sodium_mg": 15, "calcium_mg": 30, "iron_mg": 2.0}]),
        encoding="utf-8"
    )
    res_list = ingest_wafct(list_json)
    assert "ING_Y" in res_list


def test_ingest_wafct_errors(tmp_path):
    """Verify error handling on invalid paths or unsupported formats."""
    with pytest.raises(FileNotFoundError):
        ingest_wafct(tmp_path / "non_existent.csv")

    bad_ext = tmp_path / "data.xml"
    bad_ext.write_text("<data></data>", encoding="utf-8")
    with pytest.raises(ValueError):
        ingest_wafct(bad_ext)


def test_ingest_wafct_cli_main(tmp_path, monkeypatch):
    """Verify CLI main entrypoint."""
    csv_file = tmp_path / "test_raw.csv"
    csv_file.write_text("code,food_name,energy_kcal\nING_1,Food 1,50\n", encoding="utf-8")
    out_file = tmp_path / "out.json"

    monkeypatch.setattr("sys.argv", ["ingest_wafct.py", "--input", str(csv_file), "--output", str(out_file)])
    exit_code = cli_main()
    assert exit_code == 0
    assert out_file.exists()


def test_blend_nutrients():
    """Verify _blend_nutrients produces correct weighted average."""
    from data_pipeline.src.ingest_wafct import _blend_nutrients
    from data_pipeline.src.schemas import NutrientProfile

    by_code = {
        "A": FoodItemFCT(code="A", food_name="Food A", nutrients=NutrientProfile(calories_kcal=100.0, protein_g=10.0, fat_g=5.0, carbs_g=10.0)),
        "B": FoodItemFCT(code="B", food_name="Food B", nutrients=NutrientProfile(calories_kcal=200.0, protein_g=20.0, fat_g=10.0, carbs_g=20.0)),
    }
    blended = _blend_nutrients([("A", 50.0), ("B", 50.0)], by_code)
    assert blended.calories_kcal == 150.0
    assert blended.protein_g == 15.0
    assert blended.fat_g == 7.5
    assert blended.carbs_g == 15.0


def test_generate_riq_mappings_from_nct():
    """Verify generate_riq_mappings_from_nct maps NCT codes to ING_001..044."""
    from data_pipeline.src.ingest_wafct import generate_riq_mappings_from_nct
    from data_pipeline.src.schemas import NutrientProfile

    sample_nct = {
        "14": FoodItemFCT(code="14", food_name="Rice", nutrients=NutrientProfile(calories_kcal=350, protein_g=7, fat_g=1, carbs_g=78)),
        "71": FoodItemFCT(code="71", food_name="Tomato Paste", nutrients=NutrientProfile(calories_kcal=80, protein_g=4, fat_g=0.5, carbs_g=15)),
        "76": FoodItemFCT(code="76", food_name="Pepper", nutrients=NutrientProfile(calories_kcal=40, protein_g=2, fat_g=0.2, carbs_g=8)),
        "72": FoodItemFCT(code="72", food_name="Onion", nutrients=NutrientProfile(calories_kcal=45, protein_g=1.5, fat_g=0.1, carbs_g=9)),
        "1071": FoodItemFCT(code="1071", food_name="Crayfish", nutrients=NutrientProfile(calories_kcal=250, protein_g=50, fat_g=3, carbs_g=2)),
        "149": FoodItemFCT(code="149", food_name="Stock cube", nutrients=NutrientProfile(calories_kcal=150, protein_g=10, fat_g=5, carbs_g=15)),
    }
    generated = generate_riq_mappings_from_nct(sample_nct)
    assert "ING_001" in generated
    assert generated["ING_001"].nutrients.calories_kcal == 350
    assert "ING_014" in generated  # Compound blend of 72 and 76
    assert "ING_041" in generated  # Compound blend of 76 and 72
    assert "ING_043" in generated  # Compound blend of 1071 and 149


def test_ingest_wafct_excel(tmp_path):
    """Verify ingestion of official NCT_Nigeria.xlsx if present, or mock excel."""
    nct_file = Path("data/NCT_Nigeria.xlsx")
    if nct_file.exists():
        out_json = tmp_path / "nct_out.json"
        res = ingest_wafct(nct_file, output_path=out_json)
        assert len(res) > 200
        assert "ING_001" in res
        assert res["ING_001"]["nutrients"]["calories_kcal"] > 0
        assert res["ING_001"]["nutrients"]["protein_g"] > 0
        assert "14" in res
        assert "NCT_14" in res

