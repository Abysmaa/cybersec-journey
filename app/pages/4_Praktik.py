import streamlit as st

from app.core.constants import PHASES, PRACTICE_LEVELS, PRACTICE_STATUSES
from app.core.db import fetch_all, upsert_rows
from app.core.ui import connection, editable_table, load_frame, require_login, show_empty_hint

st.set_page_config(page_title="Praktik", layout="wide")
require_login()
st.title("Praktik / Lab")
db = connection()
rows = fetch_all(db, "praktik")
phase_filter = st.selectbox("Filter fase", ["Semua"] + PHASES)
categories = sorted({str(row.get("kategori") or "") for row in rows if row.get("kategori")})
category_filter = st.selectbox("Filter kategori", ["Semua"] + categories)
status_filter = st.selectbox("Filter status", ["Semua"] + PRACTICE_STATUSES)
weeks = sorted({int(row["minggu_target"]) for row in rows if row.get("minggu_target")})
week_filter = st.selectbox("Filter minggu target", ["Semua"] + weeks)
frame = load_frame(db, "praktik")
if phase_filter != "Semua":
    frame = frame[frame["fase"] == phase_filter]
if status_filter != "Semua":
    frame = frame[frame["status"] == status_filter]
if category_filter != "Semua":
    frame = frame[frame["kategori"] == category_filter]
if week_filter != "Semua":
    frame = frame[frame["minggu_target"] == week_filter]
editable_table(db, "praktik", frame, "practices")

with st.expander("Ubah status massal"):
    categories = sorted({str(row.get("kategori") or "") for row in rows}) or [""]
    category = st.selectbox("Kategori diawali", categories)
    status = st.selectbox("Status baru", PRACTICE_STATUSES)
    if st.button("Terapkan ke praktik"):
        upsert_rows(db, "praktik", [
            {**row, "status": status}
            for row in rows if str(row.get("kategori") or "").startswith(category)
        ])
        st.success("Status diperbarui.")
        st.rerun()

with st.expander("Tambah praktik"):
    with st.form("new_practice"):
        item_id = st.text_input("ID", value=f"P-{len(rows) + 1:03d}")
        phase = st.selectbox("Fase", PHASES)
        task = st.text_input("Tugas / Lab")
        category_new = st.text_input("Kategori")
        platform = st.text_input("Platform")
        level = st.selectbox("Level", [""] + PRACTICE_LEVELS)
        estimated = st.number_input("Jam estimasi", min_value=0.0, step=0.5)
        week = st.number_input("Minggu target", min_value=1, max_value=52, value=1)
        if st.form_submit_button("Tambah"):
            if not task.strip():
                st.error("Tugas wajib diisi.")
            elif any(row["id"] == item_id for row in rows):
                st.error("ID praktik sudah digunakan.")
            else:
                upsert_rows(db, "praktik", [{
                    "id": item_id, "fase": phase, "kategori": category_new or None,
                    "tugas": task, "platform": platform or None, "level": level or None,
                    "jam_est": estimated, "minggu_target": week, "status": "Belum Mulai",
                }])
                st.success("Praktik ditambahkan.")
                st.rerun()
show_empty_hint(db)
