#!/usr/bin/env python3
import os
import re
import sys
from urllib.parse import parse_qs, urlparse

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*_args, **_kwargs):  # type: ignore
        return False


KEY_PATH = "Keys/google-sheet-key.json"
OUTPUT_CSV = "sheet.csv"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def extract_ids(sheet_url: str) -> tuple[str, str]:
    """
    Extract spreadsheet id and gid (worksheet id) from a Google Sheets URL.
    If no gid is found, default to 0.
    """
    parsed = urlparse(sheet_url)

    # Spreadsheet id is in /spreadsheets/d/<id>/
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", parsed.path)
    if not match:
        raise ValueError("Could not extract spreadsheet id from SHEET_URL")

    spreadsheet_id = match.group(1)

    # gid is usually in the fragment, sometimes in query
    gid = "0"  # default to first sheet
    for part in (parsed.fragment, parsed.query):
        if part:
            qs = parse_qs(part)
            if "gid" in qs and qs["gid"]:
                gid = qs["gid"][0]
                break

    return spreadsheet_id, gid


def main() -> None:
    # Load SHEET_URL from .env
    load_dotenv()
    sheet_url = os.getenv("SHEET_URL")
    if not sheet_url:
        print("Error: SHEET_URL is not set in .env", file=sys.stderr)
        sys.exit(1)

    try:
        spreadsheet_id, gid = extract_ids(sheet_url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Load service account credentials
    if not os.path.exists(KEY_PATH):
        print(f"Error: key file not found at {KEY_PATH}", file=sys.stderr)
        sys.exit(1)

    # Lazy import Google libs so simply importing this module doesn't require them
    try:
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account
    except Exception as e:  # pragma: no cover
        print("Error: Google libraries are required for downloading the sheet.", file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)

    creds = service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
    authed_session = AuthorizedSession(creds)

    # Drive export endpoint for CSV
    export_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/export?format=csv&gid={gid}"
    )

    print(f"Downloading CSV from: {export_url}")
    resp = authed_session.get(export_url)
    resp.raise_for_status()

    with open(OUTPUT_CSV, "wb") as f:
        f.write(resp.content)

    print(f"Saved CSV to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
