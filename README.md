# NewYearsCards

[![Version](docs/badges/version.svg)](https://github.com/bprager/NewYearsCards/releases)
![CI](https://github.com/bprager/NewYearsCards/actions/workflows/ci.yml/badge.svg)
[![Release](https://img.shields.io/github/v/release/bprager/NewYearsCards?display_name=tag&sort=semver)](https://github.com/bprager/NewYearsCards/releases)
![Coverage](https://github.com/bprager/NewYearsCards/actions/workflows/coverage.yml/badge.svg)
![Release Notes](https://github.com/bprager/NewYearsCards/actions/workflows/release-notes.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
[![codecov](https://codecov.io/gh/bprager/NewYearsCards/branch/main/graph/badge.svg?token=REPLACE_WITH_CODECOV_BADGE_TOKEN)](https://codecov.io/gh/bprager/NewYearsCards?token=REPLACE_WITH_CODECOV_BADGE_TOKEN)
![Ruff](https://img.shields.io/badge/ruff-checked-4B8BBE)
![mypy](https://img.shields.io/badge/mypy-checked-2A6DBB)

Prepare New Year’s card envelopes: download the Google Sheet, format addresses per country, export a mail‑merge CSV.

## Quick Start

1. Create a Google service account and download its JSON key. Save it to `Keys/google-sheet-key.json` (or point `SERVICE_ACCOUNT_KEY` to it). Do not commit this file. Setup guide: https://docs.cloud.google.com/iam/docs/keys-create-delete (see also docs/GOOGLE_AUTH.md)
2. Copy `.env.example` to `.env` and set variables.
   - Required:
     - `SHEET_URL="https://docs.google.com/spreadsheets/d/<id>/edit#gid=0"`
   - Optional:
     - `RAW_DATA_DIR` (default `data/raw`)
     - `PROCESSED_DATA_DIR` (default `data/processed`)
     - `ADDRESS_TEMPLATES` (default `config/address_formats.yml`)
     - `SERVICE_ACCOUNT_KEY` (default `Keys/google-sheet-key.json`)
   Tip: Share the Sheet with the service account’s email so it can read it.

Run from source (no install):
- Download: `python newyearscards download --year 2025`
- Build: `python newyearscards build-labels --year 2025`
  (use `uv run python ...` if you prefer uv)
  Note: after a successful download, an encrypted backup is created automatically when `AGE_RECIPIENT` or `AGE_RECIPIENTS_FILE` is set and `age` is installed.

Then, in Pages/Word, use a template from `templates/envelopes/`, and attach `data/processed/<year>/labels_for_mailmerge.csv` as the data source.

## Output CSV Schema

`Prefix,FirstName,LastName,Country,Line1,Line2,Line3,Line4,Line5`

Address lines are generated using templates in `config/address_formats.yml`. Empty components are omitted. See `docs/SCHEMA_LABELS.md` for more details.

## Google Sheet Format

Use this single header row to ensure automatic mapping:
`Prefix, First Name, Last Name, Address 1, Address 2, City, State, Zip Code, Country`

Example row (US):
`", Bernd, Prager, 504 S Sierra Bonita Ave, , Los Angeles, CA, 90036-3205, US"`

Notes:
- Common header variants (e.g., `FirstName`, `Postal Code`, `Address1`) are normalized, but the header row above is recommended.
- The `Country` column drives the template. Accepted US variants include `US`, `USA`, and `United States`; they are mapped to `US` internally.

For a fuller guide with sample rows and tips, see docs/SETUP_SHEET.md.

## Directories

- `data/raw/<year>/` – downloaded Google Sheet (`mailing_list.csv`)
- `data/processed/<year>/` – final CSV for mail merge (`labels_for_mailmerge.csv`)
- `config/` – configuration files such as `address_formats.yml`
- `templates/envelopes/` – reusable Pages and Word templates
- `src/newyearscards/` – CLI, sheet download, and address formatting logic
- `docs/` – detailed docs (architecture, workflow, changelog, tasks)

## Commands
- `python newyearscards download --year <YYYY> [--url <SHEET_URL>] [--out <file-or-dir>]`
- `python newyearscards build-labels [--year <YYYY>] [--input <raw.csv>] [--out <file-or-dir>] [--dry-run]`
Tip: Use `uv run python` to avoid installing dev tools locally. If `--url` is omitted, `SHEET_URL` from `.env` is used. Default paths are `data/raw/<year>/mailing_list.csv` and `data/processed/<year>/labels_for_mailmerge.csv`.

## Credentials

- Service account key: `Keys/google-sheet-key.json`
 - Create/manage keys: https://docs.cloud.google.com/iam/docs/keys-create-delete (more in docs/GOOGLE_AUTH.md)
- `.env`:
  - `SHEET_URL="https://docs.google.com/spreadsheets/d/<id>/edit#gid=0"`
  - Optional: `RAW_DATA_DIR`, `PROCESSED_DATA_DIR`, `ADDRESS_TEMPLATES`

## Contributing
- Install dev tools: `pip install -e .[dev]` (or `uv pip install -e .[dev]`)
- Tests: `pytest`
- Type-check: `mypy src/newyearscards` (or `uv run mypy src/newyearscards`)
- Dev help: `PYTHONPATH=src python -m newyearscards.cli --help`
Dev extra includes Ruff.

### Coverage
- `make coverage` (shows per-file, missing lines). CI enforces 90% overall and Codecov thresholds (project 90%, patch 95%).
Private repos: set the Codecov badge token in README (see docs/CI.md).

### Encrypted backups (age)
- Exclude plain CSVs from Git: `data/raw/`, `data/processed/` are ignored by default.
- Generate keys (once): `age-keygen -o Keys/backup.agekey && age-keygen -y Keys/backup.agekey`
  - Keep `Keys/backup.agekey` private; the `-y` output is your public recipient.
- Create backup: `make age-backup AGE_RECIPIENT='<age1...public-key>'`
  - Writes `backups/addresses-<timestamp>.tgz.age` (safe to commit/store)
- Restore backup: `make age-restore AGE_IDENTITY=Keys/backup.agekey ARGS='--input backups/addresses-....tgz.age --out-dir .'`
- More: see `scripts/age_backup.py` for options.

### Makefile shortcuts

- `make dev-install` – install dev extras (pytest, mypy)
- `make test` – run tests
- `make typecheck` – run mypy on source
- `make lint` – run Ruff if installed (optional)
- `make format` – run Ruff formatter if installed (optional)
- `make check` – typecheck + tests
