# NewYearsCards

![CI](https://github.com/bprager/NewYearsCards/actions/workflows/ci.yml/badge.svg)
[![Release](https://img.shields.io/github/v/release/bprager/NewYearsCards?display_name=tag&sort=semver)](https://github.com/bprager/NewYearsCards/releases)
![Coverage](https://github.com/bprager/NewYearsCards/actions/workflows/coverage.yml/badge.svg)
![Release Notes](https://github.com/bprager/NewYearsCards/actions/workflows/release-notes.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
[![codecov](https://codecov.io/gh/bprager/NewYearsCards/branch/main/graph/badge.svg?token=REPLACE_WITH_CODECOV_BADGE_TOKEN)](https://codecov.io/gh/bprager/NewYearsCards?token=REPLACE_WITH_CODECOV_BADGE_TOKEN)
![Ruff](https://img.shields.io/badge/ruff-checked-4B8BBE)
![mypy](https://img.shields.io/badge/mypy-checked-2A6DBB)

Annual workflow for preparing New Year’s card envelopes. Downloads the Google Sheets mailing list, formats addresses per country, and produces a mail‑merge CSV for Pages or Word.

## Quick Start

1. Copy `.env.example` to `.env` and set variables.
   - Required:
     - `SHEET_URL="https://docs.google.com/spreadsheets/d/<id>/edit#gid=0"`
   - Optional:
     - `RAW_DATA_DIR` (default `data/raw`)
     - `PROCESSED_DATA_DIR` (default `data/processed`)
     - `ADDRESS_TEMPLATES` (default `config/address_formats.yml`)
     - `SERVICE_ACCOUNT_KEY` (default `Keys/google-sheet-key.json`)
2. Place your Google service-account key at `Keys/google-sheet-key.json` (or point `SERVICE_ACCOUNT_KEY` to it). Do not commit this file.

Run from source (no install):
 
- From source (no install, no PYTHONPATH):
  - Download: `python newyearscards download --year 2025`
  - Build: `python newyearscards build-labels --year 2025`

- Using uv without install:
  - Download: `uv run python newyearscards download --year 2025`
  - Build: `uv run python newyearscards build-labels --year 2025`

Then, in Pages/Word, use a template from `templates/envelopes/`, and attach `data/processed/<year>/labels_for_mailmerge.csv` as the data source.

## Output CSV Schema

`Prefix,FirstName,LastName,Country,Line1,Line2,Line3,Line4,Line5`

Address lines are generated using templates in `config/address_formats.yml`. Empty components are omitted. See `docs/SCHEMA_LABELS.md` for more details.

## Google Sheet Format

Use the following header row in your Google Sheet so the CSV is recognized without extra mapping:

- `Prefix`
- `First Name`
- `Last Name`
- `Address 1`
- `Address 2`
- `City`
- `State`
- `Zip Code`
- `Country`

Notes:
- The tool normalizes common variants (e.g., `FirstName`, `Postal Code`, `Address1`) but the above headers are the recommended, tested defaults.
- The `Country` column drives template selection and formatting rules (uppercasing last lines, country-specific layouts, etc.).

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

Tip: Replace `python` with `uv run python` to avoid installing dev tools locally.

If `--url` is omitted, `SHEET_URL` from `.env` is used. If paths are omitted, defaults are `data/raw/<year>/mailing_list.csv` and `data/processed/<year>/labels_for_mailmerge.csv`.

## Credentials

- Service account key: `Keys/google-sheet-key.json`
- `.env`:
  - `SHEET_URL="https://docs.google.com/spreadsheets/d/<id>/edit#gid=0"`
  - Optional: `RAW_DATA_DIR`, `PROCESSED_DATA_DIR`, `ADDRESS_TEMPLATES`

## Contributing

- Install dev tools (pytest, mypy):
  - pip: `pip install -e .[dev]`
  - uv: `uv pip install -e .[dev]`
- Run tests:
  - `pytest`
- Type-check with mypy:
  - `mypy src/newyearscards`
  - or with uv: `uv run mypy src/newyearscards`
- Quick CLI help during development:
  - `PYTHONPATH=src python -m newyearscards.cli --help`
  
Note: The dev extra also installs Ruff for linting/formatting.

### Coverage

- Install dev extras first (includes `pytest-cov`):
  - `pip install -e .[dev]` or `uv pip install -e .[dev]`
- Run coverage locally:
  - `make coverage` (shows per-file, missing lines)
  - CI enforces `--cov-fail-under=90` and Codecov thresholds (project 90%, patch 95%).

Note for private repositories: the Codecov badge in this README uses the tokenized URL variant. Replace `REPLACE_WITH_CODECOV_BADGE_TOKEN` with the Badge token from Codecov project settings (Repository Settings → Badge). See docs/CI.md for details.

### Makefile shortcuts

- `make dev-install` – install dev extras (pytest, mypy)
- `make test` – run tests
- `make typecheck` – run mypy on source
- `make lint` – run Ruff if installed (optional)
- `make format` – run Ruff formatter if installed (optional)
- `make check` – typecheck + tests
