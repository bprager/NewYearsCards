# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_No changes yet._

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
