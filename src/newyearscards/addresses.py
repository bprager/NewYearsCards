from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

from .config import load_paths, ensure_dir


NORMALIZE_MAP: Dict[str, str] = {
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


def _canon(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_headers(headers: Iterable[str]) -> List[str]:
    result: List[str] = []
    for h in headers:
        key = NORMALIZE_MAP.get(_canon(h), _canon(h))
        result.append(key)
    return result


def load_templates(path: Path) -> Dict[str, Dict[str, List[str]]]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("address templates file must be a mapping")
        return data  # type: ignore[return-value]

    # Minimal fallback parser for the supported structure:
    # top-level keys, with a 'lines:' array of quoted strings
    templates: Dict[str, Dict[str, List[str]]] = {}
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
        if line.strip() == "lines:":
            in_lines = True
            continue
        if in_lines and line.strip().startswith("- "):
            item = line.strip()[2:].strip()
            if item and item[0] in {'"', "'"} and item[-1] == item[0]:
                item = item[1:-1]
            templates[current]["lines"].append(item)
    return templates


def infer_country(row: Dict[str, str]) -> Tuple[str, str]:
    raw = (row.get("country") or "").strip()
    state = (row.get("state") or "").strip().upper()
    if not raw and state in US_STATE_ABBR:
        return "US", "United States"

    key = _canon(raw)
    if key in {"germany", "de", "deutschland"}:
        return "DE", "Germany"
    if key in {"france", "fr", "français", "francaise", "république française"}:
        return "FR", "France"
    if key in {"united states", "usa", "us", "united states of america"}:
        return "US", "United States"

    # Fall back to given text, or empty
    return (raw or "", raw or "")


def build_address_lines(
    row: Dict[str, str], templates: Dict[str, Dict[str, List[str]]]
) -> List[str]:
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

    out: List[str] = []
    for pattern in tmpl.get("lines", []):
        try:
            s = pattern.format(**fmt_map)
        except KeyError:
            # Unknown placeholder — treat as empty
            s = pattern
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            out.append(s)
    return out


def transform_rows(
    rows: Iterable[Dict[str, str]], templates: Dict[str, Dict[str, List[str]]]
) -> List[Dict[str, str]]:
    output: List[Dict[str, str]] = []
    for row in rows:
        # Skip if clearly empty
        if not any((row.get("address1"), row.get("address2"), row.get("city"))):
            continue

        code, display_country = infer_country(row)
        lines = build_address_lines(row, templates)
        # ensure exactly 5 columns
        lines5 = (lines + [""] * 5)[:5]

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
        except StopIteration:
            raise ValueError("Input CSV is empty")

        headers = normalize_headers(raw_headers)
        rows: List[Dict[str, str]] = []
        for raw_row in reader:
            row_dict: Dict[str, str] = {}
            for i, val in enumerate(raw_row[: len(headers)]):
                row_dict[headers[i]] = val.strip()
            rows.append(row_dict)

    processed = transform_rows(rows, templates)

    if out_csv is None:
        # Deduce year from parent folder name if possible
        try:
            year = int(in_csv.parent.name)
        except ValueError:
            raise ValueError(
                "Cannot infer year from input path; please provide output path"
            )
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
