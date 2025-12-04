from __future__ import annotations

import sys
import types
from pathlib import Path

import csv

from newyearscards import cli as cli_mod


def run(argv: list[str]) -> int:
    return cli_mod.main(argv)


def write_minimal_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Prefix",
            "First Name",
            "Last Name",
            "Address 1",
            "Address 2",
            "City",
            "State",
            "Zip Code",
            "Country",
        ])
        w.writerow(["Fam.", "Frank", "Prager", "Satower Str. 26", "", "Stäbelow", "", "18198", "Germany"])


def test_build_labels_year_default_paths(tmp_path, monkeypatch, capsys):
    # Override base dirs to tmp_path
    monkeypatch.setenv("RAW_DATA_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("PROCESSED_DATA_DIR", str(tmp_path / "processed"))

    year = 2033
    in_csv = Path(str(tmp_path / "raw")) / str(year) / "mailing_list.csv"
    write_minimal_csv(in_csv)

    code = run(["build-labels", "--year", str(year)])
    assert code == 0
    out = capsys.readouterr().out
    assert "Wrote labels CSV:" in out
    out_csv = Path(str(tmp_path / "processed")) / str(year) / "labels_for_mailmerge.csv"
    assert out_csv.exists()


def test_build_labels_out_dir_and_file(tmp_path, capsys):
    # Prepare an explicit input
    in_csv = tmp_path / "mailing_list.csv"
    write_minimal_csv(in_csv)

    # Out as directory
    out_dir = tmp_path / "outdir"
    code = run(["build-labels", "--input", str(in_csv), "--out", str(out_dir)])
    assert code == 0
    out = capsys.readouterr().out
    assert "Wrote labels CSV:" in out
    expected = out_dir / "labels_for_mailmerge.csv"
    assert expected.exists()

    # Out as file
    out_file = tmp_path / "custom.csv"
    code2 = run(["build-labels", "--input", str(in_csv), "--out", str(out_file)])
    assert code2 == 0
    assert out_file.exists()


def test_download_out_file_uses_exact_path(tmp_path, monkeypatch, capsys):
    # Fake sheets module
    fake = types.ModuleType("newyearscards.sheets")

    def fake_download_sheet(year: int, *, sheet_url=None, out_path=None):  # noqa: ARG001
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("ok", encoding="utf-8")
        return p

    fake.download_sheet = fake_download_sheet  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "newyearscards.sheets", fake)

    out_file = tmp_path / "dl.csv"
    code = run(["download", "--year", "2042", "--out", str(out_file)])
    assert code == 0
    assert out_file.exists()
    assert "Saved CSV" in capsys.readouterr().out


def test_build_labels_dry_run_cleans_temp(tmp_path, monkeypatch, capsys):
    in_csv = tmp_path / "mailing_list.csv"
    write_minimal_csv(in_csv)

    # Force temp dir to tmp_path so we can check cleanup
    import tempfile as _tempfile

    monkeypatch.setattr(_tempfile, "gettempdir", lambda: str(tmp_path))

    code = run(["build-labels", "--input", str(in_csv), "--dry-run"])
    assert code == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0].startswith("Prefix,FirstName,LastName,Country,Line1,Line2")
    temp_file = tmp_path / "labels_for_mailmerge.csv"
    assert not temp_file.exists()
