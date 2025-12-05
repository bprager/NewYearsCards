#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile


def tar_sources(sources: list[Path], out_tar_gz: Path) -> None:
    with tarfile.open(out_tar_gz, "w:gz") as tar:
        for src in sources:
            tar.add(src, arcname=src.name)


def run_age_encrypt(in_file: Path, out_file: Path, recipients: list[str]) -> None:
    cmd = [
        "age",
        *(sum([["-r", r] for r in recipients], [])),
        "-o",
        str(out_file),
        str(in_file),
    ]
    subprocess.run(cmd, check=True)


def run_age_decrypt(in_file: Path, out_file: Path, identity: Path) -> None:
    cmd = [
        "age",
        "-d",
        "-i",
        str(identity),
        "-o",
        str(out_file),
        str(in_file),
    ]
    subprocess.run(cmd, check=True)


def backup(args: argparse.Namespace) -> int:
    raw_dir = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
    processed_dir = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed"))
    backup_dir = Path(args.out_dir or "backups")

    sources = [p for p in [raw_dir, processed_dir] if p.exists()]
    if not sources:
        print("No sources found to back up (data/raw, data/processed)", file=sys.stderr)
        return 2

    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    tmp_tar = backup_dir / f"addresses-{stamp}.tgz"
    out_age = backup_dir / f"addresses-{stamp}.tgz.age"

    tar_sources(sources, tmp_tar)

    rec = args.recipient or os.getenv("AGE_RECIPIENT")
    rec_file = args.recipients_file or os.getenv("AGE_RECIPIENTS_FILE")
    recipients: list[str] = []
    if rec:
        recipients.append(rec)
    if rec_file:
        for line in Path(rec_file).read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s:
                recipients.append(s)
    if not recipients:
        print(
            "Missing recipients. Set --recipient or --recipients-file (or AGE_RECIPIENT / AGE_RECIPIENTS_FILE)",
            file=sys.stderr,
        )
        tmp_tar.unlink(missing_ok=True)
        return 2

    try:
        run_age_encrypt(tmp_tar, out_age, recipients)
    finally:
        tmp_tar.unlink(missing_ok=True)

    print(f"Wrote encrypted backup: {out_age}")
    return 0


def restore(args: argparse.Namespace) -> int:
    in_age = Path(args.input)
    if not in_age.exists():
        print(f"Input not found: {in_age}", file=sys.stderr)
        return 2

    identity = Path(args.identity or os.getenv("AGE_IDENTITY", ""))
    if not identity.exists():
        print("Missing identity. Provide --identity or set AGE_IDENTITY", file=sys.stderr)
        return 2

    tmp_tar = in_age.with_suffix("")  # strip .age
    run_age_decrypt(in_age, tmp_tar, identity)

    target_base = Path(args.out_dir or ".")
    with tarfile.open(tmp_tar, "r:gz") as tar:
        tar.extractall(path=target_base)
    tmp_tar.unlink(missing_ok=True)
    print(f"Restored into: {target_base.resolve()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Encrypted backup/restore of address data via age")
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("backup", help="Create encrypted backup of data/raw and data/processed")
    pb.add_argument("--out-dir", help="Output directory for .age file (default: backups)")
    pb.add_argument("--recipient", help="age recipient (public key)")
    pb.add_argument("--recipients-file", help="File with one recipient per line")
    pb.set_defaults(func=backup)

    pr = sub.add_parser("restore", help="Restore an encrypted backup to the current directory")
    pr.add_argument("--input", required=True, help="Path to .age file")
    pr.add_argument("--identity", help="age identity (private key) file path")
    pr.add_argument("--out-dir", help="Directory to extract into (default: current directory)")
    pr.set_defaults(func=restore)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

