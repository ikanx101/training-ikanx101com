# Study Data with ikanx101.com

Platform belajar Data Science berbasis video YouTube yang terstruktur. Dibangun dengan FastAPI + Jinja2 + Tailwind CSS.

---

## Fitur

- Landing page untuk pengunjung, konten hanya bisa diakses setelah login
- Materi video YouTube terstruktur per kategori dan sub-kategori
- Lacak progres belajar dan bookmark materi
- Quiz di akhir setiap materi dengan nilai lulus yang bisa diatur admin
- Upload file data pendukung per materi (CSV, XLSX, PDF, ZIP, dll)
- Tanya jawab privat antara user dan admin per materi
- Dashboard user dan panel admin lengkap

---

## Menjalankan Secara Lokal

### 1. Clone repo

```bash
git clone https://github.com/USERNAME/training-ikanx101com.git
cd training-ikanx101com
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan server

```bash
bash start.sh
```

Server berjalan di `http://localhost:209`.

Login admin default:
- **Email:** admin@ikanx101.com
- **Password:** admin123

### 4. Menghentikan server

```bash
bash stop.sh
```

---

## Deploy ke Railway

### Langkah 1 — Push repo ke GitHub

```bash
git remote add origin https://github.com/USERNAME/NAMA-REPO.git
git push -u origin main
```

### Langkah 2 — Buat project di Railway

1. Buka [railway.app](https://railway.app) dan login
2. Klik **"New Project"**
3. Pilih **"Deploy from GitHub repo"**
4. Pilih repo ini
5. Railway otomatis mendeteksi `Procfile` dan mulai build

### Langkah 3 — Tambahkan PostgreSQL

1. Di dalam project, klik **"+ Add Service"**
2. Pilih **"Database"** → **"Add PostgreSQL"**
3. Railway otomatis membuat database dan menyiapkan variabel `DATABASE_URL`

### Langkah 4 — Sambungkan DATABASE_URL ke app

1. Klik service **app** (bukan database)
2. Buka tab **"Variables"**
3. Klik **"+ Add Variable Reference"** → pilih `DATABASE_URL` dari service PostgreSQL
4. Railway otomatis menyuntikkan URL ke app saat runtime

### Langkah 5 — Tambah SECRET_KEY

Masih di tab **Variables**, tambahkan:

```
SECRET_KEY = isi-dengan-string-acak-panjang-minimal-32-karakter
```

### Langkah 6 — Deploy

Railway akan otomatis deploy ulang setiap kali ada perubahan di branch `main`.

Setelah deploy selesai, Railway memberikan URL publik seperti:
```
https://training-ikanx101com-production.up.railway.app
```

Akun admin (`admin@ikanx101.com / admin123`) dibuat otomatis saat pertama kali deploy. Tabel database juga dibuat otomatis — tidak perlu migrasi manual.

---

## Catatan Penting untuk Production

**File uploads tidak persisten secara default di Railway.** File yang diupload user akan hilang setiap kali deploy ulang. Ada dua solusi:

| Solusi | Cara |
|---|---|
| Railway Volume (berbayar) | Di Railway: Add Service → Volume, mount ke `/app/uploads` |
| Object Storage (S3/R2) | Simpan file ke Cloudflare R2 atau AWS S3 |

Untuk tahap awal, app tetap berjalan normal meskipun tanpa persistent storage untuk uploads.

---

## Struktur Folder

```
training-ikanx101com/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── schemas/
│   ├── templates/
│   └── static/
├── requirements.txt
├── Procfile
├── start.sh
├── stop.sh
└── README.md
```

---

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Backend | FastAPI (Python) |
| Templating | Jinja2 |
| Styling | Tailwind CSS (CDN) |
| Interaktivitas | HTMX + Alpine.js |
| Database lokal | SQLite |
| Database production | PostgreSQL |
| Auth | JWT (httponly cookie) |
| Password hashing | bcrypt |
