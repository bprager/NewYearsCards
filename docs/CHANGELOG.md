# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes.

## [1.1.5] - 2025-12-06

### Added
- Integrated Deptry into the development chain:
  - Added Deptry to dev extras and a `make deptry` target.
  - Included Deptry in `make check` and CI (runs after installing dev deps).

### Changed
- Removed unused runtime dependency `google-auth-httplib2` (was not imported).

### CI
- CI pipeline now runs Deptry to audit missing/obsolete dependencies.

## [1.1.4] - 2025-12-05

### Fixed
- Auto‑encrypted backup: resolve recipients (ENV or file) before creating any backup directories
  or temp files; provide clear skip messages when recipients are missing or `age` is not found.
- Ensures a backup is created for every successful `download` when properly configured.

### Tests
- Added unit test for missing `AGE_RECIPIENTS_FILE` path to ensure clean skip without creating
  `backups/<year>/`.

## [1.1.3] - 2025-12-05

### Added
- Country alias for Thailand in Thai script: `ประเทศไทย` → `TH`. Ensures Thai addresses use the `TH`
  template when users provide the country in Thai.

### Tests
- Added unit test for the Thai-script alias, confirming `ประเทศไทย` maps to `TH` and display name
  `Thailand`.

## [1.1.2] - 2025-12-05

### Added
- Address template for Thailand (`TH`), combining district/province (`state`), city, and ZIP into one line
  and uppercasing the last two lines per international addressing conventions.
- Country inference aliases for Thailand: `Thailand`, `TH`.

### Tests
- Unit tests covering Thailand formatting and country inference.

## [1.1.1] - 2025-12-05

### Fixed
- Ensure encrypted backup logic never creates `backups/<year>/` when encryption is disabled
  (no `AGE_RECIPIENT`/`AGE_RECIPIENTS_FILE`) or when `age` is not present.
- Kept `.env` loading strictly scoped to the current working directory to avoid
  test leakage and accidental env overrides.

### Internal
- Synced `__version__` with `pyproject.toml` to `1.1.1`.
- Minor test hardening and cleanup; all checks green.

## [1.1.0] - 2025-12-05

### Added
- Encrypted backups with age:
  - Auto‑backup runs after successful `download`, writing `.tgz.age` to `backups/<year>/`.
  - Unit tests for auto‑backup, including recipients file usage.
  - Make targets `age-backup` and `age-restore` for manual workflows.
- .env configuration for AGE_*:
  - `AGE_RECIPIENT` / `AGE_RECIPIENTS_FILE` for encryption; `AGE_IDENTITY` for restore.
  - Makefile now reads `.env` automatically; `age-backup` accepts recipients file without requiring single recipient.
- Documentation:
  - `docs/GOOGLE_AUTH.md` with service account setup and a “Test your setup” checklist.
  - README compacted; clear Google Sheet one‑line headers and US example; service‑account key emphasized with official link.

### Changed
- Auto‑backup destination from `backups/` to `backups/<year>/`.
- CLI loads `.env` before reading AGE_* for reliability; prints helpful skip notes when not configured.
- US country aliases expanded (US/USA/United States/U.S. map to `US`).

### Security
- `.gitignore` excludes `data/raw/`, `data/processed/`, and CSVs; plaintext address data stays out of the repo.
- `keys/*.agekey` ignored; only encrypted `.age` files are intended for storage/commit.

## [1.0.0] - 2025-12-04

This is the first complete, stable release.

### Added
- CI/CD hardening and coverage reporting:
  - GitHub Actions workflows for CI and Coverage with stage banners and strict gates.
  - Codecov integration with OIDC tokenless uploads (GitHub App) and a guarded token fallback on main.
  - Coverage thresholds: project 90%, patch 95%; pytest enforces `--cov-fail-under=90`.
- Developer experience:
  - Run from source without install or PYTHONPATH (top-level `newyearscards` launcher).
  - Makefile shortcuts: `check`, `coverage`, `run-download`, `run-build`.
  - Ruff and mypy configured; `make check` prints stage banners and runs lint, mypy, and tests.
  - `docs/CI.md` and `docs/SETUP_SHEET.md` with setup guidance and examples.
- Address formatting:
  - Template-driven uppercasing via `uppercase_last_n_lines` (e.g., FR, DE, UA).
  - Country aliases (Unicode-aware), including Ukraine and French Polynesia.
  - Fallback YAML parser for `address_formats.yml` if PyYAML is unavailable.

### Changed
- README restructured to emphasize no-install usage and correct CLI invocation (`python newyearscards ...`).
- Added explicit Google Sheet header template to README and docs to ensure a clean first-time setup.
- Type annotations improved (TypedDict for templates) and lint fixes across tests.

### Fixed
- CI badge and Codecov badge now reflect accurate status; private-repo badge uses tokenized URL.
- CLI and address tests expanded to push coverage well above 90% overall.

## [0.2.2] - 2025-12-04

### Added
- Developer launcher script `newyearscards` to run CLI without install or PYTHONPATH.
- Makefile targets `run-download` and `run-build` for no‑install usage.
- Ruff configured and added to `[project.optional-dependencies].dev`.

### Changed
- README clarified with correct command invocations:
  - Installed usage, from‑source `python newyearscards ...`, and `uv run` examples.
  - Highlighted `.env` configuration (SHEET_URL required; RAW/PROCESSED dir overrides; ADDRESS_TEMPLATES; SERVICE_ACCOUNT_KEY).
- Minor CLI cleanup and formatting, tests remain green.

## [0.2.1] - 2025-12-04

### Added
- Address templates and rules for international formatting:
  - New template `US` without a country line (domestic addressing).
  - New template `PF` (French Polynesia) with `zip city state` and country line.
  - New template `UA` and Unicode-aware country aliases (e.g., "україна").
- Configurable uppercasing via `uppercase_last_n_lines` in templates, applied to:
  - `FR`, `DE`, `UA` (uppercases the last two lines, e.g., city/zip and country).
  - `default` (uppercases the last line, typically the country).
- Unit tests covering:
  - UTF‑8 handling (Cyrillic for Ukraine) without ASCII coercion.
  - French zip+city uppercased per template.
  - Default template uppercasing only the country line.
  - US template omitting the country line; last line is `CITY STATE ZIP`.

### Changed
- Address processing now applies uppercasing based on template settings instead of hardcoding logic in Python.

## [0.2.0] - 2025-12-04

### Added
- Comprehensive unit tests covering address processing, Sheets URL parsing, and CLI.
- `--dry-run` for `build-labels` to preview output without writing files.
- Console script wiring in `pyproject.toml` (entry `newyearscards`).
- Core modules: `sheets.py`, `addresses.py`, and `config.py`.

### Changed
- Moved non-essential documentation into `docs/` and updated references in README.
- README and workflow documentation aligned with actual CLI behavior.
- Lazy-load Google auth in downloader to avoid unnecessary runtime deps for non-download commands.

## [0.1.0] - 2025-12-03

### Added
- Project directory restructuring for long-term maintainability.
- `data/raw/` and `data/processed/` folder structure for yearly input and output data.
- `templates/envelopes/` for reusable Pages and Word mail-merge templates.
- Config files to support developer and AI-assisted workflows:
  - `ARCHITECTURE.md`
  - `CODING_NOTES_FOR_AI.md`
  - `SCHEMA_LABELS.md`
  - `.env.example`
  - `TASKS.md`
- Initial `address_formats.yml` concept for per-country formatting rules.

### Notes
First functional milestone. Establishes the foundation for yearly maintenance and extensions.
