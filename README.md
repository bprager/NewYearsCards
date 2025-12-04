# NewYearsCards

Annual workflow for preparing New Year’s card envelopes. Downloads the Google Sheets mailing list, formats addresses per country, and produces a mail‑merge CSV for Pages or Word.

## Installation

- Runtime only:
  - pip: `pip install -e .`
  - uv: `uv pip install -e .`
- Development (adds pytest, mypy):
  - pip: `pip install -e .[dev]`
  - uv: `uv pip install -e .[dev]`

## Quick Start

1. Copy `.env.example` to `.env` and set `SHEET_URL`.
2. Place your Google service-account key at `Keys/google-sheet-key.json` (not committed).
3. Download the mailing list CSV:
   
   `newyearscards download --year 2025`

4. Build the processed labels CSV:
   
   `newyearscards build-labels --year 2025`

5. In Pages/Word, use a template from `templates/envelopes/`, and attach `data/processed/<year>/labels_for_mailmerge.csv` as the data source.

## Output CSV Schema

`Prefix,FirstName,LastName,Country,Line1,Line2,Line3,Line4,Line5`

Address lines are generated using templates in `config/address_formats.yml`. Empty components are omitted. See `docs/SCHEMA_LABELS.md` for more details.

## Directories

- `data/raw/<year>/` – downloaded Google Sheet (`mailing_list.csv`)
- `data/processed/<year>/` – final CSV for mail merge (`labels_for_mailmerge.csv`)
- `config/` – configuration files such as `address_formats.yml`
- `templates/envelopes/` – reusable Pages and Word templates
- `src/newyearscards/` – CLI, sheet download, and address formatting logic
- `docs/` – detailed docs (architecture, workflow, changelog, tasks)

## Commands

- `newyearscards download --year <YYYY> [--url <SHEET_URL>] [--out <file-or-dir>]`
- `newyearscards build-labels [--year <YYYY>] [--input <raw.csv>] [--out <file-or-dir>] [--dry-run]`

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

### Makefile shortcuts

- `make dev-install` – install dev extras (pytest, mypy)
- `make test` – run tests
- `make typecheck` – run mypy on source
- `make lint` – run Ruff if installed (optional)
- `make format` – run Ruff formatter if installed (optional)
- `make check` – typecheck + tests
