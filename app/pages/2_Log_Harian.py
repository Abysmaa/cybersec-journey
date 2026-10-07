from datetime import date

import pandas as pd
import streamlit as st

from app.core.db import fetch_all, upsert_rows
from app.core.metrics import streaks
from app.core.ui import connection, date_input, editable_table

st.set_page_config(page_title="Log Harian", layout="wide")
st.title("Log Harian")
db = connection()
logs = fetch_all(db, "log_harian")
st.metric("Streak saat ini", streaks(logs)["saat_ini"])
refs = [""]
for table in ("materi", "praktik"):
    refs.extend(row["id"] for row in fetch_all(db, table) if row.get("id"))

with st.form("daily_log_form"):
    day = date_input("Tanggal", date.today(), "log_date")
    hours = st.number_input("Jam belajar", min_value=0.0, max_value=24.0, step=0.5)
    activity = st.text_input("Aktivitas / Topik")
    platform = st.text_input("Platform")
    reference = st.selectbox("ID Materi/Praktik (opsional)", refs)
    energy = st.selectbox("Energi (1-5)", [None, 1, 2, 3, 4, 5], index=0)
    note = st.text_area("Catatan")
    duplicate = next((row for row in logs if str(row["tanggal"])[:10] == day.isoformat()), None)
    replace_existing = st.checkbox(
        f"Tanggal sudah memiliki log ({duplicate['jam']} jam); perbarui log itu"
        if duplicate else "Simpan log untuk tanggal ini"
    )
    submitted = st.form_submit_button("Simpan log")
    if submitted:
        if duplicate and not replace_existing:
            st.error("Tanggal tersebut sudah memiliki log. Pilih konfirmasi pembaruan.")
        else:
            upsert_rows(db, "log_harian", [{
                "tanggal": day.isoformat(), "jam": hours, "aktivitas": activity or None,
                "platform": platform or None, "ref_id": reference or None,
                "energi": energy, "catatan": note or None,
            }])
            st.success("Log harian tersimpan.")
            st.rerun()

st.subheader("Riwayat")
if logs:
    frame = pd.DataFrame(fetch_all(db, "log_harian"))
    editable_table(db, "log_harian", frame, "daily_history")
else:
    st.info("Belum ada log harian.")
