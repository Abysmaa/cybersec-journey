# 🛡️ Cybersec Journey Tracker

> **Satu tempat untuk merencanakan, mencatat, dan melihat progres belajar cybersecurity selama 52 minggu.**

[![Buka aplikasi](https://img.shields.io/badge/🚀-Buka%20Aplikasi-FF4B4B?style=for-the-badge)](https://cybersec-journey.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Dibuat%20dengan-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)

**[Buka Cybersec Journey Tracker](https://cybersec-journey.streamlit.app/)** · Login dengan akun Google yang diizinkan.

---

## ✨ Tentang aplikasi

Cybersec Journey Tracker membantu menjaga ritme belajar melalui target mingguan, catatan harian, dan ringkasan progres. Aplikasi ini dibuat dengan Streamlit dan menyimpan data menggunakan SQLite.

## 🧭 Fitur

| Halaman | Yang bisa dilakukan |
|---|---|
| **Dashboard** | Melihat minggu belajar, total jam, streak, dan ringkasan progres. |
| **Log Harian** | Mencatat waktu belajar, aktivitas, energi, dan refleksi. |
| **Materi** | Mengatur topik teori, status, target, dan jam belajar aktual. |
| **Praktik / Lab** | Mencatat latihan, tingkat kesulitan, deliverable, dan write-up. |
| **Jadwal** | Meninjau rencana 52 minggu dan menulis catatan mingguan. |
| **Personal Best** | Memantau metrik belajar dan rekor pribadi. |
| **Sertifikasi & Portofolio** | Mengelola target sertifikasi dan hasil karya. |
| **Pengaturan** | Mengatur tanggal mulai dan target mingguan, impor workbook, serta ekspor cadangan. |

> Aplikasi ini adalah **tracker belajar**, bukan alat untuk memindai, menyerang, atau menguji jaringan.

## 🚀 Mulai menggunakan aplikasi

1. Buka [aplikasi](https://cybersec-journey.streamlit.app/).
2. Pilih **Masuk dengan Google**.
3. Gunakan akun Google yang sudah diizinkan oleh pemilik aplikasi.
4. Mulai dari **Log Harian** untuk mencatat sesi belajar, atau buka **Pengaturan** untuk mengimpor workbook.

Jika akun Google belum diizinkan, hubungi pemilik aplikasi. Jangan kirim kata sandi atau secret OAuth melalui chat atau issue GitHub.

## 💻 Jalankan secara lokal

Memerlukan Python 3.11 atau versi lebih baru.

```powershell
git clone https://github.com/Abysmaa/cybersec-journey.git
cd cybersec-journey
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:CYBERSEC_LOCAL_DEV = "1"
streamlit run app/main.py
```

`CYBERSEC_LOCAL_DEV=1` menonaktifkan autentikasi **hanya untuk pengembangan lokal**. Jangan aktifkan di deployment publik. Database lokal dibuat otomatis di `data/tracker.db`; tanggal mulai dan target jam dapat diubah dari halaman **Pengaturan**.

## 🔐 Informasi login dan deployment

Aplikasi publik menggunakan Google OpenID Connect (OIDC). Pemilik perlu mengatur OAuth client dan secrets di Streamlit Community Cloud sebelum aplikasi dapat diakses.

Konfigurasi rahasia disimpan di **Streamlit Cloud → app → Settings → Secrets**, bukan di repository:

```toml
[auth]
redirect_uri = "https://NAMA-APP.streamlit.app/oauth2callback"
cookie_secret = "GANTI_DENGAN_SECRET_ACAK_YANG_PANJANG"
client_id = "GOOGLE_OAUTH_CLIENT_ID"
client_secret = "GOOGLE_OAUTH_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[tracker]
allowed_emails = ["email-yang-diizinkan@example.com"]
```

Pastikan URL callback sama dengan URL aplikasi, dan `client_id` serta `client_secret` berasal dari **OAuth client Google yang sama**. Buat `cookie_secret` acak dan simpan tetap—jangan mengubahnya setiap kali aplikasi dijalankan. Setelah mengubah Secrets, simpan lalu reboot aplikasi.

**Jangan pernah commit** `client_secret`, `cookie_secret`, file `.streamlit/secrets.toml`, database, atau data pribadi ke GitHub. File secrets lokal sudah dikecualikan melalui `.gitignore`.

### Jika login kembali ke layar masuk

- Periksa **Manage app → Logs** di Streamlit Community Cloud.
- `invalid_client` biasanya berarti `client_secret` salah atau tidak cocok dengan `client_id`. Pastikan kedua nilai dari OAuth client yang sama.
- `Origin mismatch` biasanya berarti host pada `redirect_uri` tidak sama dengan host aplikasi yang sedang dibuka.
- Pastikan email Google yang dipakai tercantum di `tracker.allowed_emails`.
- Setelah memperbaiki Secrets, reboot app dan coba lagi.

Jangan membagikan screenshot log yang berisi token atau nilai secret.

## 📥 Impor dan cadangan data

Unggah workbook `.xlsx` dari halaman **Pengaturan**. Header sheet dibaca dari baris ke-4. Impor dapat dijalankan ulang untuk memperbarui data tanpa menggandakan baris yang sama. Workbook sumber tidak disertakan di repository.

Ekspor tabel sebagai CSV atau unduh workbook Excel dari halaman **Pengaturan**. **Penting:** SQLite di Streamlit Community Cloud tersimpan pada filesystem lokal yang tidak dijamin persisten. Unduh cadangan secara rutin; jangan mengandalkan deployment Cloud sebagai satu-satunya tempat menyimpan data.

## 🧪 Untuk pengembang

Jalankan tes dan pemeriksaan gaya kode dari root repository:

```powershell
python -m pytest
ruff check .
```

## 🧰 Teknologi

Python · Streamlit · SQLite · pandas · Plotly · openpyxl · pytest · Ruff

---

<p align="center">
  Dibuat untuk membangun kebiasaan belajar cybersecurity, satu sesi dalam satu waktu. 🛡️
</p>
