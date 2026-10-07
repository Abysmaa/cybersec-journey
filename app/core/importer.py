"""Import workbook sheets using stable keys and ignore calculated columns."""

from datetime import date, datetime
from io import BytesIO
from typing import BinaryIO

import pandas as pd

from app.core.db import set_setting, upsert_rows

SHEET_COLUMNS = {
    "Materi": {
        "ID": "id", "Fase": "fase", "Kategori": "kategori", "Topik": "topik",
        "Fokus / Detail": "detail", "Sumber Belajar": "sumber", "Jam Est.": "jam_est",
        "Minggu Target": "minggu_target", "Status": "status", "Tgl Mulai": "tgl_mulai",
        "Tgl Selesai": "tgl_selesai", "Jam Aktual": "jam_aktual", "Catatan": "catatan",
    },
    "Praktik": {
        "ID": "id", "Fase": "fase", "Kategori": "kategori", "Platform": "platform",
        "Tugas / Lab": "tugas", "Deliverable (bukti)": "deliverable", "Level": "level",
        "Jam Est.": "jam_est", "Minggu Target": "minggu_target", "Status": "status",
        "Tgl Selesai": "tgl_selesai", "Jam Aktual": "jam_aktual",
        "Skor Pemahaman (1-5)": "skor_pemahaman", "Link Writeup / Repo": "link",
        "Catatan": "catatan",
    },
    "Jadwal": {
        "Minggu": "minggu", "Fase": "fase", "Fokus Materi": "fokus_materi",
        "Praktik Utama": "praktik_utama", "Refleksi": "refleksi",
    },
    "LogHarian": {
        "Tanggal": "tanggal", "Jam Belajar": "jam", "Aktivitas / Topik": "aktivitas",
        "Platform": "platform", "ID Materi/Praktik": "ref_id", "Energi (1-5)": "energi",
        "Catatan": "catatan",
    },
    "Sertifikasi": {
        "No": "no", "Sertifikasi": "nama", "Jalur / Level": "jalur",
        "Target Waktu": "target_waktu", "Rekomendasi Persiapan": "persiapan",
        "Estimasi Biaya": "biaya", "Status": "status", "Tanggal Ujian": "tgl_ujian",
        "Hasil / Skor": "hasil", "Catatan": "catatan",
    },
    "Portofolio": {
        "ID": "id", "Deliverable": "deliverable", "Kategori": "kategori",
        "Target Minggu": "minggu_target", "Status": "status", "Link": "link",
        "Catatan": "catatan",
    },
}


def _clean(value: object) -> object:
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        if isinstance(value, (pd.Timestamp, datetime)):
            return value.date().isoformat()
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


def _rows(frame: pd.DataFrame, mapping: dict[str, str], key: str) -> list[dict]:
    available = {str(column).strip(): column for column in frame.columns}
    rows = []
    for _, source in frame.iterrows():
        row = {
            target: _clean(source[available[column]])
            for column, target in mapping.items()
            if column in available
        }
        if row.get(key) not in (None, ""):
            rows.append(row)
    return rows


def _manual_records(book: pd.ExcelFile, connection) -> list[dict]:
    if "PersonalBest" not in book.sheet_names:
        return []
    frame = pd.read_excel(book, sheet_name="PersonalBest", header=None)
    required = {"Tanggal", "Kategori", "Metrik", "Nilai"}
    for header_index, values in frame.iterrows():
        labels = {str(value).strip() for value in values if not pd.isna(value)}
        if required.issubset(labels):
            columns = [str(value).strip() if not pd.isna(value) else "" for value in values]
            data = frame.iloc[header_index + 1:].copy()
            data.columns = columns
            mapping = {
                "Tanggal": "tanggal", "Kategori": "kategori", "Metrik": "metrik",
                "Nilai": "nilai", "Satuan": "satuan",
                "Rekor Sebelumnya": "rekor_sebelumnya", "Arah Lebih Baik": "arah",
                "Catatan": "catatan",
            }
            rows = _rows(data, mapping, "metrik")
            next_id = connection.execute(
                "SELECT COALESCE(MAX(id), 0) + 1 FROM rekor_manual"
            ).fetchone()[0]
            for index, row in enumerate(rows):
                existing = connection.execute(
                    "SELECT id FROM rekor_manual WHERE tanggal IS ? AND kategori IS ? "
                    "AND metrik = ? AND nilai IS ?",
                    (
                        row.get("tanggal"), row.get("kategori"), row.get("metrik"),
                        row.get("nilai"),
                    ),
                ).fetchone()
                row["id"] = existing["id"] if existing else next_id + index
            return rows
    return []


def import_workbook(file: BinaryIO | bytes, connection) -> dict[str, int]:
    """Import available sheets from the Excel source; rows with empty keys are skipped."""
    stream = BytesIO(file) if isinstance(file, bytes) else file
    book = pd.ExcelFile(stream, engine="openpyxl")
    counts: dict[str, int] = {}
    for sheet, mapping in SHEET_COLUMNS.items():
        if sheet not in book.sheet_names:
            continue
        frame = pd.read_excel(book, sheet_name=sheet, header=3)
        key = {
            "Materi": "id", "Praktik": "id", "Jadwal": "minggu",
            "LogHarian": "tanggal", "Sertifikasi": "no", "Portofolio": "id",
        }[sheet]
        table = {
            "Materi": "materi", "Praktik": "praktik", "Jadwal": "jadwal",
            "LogHarian": "log_harian", "Sertifikasi": "sertifikasi",
            "Portofolio": "portofolio",
        }[sheet]
        rows = _rows(frame, mapping, key)
        counts[sheet] = upsert_rows(connection, table, rows)
    if "PersonalBest" in book.sheet_names:
        counts["PersonalBest"] = upsert_rows(
            connection, "rekor_manual", _manual_records(book, connection)
        )
    if not counts:
        raise ValueError("Workbook tidak memiliki sheet yang dikenali.")
    if "Dashboard" in book.sheet_names:
        dashboard = pd.read_excel(book, sheet_name="Dashboard", header=None)
        if dashboard.shape[0] >= 6 and dashboard.shape[1] >= 3:
            start = _clean(dashboard.iat[4, 2])
            target = _clean(dashboard.iat[5, 2])
            if start not in (None, ""):
                set_setting(connection, "start_date", str(start)[:10])
            if target not in (None, ""):
                set_setting(connection, "weekly_target_hours", str(target))
    return counts
