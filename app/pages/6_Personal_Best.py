import pandas as pd
import streamlit as st

from app.core.constants import RECORD_DIRECTIONS
from app.core.db import fetch_all, get_settings, upsert_rows
from app.core.metrics import manual_record_status, personal_best, weekly_schedule
from app.core.ui import connection, editable_table

st.set_page_config(page_title="Personal Best", layout="wide")
st.title("Personal Best")
db = connection()
settings = get_settings(db)
metrics = personal_best(
    fetch_all(db, "log_harian"),
    weekly_schedule(
        settings["start_date"], float(settings["weekly_target_hours"]),
        fetch_all(db, "log_harian"), fetch_all(db, "jadwal"),
    ),
    fetch_all(db, "materi"), fetch_all(db, "praktik"), fetch_all(db, "portofolio"),
    fetch_all(db, "sertifikasi"), settings["start_date"],
)
labels = {
    "total_jam": "Total jam", "hari_belajar": "Hari belajar",
    "rata_jam_per_hari": "Rata-rata jam/hari",
    "jam_terbanyak_hari": "Jam terbanyak/hari", "tanggal_jam_terbanyak": "Tanggal terbaik",
    "jam_terbanyak_minggu": "Jam terbanyak/minggu", "minggu_jam_terbanyak": "Minggu terbaik",
    "streak_terpanjang": "Streak terpanjang", "streak_saat_ini": "Streak saat ini",
    "minggu_tercapai": "Minggu tercapai", "materi_selesai": "Materi selesai",
    "praktik_selesai": "Praktik selesai", "lab_hard_selesai": "Lab Hard selesai",
    "lab_medium_selesai": "Lab Medium selesai",
    "rata_skor_pemahaman": "Rata-rata skor pemahaman",
    "portofolio_selesai": "Portofolio selesai", "sertifikasi_lulus": "Sertifikasi lulus",
}
for start in range(0, len(labels), 4):
    columns = st.columns(4)
    for column, (key, label) in zip(columns, list(labels.items())[start:start + 4]):
        value = metrics[key]
        column.metric(label, f"{value:.2f}" if isinstance(value, float) else value)

st.subheader("Rekor manual")
records = fetch_all(db, "rekor_manual")
if records:
    frame = pd.DataFrame(records)
    frame["status_rekor"] = frame.apply(
        lambda row: manual_record_status(row["nilai"], row["rekor_sebelumnya"], row["arah"]),
        axis=1,
    )
    st.dataframe(frame, width="stretch", hide_index=True)
    editable_table(db, "rekor_manual", frame, "manual_records")
else:
    st.info("Belum ada rekor manual.")
with st.expander("Tambah rekor manual"):
    with st.form("manual_record"):
        record_date = st.date_input("Tanggal", format="DD/MM/YYYY")
        category = st.text_input("Kategori")
        metric = st.text_input("Metrik")
        value = st.number_input("Nilai")
        unit = st.text_input("Satuan")
        previous = st.number_input("Rekor sebelumnya (0 jika belum ada)", min_value=0.0)
        direction = st.selectbox("Arah lebih baik", RECORD_DIRECTIONS)
        note = st.text_area("Catatan")
        if st.form_submit_button("Tambah rekor"):
            if not metric.strip():
                st.error("Metrik wajib diisi.")
            else:
                upsert_rows(db, "rekor_manual", [{
                    "tanggal": record_date.isoformat(), "kategori": category or None,
                    "metrik": metric, "nilai": value, "satuan": unit or None,
                    "rekor_sebelumnya": previous, "arah": direction, "catatan": note or None,
                }])
                st.success("Rekor ditambahkan.")
                st.rerun()
