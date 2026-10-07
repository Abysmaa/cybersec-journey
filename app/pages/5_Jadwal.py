import pandas as pd
import streamlit as st

from app.core.db import fetch_all, get_settings, upsert_rows
from app.core.metrics import current_week, weekly_schedule
from app.core.ui import connection, require_login

st.set_page_config(page_title="Jadwal", layout="wide")
require_login()
st.title("Jadwal Mingguan")
db = connection()
settings = get_settings(db)
today = pd.Timestamp.now().date()
rows = weekly_schedule(
    settings["start_date"], float(settings["weekly_target_hours"]),
    fetch_all(db, "log_harian"), fetch_all(db, "jadwal"), today,
)
frame = pd.DataFrame(rows)
frame["sekarang"] = frame["minggu"] == current_week(today, settings["start_date"])
def highlight_week(row):
    if row["sekarang"]:
        return ["background-color: #fff3cd"] * len(row)
    return [""] * len(row)


styled = frame.style.apply(highlight_week, axis=1).map(
    lambda value: {
        "Tercapai": "color: #198754; font-weight: bold",
        "Tidak tercapai": "color: #dc3545; font-weight: bold",
        "Berjalan": "color: #0d6efd; font-weight: bold",
        "Akan datang": "color: #6c757d",
    }.get(value, ""),
    subset=["status"],
)
st.dataframe(
    styled,
    width="stretch",
    hide_index=True,
    column_config={
        "capaian": st.column_config.ProgressColumn("Capaian", min_value=0, max_value=1),
        "sekarang": st.column_config.CheckboxColumn("Minggu sekarang"),
        "mulai": st.column_config.DateColumn("Mulai", format="DD-MMM-YYYY", disabled=True),
        "selesai": st.column_config.DateColumn("Selesai", format="DD-MMM-YYYY", disabled=True),
    },
)
edited = st.data_editor(
    frame[["minggu", "fase", "fokus_materi", "praktik_utama", "refleksi"]],
    key="schedule_editor",
    width="stretch",
    hide_index=True,
    disabled=["minggu"],
    num_rows="fixed",
)
if st.button("Simpan fokus dan refleksi"):
    upsert_rows(db, "jadwal", edited.to_dict(orient="records"))
    st.success("Jadwal diperbarui.")
    st.rerun()
