from datetime import date

import pytest

from app.core.metrics import (
    current_week,
    item_progress,
    manual_record_status,
    overall_progress,
    personal_best,
    schedule_status,
    streaks,
    weekly_schedule,
    weighted_progress,
)


def test_weekly_log_totals_and_personal_best():
    logs = [
        {"tanggal": day, "jam": hours}
        for day, hours in [
            ("2026-10-05", 1.5), ("2026-10-06", 2),
            ("2026-10-07", 1), ("2026-10-09", 3), ("2026-10-13", 2.5),
        ]
    ]
    weeks = weekly_schedule("2026-10-05", 12, logs, today="2026-10-15")
    assert sum(row["jam"] for row in logs) == 10
    assert len(logs) == 5
    assert max(logs, key=lambda row: row["jam"]) == {"tanggal": "2026-10-09", "jam": 3}
    assert weeks[0]["jam_aktual"] == 7.5
    assert weeks[1]["jam_aktual"] == 2.5
    assert streaks(logs, "2026-10-14") == {"terpanjang": 3, "saat_ini": 1}


def test_completed_estimates_exclude_skipped_items():
    materials = [
        {"status": "Selesai", "jam_est": 2},
        {"status": "Dilewati", "jam_est": 100},
        {"status": "Belum Mulai", "jam_est": 2},
    ]
    assert weighted_progress(materials) == pytest.approx(0.5)
    assert item_progress(materials, [])["gabungan"] == pytest.approx(0.5)
    assert overall_progress(materials, []) == pytest.approx(0.5)


def test_overall_progress_is_weighted_by_estimated_hours():
    materials = [
        {"status": "Selesai", "jam_est": 8},
        {"status": "Belum Mulai", "jam_est": 2},
    ]
    assert overall_progress(materials, []) == pytest.approx(0.8)


def test_specialization_progress_aggregates_path_prefixes():
    from app.core.metrics import progress_by_phase

    rows = [
        {"kategori": "Jalur A - Web", "status": "Selesai"},
        {"kategori": "Jalur A - Cloud", "status": "Belum Mulai"},
        {"kategori": "Other", "status": "Selesai"},
    ]
    result = progress_by_phase(rows, [], paths=True)
    assert result == [{
        "nama": "Jalur A",
        "materi": 0.5,
        "praktik": 0.0,
        "gabungan": 0.5,
        "materi_selesai": 1.0,
        "materi_aktif": 2.0,
        "praktik_selesai": 0.0,
        "praktik_aktif": 0.0,
    }]


def test_current_week_and_schedule_status_before_start():
    assert current_week("2026-10-04", "2026-10-05") == 0
    assert schedule_status(0, 0, 12) == "Belum dimulai"


def test_week_boundaries_cap_and_schedule_status():
    assert current_week("2026-10-11", "2026-10-05") == 1
    assert current_week("2027-10-10", "2026-10-05") == 52
    assert schedule_status(2, 24, 24) == "Sesuai / di depan jadwal"
    assert schedule_status(2, 23.9, 24) == "Tertinggal"


def test_empty_data_returns_zeroes():
    result = personal_best([], [], [], [], [], [], "2026-10-05", "2026-10-05")
    assert result["total_jam"] == 0
    assert result["streak_saat_ini"] == 0
    assert result["tanggal_jam_terbanyak"] == "-"
    assert item_progress([], [])["gabungan"] == 0


def test_manual_record_status():
    assert manual_record_status(45, 60, "Rendah") == "REKOR BARU"
    assert manual_record_status(60, 60, "Tinggi") == "Belum melampaui"
    assert manual_record_status(12, None, "Tinggi") == "Rekor pertama"


def test_weekly_status_upcoming_and_incomplete():
    rows = weekly_schedule(
        date(2026, 10, 5), 12, [], today=date(2026, 10, 4)
    )
    assert rows[0]["status"] == "Akan datang"
    assert rows[1]["status"] == "Akan datang"
