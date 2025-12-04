Google Service Account Setup

Follow these steps to allow the tool to download your Google Sheet as CSV using a service account.

What you need
- A Google Cloud project (free tier works)
- A service account with a JSON key file
- The service account email must have access to your Google Sheet

Steps
1) Create a service account and key
   - Guide: https://docs.cloud.google.com/iam/docs/keys-create-delete
   - Download the JSON key and save it locally.

2) Enable the Google Drive API for your project (recommended)
   - Visit Google Cloud Console → APIs & Services → Enable APIs and Services
   - Search for “Google Drive API” and enable it

3) Share the Sheet with the service account
   - Open your Google Sheet in the browser
   - Click Share and add the service account email (from the JSON key) with Viewer access

4) Point the app to your key and sheet
   - Copy `.env.example` to `.env`
   - Set:
     - `SHEET_URL="https://docs.google.com/spreadsheets/d/<id>/edit#gid=<gid>"`
     - Optionally set `SERVICE_ACCOUNT_KEY` (defaults to `Keys/google-sheet-key.json`)
   - Place the JSON key at that path

5) Test from source (no install)
   - Download: `python newyearscards download --year 2025`
   - Build: `python newyearscards build-labels --year 2025`

Scopes used
- The code requests the read-only Drive scope: `https://www.googleapis.com/auth/drive.readonly`
  This is sufficient to export the shared Sheet as CSV.

Security tips
- Keep the JSON key file out of source control
- Rotate or delete keys you don’t use (see the Google docs in step 1)
- Share the sheet only with the service account(s) you intend to use

