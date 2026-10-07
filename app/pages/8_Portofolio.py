import streamlit as st

from app.core.constants import PORTFOLIO_STATUSES
from app.core.db import fetch_all, upsert_rows
from app.core.ui import connection, editable_table, load_frame

st.set_page_config(page_title="Portofolio", layout="wide")
st.title("Portofolio")
db = connection()
rows = fetch_all(db, "portofolio")
completed = sum(row.get("status") == "Selesai" for row in rows)
st.progress(completed / len(rows) if rows else 0.0, text=f"{completed} / {len(rows)} selesai")
editable_table(db, "portofolio", load_frame(db, "portofolio"), "portfolio")
with st.expander("Tambah deliverable"):
    with st.form("new_portfolio"):
        item_id = st.text_input("ID", value=f"PF-{len(rows) + 1:03d}")
        deliverable = st.text_input("Deliverable")
        category = st.text_input("Kategori")
        week = st.number_input("Minggu target", min_value=1, max_value=52, value=1)
        status = st.selectbox("Status", PORTFOLIO_STATUSES)
        link = st.text_input("Link")
        if st.form_submit_button("Tambah"):
            if not deliverable.strip():
                st.error("Deliverable wajib diisi.")
            elif any(row["id"] == item_id for row in rows):
                st.error("ID sudah digunakan.")
            else:
                upsert_rows(db, "portofolio", [{
                    "id": item_id, "deliverable": deliverable, "kategori": category or None,
                    "minggu_target": week, "status": status, "link": link or None,
                }])
                st.success("Deliverable ditambahkan.")
                st.rerun()
