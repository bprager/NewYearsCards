# Output CSV Schema

The final CSV for mail‑merge contains one row per recipient.

## Columns

- `Prefix` – optional courtesy prefix
- `FirstName`
- `LastName`
- `Country`
- `Line1` … `Line5` – Address lines prepared for envelope printing

## Notes
- Empty lines are removed at generation time.
- Templates in `address_formats.yml` define the content of each line.
- The sheet downloader does not alter the raw data, all normalization happens in `addresses.py`.

