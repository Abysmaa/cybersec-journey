from datetime import date

import streamlit as st

from app.core.db import connect, fetch_all, get_settings
from app.core.metrics import current_week, streaks
from app.core.ui import require_login

st.set_page_config(page_title="Cybersec Journey Tracker", page_icon="🛡️", layout="wide")
require_login()

db = connect()
settings = get_settings(db)
logs = fetch_all(db, "log_harian")
week = current_week(date.today(), settings["start_date"])
progress = streaks(logs)

st.title("Cybersec Journey Tracker")
st.caption("Catat perjalanan belajar keamanan siber selama 52 minggu.")
first, second, third = st.columns(3)
first.metric("Minggu sekarang", f"{week} / 52")
second.metric("Jam belajar tercatat", f"{sum(float(row['jam']) for row in logs):g}")
third.metric("Streak saat ini", progress["saat_ini"])

if not fetch_all(db, "materi") and not fetch_all(db, "praktik"):
    st.info("Mulai dengan mengimpor workbook dari halaman Pengaturan.")
else:
    st.success("Data belajar siap. Buka Dashboard untuk melihat progres lengkap.")

st.markdown("Gunakan navigasi halaman di sisi kiri untuk mencatat aktivitas dan melihat progres.")
