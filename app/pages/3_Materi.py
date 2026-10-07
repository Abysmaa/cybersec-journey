import streamlit as st

from app.core.constants import MATERIAL_STATUSES, PHASES
from app.core.db import fetch_all, upsert_rows
from app.core.ui import connection, editable_table, load_frame, show_empty_hint

st.set_page_config(page_title="Materi", layout="wide")
st.title("Materi")
db = connection()
rows = fetch_all(db, "materi")
phase_filter = st.selectbox("Filter fase", ["Semua"] + PHASES)
categories = sorted({str(row.get("kategori") or "") for row in rows if row.get("kategori")})
category_filter = st.selectbox("Filter kategori", ["Semua"] + categories)
status_filter = st.selectbox("Filter status", ["Semua"] + MATERIAL_STATUSES)
weeks = sorted({int(row["minggu_target"]) for row in rows if row.get("minggu_target")})
week_filter = st.selectbox("Filter minggu target", ["Semua"] + weeks)
frame = load_frame(db, "materi")
if phase_filter != "Semua":
    frame = frame[frame["fase"] == phase_filter]
if status_filter != "Semua":
    frame = frame[frame["status"] == status_filter]
if category_filter != "Semua":
    frame = frame[frame["kategori"] == category_filter]
if week_filter != "Semua":
    frame = frame[frame["minggu_target"] == week_filter]
editable_table(db, "materi", frame, "materials")

with st.expander("Ubah status massal"):
    category = st.selectbox(
        "Kategori diawali", sorted({str(row.get("kategori") or "") for row in rows}) or [""]
    )
    status = st.selectbox("Status baru", MATERIAL_STATUSES)
    if st.button("Terapkan ke kategori"):
        changed = [
            {**row, "status": status}
            for row in rows
            if str(row.get("kategori") or "").startswith(category)
        ]
        upsert_rows(db, "materi", changed)
        st.success(f"Status diperbarui untuk {len(changed)} materi.")
        st.rerun()

with st.expander("Tambah materi"):
    with st.form("new_material"):
        item_id = st.text_input("ID", value=f"M-{len(rows) + 1:03d}")
        phase = st.selectbox("Fase", PHASES)
        topic = st.text_input("Topik")
        category_new = st.text_input("Kategori")
        detail = st.text_area("Fokus / Detail")
        estimated = st.number_input("Jam estimasi", min_value=0.0, step=0.5)
        week = st.number_input("Minggu target", min_value=1, max_value=52, value=1)
        if st.form_submit_button("Tambah"):
            if not topic.strip():
                st.error("Topik wajib diisi.")
            elif any(row["id"] == item_id for row in rows):
                st.error("ID materi sudah digunakan.")
            else:
                upsert_rows(db, "materi", [{
                    "id": item_id, "fase": phase, "kategori": category_new or None,
                    "topik": topic, "detail": detail or None, "jam_est": estimated,
                    "minggu_target": week, "status": "Belum Mulai",
                }])
                st.success("Materi ditambahkan.")
                st.rerun()
show_empty_hint(db)
