from io import BytesIO

import pandas as pd

from app.core.db import connect, fetch_all
from app.core.importer import import_workbook


def make_workbook() -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet, columns, rows in [
            ("Materi", ["ID", "Fase", "Topik", "Status", "Jam Aktual"], [
                ["M-001", "F1 Fondasi", "Dasar", "Selesai", 9],
                [None, None, None, None, None],
            ]),
            ("Praktik", ["ID", "Fase", "Tugas / Lab", "Status"], [
                ["P-001", "F1 Fondasi", "Lab", "Belum Mulai"],
            ]),
            ("Jadwal", ["Minggu", "Fase", "Fokus Materi", "Jam Aktual"], [
                [1, "F1 Fondasi", "Dasar", 42],
            ]),
            ("Sertifikasi", ["No", "Sertifikasi", "Status"], [[1, "Cert", "Rencana"]]),
        ]:
            preamble = pd.DataFrame([[], [], []])
            data = pd.DataFrame(rows, columns=columns)
            preamble.to_excel(writer, sheet_name=sheet, index=False, header=False)
            data.to_excel(writer, sheet_name=sheet, index=False, startrow=3)
    return output.getvalue()


def test_import_is_idempotent_and_ignores_calculated_values(tmp_path):
    db = connect(tmp_path / "tracker.db")
    workbook = make_workbook()
    first = import_workbook(workbook, db)
    second = import_workbook(workbook, db)
    assert first["Materi"] == second["Materi"] == 1
    assert len(fetch_all(db, "materi")) == 1
    assert fetch_all(db, "materi")[0]["jam_aktual"] == 9
    assert fetch_all(db, "jadwal")[0]["fase"] == "F1 Fondasi"
    assert fetch_all(db, "jadwal")[0]["fokus_materi"] == "Dasar"


def test_unrecognized_workbook_is_rejected(tmp_path):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame({"unknown": [1]}).to_excel(writer, index=False)
    db = connect(tmp_path / "tracker.db")
    try:
        import_workbook(output.getvalue(), db)
    except ValueError as error:
        assert "tidak memiliki sheet" in str(error)
    else:
        raise AssertionError("Expected a workbook without recognized sheets to fail.")
