"""Shared labels and controlled values for the tracker."""

PHASES = [
    "F0 Persiapan",
    "F1 Fondasi",
    "F2 Web Security",
    "F3 Spesialisasi",
    "F4 Lanjutan",
]
MATERIAL_STATUSES = ["Belum Mulai", "Sedang Dipelajari", "Selesai", "Dilewati"]
PRACTICE_STATUSES = ["Belum Mulai", "Dikerjakan", "Selesai", "Dilewati"]
CERTIFICATION_STATUSES = ["Rencana", "Belajar", "Terjadwal", "Lulus", "Ditunda", "Dilewati"]
PORTFOLIO_STATUSES = ["Belum", "Proses", "Selesai"]
PRACTICE_LEVELS = ["Easy", "Medium", "Hard"]
RECORD_DIRECTIONS = ["Tinggi", "Rendah"]
PATHS = ["Jalur A", "Jalur B", "Jalur C", "Jalur D"]

TABLE_COLUMNS = {
    "materi": [
        "id", "fase", "kategori", "topik", "detail", "sumber", "jam_est",
        "minggu_target", "status", "tgl_mulai", "tgl_selesai", "jam_aktual", "catatan",
    ],
    "praktik": [
        "id", "fase", "kategori", "platform", "tugas", "deliverable", "level", "jam_est",
        "minggu_target", "status", "tgl_selesai", "jam_aktual", "skor_pemahaman", "link",
        "catatan",
    ],
    "jadwal": ["minggu", "fase", "fokus_materi", "praktik_utama", "refleksi"],
    "log_harian": [
        "tanggal", "jam", "aktivitas", "platform", "ref_id", "energi", "catatan",
    ],
    "sertifikasi": [
        "no", "nama", "jalur", "target_waktu", "persiapan", "biaya", "status",
        "tgl_ujian", "hasil", "catatan",
    ],
    "portofolio": ["id", "deliverable", "kategori", "minggu_target", "status", "link", "catatan"],
    "rekor_manual": [
        "id", "tanggal", "kategori", "metrik", "nilai", "satuan", "rekor_sebelumnya",
        "arah", "catatan",
    ],
}

PRIMARY_KEYS = {
    "materi": "id",
    "praktik": "id",
    "jadwal": "minggu",
    "log_harian": "tanggal",
    "sertifikasi": "no",
    "portofolio": "id",
    "rekor_manual": "id",
}
