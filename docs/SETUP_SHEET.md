Google Sheet Setup

Use these exact headers for the first row of your Google Sheet to ensure the CSV is recognized without manual mapping:

- Prefix
- First Name
- Last Name
- Address 1
- Address 2
- City
- State
- Zip Code
- Country

Sample rows

Example 1 — Germany

Prefix,First Name,Last Name,Address 1,Address 2,City,State,Zip Code,Country
Fam.,Frank,Prager,Satower Str. 26,,Stäbelow,,18198,Germany

Example 2 — United States (country line is omitted in labels by template)

Prefix,First Name,Last Name,Address 1,Address 2,City,State,Zip Code,Country
Mr.,John,Doe,123 Main St,Unit 5,Springfield,MA,01103,USA

Example 3 — Ukraine (city and ZIP may be merged during compaction)

Prefix,First Name,Last Name,Address 1,Address 2,City,State,Zip Code,Country
,Олександр,Шевченко,"вул. Хрещатик, 1",Кв. 5,Київ,,01001,Україна

Notes and recommendations

- Encoding: Use UTF-8. The tool and tests verify correct handling of Unicode (e.g., Київ).
- Normalization: Common variants like "Address1", "Postal Code", or "FirstName" are auto-normalized, but using the headers above is recommended and tested.
- Country names: Country drives the template. Aliases include:
  - Ukraine: "ukraine", "україна"
  - French Polynesia: "french polynesia", "polynésie française", "polynesie francaise", "pf"
  - United States: "united states", "usa", "us", "united states of america"
- Uppercasing: Many templates uppercase the last lines (e.g., city/country) per postal guidance; this is controlled by the YAML `uppercase_last_n_lines` in `config/address_formats.yml`.
- US template: The US template omits the country line when generating labels.
- Empty fields: Leave Address 2 blank if unused; the tool omits empty lines.

Running without install

- Download CSV from the configured Google Sheet:
  - python newyearscards download --year 2025
- Build labels from source CSV (no install, no PYTHONPATH needed):
  - python newyearscards build-labels --year 2025

See also

- README: Quick Start and Google Sheet Format
- docs/CI.md: CI and coverage setup
- config/address_formats.yml: Address line templates per country

