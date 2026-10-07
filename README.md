# Cybersec Journey Tracker

A local, single-user Streamlit app for tracking a 52-week cybersecurity learning plan. It stores data in SQLite and works offline.

## Run locally

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app/main.py
```

The database is created automatically at `data/tracker.db`. Start date and weekly target default to 5 October 2026 and 12 hours and can be changed on the Pengaturan page. When the database is empty, use that page to import the workbook.

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

- The app is for one local user and has no login, external API, network scanning, or deployment functionality.
- Only one daily log is stored per date. Saving that date replaces its current record.
- Weekly target hours come from Settings; imported calculated schedule values are intentionally ignored.
- An absent optional sheet is skipped during import, while a workbook with no recognized sheets is rejected.
- Percentages with no active items are zero. A record direction is compared strictly, so matching its previous value is not a new record.
