"""SQLite schema and parameterized persistence helpers."""

import sqlite3
from pathlib import Path

from app.core.constants import PRIMARY_KEYS, TABLE_COLUMNS

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "tracker.db"
TABLE_NAMES = set(TABLE_COLUMNS)

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS materi (
    id TEXT PRIMARY KEY, fase TEXT NOT NULL, kategori TEXT, topik TEXT NOT NULL,
    detail TEXT, sumber TEXT, jam_est REAL, minggu_target INTEGER,
    status TEXT NOT NULL DEFAULT 'Belum Mulai', tgl_mulai DATE, tgl_selesai DATE,
    jam_aktual REAL, catatan TEXT
);
CREATE TABLE IF NOT EXISTS praktik (
    id TEXT PRIMARY KEY, fase TEXT NOT NULL, kategori TEXT, platform TEXT,
    tugas TEXT NOT NULL, deliverable TEXT, level TEXT, jam_est REAL, minggu_target INTEGER,
    status TEXT NOT NULL DEFAULT 'Belum Mulai', tgl_selesai DATE, jam_aktual REAL,
    skor_pemahaman INTEGER CHECK (skor_pemahaman BETWEEN 1 AND 5),
    link TEXT, catatan TEXT
);
CREATE TABLE IF NOT EXISTS jadwal (
    minggu INTEGER PRIMARY KEY, fase TEXT, fokus_materi TEXT, praktik_utama TEXT, refleksi TEXT
);
CREATE TABLE IF NOT EXISTS log_harian (
    tanggal DATE PRIMARY KEY, jam REAL NOT NULL CHECK (jam BETWEEN 0 AND 24),
    aktivitas TEXT, platform TEXT, ref_id TEXT,
    energi INTEGER CHECK (energi BETWEEN 1 AND 5), catatan TEXT
);
CREATE TABLE IF NOT EXISTS sertifikasi (
    no INTEGER PRIMARY KEY, nama TEXT NOT NULL, jalur TEXT, target_waktu TEXT,
    persiapan TEXT, biaya TEXT, status TEXT DEFAULT 'Rencana',
    tgl_ujian DATE, hasil TEXT, catatan TEXT
);
CREATE TABLE IF NOT EXISTS portofolio (
    id TEXT PRIMARY KEY, deliverable TEXT NOT NULL, kategori TEXT,
    minggu_target INTEGER, status TEXT DEFAULT 'Belum', link TEXT, catatan TEXT
);
CREATE TABLE IF NOT EXISTS rekor_manual (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tanggal DATE, kategori TEXT, metrik TEXT NOT NULL,
    nilai REAL NOT NULL, satuan TEXT, rekor_sebelumnya REAL, arah TEXT, catatan TEXT
);
"""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a row-aware SQLite connection after ensuring the schema exists."""
    path = Path(db_path) if db_path is not None else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    connection.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        ("start_date", "2026-10-05"),
    )
    connection.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        ("weekly_target_hours", "12"),
    )
    connection.commit()
    return connection


def fetch_all(connection: sqlite3.Connection, table: str) -> list[dict]:
    if table not in TABLE_NAMES:
        raise ValueError(f"Unsupported table: {table}")
    rows = connection.execute(f'SELECT * FROM "{table}"').fetchall()
    return [dict(row) for row in rows]


def upsert_rows(connection: sqlite3.Connection, table: str, rows: list[dict]) -> int:
    """Insert or replace rows for a known table using bound values."""
    if table not in TABLE_NAMES:
        raise ValueError(f"Unsupported table: {table}")
    columns = TABLE_COLUMNS[table]
    if table == "rekor_manual":
        next_id = connection.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM rekor_manual"
        ).fetchone()[0]
        rows = [
            ({**row, "id": next_id + index} if row.get("id") in (None, "") else row)
            for index, row in enumerate(rows)
        ]
    selected_rows = [
        {column: row.get(column) for column in columns}
        for row in rows
        if row.get(PRIMARY_KEYS[table]) not in (None, "")
    ]
    if not selected_rows:
        return 0
    column_sql = ", ".join(f'"{column}"' for column in columns)
    placeholders = ", ".join("?" for _ in columns)
    conflict = PRIMARY_KEYS[table]
    updates = ", ".join(
        f'"{column}" = excluded."{column}"' for column in columns if column != conflict
    )
    sql = (
        f'INSERT INTO "{table}" ({column_sql}) VALUES ({placeholders}) '
        f'ON CONFLICT("{conflict}") DO UPDATE SET {updates}'
    )
    connection.executemany(sql, [[row[column] for column in columns] for row in selected_rows])
    connection.commit()
    return len(selected_rows)


def update_row(connection: sqlite3.Connection, table: str, row: dict) -> None:
    if table not in TABLE_NAMES:
        raise ValueError(f"Unsupported table: {table}")
    key = PRIMARY_KEYS[table]
    if row.get(key) in (None, ""):
        raise ValueError(f"Missing primary key for {table}")
    columns = [column for column in TABLE_COLUMNS[table] if column != key]
    assignments = ", ".join(f'"{column}" = ?' for column in columns)
    values = [row.get(column) for column in columns] + [row[key]]
    connection.execute(f'UPDATE "{table}" SET {assignments} WHERE "{key}" = ?', values)
    connection.commit()


def delete_row(connection: sqlite3.Connection, table: str, key_value: object) -> None:
    if table not in TABLE_NAMES:
        raise ValueError(f"Unsupported table: {table}")
    key = PRIMARY_KEYS[table]
    connection.execute(f'DELETE FROM "{table}" WHERE "{key}" = ?', (key_value,))
    connection.commit()


def get_settings(connection: sqlite3.Connection) -> dict[str, str]:
    rows = connection.execute("SELECT key, value FROM settings")
    return {row["key"]: row["value"] for row in rows}


def set_setting(connection: sqlite3.Connection, key: str, value: str) -> None:
    if key not in {"start_date", "weekly_target_hours"}:
        raise ValueError(f"Unsupported setting: {key}")
    connection.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    connection.commit()
