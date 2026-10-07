from datetime import date

import streamlit as st

from app.core.constants import TABLE_COLUMNS
from app.core.db import connect, get_settings, set_setting
from app.core.exporter import export_csv, export_excel
from app.core.importer import import_workbook
from app.core.ui import require_login

st.set_page_config(page_title="Pengaturan", layout="wide")
require_login()
st.title("Pengaturan")
db = connect()
settings = get_settings(db)
st.subheader("Pengaturan perjalanan")
with st.form("settings"):
    start = st.date_input(
        "Tanggal mulai", date.fromisoformat(settings["start_date"]), format="DD/MM/YYYY"
    )
    target = st.number_input(
        "Target jam per minggu", min_value=0.0, value=float(settings["weekly_target_hours"]),
        step=0.5,
    )
    if st.form_submit_button("Simpan pengaturan"):
        set_setting(db, "start_date", start.isoformat())
        set_setting(db, "weekly_target_hours", str(target))
        st.success("Pengaturan disimpan.")
        st.rerun()

st.subheader("Impor workbook")
uploaded = st.file_uploader("Pilih file Excel (.xlsx)", type=["xlsx"])
if st.button("Impor", disabled=uploaded is None):
    try:
        counts = import_workbook(uploaded, db)
    except (ValueError, OSError, KeyError) as error:
        st.error(f"Impor gagal: {error}")
    else:
        st.success("Impor selesai. Baris yang diproses:")
        st.dataframe(
            [{"Sheet": sheet, "Baris": count} for sheet, count in counts.items()],
            hide_index=True,
        )

st.subheader("Ekspor cadangan")
st.download_button(
    "Ekspor Excel", data=export_excel(db),
    file_name="cybersec-journey-backup.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
st.caption("Ekspor CSV per tabel")
for table in TABLE_COLUMNS:
    st.download_button(
        f"Unduh {table}.csv", data=export_csv(db, table), file_name=f"{table}.csv",
        mime="text/csv", key=f"csv_{table}",
    )
