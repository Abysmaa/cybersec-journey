"""Common Streamlit helpers shared by tracker pages."""

import os
from datetime import date

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

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


def _email_is_allowed(email: str, allowed_emails: list[str]) -> bool:
    return email.strip().casefold() in {
        allowed.strip().casefold() for allowed in allowed_emails if allowed.strip()
    }


def require_login() -> None:
    if os.environ.get("CYBERSEC_LOCAL_DEV") == "1":
        st.warning("Mode pengembangan lokal: autentikasi dinonaktifkan.")
        return

    try:
        auth = st.secrets["auth"]
        tracker = st.secrets["tracker"]
    except (KeyError, StreamlitSecretNotFoundError):
        st.error(
            "Aplikasi terkunci: konfigurasi OIDC dan daftar email yang diizinkan "
            "belum dipasang di Streamlit Secrets."
        )
        st.stop()

    required_auth = {
        "redirect_uri", "cookie_secret", "client_id",
        "client_secret", "server_metadata_url",
    }
    allowed_emails = tracker.get("allowed_emails", [])
    incomplete_auth = not required_auth.issubset(auth)
    invalid_allowlist = not isinstance(allowed_emails, list) or not allowed_emails
    if incomplete_auth or invalid_allowlist:
        st.error("Konfigurasi login atau daftar akun yang diizinkan belum lengkap.")
        st.stop()

    if not st.user.is_logged_in:
        st.title("Cybersec Journey Tracker")
        st.info("Masuk menggunakan akun Google yang telah diizinkan.")
        st.button("Masuk dengan Google", on_click=st.login)
        st.stop()

    email = str(st.user.get("email", ""))
    if not email or not _email_is_allowed(email, allowed_emails):
        st.error("Akun ini tidak memiliki akses ke tracker.")
        st.button("Keluar", on_click=st.logout)
        st.stop()

    st.sidebar.caption(f"Masuk sebagai {email}")
    st.sidebar.button("Keluar", on_click=st.logout)


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
