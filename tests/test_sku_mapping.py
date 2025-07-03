import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from automation_tool.sku_mapping import load_mapping, apply_mapping


def test_load_and_apply(tmp_path: Path):
    mapping_file = tmp_path / "map.csv"
    mapping_file.write_text("SKU,AMAZON SKU\nA1,ASKU1\nB2,ASKU2\n")
    mapping = load_mapping(mapping_file)
    assert mapping == {"A1": "ASKU1", "B2": "ASKU2"}

    rows = [
        {"SKU": "A1", "QUANTITY": 5},
        {"SKU": "C3", "QUANTITY": 1},
    ]
    mapped = apply_mapping(rows, mapping)
    assert mapped[0]["AMAZON SKU"] == "ASKU1"
    assert mapped[1]["AMAZON SKU"] == "C3"
