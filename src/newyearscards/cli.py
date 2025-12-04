from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import load_paths, ensure_dir
from .addresses import build_labels


def cmd_download(args: argparse.Namespace) -> int:
    # Import lazily to avoid requiring google deps for other commands
    try:
        from .sheets import download_sheet  # type: ignore
    except Exception as e:
        print("Error: google auth dependencies are missing for download command", file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 2
    paths = load_paths()
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
    return 0


def cmd_build_labels(args: argparse.Namespace) -> int:
    paths = load_paths()

    if args.input:
        in_csv = Path(args.input)
    else:
        in_csv = paths.raw_dir(args.year) / "mailing_list.csv"

    if not in_csv.exists():
        print(f"Error: input CSV not found at {in_csv}", file=sys.stderr)
        return 2

    if args.dry_run:
        # Build to a temp path but don't persist
        try:
            out_path = build_labels(in_csv, out_csv=Path("/tmp/labels_for_mailmerge.csv"))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2
        # Show first few lines
        try:
            preview = out_path.read_text(encoding="utf-8").splitlines()[:6]
            print("\n".join(preview))
        except Exception:
            pass
        # Clean-up best-effort; okay to leave /tmp in some environments
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
    bl.add_argument("--input", help="Input raw CSV path (defaults to data/raw/<year>/mailing_list.csv)")
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
