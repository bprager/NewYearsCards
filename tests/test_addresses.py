import csv
from pathlib import Path

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
    assert lines_de[-1] == "GERMANY"
    assert any("19322 WITTENBERGE" in line for line in lines_de)

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
    assert lines_fr[-1] == "FRANCE"
    # With uppercase_last_n_lines=2 for FR, the zip+city line should be uppercased
    assert any("13210 SAINT RÉMY DE PROVENCE" in line for line in lines_fr)

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
    # With a dedicated US template, the last line is city/state/zip, uppercased
    assert lines_us[-1] == "LOS ANGELES CA 90036"
    # No country line for US domestic addresses
    assert all("UNITED STATES" not in line for line in lines_us)


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
    # US row inferred by state (Country column remains title case)
    assert ",United States," in content[2]


def test_default_template_uppercases_only_country():
    templates = addresses.load_templates(Path("config/address_formats.yml"))
    row = {
        "prefix": "Sr.",
        "first_name": "Juan",
        "last_name": "Pérez",
        "address1": "Carrer Major 1",
        "address2": "",
        "city": "Barcelona",
        "zip": "08001",
        "country": "Spain",
    }
    lines = addresses.build_address_lines(row, templates)
    # Default template uppercases only the final country line
    assert lines[-1] == "SPAIN"
    assert any("08001 Barcelona" in line for line in lines)


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

    # French Polynesia should map to PF and keep display name
    code, name = addresses.infer_country({"country": "French Polynesia"})
    assert code == "PF"
    assert name == "French Polynesia"


def test_build_address_lines_french_polynesia():
    templates = addresses.load_templates(Path("config/address_formats.yml"))
    pf_row = {
        "prefix": "Fam.",
        "first_name": "Moetai",
        "last_name": "Brotherson",
        "address1": "BP 42883",
        "address2": "",
        "city": "Papeete",
        "state": "Tahiti",
        "zip": "98713",
        "country": "French Polynesia",
    }
    lines_pf = addresses.build_address_lines(pf_row, templates)
    assert lines_pf[-1] == "FRENCH POLYNESIA"
    assert any("98713 Papeete" in line for line in lines_pf)
    assert any("Tahiti" in line for line in lines_pf)

    # Unicode alias should also resolve
    pf_row2 = dict(pf_row)
    pf_row2["country"] = "Polynésie française"
    lines_pf2 = addresses.build_address_lines(pf_row2, templates)
    assert lines_pf2[-1] == "FRENCH POLYNESIA"


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


def test_infer_country_aliases_ukraine():
    # ASCII alias
    code, name = addresses.infer_country({"country": "Ukraine"})
    assert code == "UA"
    assert name == "Ukraine"
    # Unicode alias (Cyrillic)
    code2, name2 = addresses.infer_country({"country": "україна"})
    assert code2 == "UA"
    assert name2 == "Ukraine"


def test_ukraine_template_utf8_preserved(tmp_path):
    # Ensure Cyrillic characters survive end-to-end, with the UA template
    year_dir = tmp_path / "2027"
    year_dir.mkdir(parents=True)
    input_csv = year_dir / "mailing_list.csv"

    header = [
        "First Name",
        "Last Name",
        "Address 1",
        "Address 2",
        "City",
        "Zip Code",
        "Country",
    ]
    rows = [
        ["Олександр", "Шевченко", "вул. Хрещатик, 1", "", "Київ", "01001", "україна"],
    ]
    with input_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    out = addresses.build_labels(input_csv)
    content = out.read_text(encoding="utf-8").splitlines()
    # Header + 1 row
    assert len(content) == 2
    # First/LastName with Cyrillic preserved
    assert "Олександр" in content[1]
    assert "Шевченко" in content[1]
    # City and ZIP should both appear across the address lines
    assert "Київ" in content[1]
    assert "01001" in content[1]
    # Country column and last line should reflect Ukraine; last line specifically 'UKRAINE'
    assert ",Ukraine," in content[1]
    assert content[1].endswith(",UKRAINE") or ",UKRAINE" in content[1]
