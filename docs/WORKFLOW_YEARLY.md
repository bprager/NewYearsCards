Checklist

- Update `SHEET_URL` in `.env` (or pass `--url`).
- Run `newyearscards download --year <YYYY>`.
- Inspect `data/raw/<year>/mailing_list.csv` for obvious issues.
- Run `newyearscards build-labels --year <YYYY>`.
- In Pages/Word, attach `data/processed/<year>/labels_for_mailmerge.csv`.

Notes

- Ensure the service account has access to the Google Sheet.
- Address lines are controlled via `config/address_formats.yml`.

