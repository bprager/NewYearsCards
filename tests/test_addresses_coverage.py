from __future__ import annotations

import sys
from pathlib import Path

import pytest

from newyearscards import addresses


def test_load_templates_yaml_module_path(tmp_path, monkeypatch):
    # Create a dummy file; content is ignored by fake yaml
    p = tmp_path / "t.yml"
    p.write_text("ignored", encoding="utf-8")

    class FakeYaml:
        @staticmethod
        def safe_load(_text: str):  # type: ignore[no-untyped-def]
            return {"XX": {"lines": ["{address1}"]}}

    monkeypatch.setattr(addresses, "yaml_module", FakeYaml)
    t = addresses.load_templates(p)
    assert t["XX"]["lines"] == ["{address1}"]


def test_fallback_parser_current_none_and_bad_uppercase(tmp_path, monkeypatch):
    # Leading stray key will trigger 'current is None: continue'
    text = (
        "uppercase_last_n_lines: 2\n"
        "ZZ:\n"
        "  lines:\n"
        "    - \"{address1}\"\n"
        "  uppercase_last_n_lines: not-a-number\n"
    )
    p = tmp_path / "cfg.yml"
    p.write_text(text, encoding="utf-8")
    # Ensure fallback parser is used
    monkeypatch.setattr(addresses, "yaml_module", None)
    t = addresses.load_templates(p)
    # Invalid uppercase value should be ignored (not crashing), and lines parsed
    assert t["ZZ"]["lines"] == ["{address1}"]


def test_infer_country_united_states_string():
    code, name = addresses.infer_country({"country": "united states of america"})
    assert code == "US"
    assert name == "United States"


def test_build_address_lines_missing_lines_raises():
    with pytest.raises(ValueError):
        addresses.build_address_lines({"country": "XX"}, {"XX": {}})


def test_build_address_lines_unknown_placeholder_uppercase():
    # Unknown placeholders are left as-is and then uppercased if in the tail
    lines = addresses.build_address_lines(
        {"country": "XX"}, {"XX": {"lines": ["{unknown}"]}}
    )
    assert lines[-1] == "{UNKNOWN}"


def test_compact_lines_ua_no_indices():
    # UA compaction: when city/zip not present in lines, indices are -1
    lines = ["L1", "L2", "L3", "L4", "L5", "UKRAINE"]
    out = addresses._compact_lines_for_schema(
        "UA", lines, {"city": "Kyiv", "zip": "01001"}
    )
    # Still compacts to first4 + last when >5
    assert out[0:4] == ["L1", "L2", "L3", "L4"]
    assert out[4] == "UKRAINE"


def test_build_labels_empty_and_bad_year(tmp_path, monkeypatch):
    # Empty file -> Input CSV is empty
    empty = tmp_path / "2020" / "mailing_list.csv"
    empty.parent.mkdir(parents=True)
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        addresses.build_labels(empty)

    # Valid CSV but parent directory not a year -> cannot infer year
    f = tmp_path / "notayear" / "mailing_list.csv"
    f.parent.mkdir(parents=True)
    f.write_text("Prefix\n\n", encoding="utf-8")
    with pytest.raises(ValueError):
        addresses.build_labels(f)

