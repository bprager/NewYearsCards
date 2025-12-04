# Coding Notes for AI Helpers

## General
Keep code simple and direct. Avoid unnecessary abstractions.
Use Python 3.12 and the standard library whenever possible.

## Style
- Small focused functions.
- Keep modules short and purpose driven.
- Prefer explicit paths (no magic).
- Do not add dependencies unless really needed.

## Tooling
- Project uses `uv` for dependency management.
- CLI entry point is `newyearscards` (exposed via `cli.py`).

## Functionality Rules
- All downloads go to `data/raw/<year>/`.
- All processed files go to `data/processed/<year>/`.
- Address formatting must respect the templates in `config/address_formats.yml`.
- Empty address components should be omitted in final lines.

## Safety
- Do not commit credentials.
- Never modify original raw CSVs, only produce new processed files.

