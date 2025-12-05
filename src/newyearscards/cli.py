from __future__ import annotations

import argparse
from contextlib import suppress
from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

from . import __version__
from .addresses import build_labels
from .config import ensure_dir, load_paths

# Best-effort .env loading (keep optional like in sheets.py)
try:  # pragma: no cover - trivial import
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        return False


def cmd_download(args: argparse.Namespace) -> int:
    """Download the Google Sheet into data/raw/<year>/mailing_list.csv.

    Imports the google client lazily so other commands don't need those deps.
    """
    try:
        from .sheets import download_sheet
    except Exception as e:
        print(
            "Error: google auth dependencies are missing for download command",
            file=sys.stderr,
        )
        print(str(e), file=sys.stderr)
        return 2

    out_path: Path | None = None
    if args.out:
        out = Path(args.out)
        if out.suffix.lower() == ".csv":
            out_path = out
        else:
            ensure_dir(out)
            out_path = out / "mailing_list.csv"
    try:
        path = download_sheet(args.year, sheet_url=args.url, out_path=out_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    print(f"Saved CSV to {path}")
    _attempt_encrypted_backup(args.year)
    return 0


def _attempt_encrypted_backup(year: int | None = None) -> None:
    """Create an encrypted backup with age, if configured.

    Looks for AGE_RECIPIENT or AGE_RECIPIENTS_FILE and the `age` executable.
    Archives data/raw and data/processed (if present) into backups/*.tgz.age.
    Never raises; prints a short status message on success or skip.
    """
    # Load .env so local AGE_* vars are available
    load_dotenv()

    # Ensure age is available and recipients configured
    recipient = os.getenv("AGE_RECIPIENT")
    recipients_file = os.getenv("AGE_RECIPIENTS_FILE")
    if not (recipient or recipients_file):
        print(
            "Note: skipping encrypted backup; set AGE_RECIPIENT or AGE_RECIPIENTS_FILE to enable.",
            file=sys.stderr,
        )
        return
    if shutil.which("age") is None:
        print("Note: 'age' not found in PATH; skipping encrypted backup.", file=sys.stderr)
        return

    raw_dir = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
    processed_dir = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed"))
    sources = [p for p in (raw_dir, processed_dir) if p.exists()]
    if not sources:
        return

    backups_dir = Path("backups") / (str(year) if year is not None else "")
    ensure_dir(backups_dir)

    # Include microseconds to avoid collisions on rapid consecutive invocations
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    tmp_tar = backups_dir / f"addresses-{stamp}.tgz"
    out_age = backups_dir / f"addresses-{stamp}.tgz.age"

    try:
        with tarfile.open(tmp_tar, "w:gz") as tar:
            for src in sources:
                tar.add(src, arcname=src.name)

        # Build recipients
        rec_args: list[str] = []
        if recipient:
            rec_args += ["-r", recipient]
        if recipients_file and Path(recipients_file).exists():
            for line in Path(recipients_file).read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if s:
                    rec_args += ["-r", s]
        if not rec_args:
            return

        cmd = ["age", *rec_args, "-o", str(out_age), str(tmp_tar)]
        subprocess.run(cmd, check=True)
        print(f"Encrypted backup: {out_age}")
    except Exception as e:  # pragma: no cover - best-effort
        print(f"Note: encrypted backup failed: {e}", file=sys.stderr)
    finally:
        with suppress(Exception):
            tmp_tar.unlink(missing_ok=True)


def cmd_build_labels(args: argparse.Namespace) -> int:
    paths = load_paths()

    if args.input:
        in_csv = Path(args.input)
    else:
        if args.year is None:
            print(
                "Error: --year is required when --input is not provided",
                file=sys.stderr,
            )
            return 2
        in_csv = paths.raw_dir(args.year) / "mailing_list.csv"

    if not in_csv.exists():
        print(f"Error: input CSV not found at {in_csv}", file=sys.stderr)
        return 2

    if args.dry_run:
        # Build to a temp path but don't persist
        try:
            temp_dir = Path(tempfile.gettempdir())
            out_path = build_labels(in_csv, out_csv=temp_dir / "labels_for_mailmerge.csv")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2
        # Show first few lines
        try:
            preview = out_path.read_text(encoding="utf-8").splitlines()[:6]
            print("\n".join(preview))
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: unable to show dry-run preview: {e}", file=sys.stderr)
        finally:
            try:
                out_path.unlink()
            except FileNotFoundError:
                pass
            except OSError as e:
                print(
                    f"Warning: could not delete temporary preview file {out_path}: {e}",
                    file=sys.stderr,
                )
        return 0

    if args.out:
        out_arg = Path(args.out)
        if out_arg.suffix.lower() == ".csv":
            out_csv = out_arg
        else:
            ensure_dir(out_arg)
            out_csv = out_arg / "labels_for_mailmerge.csv"
    else:
        out_csv = None

    try:
        of = build_labels(in_csv, out_csv=out_csv)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    print(f"Wrote labels CSV: {of}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="newyearscards", description="New Year’s cards workflow")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sp = p.add_subparsers(dest="command", required=True)

    dl = sp.add_parser("download", help="Download mailing list CSV from Google Sheets")
    dl.add_argument("--year", type=int, required=True, help="Target year")
    dl.add_argument("--url", help="Google Sheet URL (defaults to SHEET_URL from .env)")
    dl.add_argument("--out", help="Output file or directory (defaults to data/raw/<year>/)")
    dl.set_defaults(func=cmd_download)

    bl = sp.add_parser("build-labels", help="Build processed labels CSV for mail merge")
    bl.add_argument("--year", type=int, required=False, help="Year (used to infer default paths)")
    bl.add_argument(
        "--input",
        help="Input raw CSV path (defaults to data/raw/<year>/mailing_list.csv)",
    )
    bl.add_argument("--out", help="Output file or directory (defaults to data/processed/<year>/)")
    bl.add_argument("--dry-run", action="store_true", help="Preview output to stdout, do not write")
    bl.set_defaults(func=cmd_build_labels)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
