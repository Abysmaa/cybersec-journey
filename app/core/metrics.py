"""Pure calculations for tracker progress and personal records."""

from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from math import floor

Row = Mapping[str, object]
PATH_PREFIXES = ("Jalur A", "Jalur B", "Jalur C", "Jalur D")


def as_date(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def week_number(value: date | datetime | str, start_date: date | datetime | str) -> int:
    return floor((as_date(value) - as_date(start_date)).days / 7) + 1


def current_week(today: date | datetime | str, start_date: date | datetime | str) -> int:
    current = as_date(today)
    start = as_date(start_date)
    if current < start:
        return 0
    return min(week_number(current, start), 52)


def schedule_status(week: int, actual_hours: float, target_hours: float) -> str:
    if week == 0:
        return "Belum dimulai"
    return "Sesuai / di depan jadwal" if actual_hours - target_hours >= 0 else "Tertinggal"


def weighted_progress(items: Iterable[Row]) -> float:
    active = [item for item in items if item.get("status") != "Dilewati"]
    estimate = sum(float(item.get("jam_est") or 0) for item in active)
    completed = sum(
        float(item.get("jam_est") or 0) for item in active if item.get("status") == "Selesai"
    )
    return completed / estimate if estimate else 0.0


def overall_progress(materials: Iterable[Row], practices: Iterable[Row]) -> float:
    material_rows = list(materials)
    practice_rows = list(practices)
    active_hours = sum(
        float(row.get("jam_est") or 0)
        for row in [*material_rows, *practice_rows]
        if row.get("status") != "Dilewati"
    )
    completed_hours = sum(
        float(row.get("jam_est") or 0)
        for row in [*material_rows, *practice_rows]
        if row.get("status") == "Selesai"
    )
    return completed_hours / active_hours if active_hours else 0.0


def item_progress(materials: Iterable[Row], practices: Iterable[Row]) -> dict[str, float]:
    material_rows = [row for row in materials if row.get("status") != "Dilewati"]
    practice_rows = [row for row in practices if row.get("status") != "Dilewati"]
    material_done = sum(row.get("status") == "Selesai" for row in material_rows)
    practice_done = sum(row.get("status") == "Selesai" for row in practice_rows)
    total = len(material_rows) + len(practice_rows)
    return {
        "materi": material_done / len(material_rows) if material_rows else 0.0,
        "praktik": practice_done / len(practice_rows) if practice_rows else 0.0,
        "gabungan": (material_done + practice_done) / total if total else 0.0,
        "materi_selesai": float(material_done),
        "materi_aktif": float(len(material_rows)),
        "praktik_selesai": float(practice_done),
        "praktik_aktif": float(len(practice_rows)),
    }


def progress_by_phase(
    materials: Iterable[Row], practices: Iterable[Row], paths: bool = False
) -> list[dict[str, object]]:
    material_rows = list(materials)
    practice_rows = list(practices)
    groups: dict[str, tuple[list[Row], list[Row]]] = {}
    for item in material_rows:
        key = str(item.get("kategori") or "") if paths else str(item.get("fase") or "")
        if paths:
            key = next((prefix for prefix in PATH_PREFIXES if key.startswith(prefix)), "")
            if not key:
                continue
        groups.setdefault(key, ([], []))[0].append(item)
    for item in practice_rows:
        key = str(item.get("kategori") or "") if paths else str(item.get("fase") or "")
        if paths:
            key = next((prefix for prefix in PATH_PREFIXES if key.startswith(prefix)), "")
            if not key:
                continue
        groups.setdefault(key, ([], []))[1].append(item)
    results = []
    for name, (group_materials, group_practices) in groups.items():
        result = item_progress(group_materials, group_practices)
        results.append({"nama": name, **result})
    return sorted(results, key=lambda row: str(row["nama"]))


def weekly_schedule(
    start_date: date | datetime | str,
    weekly_target_hours: float,
    logs: Iterable[Row],
    schedule_rows: Iterable[Row] = (),
    today: date | datetime | str | None = None,
) -> list[dict[str, object]]:
    start = as_date(start_date)
    current = as_date(today or date.today())
    log_rows = list(logs)
    details = {int(row["minggu"]): row for row in schedule_rows if row.get("minggu") is not None}
    weeks = []
    for week in range(1, 53):
        begins = start + timedelta(days=(week - 1) * 7)
        ends = begins + timedelta(days=6)
        hours = sum(
            float(log.get("jam") or 0)
            for log in log_rows
            if week_number(log["tanggal"], start) == week
        )
        target = float(weekly_target_hours)
        if begins > current:
            status = "Akan datang"
        elif hours >= target:
            status = "Tercapai"
        elif ends < current:
            status = "Tidak tercapai"
        else:
            status = "Berjalan"
        detail = details.get(week, {})
        weeks.append({
            "minggu": week,
            "mulai": begins.isoformat(),
            "selesai": ends.isoformat(),
            "fase": detail.get("fase"),
            "fokus_materi": detail.get("fokus_materi"),
            "praktik_utama": detail.get("praktik_utama"),
            "jam_target": target,
            "jam_aktual": hours,
            "capaian": hours / target if target else 0.0,
            "status": status,
            "refleksi": detail.get("refleksi"),
        })
    return weeks


def streaks(
    logs: Iterable[Row], today: date | datetime | str | None = None
) -> dict[str, int]:
    ordered = sorted({as_date(row["tanggal"]) for row in logs})
    if not ordered:
        return {"terpanjang": 0, "saat_ini": 0}
    best = running = 0
    previous = None
    per_day = {}
    for day in ordered:
        running = running + 1 if previous and day - previous == timedelta(days=1) else 1
        per_day[day] = running
        best = max(best, running)
        previous = day
    reference = as_date(today or date.today())
    last_day = ordered[-1]
    current = per_day[last_day] if last_day >= reference - timedelta(days=1) else 0
    return {"terpanjang": best, "saat_ini": current}


def personal_best(
    logs: Iterable[Row],
    weeks: Iterable[Row],
    materials: Iterable[Row],
    practices: Iterable[Row],
    portfolios: Iterable[Row],
    certifications: Iterable[Row],
    start_date: date | datetime | str,
    today: date | datetime | str | None = None,
) -> dict[str, object]:
    log_rows = list(logs)
    week_rows = list(weeks)
    material_rows = list(materials)
    practice_rows = list(practices)
    portfolio_rows = list(portfolios)
    certification_rows = list(certifications)
    daily: dict[date, float] = {}
    weekly: dict[int, float] = {}
    for row in log_rows:
        day = as_date(row["tanggal"])
        hours = float(row.get("jam") or 0)
        daily[day] = daily.get(day, 0) + hours
        number = week_number(day, start_date)
        weekly[number] = weekly.get(number, 0) + hours
    max_day = max(daily.items(), key=lambda pair: pair[1], default=(None, 0))
    max_week = max(weekly.items(), key=lambda pair: pair[1], default=(None, 0))
    understanding = [
        float(row["skor_pemahaman"])
        for row in practice_rows
        if row.get("skor_pemahaman") is not None
    ]
    streak = streaks(log_rows, today)
    return {
        "total_jam": sum(float(row.get("jam") or 0) for row in log_rows),
        "hari_belajar": len(daily),
        "rata_jam_per_hari": sum(daily.values()) / len(daily) if daily else 0,
        "jam_terbanyak_hari": max_day[1],
        "tanggal_jam_terbanyak": max_day[0].isoformat() if max_day[0] else "-",
        "jam_terbanyak_minggu": max_week[1],
        "minggu_jam_terbanyak": max_week[0] if max_week[0] is not None else "-",
        "streak_terpanjang": streak["terpanjang"],
        "streak_saat_ini": streak["saat_ini"],
        "minggu_tercapai": sum(row.get("status") == "Tercapai" for row in week_rows),
        "materi_selesai": sum(row.get("status") == "Selesai" for row in material_rows),
        "praktik_selesai": sum(row.get("status") == "Selesai" for row in practice_rows),
        "lab_hard_selesai": sum(
            row.get("status") == "Selesai" and row.get("level") == "Hard"
            for row in practice_rows
        ),
        "lab_medium_selesai": sum(
            row.get("status") == "Selesai" and row.get("level") == "Medium"
            for row in practice_rows
        ),
        "rata_skor_pemahaman": sum(understanding) / len(understanding) if understanding else 0,
        "portofolio_selesai": sum(row.get("status") == "Selesai" for row in portfolio_rows),
        "sertifikasi_lulus": sum(row.get("status") == "Lulus" for row in certification_rows),
    }


def manual_record_status(value: object, previous: object, direction: str | None) -> str:
    if value is None or value == "":
        return ""
    if previous is None or previous == "":
        return "Rekor pertama"
    if direction == "Tinggi" and float(value) > float(previous):
        return "REKOR BARU"
    if direction == "Rendah" and float(value) < float(previous):
        return "REKOR BARU"
    return "Belum melampaui"
