from pathlib import Path

import csv

from newyearscards import addresses


def test_normalize_headers_maps_common_columns():
    raw = [
        "Prefix",
        "First Name",
        "Last Name",
        "Address 1",
        "Address 2",
        "City",
        "State",
        "Zip Code",
        "Country",
    ]
    norm = addresses.normalize_headers(raw)
    assert norm == [
        "prefix",
        "first_name",
        "last_name",
        "address1",
        "address2",
        "city",
        "state",
        "zip",
        "country",
    ]


def test_infer_country_uses_state_for_us_when_country_missing():
    code, name = addresses.infer_country({"state": "NY", "country": ""})
    assert code == "US"
    assert name == "United States"


def test_build_address_lines_various_countries():
    templates = addresses.load_templates(Path("config/address_formats.yml"))

    de_row = {
        "prefix": "Fam.",
        "first_name": "Andreas",
        "last_name": "Merfort",
        "address1": "Musterweg 1",
        "address2": "",
        "city": "Wittenberge",
        "zip": "19322",
        "country": "Germany",
    }
    lines_de = addresses.build_address_lines(de_row, templates)
    assert lines_de[-1] == "Germany"
    assert any("19322 Wittenberge" in l for l in lines_de)

    fr_row = {
        "prefix": "",
        "first_name": "Guillaume",
        "last_name": "Martin",
        "address1": "919 Chemin de Bigau",
        "address2": "",
        "city": "Saint Rémy de Provence",
        "zip": "13210",
        "country": "France",
    }
    lines_fr = addresses.build_address_lines(fr_row, templates)
    assert lines_fr[-1] == "France"

    us_row = {
        "prefix": "Family",
        "first_name": "Brian",
        "last_name": "Vary",
        "address1": "5669 W. 6th St.",
        "address2": "",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90036",
        "country": "",  # inferred by state
    }
    lines_us = addresses.build_address_lines(us_row, templates)
    assert lines_us[-1] == "United States"


def test_transform_and_build_labels_end_to_end(tmp_path):
    # Prepare a minimal input CSV
    year_dir = tmp_path / "2025"
    year_dir.mkdir(parents=True)
    input_csv = year_dir / "mailing_list.csv"

    header = [
        "Prefix",
        "First Name",
        "Last Name",
        "Address 1",
        "Address 2",
        "City",
        "State",
        "Zip Code",
        "Country",
    ]
    rows = [
        [
            "Fam.",
            "Frank",
            "Prager",
            "Satower Str. 26",
            "",
            "Stäbelow",
            "",
            "18198",
            "Germany",
        ],
        [
            "Family",
            "Brian",
            "Vary",
            "5669 W. 6th St.",
            "",
            "Los Angeles",
            "CA",
            "90036",
            "",
        ],
    ]
    with input_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    out = addresses.build_labels(input_csv)
    assert out.name == "labels_for_mailmerge.csv"
    assert out.parent.name == "2025"

    content = out.read_text(encoding="utf-8").splitlines()
    assert content[0].startswith("Prefix,FirstName,LastName,Country,Line1,Line2")
    # Germany row should end with Germany
    assert ",Germany," in content[1]
    # US row inferred by state
    assert ",United States," in content[2]


def test_transform_skips_empty_rows(tmp_path):
    # Row with no address components should be ignored
    input_csv = tmp_path / "2026" / "mailing_list.csv"
    input_csv.parent.mkdir(parents=True)
    with input_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "Prefix",
                "First Name",
                "Last Name",
                "Address 1",
                "Address 2",
                "City",
                "Country",
            ]
        )
        w.writerow(["", "", "", "", "", "", ""])  # empty
        w.writerow(
            [
                "",
                "Guillaume",
                "Martin",
                "919 Chemin",
                "",
                "Saint Rémy de Provence",
                "France",
            ]
        )  # valid

    out = addresses.build_labels(input_csv)
    lines = out.read_text(encoding="utf-8").splitlines()
    # header + 1 data row
    assert len(lines) == 2


def test_infer_country_variants_and_default():
    # Variants for Germany
    # Test known country code
    code, name = addresses.infer_country({"country": "DE"})
    assert code == "DE"
    assert name == "Germany"

    # Test German variants (if supported)
    for val in ["Deutschland", "germany"]:
        code, name = addresses.infer_country({"country": val})
        assert code == "DE"
        assert name == "Germany"

    # French Polynesia should pass through using default template
    code, name = addresses.infer_country({"country": "French Polynesia"})
    assert name == "French Polynesia"


def test_normalize_headers_with_extra_columns():
    raw = [
        "First Name",
        "Last Name",
        "Address 1",
        "Some Extra Col",
        "Zip Code",
        "Country",
    ]
    norm = addresses.normalize_headers(raw)
    # Extra column should be carried through in lowercase canonical form
    assert norm[3] == "some extra col"
