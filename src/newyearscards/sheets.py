from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover

    def load_dotenv(*_args, **_kwargs):  # type: ignore
        return False


from .config import load_paths, ensure_dir


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def extract_ids(sheet_url: str) -> Tuple[str, str]:
    """
    Extract spreadsheet id and gid (worksheet id) from a Google Sheets URL.
    If no gid is found, default to "0".
    """
    parsed = urlparse(sheet_url)

    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", parsed.path)
    if not match:
        raise ValueError("Could not extract spreadsheet id from SHEET_URL")

    spreadsheet_id = match.group(1)

    gid = "0"
    for part in (parsed.fragment, parsed.query):
        if part:
            qs = parse_qs(part)
            if "gid" in qs and qs["gid"]:
                gid = qs["gid"][0]
                break

    return spreadsheet_id, gid


def download_sheet(
    year: int, *, sheet_url: Optional[str] = None, out_path: Optional[Path] = None
) -> Path:
    """
    Download the specified Google Sheet as CSV via service-account credentials.
    Saves to data/raw/<year>/mailing_list.csv by default.
    """
    load_dotenv()
    paths = load_paths()

    if not sheet_url:
        sheet_url = os.getenv("SHEET_URL")
    if not sheet_url:
        raise RuntimeError("SHEET_URL is not set (provide --url or set in .env)")

    spreadsheet_id, gid = extract_ids(sheet_url)

    # Import heavy google deps lazily to keep module import light for tests
    from google.oauth2 import service_account  # type: ignore
    from google.auth.transport.requests import AuthorizedSession  # type: ignore

    key_path = paths.key_path
    if not key_path.exists():
        raise FileNotFoundError(f"Service account key not found at {key_path}")

    creds = service_account.Credentials.from_service_account_file(
        str(key_path), scopes=SCOPES
    )
    authed_session = AuthorizedSession(creds)

    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"

    resp = authed_session.get(export_url, timeout=30)
    resp.raise_for_status()

    if out_path is None:
        target_dir = paths.raw_dir(year)
        ensure_dir(target_dir)
        out_path = target_dir / "mailing_list.csv"
    else:
        ensure_dir(out_path.parent)

    out_path.write_bytes(resp.content)
    return out_path
