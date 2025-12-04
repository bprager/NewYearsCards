from __future__ import annotations

import builtins
import sys
from pathlib import Path

from newyearscards import cli as cli_mod


def run(argv: list[str]) -> int:
    return cli_mod.main(argv)


def test_build_labels_requires_year_when_no_input(capsys):
    code = run(["build-labels"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--year is required" in err


def test_build_labels_missing_input_file(tmp_path, capsys):
    missing = tmp_path / "no.csv"
    code = run(["build-labels", "--input", str(missing)])
    assert code == 2
    err = capsys.readouterr().err
    assert "input CSV not found" in err


def test_download_import_error(monkeypatch, capsys):
    # Force the relative import in cmd_download to fail
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[no-untyped-def]
        if name.endswith("newyearscards.sheets") or (level == 1 and fromlist == ("download_sheet",)):
            raise ImportError("simulated import failure")
        return orig_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    code = run(["download", "--year", "2031"])  # no need to actually write anything
    assert code == 2
    err = capsys.readouterr().err
    assert "dependencies are missing" in err

