from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from app.core.db import fetch_all, get_settings
from app.core.metrics import (
    current_week,
    overall_progress,
    progress_by_phase,
    schedule_status,
    streaks,
    weekly_schedule,
)
from app.core.ui import connection, require_login, show_empty_hint

st.set_page_config(page_title="Dashboard", layout="wide")
require_login()
st.title("Dashboard")
db = connection()
settings = get_settings(db)
materials = fetch_all(db, "materi")
practices = fetch_all(db, "praktik")
logs = fetch_all(db, "log_harian")
today = date.today()
week_no = current_week(today, settings["start_date"])
target = float(settings["weekly_target_hours"]) * week_no
actual = sum(float(row.get("jam") or 0) for row in logs)
delta = actual - target
all_progress = overall_progress(materials, practices)
streak = streaks(logs, today)["saat_ini"]
cols = st.columns(7)
labels = [
    ("Minggu ke-", f"{week_no} / 52"),
    ("Total jam aktual", f"{actual:g}"),
    ("Target s/d sekarang", f"{target:g}"),
    ("Selisih", f"{delta:+g}"),
    ("Status jadwal", schedule_status(week_no, actual, target)),
    ("Progres keseluruhan", f"{all_progress:.0%}"),
    ("Streak saat ini", str(streak)),
]
for col, (label, value) in zip(cols, labels):
    col.metric(label, value)

phase = progress_by_phase(materials, practices)
phase_frame = pd.DataFrame(phase)
left, right = st.columns(2)
with left:
    st.subheader("Progres per fase")
    if phase_frame.empty:
        st.info("Belum ada data fase.")
    else:
        chart = px.bar(phase_frame, x="nama", y="gabungan", range_y=[0, 1], labels={
            "nama": "Fase", "gabungan": "Progres gabungan",
        })
        st.plotly_chart(chart, width="stretch")
        st.dataframe(
            phase_frame.rename(columns={
                "nama": "Fase", "materi": "% Materi", "praktik": "% Praktik",
                "gabungan": "% Gabungan",
            }),
            width="stretch",
            hide_index=True,
            column_config={
                "% Materi": st.column_config.NumberColumn(format="percent"),
                "% Praktik": st.column_config.NumberColumn(format="percent"),
                "% Gabungan": st.column_config.NumberColumn(format="percent"),
            },
        )
with right:
    st.subheader("Progres per jalur spesialisasi")
    paths = pd.DataFrame(progress_by_phase(materials, practices, paths=True))
    if paths.empty:
        st.info("Belum ada data kategori Jalur A–D.")
    else:
        st.dataframe(paths, width="stretch", hide_index=True)

st.subheader("Jam belajar mingguan")
weeks = weekly_schedule(
    settings["start_date"], float(settings["weekly_target_hours"]), logs,
    fetch_all(db, "jadwal"), today,
)
week_frame = pd.DataFrame(weeks)
chart_data = week_frame.melt(
    id_vars=["minggu"], value_vars=["jam_aktual", "jam_target"],
    var_name="jenis", value_name="jam",
)
chart = px.line(chart_data, x="minggu", y="jam", color="jenis", markers=True)
chart.update_layout(xaxis_title="Minggu", yaxis_title="Jam")
st.plotly_chart(chart, width="stretch")
show_empty_hint(db)
