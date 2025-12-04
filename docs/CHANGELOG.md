# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_No changes yet._

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
