# Architecture Overview

This project manages New Year’s card assets and produces a yearly mail‑merge CSV from a Google Sheets mailing list.

## Modules

### `sheets.py`
Handles downloading the Google Sheet via service‑account credentials.
Writes to `data/raw/<year>/mailing_list.csv`.

### `addresses.py`
Loads `config/address_formats.yml`.
Builds per‑country address lines and outputs `labels_for_mailmerge.csv`.

### `cli.py`
Provides two commands:
- `download` (fetch and store the raw sheet)
- `build-labels` (generate the processed CSV)

### `config.py`
Loads `.env` and resolves paths for data folders.

## Data Flow

Google Sheet → `data/raw/<year>/mailing_list.csv`
Raw CSV → `addresses.py` → `data/processed/<year>/labels_for_mailmerge.csv`

