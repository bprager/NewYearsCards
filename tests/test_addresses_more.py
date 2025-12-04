from __future__ import annotations

from pathlib import Path

from newyearscards import addresses


def test_compact_lines_for_non_ua_truncates():
    lines = ["L1", "L2", "L3", "L4", "L5", "L6"]
    out = addresses._compact_lines_for_schema("XX", lines, {})
    assert out[:4] == ["L1", "L2", "L3", "L4"]
    assert out[4] == "L6"


def test_ua_compaction_keeps_country_and_merges_city_zip(tmp_path):
    templates = addresses.load_templates(Path("config/address_formats.yml"))
    row = {
        "first_name": "Олександр",
        "last_name": "Шевченко",
        "address1": "вул. Хрещатик, 1",
        "address2": "Кв. 5",
        "city": "Київ",
        "zip": "01001",
        "country": "україна",
    }
    # Compaction happens during transform_rows (when preparing schema lines)
    out_rows = addresses.transform_rows([row], templates)
    assert len(out_rows) == 1
    r = out_rows[0]
    # Ensure we have 5 address lines (Line1..Line5)
    lines = [r["Line1"], r["Line2"], r["Line3"], r["Line4"], r["Line5"]]
    assert len(lines) == 5
    assert lines[-1] == "UKRAINE"
    assert any("Київ" in l for l in lines)
    assert any("01001" in l for l in lines)
