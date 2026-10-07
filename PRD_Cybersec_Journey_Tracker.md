# PRD: Cybersec Journey Tracker

> **Untuk coding agent.** Baca seluruh dokumen sebelum menulis kode. Kerjakan per milestone (Bagian 12), commit kecil di setiap milestone, dan jangan menambah fitur di luar cakupan (Bagian 3).

- **Pemilik:** Muhammad Abiyu Bisma Reswara Oetama
- **Versi:** 1.0 (7 Oktober 2026)
- **Bahasa UI:** Indonesia. **Bahasa kode, nama variabel, dan commit message:** Inggris.
- **Sumber data awal:** `Tracker_Belajar_Cyber_Security.xlsx` (sudah ada, lihat Bagian 6).

---

## 1. Ringkasan

Aplikasi web lokal untuk memantau perjalanan belajar cyber security selama 52 minggu: materi teori, praktik/lab, log jam belajar harian, jadwal mingguan, personal best, sertifikasi, dan portofolio. Aplikasi menggantikan spreadsheet Excel dengan antarmuka yang lebih nyaman, grafik, dan perhitungan otomatis, tanpa mengubah logika yang sudah ada di Excel.

## 2. Tujuan

1. Mencatat progres belajar harian dengan usaha minimal (maksimal 30 detik per entri log).
2. Menampilkan progres per fase dan per jalur spesialisasi secara visual.
3. Menjaga motivasi lewat streak, rekor pribadi, dan status jadwal (di depan atau tertinggal).
4. Menjadi bagian portofolio GitHub (kode rapi, README jelas, ada tes).

**Metrik sukses**
- Semua angka di Dashboard identik dengan hasil Excel untuk data yang sama (diverifikasi lewat tes, Bagian 11).
- Entri log harian dapat dibuat dalam 3 klik atau kurang dari satu halaman form.
- Aplikasi berjalan lokal dengan satu perintah: `streamlit run app/main.py`.

## 3. Cakupan

### Dalam cakupan (MVP)
- Impor data awal dari file Excel ke SQLite.
- CRUD untuk Materi, Praktik, Log Harian, Sertifikasi, Portofolio, Rekor Manual.
- Dashboard, Jadwal Mingguan, Personal Best (perhitungan otomatis).
- Ekspor data kembali ke Excel/CSV sebagai cadangan.

### Di luar cakupan (jangan dibuat)
- Multi-user, login, atau deployment publik.
- Integrasi API pihak ketiga (TryHackMe, HackTheBox, GitHub).
- Notifikasi, aplikasi mobile native, atau fitur AI.
- Fitur apa pun yang memindai, menyerang, atau menguji sistem jaringan. Ini murni aplikasi pencatat.

## 4. Pengguna

Satu pengguna: pemilik, mahasiswa Sistem Informasi, familiar dengan Python, pandas, Streamlit, dan Laravel. Menggunakan Windows 11. Aplikasi dipakai di komputer pribadi.

## 5. Tech Stack

| Komponen | Pilihan | Catatan |
|---|---|---|
| Bahasa | Python 3.11+ | |
| UI | Streamlit | Multi-page (`pages/`) |
| Database | SQLite | File `data/tracker.db`, akses lewat SQLAlchemy 2.x atau `sqlite3` |
| Data | pandas | Impor/ekspor dan agregasi |
| Grafik | Plotly (`plotly.express`) | Interaktif |
| Excel I/O | openpyxl | Baca file sumber, tulis ekspor |
| Tes | pytest | Wajib untuk modul perhitungan |
| Lint/format | ruff | Konfigurasi di `pyproject.toml` |
| Dependensi | `requirements.txt` dengan versi terkunci | |

Jangan menambah dependensi besar tanpa alasan tertulis di README.

## 6. Sumber Data: Struktur Excel

File `Tracker_Belajar_Cyber_Security.xlsx` berisi sheet berikut (header ada di **baris 4**, data mulai **baris 5**):

| Sheet | Kolom (urutan) |
|---|---|
| `Materi` | ID, Fase, Kategori, Topik, Fokus / Detail, Sumber Belajar, Jam Est., Minggu Target, Status, Tgl Mulai, Tgl Selesai, Jam Aktual, Catatan |
| `Praktik` | ID, Fase, Kategori, Platform, Tugas / Lab, Deliverable (bukti), Level, Jam Est., Minggu Target, Status, Tgl Selesai, Jam Aktual, Skor Pemahaman (1-5), Link Writeup / Repo, Catatan |
| `Jadwal` | Minggu, Mulai, Selesai, Fase, Fokus Materi, Praktik Utama, Jam Target, Jam Aktual, Capaian, Status Minggu, Refleksi |
| `LogHarian` | Tanggal, Minggu ke-, Jam Belajar, Aktivitas / Topik, Platform, ID Materi/Praktik, Energi (1-5), Catatan, Streak (hari) |
| `Sertifikasi` | No, Sertifikasi, Jalur / Level, Target Waktu, Rekomendasi Persiapan, Estimasi Biaya, Status, Tanggal Ujian, Hasil / Skor, Catatan |
| `Portofolio` | ID, Deliverable, Kategori, Target Minggu, Status, Link, Catatan |
| `PersonalBest` | Bagian atas = metrik otomatis (abaikan saat impor). Bagian bawah = tabel rekor manual: Tanggal, Kategori, Metrik, Nilai, Satuan, Rekor Sebelumnya, Arah Lebih Baik, Status Rekor, Catatan |
| `Dashboard` | Sel konfigurasi: `C5` = Tanggal mulai (default 2026-10-05), `C6` = Target jam/minggu (default 12) |

Aturan impor:
- Baca nilai (bukan rumus). Kolom hasil rumus (Minggu ke-, Streak, Jam Aktual Jadwal, Capaian, Status Minggu, Status Rekor) **dihitung ulang oleh aplikasi**, jangan disimpan dari Excel.
- Lewati baris yang kolom kuncinya kosong.
- Impor harus idempoten: menjalankan dua kali tidak menggandakan data (gunakan `ID` sebagai kunci unik; untuk `LogHarian` gunakan `tanggal`).

### Nilai enum
- **Fase:** `F0 Persiapan`, `F1 Fondasi`, `F2 Web Security`, `F3 Spesialisasi`, `F4 Lanjutan`
- **Status Materi:** `Belum Mulai`, `Sedang Dipelajari`, `Selesai`, `Dilewati`
- **Status Praktik:** `Belum Mulai`, `Dikerjakan`, `Selesai`, `Dilewati`
- **Status Sertifikasi:** `Rencana`, `Belajar`, `Terjadwal`, `Lulus`, `Ditunda`, `Dilewati`
- **Status Portofolio:** `Belum`, `Proses`, `Selesai`
- **Level Praktik:** `Easy`, `Medium`, `Hard`
- **Arah Lebih Baik (rekor):** `Tinggi`, `Rendah`
- **Kategori Fase 3 (jalur):** diawali `Jalur A`, `Jalur B`, `Jalur C`, `Jalur D`

## 7. Model Data (SQLite)

```sql
CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
-- keys: start_date (YYYY-MM-DD), weekly_target_hours (number)

CREATE TABLE materi (
  id TEXT PRIMARY KEY, fase TEXT NOT NULL, kategori TEXT, topik TEXT NOT NULL,
  detail TEXT, sumber TEXT, jam_est REAL, minggu_target INTEGER,
  status TEXT NOT NULL DEFAULT 'Belum Mulai',
  tgl_mulai DATE, tgl_selesai DATE, jam_aktual REAL, catatan TEXT
);

CREATE TABLE praktik (
  id TEXT PRIMARY KEY, fase TEXT NOT NULL, kategori TEXT, platform TEXT,
  tugas TEXT NOT NULL, deliverable TEXT, level TEXT, jam_est REAL,
  minggu_target INTEGER, status TEXT NOT NULL DEFAULT 'Belum Mulai',
  tgl_selesai DATE, jam_aktual REAL, skor_pemahaman INTEGER CHECK (skor_pemahaman BETWEEN 1 AND 5),
  link TEXT, catatan TEXT
);

CREATE TABLE jadwal (
  minggu INTEGER PRIMARY KEY, fase TEXT, fokus_materi TEXT, praktik_utama TEXT, refleksi TEXT
);
-- mulai, selesai, jam_target, jam_aktual, capaian, status dihitung saat runtime

CREATE TABLE log_harian (
  tanggal DATE PRIMARY KEY, jam REAL NOT NULL CHECK (jam BETWEEN 0 AND 24),
  aktivitas TEXT, platform TEXT, ref_id TEXT,
  energi INTEGER CHECK (energi BETWEEN 1 AND 5), catatan TEXT
);

CREATE TABLE sertifikasi (
  no INTEGER PRIMARY KEY, nama TEXT NOT NULL, jalur TEXT, target_waktu TEXT,
  persiapan TEXT, biaya TEXT, status TEXT DEFAULT 'Rencana',
  tgl_ujian DATE, hasil TEXT, catatan TEXT
);

CREATE TABLE portofolio (
  id TEXT PRIMARY KEY, deliverable TEXT NOT NULL, kategori TEXT,
  minggu_target INTEGER, status TEXT DEFAULT 'Belum', link TEXT, catatan TEXT
);

CREATE TABLE rekor_manual (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tanggal DATE, kategori TEXT, metrik TEXT NOT NULL,
  nilai REAL NOT NULL, satuan TEXT, rekor_sebelumnya REAL, arah TEXT, catatan TEXT
);
```

Satu baris `log_harian` per tanggal. Jika pengguna menyimpan tanggal yang sudah ada, tawarkan **update** (bukan error).

## 8. Aturan Perhitungan (wajib identik dengan Excel)

Letakkan semua logika di `app/core/metrics.py` sebagai fungsi murni (tanpa Streamlit) agar mudah dites.

1. **Nomor minggu dari tanggal:** `floor((tanggal - start_date).days / 7) + 1`.
2. **Minggu sekarang:** `0` jika `today < start_date`, selain itu `min(floor((today - start_date).days / 7) + 1, 52)`.
3. **Target jam s/d sekarang:** `weekly_target_hours * minggu_sekarang`. **Selisih** = total jam aktual − target.
4. **Status jadwal:** `Belum dimulai` jika minggu = 0; `Sesuai / di depan jadwal` jika selisih ≥ 0; selain itu `Tertinggal`.
5. **Item aktif** = semua item dengan status ≠ `Dilewati`.
6. **Progres berbobot jam (Materi):** `sum(jam_est where status='Selesai') / sum(jam_est where status != 'Dilewati')`; 0 bila penyebut 0. Praktik sama, memakai tabel praktik.
7. **Progres keseluruhan:** `(jam selesai materi + jam selesai praktik) / (jam aktif materi + jam aktif praktik)`.
8. **Progres per fase / per jalur (berbasis jumlah):**
   - `% Materi = Materi Selesai / Materi Aktif`, `% Praktik` serupa.
   - `% Gabungan = (Materi Selesai + Praktik Selesai) / (Materi Aktif + Praktik Aktif)`.
   - Per jalur: filter `kategori` dengan prefix `Jalur A`, `Jalur B`, `Jalur C`, `Jalur D`.
9. **Jadwal mingguan:**
   - `mulai = start_date + (minggu-1)*7 hari`, `selesai = mulai + 6 hari`.
   - `jam_aktual = sum(jam)` log yang nomor minggunya sama; `capaian = jam_aktual / jam_target` (0 bila target 0).
   - **Status minggu:** `Akan datang` jika `mulai > today`; `Tercapai` jika `jam_aktual >= jam_target`; `Tidak tercapai` jika `selesai < today`; selain itu `Berjalan`.
10. **Streak:** urutkan log menurut tanggal. Streak hari-i = 1 jika hari pertama atau ada celah > 1 hari; = streak sebelumnya + 1 jika selisih tepat 1 hari.
    - **Streak terpanjang** = nilai maksimum.
    - **Streak saat ini** = streak pada tanggal log terakhir, hanya jika tanggal itu ≥ `today − 1`; selain itu 0.
11. **Personal best otomatis:** total jam; total hari belajar; rata-rata jam per hari belajar; jam terbanyak per hari beserta tanggalnya; jam terbanyak per minggu beserta nomor minggunya; streak terpanjang; streak saat ini; jumlah minggu `Tercapai`; materi selesai; praktik selesai; lab `Hard` dan `Medium` selesai; rata-rata `skor_pemahaman` (abaikan null; 0 bila kosong); jumlah portofolio `Selesai`; jumlah sertifikasi `Lulus`.
12. **Status rekor manual:** kosong jika `nilai` kosong; `Rekor pertama` jika `rekor_sebelumnya` kosong; `REKOR BARU` jika (`arah='Tinggi'` dan nilai > sebelumnya) atau (`arah='Rendah'` dan nilai < sebelumnya); selain itu `Belum melampaui`.

## 9. Fitur & Kriteria Penerimaan

### F1. Impor & ekspor
- Halaman **Pengaturan**: unggah `.xlsx`, tombol "Impor", ringkasan jumlah baris per sheet.
- Tombol "Ekspor Excel" dan "Ekspor CSV" (per tabel).
- **AC:** impor dua kali menghasilkan jumlah baris sama; data Materi = 79 baris, Praktik = 68 baris dari file contoh.

### F2. Dashboard (`pages/1_Dashboard.py`)
- Kartu metrik: minggu ke-, total jam aktual, target s/d sekarang, selisih, status jadwal, progres keseluruhan, streak saat ini.
- Bar chart `% Gabungan` per fase; tabel progres per fase dan per jalur; line chart jam mingguan aktual vs target (52 minggu).
- **AC:** angka sama dengan Bagian 8 untuk dataset uji; grafik tidak error saat data kosong.

### F3. Log Harian (`pages/2_Log_Harian.py`)
- Form: tanggal (default hari ini), jam, aktivitas, platform, ID materi/praktik (dropdown), energi (1-5), catatan.
- Tabel riwayat yang bisa diedit/dihapus. Tampilkan streak saat ini.
- **AC:** validasi jam 0-24; tanggal duplikat memicu opsi update; simpan memperbarui Dashboard tanpa restart.

### F4. Materi & Praktik (`pages/3_Materi.py`, `pages/4_Praktik.py`)
- Tabel dengan filter fase, kategori, status, minggu target; edit status/tanggal/jam/skor/link/catatan inline.
- Ubah massal status (misalnya semua `Jalur B` → `Dilewati`).
- Tambah item baru (ID otomatis `M-xxx`/`P-xxx`).
- **AC:** perubahan status langsung memengaruhi persentase di Dashboard.

### F5. Jadwal (`pages/5_Jadwal.py`)
- 52 minggu: fokus, jam target, jam aktual, capaian (progress bar), status minggu berwarna, kolom refleksi dapat diedit. Minggu sekarang disorot.
- **AC:** logika status sesuai aturan 9.

### F6. Personal Best (`pages/6_Personal_Best.py`)
- Kartu rekor otomatis (aturan 11) dan tabel rekor manual dengan penanda `REKOR BARU`.

### F7. Sertifikasi & Portofolio (`pages/7_Sertifikasi.py`, `pages/8_Portofolio.py`)
- Tabel dapat diedit dengan status dropdown; progress bar portofolio.

### Non-fungsional
- Waktu muat halaman < 2 detik pada data uji.
- Semua operasi tulis memakai parameterized query (tanpa string SQL manual).
- Aplikasi tetap bekerja saat DB kosong (tampilkan petunjuk impor).
- Format tanggal UI `dd-mmm-yyyy`; penyimpanan ISO `YYYY-MM-DD`.

## 10. Struktur Proyek

```
cybersec-journey-tracker/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore               # data/*.db, .venv, __pycache__, .env
├── app/
│   ├── main.py              # halaman Beranda / ringkasan singkat
│   ├── pages/               # 1_Dashboard.py ... 8_Portofolio.py
│   └── core/
│       ├── db.py            # koneksi, skema, helper CRUD
│       ├── importer.py      # impor dari Excel (idempoten)
│       ├── exporter.py
│       ├── metrics.py       # semua rumus Bagian 8 (fungsi murni)
│       └── constants.py     # enum fase, status, level
├── data/
│   ├── seed/Tracker_Belajar_Cyber_Security.xlsx
│   └── tracker.db           # di-gitignore
└── tests/
    ├── test_metrics.py
    └── test_importer.py
```

## 11. Pengujian

Tulis tes `pytest` untuk `metrics.py` dengan dataset kecil yang hasilnya diketahui. Kasus minimum:

| Kasus | Ekspektasi |
|---|---|
| Log: 5, 6, 7, 9, 13 Okt 2026 (jam 1.5, 2, 1, 3, 2.5), start 5 Okt | Total 10 jam; hari 5; maks/hari 3 pada 9 Okt; streak terpanjang 3; minggu 1 = 7.5 jam, minggu 2 = 2.5 jam |
| 1 materi `Selesai`, 1 materi `Dilewati`, sisanya belum | Penyebut persentase tidak menghitung item `Dilewati` |
| `today < start_date` | Minggu sekarang = 0, status `Belum dimulai` |
| Rekor manual `arah=Rendah`, nilai 45, sebelumnya 60 | `REKOR BARU` |
| Data kosong | Semua metrik bernilai 0 atau `-`, tanpa exception |
| Impor dua kali | Jumlah baris tidak berubah |

Tes impor memakai file seed dan menegaskan jumlah baris (Materi 79, Praktik 68, Jadwal 52, Sertifikasi 12).

## 12. Milestone

1. **M1: Fondasi.** Struktur proyek, skema DB, `constants.py`, `importer.py`, tes impor lulus.
2. **M2: Perhitungan.** `metrics.py` lengkap dengan tes (Bagian 11) lulus.
3. **M3: Input harian.** Halaman Log Harian dan Materi/Praktik (CRUD).
4. **M4: Visualisasi.** Dashboard, Jadwal, Personal Best.
5. **M5: Pelengkap.** Sertifikasi, Portofolio, ekspor, Pengaturan.
6. **M6: Poles.** README (cara jalan, screenshot, struktur), lint bersih, tes hijau.

Definition of Done per milestone: tes terkait lulus, `ruff check` tanpa error, commit dengan pesan jelas (contoh: `feat: add streak calculation with tests`).

## 13. Aturan untuk Agent

- Jangan mengubah isi/teks rencana belajar di file seed; itu data milik pengguna.
- Jangan menaruh rumus di file halaman Streamlit; panggil `metrics.py`.
- Jangan hardcode path absolut; gunakan `pathlib` relatif terhadap root proyek.
- Jangan commit `tracker.db`, kredensial, atau data pribadi. Tambahkan ke `.gitignore`.
- Jangan membuat fitur jaringan keluar (HTTP request, scraping, port scan). Aplikasi harus berjalan offline.
- Jika spesifikasi ambigu, pilih perilaku paling sederhana yang konsisten dengan Excel dan tuliskan asumsi di bagian "Asumsi" pada README.
- Setelah tiap milestone, tampilkan ringkasan: apa yang selesai, apa yang diuji, apa yang belum.

## 14. Asumsi & Pertanyaan Terbuka

- Asumsi: satu pengguna, satu perangkat, data disimpan lokal.
- Tanggal mulai default 5 Okt 2026 dan target 12 jam/minggu dapat diubah di Pengaturan; seluruh jadwal harus ikut bergeser.
- Terbuka: apakah ingin sinkronisasi cadangan otomatis ke GitHub (hanya ekspor CSV tanpa data sensitif)? Jika ya, jadikan fase 2.
