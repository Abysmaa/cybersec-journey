"""Common Streamlit helpers shared by tracker pages."""

from datetime import date

import pandas as pd
import streamlit as st

from app.core.constants import (
    CERTIFICATION_STATUSES,
    MATERIAL_STATUSES,
    PORTFOLIO_STATUSES,
    PRACTICE_LEVELS,
    PRACTICE_STATUSES,
    PRIMARY_KEYS,
    RECORD_DIRECTIONS,
    TABLE_COLUMNS,
)
from app.core.db import delete_row, fetch_all, update_row


def connection():
    from app.core.db import connect

    return connect()


def load_frame(db, table: str) -> pd.DataFrame:
    return pd.DataFrame(fetch_all(db, table), columns=TABLE_COLUMNS[table])


def show_empty_hint(db) -> bool:
    has_materials = fetch_all(db, "materi")
    has_practices = fetch_all(db, "praktik")
    has_logs = fetch_all(db, "log_harian")
    if not has_materials and not has_practices and not has_logs:
        st.info("Database masih kosong. Buka Pengaturan untuk mengimpor workbook Excel.")
        return True
    return False


def editable_table(db, table: str, frame: pd.DataFrame, key: str, disabled=None) -> pd.DataFrame:
    if frame.empty:
        st.info("Belum ada data untuk ditampilkan.")
        return frame
    choices = {
        "status": {
            "materi": MATERIAL_STATUSES,
            "praktik": PRACTICE_STATUSES,
            "sertifikasi": CERTIFICATION_STATUSES,
            "portofolio": PORTFOLIO_STATUSES,
        },
        "level": {"praktik": ["", *PRACTICE_LEVELS]},
        "arah": {"rekor_manual": RECORD_DIRECTIONS},
    }
    column_config = {}
    for column, tables in choices.items():
        if table in tables and column in frame:
            column_config[column] = st.column_config.SelectboxColumn(
                column.title(), options=tables[table]
            )
    edited = st.data_editor(
        frame,
        key=key,
        width="stretch",
        hide_index=True,
        num_rows="fixed",
        disabled=disabled or [PRIMARY_KEYS[table]],
        column_config=column_config,
    )
    if st.button("Simpan perubahan", key=f"{key}_save"):
        records = edited.to_dict(orient="records")
        for record in records:
            update_row(db, table, record)
        st.success(f"{len(records)} baris disimpan.")
        st.rerun()
    with st.expander("Hapus baris"):
        key_column = PRIMARY_KEYS[table]
        selected = st.selectbox(
            "Pilih baris", frame[key_column].tolist(), key=f"{key}_delete_value"
        )
        if st.button("Hapus pilihan", key=f"{key}_delete"):
            delete_row(db, table, selected)
            st.success("Baris dihapus.")
            st.rerun()
    return edited


def date_input(label: str, value=None, key=None):
    parsed = date.fromisoformat(str(value)[:10]) if value else date.today()
    return st.date_input(label, value=parsed, format="DD/MM/YYYY", key=key)


def format_date_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in ("tanggal", "tgl_mulai", "tgl_selesai", "tgl_ujian", "mulai", "selesai"):
        if column in result:
            result[column] = pd.to_datetime(result[column], errors="coerce").dt.strftime("%d-%b-%Y")
    return result
