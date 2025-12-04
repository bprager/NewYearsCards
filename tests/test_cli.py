from __future__ import annotations

import types
from pathlib import Path

import csv
import builtins

from newyearscards import cli as cli_mod


def run_cli(argv: list[str]) -> int:
    return cli_mod.main(argv)


def test_cli_build_labels_dry_run(tmp_path, capsys):
    # Prepare a small input CSV
    input_csv = tmp_path / "mailing_list.csv"
    with input_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Prefix", "First Name", "Last Name", "Address 1", "Address 2", "City", "State", "Zip Code", "Country"])
        w.writerow(["Fam.", "Frank", "Prager", "Satower Str. 26", "", "Stäbelow", "", "18198", "Germany"])

    code = run_cli(["build-labels", "--input", str(input_csv), "--dry-run"])
    assert code == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("Prefix,FirstName,LastName,Country,Line1,Line2")
    assert any(",Germany," in line for line in out[1:])


def test_cli_download_uses_mocked_sheets_module(tmp_path, monkeypatch, capsys):
    # Create a fake sheets module to satisfy lazy import
    fake = types.ModuleType("newyearscards.sheets")

    def fake_download_sheet(year: int, *, sheet_url=None, out_path=None):
        # Simulate writing a CSV to out_path or default path
        if out_path is None:
            out_dir = Path("data/raw") / str(year)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "mailing_list.csv"
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("Prefix,FirstName\n,,\n", encoding="utf-8")
        return out_path

    fake.download_sheet = fake_download_sheet  # type: ignore[attr-defined]

    # Register fake module so cli can import it
    monkeypatch.setitem(builtins.__dict__["__import__"]("sys").modules, "newyearscards.sheets", fake)

    out_dir = tmp_path / "raw"
    code = run_cli(["download", "--year", "2030", "--out", str(out_dir)])
    assert code == 0
    stdout = capsys.readouterr().out
    assert "Saved CSV to" in stdout
    # Ensure file exists
    # If a directory was provided, the CLI appends mailing_list.csv
    expected = out_dir / "mailing_list.csv"
    assert expected.exists()

