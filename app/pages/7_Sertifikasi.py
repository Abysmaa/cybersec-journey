import streamlit as st

from app.core.constants import CERTIFICATION_STATUSES
from app.core.db import fetch_all, upsert_rows
from app.core.ui import connection, editable_table, load_frame, require_login

st.set_page_config(page_title="Sertifikasi", layout="wide")
require_login()
st.title("Sertifikasi")
db = connection()
frame = load_frame(db, "sertifikasi")
editable_table(db, "sertifikasi", frame, "certifications")
rows = fetch_all(db, "sertifikasi")
with st.expander("Tambah sertifikasi"):
    with st.form("new_certification"):
        number = st.number_input(
            "No", min_value=1,
            value=max([int(row["no"]) for row in rows], default=0) + 1,
        )
        name = st.text_input("Sertifikasi")
        path = st.text_input("Jalur / Level")
        target = st.text_input("Target waktu")
        cost = st.text_input("Estimasi biaya")
        status = st.selectbox("Status", CERTIFICATION_STATUSES)
        if st.form_submit_button("Tambah"):
            if not name.strip():
                st.error("Nama sertifikasi wajib diisi.")
            elif any(int(row["no"]) == number for row in rows):
                st.error("Nomor sertifikasi sudah digunakan.")
            else:
                upsert_rows(db, "sertifikasi", [{
                    "no": number, "nama": name, "jalur": path or None,
                    "target_waktu": target or None, "biaya": cost or None, "status": status,
                }])
                st.success("Sertifikasi ditambahkan.")
                st.rerun()
