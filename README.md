# Cybersec Journey Tracker

A Streamlit app for tracking a 52-week cybersecurity learning plan. It uses SQLite and supports private, single-user access behind Google OpenID Connect (OIDC).

## Run locally

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:CYBERSEC_LOCAL_DEV = "1"
streamlit run app/main.py
```

`CYBERSEC_LOCAL_DEV=1` disables login only for local development. Never set it in Streamlit Community Cloud. Without valid OIDC and allowlist secrets, the app fails closed and does not open the database.

The database is created automatically at `data/tracker.db`. Start date and weekly target default to 5 October 2026 and 12 hours and can be changed on the Pengaturan page.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub, sign in to [Streamlit Community Cloud](https://share.streamlit.io/), and deploy the `main` branch with `app/main.py`. The app remains locked until authentication is configured.
2. Note the app URL assigned by Streamlit, then create a Google OAuth 2.0 **Web application** client in Google Cloud Console. Add the app URL as an authorized JavaScript origin, and add `<APP-URL>/oauth2callback` as an authorized redirect URI.
3. In the app's **Settings → Secrets**, copy `.streamlit/secrets.toml.example`, replace every placeholder, and set `tracker.allowed_emails` to the exact Google account email(s) that may access the tracker.
4. Save the secrets and restart/reboot the app. Verify the login screen, an allowlisted account, and a non-allowlisted account before sharing the public URL.

Keep the OAuth client secret and `cookie_secret` only in the hosting platform's Secrets configuration. Do not commit `.streamlit/secrets.toml`; it is gitignored. OIDC identifies users, while the app's email allowlist controls who can access the data.

**Storage warning:** Community Cloud's local filesystem is not a durable database service. The app currently uses a local SQLite file, so data can be lost when the app is restarted, rebuilt, or moved. Export backups regularly from Pengaturan. For durable private data, use a persistent database before relying on the public deployment.

## Import and backup

Upload the source `.xlsx` workbook from Pengaturan. The importer reads sheet headers from row 4, recalculates derived values at runtime, and upserts rows by their stable ID (or by date for daily logs). Run an import again safely to refresh the same records. The original workbook is not included in this repository; provide it locally to import its learning-plan data.

Export individual tables as CSV or download a complete Excel workbook from Pengaturan. The local SQLite database, uploaded workbook, and exports are not intended for Git.

## Pages

- Beranda and Dashboard: current-week summary, progress by phase and specialization path, and weekly hours chart.
- Log Harian: daily study entry, streak, and editable history.
- Materi and Praktik: editable progress tables, bulk status changes, and new items.
- Jadwal: 52 calculated weeks and editable weekly notes.
- Personal Best: automatic metrics and manual records.
- Sertifikasi and Portofolio: editable tracking tables.
- Pengaturan: start date, weekly target, workbook import, and exports.

## Tests and lint

```powershell
python -m pytest
ruff check .
```

## Assumptions

- One local user is the default; OIDC and an explicit email allowlist are required before public deployment.
- Only one daily log is stored per date. Saving that date replaces its current record.
- Weekly target hours come from Settings; imported calculated schedule values are intentionally ignored.
- An absent optional sheet is skipped during import, while a workbook with no recognized sheets is rejected.
- Percentages with no active items are zero. A record direction is compared strictly, so matching its previous value is not a new record.
