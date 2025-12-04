# Tasks

## Planned
- Add more country templates to `address_formats.yml`.
- Add validation for missing fields in the raw sheet.
- Add logging for download and processing steps.

## Backlog
- Generate a simple PDF preview for a few sample addresses.
- Add a command to list all countries present in the latest sheet.

## Done
- Basic CLI (`newyearscards`).
- Sheet download via service account into `data/raw/<year>/mailing_list.csv`.
- Address formatting pipeline to `data/processed/<year>/labels_for_mailmerge.csv`.
- `--dry-run` for `build-labels` (prints preview).

