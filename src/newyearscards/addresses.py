from __future__ import annotations

from collections.abc import Iterable
import csv
import importlib
from pathlib import Path
import re
from typing import Any, TypedDict, cast
import unicodedata

from .config import ensure_dir, load_paths

NORMALIZE_MAP: dict[str, str] = {
    "prefix": "prefix",
    "first name": "first_name",
    "firstname": "first_name",
    "first": "first_name",
    "last name": "last_name",
    "lastname": "last_name",
    "last": "last_name",
    "surname": "last_name",
    "address 1": "address1",
    "address1": "address1",
    "street": "address1",
    "line1": "address1",
    "address 2": "address2",
    "address2": "address2",
    "line2": "address2",
    "city": "city",
    "town": "city",
    "state": "state",
    "province": "state",
    "region": "state",
    "zip code": "zip",
    "zipcode": "zip",
    "postal code": "zip",
    "postcode": "zip",
    "country": "country",
}


US_STATE_ABBR = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}

# Country aliases mapping (case-insensitive, supports Unicode)
# Keys are expected to be NFC-normalized, casefolded strings.
COUNTRY_ALIASES: dict[str, str] = {
    "ukraine": "UA",
    "україна": "UA",
    "french polynesia": "PF",
    "polynésie française": "PF",
    "polynesie francaise": "PF",
    "pf": "PF",
}


def _canon(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_headers(headers: Iterable[str]) -> list[str]:
    result: list[str] = []
    for h in headers:
        key = NORMALIZE_MAP.get(_canon(h), _canon(h))
        result.append(key)
    return result


yaml_module: Any | None
try:
    yaml_module = importlib.import_module("yaml")
except Exception:  # pragma: no cover
    yaml_module = None


class TemplateEntry(TypedDict, total=False):
    lines: list[str]
    uppercase_last_n_lines: int


def load_templates(path: Path) -> dict[str, TemplateEntry]:
    text = path.read_text(encoding="utf-8")
    if yaml_module is not None:
        data = cast(Any, yaml_module).safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("address templates file must be a mapping")
        return cast(dict[str, TemplateEntry], data)

    # Minimal fallback parser for the supported structure:
    # top-level keys, with a 'lines:' array of quoted strings
    templates: dict[str, TemplateEntry] = {}
    current: str | None = None
    in_lines = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current = line[:-1]
            templates[current] = {"lines": []}
            in_lines = False
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped == "lines:":
            in_lines = True
            continue
        if in_lines and stripped.startswith("- "):
            item = stripped[2:].strip()
            if item and item[0] in {'"', "'"} and item[-1] == item[0]:
                item = item[1:-1]
            templates[current]["lines"].append(item)
            continue
        # support 'uppercase_last_n_lines: N' in fallback parser
        if stripped.startswith("uppercase_last_n_lines:"):
            try:
                _, val = stripped.split(":", 1)
                templates[current]["uppercase_last_n_lines"] = int(val.strip())
            except Exception:
                # ignore parse errors, default will apply in code
                pass
    return templates


def infer_country(row: dict[str, str]) -> tuple[str, str]:
    raw = (row.get("country") or "").strip()
    state = (row.get("state") or "").strip().upper()
    if not raw and state in US_STATE_ABBR:
        return "US", "United States"

    # First try Unicode-aware alias mapping
    alias_key = unicodedata.normalize("NFC", raw).casefold()
    if alias_key in COUNTRY_ALIASES:
        code = COUNTRY_ALIASES[alias_key]
        # Display names for known codes
        display = {
            "DE": "Germany",
            "FR": "France",
            "US": "United States",
            "UA": "Ukraine",
            "PF": "French Polynesia",
        }.get(code, raw or code)
        return code, display

    key = _canon(raw)
    if key in {"germany", "de", "deutschland"}:
        return "DE", "Germany"
    if key in {"france", "fr", "français", "francaise", "république française"}:
        return "FR", "France"
    if key in {"united states", "usa", "us", "united states of america"}:
        return "US", "United States"

    # Fall back to given text, or empty
    return (raw or "", raw or "")


def build_address_lines(row: dict[str, str], templates: dict[str, TemplateEntry]) -> list[str]:
    code, display_country = infer_country(row)
    tmpl = templates.get(code, templates.get("default"))
    if not tmpl or "lines" not in tmpl:
        raise ValueError("address template missing 'lines'")

    fmt_map = {
        "prefix": (row.get("prefix") or "").strip(),
        "first_name": (row.get("first_name") or "").strip(),
        "last_name": (row.get("last_name") or "").strip(),
        "address1": (row.get("address1") or "").strip(),
        "address2": (row.get("address2") or "").strip(),
        "city": (row.get("city") or "").strip(),
        "state": (row.get("state") or "").strip(),
        "zip": (row.get("zip") or "").strip(),
        "country": display_country,
    }

    out: list[str] = []
    for pattern in tmpl.get("lines", []):
        try:
            s = pattern.format(**fmt_map)
        except KeyError:
            # Unknown placeholder — treat as empty
            s = pattern
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            out.append(s)

    # Uppercase preferences: default to 1 (country line)
    try:
        uppercase_last = int(cast(Any, tmpl).get("uppercase_last_n_lines", 1))
    except Exception:
        uppercase_last = 1
    if uppercase_last > 0 and out:
        n = min(uppercase_last, len(out))
        for i in range(1, n + 1):
            out[-i] = out[-i].upper()
    return out


def _compact_lines_for_schema(code: str, lines: list[str], row: dict[str, str]) -> list[str]:
    """Ensure at most 5 address lines while preserving important info.

    - If there are more than 5 lines, try to merge city/zip for certain countries.
    - Always try to keep the country line if present at the end.
    """
    if len(lines) <= 5:
        return (lines + [""] * 5)[:5]

    # Special-case Ukraine: merge city and zip into a single line if both present
    if code == "UA":
        city_val = (row.get("city") or "").strip()
        zip_val = (row.get("zip") or "").strip()
        try:
            city_idx = lines.index(city_val)
        except ValueError:
            city_idx = -1
        try:
            zip_idx = lines.index(zip_val)
        except ValueError:
            zip_idx = -1
        if city_idx >= 0 and zip_idx >= 0 and city_idx != zip_idx:
            first_idx = min(city_idx, zip_idx)
            merged = (
                f"{city_val} {zip_val}" if city_idx < zip_idx else f"{zip_val} {city_val}"
            ).strip()
            # Remove both and insert merged at the earliest position
            new_lines = [line for idx, line in enumerate(lines) if idx not in (city_idx, zip_idx)]
            new_lines.insert(first_idx, merged)
            lines = new_lines

    # If still too many lines, keep first four and the last (likely country)
    if len(lines) > 5:
        lines = lines[:4] + [lines[-1]]
    return (lines + [""] * 5)[:5]


def transform_rows(
    rows: Iterable[dict[str, str]], templates: dict[str, TemplateEntry]
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        # Skip if clearly empty
        if not any((row.get("address1"), row.get("address2"), row.get("city"))):
            continue

        code, display_country = infer_country(row)
        lines = build_address_lines(row, templates)
        # ensure at most 5 columns, preserving country line when possible
        lines5 = _compact_lines_for_schema(code, lines, row)

        output.append(
            {
                "Prefix": row.get("prefix", ""),
                "FirstName": row.get("first_name", ""),
                "LastName": row.get("last_name", ""),
                "Country": display_country,
                "Line1": lines5[0],
                "Line2": lines5[1],
                "Line3": lines5[2],
                "Line4": lines5[3],
                "Line5": lines5[4],
            }
        )
    return output


def build_labels(in_csv: Path, out_csv: Path | None = None) -> Path:
    paths = load_paths()
    templates = load_templates(paths.templates)

    with in_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            raw_headers = next(reader)
        except StopIteration as err:
            raise ValueError("Input CSV is empty") from err

        headers = normalize_headers(raw_headers)
        rows: list[dict[str, str]] = []
        for raw_row in reader:
            row_dict: dict[str, str] = {}
            for i, val in enumerate(raw_row[: len(headers)]):
                row_dict[headers[i]] = val.strip()
            rows.append(row_dict)

    processed = transform_rows(rows, templates)

    if out_csv is None:
        # Deduce year from parent folder name if possible
        try:
            year = int(in_csv.parent.name)
        except ValueError as err:
            raise ValueError(
                "Cannot infer year from input path; please provide output path"
            ) from err
        target_dir = paths.processed_dir(year)
        ensure_dir(target_dir)
        out_csv = target_dir / "labels_for_mailmerge.csv"
    else:
        ensure_dir(out_csv.parent)

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "Prefix",
            "FirstName",
            "LastName",
            "Country",
            "Line1",
            "Line2",
            "Line3",
            "Line4",
            "Line5",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in processed:
            writer.writerow(row)

    return out_csv
