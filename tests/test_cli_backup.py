from __future__ import annotations

import os
from pathlib import Path
import types

from newyearscards import cli as cli_mod


def _write_dummy_data(base: Path) -> None:
    raw = base / "data" / "raw"
    proc = base / "data" / "processed"
    (raw / "2025").mkdir(parents=True, exist_ok=True)
    (proc / "2025").mkdir(parents=True, exist_ok=True)
    (raw / "2025" / "mailing_list.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (proc / "2025" / "labels_for_mailmerge.csv").write_text(
        "x,y\n3,4\n", encoding="utf-8"
    )


def test_attempt_encrypted_backup_creates_age_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_dummy_data(tmp_path)

    # Point env to tmp data roots
    monkeypatch.setenv("RAW_DATA_DIR", str(tmp_path / "data" / "raw"))
    monkeypatch.setenv("PROCESSED_DATA_DIR", str(tmp_path / "data" / "processed"))
    monkeypatch.setenv("AGE_RECIPIENT", "age1testrecipientpublickey")

    # Pretend age is available
    monkeypatch.setenv("PATH", "/usr/bin:" + os.getenv("PATH", ""))
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/age" if name == "age" else None)

    # Fake subprocess.run to create the output file passed after '-o'
    def fake_run(argv, check):  # type: ignore[no-untyped-def]
        assert check is True
        assert "-o" in argv
        out = Path(argv[argv.index("-o") + 1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"enc")
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr("subprocess.run", fake_run)

    cli_mod._attempt_encrypted_backup(2025)

    files = list((tmp_path / "backups" / "2025").glob("*.tgz.age"))
    assert len(files) == 1
    assert files[0].stat().st_size > 0


def test_attempt_encrypted_backup_no_age_or_no_recipient_skips(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_dummy_data(tmp_path)

    monkeypatch.setenv("RAW_DATA_DIR", str(tmp_path / "data" / "raw"))
    monkeypatch.setenv("PROCESSED_DATA_DIR", str(tmp_path / "data" / "processed"))

    # No recipient, should skip immediately
    monkeypatch.delenv("AGE_RECIPIENT", raising=False)
    monkeypatch.delenv("AGE_RECIPIENTS_FILE", raising=False)
    cli_mod._attempt_encrypted_backup(2025)
    assert not (tmp_path / "backups" / "2025").exists()

    # Recipient present but age missing -> skip
    monkeypatch.setenv("AGE_RECIPIENT", "age1abc")
    monkeypatch.setattr("shutil.which", lambda name: None)
    cli_mod._attempt_encrypted_backup(2025)
    assert not (tmp_path / "backups" / "2025").exists()


def test_attempt_encrypted_backup_uses_recipients_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_dummy_data(tmp_path)

    monkeypatch.setenv("RAW_DATA_DIR", str(tmp_path / "data" / "raw"))
    monkeypatch.setenv("PROCESSED_DATA_DIR", str(tmp_path / "data" / "processed"))

    # Create recipients file
    rec_file = tmp_path / "recipients.txt"
    rec_file.write_text("age1one\nage1two\n", encoding="utf-8")
    monkeypatch.setenv("AGE_RECIPIENTS_FILE", str(rec_file))

    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/age" if name == "age" else None)

    captured_args = {}

    def fake_run(argv, check):  # type: ignore[no-untyped-def]
        captured_args["argv"] = list(argv)
        out = Path(argv[argv.index("-o") + 1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"enc")
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr("subprocess.run", fake_run)

    cli_mod._attempt_encrypted_backup(2025)

    files = list((tmp_path / "backups" / "2025").glob("*.tgz.age"))
    assert len(files) == 1
    argv = captured_args["argv"]
    # Should contain two -r entries for both recipients
    r_indices = [i for i, v in enumerate(argv) if v == "-r"]
    assert len(r_indices) == 2


def test_attempt_encrypted_backup_multiple_calls_unique(tmp_path, monkeypatch):
    # Prepare env and data
    monkeypatch.chdir(tmp_path)
    _write_dummy_data(tmp_path)
    monkeypatch.setenv("RAW_DATA_DIR", str(tmp_path / "data" / "raw"))
    monkeypatch.setenv("PROCESSED_DATA_DIR", str(tmp_path / "data" / "processed"))
    monkeypatch.setenv("AGE_RECIPIENT", "age1abc")
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/age" if name == "age" else None)

    # Fake datetime.now to produce deterministic, distinct stamps
    from datetime import datetime as _dt

    stamps = [
        _dt(2025, 1, 1, 12, 0, 0, 0),
        _dt(2025, 1, 1, 12, 0, 0, 1),
    ]

    class FakeDT:
        calls = -1

        @classmethod
        def now(cls):  # type: ignore[no-untyped-def]
            cls.calls += 1
            return stamps[min(cls.calls, len(stamps) - 1)]

    monkeypatch.setattr(cli_mod, "datetime", FakeDT)

    def fake_run(argv, check):  # type: ignore[no-untyped-def]
        out = Path(argv[argv.index("-o") + 1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"enc")
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr("subprocess.run", fake_run)

    cli_mod._attempt_encrypted_backup(2025)
    cli_mod._attempt_encrypted_backup(2025)

    files = sorted((tmp_path / "backups" / "2025").glob("*.tgz.age"))
    assert len(files) == 2
    assert files[0].name != files[1].name
