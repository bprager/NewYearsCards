Here is a tightened, clean, single-page README.
Everything essential, nothing extra.

---

````markdown
# NewYearsCards

Annual workflow for preparing New Year’s card envelopes.
Downloads the Google Sheets mailing list, formats addresses per country, and
produces a mail-merge CSV for Pages or Word.

---

## Workflow

1. Set `SHEET_URL` in `.env`.
2. Download the mailing list:

   ```bash
   newyearscards download --year 2025
````

3. Build the processed label CSV:

   ```bash
   newyearscards build-labels --year 2025
   ```

4. Open a template from `templates/envelopes/` (Pages or Word).

5. Attach `data/processed/<year>/labels_for_mailmerge.csv`.

6. Export final envelopes into `cards/<year>/outputs/`.

---

## Output CSV Format

```
Prefix,FirstName,LastName,Country,Line1,Line2,Line3,Line4,Line5
```

Address lines are generated using templates in `config/address_formats.yml`.

---

## Directory Highlights

* `data/raw/<year>/` – downloaded Google Sheet
* `data/processed/<year>/` – final CSV for mail merge
* `templates/envelopes/` – reusable Pages and Word templates
* `src/newyearscards/` – CLI, sheet download, and address formatting logic

---

## Credentials

Google service-account key:

```
Keys/google-sheet-key.json
```

`.env`:

```
SHEET_URL="<google-sheets-url>"
```

---

