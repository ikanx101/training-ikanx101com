# Project Description — Study Data with ikanx101.com

> LMS (Learning Management System) untuk kursus data science, machine learning, dan computational science.
> **Author:** Ikang Fadhli
> **Deployment:** Railway.app + Custom Domain Railway

---

## 1. 🎯 Scope — Full Fitur

Semua fitur langsung dibangun dari awal (bukan MVP bertahap):
- Registrasi, login, manajemen user
- Manajemen materi lengkap dengan kategori, sub-kategori, draft/publish
- Progress tracking per user
- Admin panel superadmin
- Search & bookmark materi

---

## 2. 🧱 Tech Stack

| Lapisan | Teknologi |
|---|---|
| **Backend** | FastAPI (Python) — async, auto Swagger docs |
| **Frontend** | Jinja2 Server-Side Rendering + HTMX (interaksi tanpa reload) |
| **CSS** | Tailwind CSS |
| **Database** | PostgreSQL |
| **Auth** | JWT (FastAPI OAuth2 built-in) |
| **Deployment** | Railway.app + Docker |

---

## 3. 👤 User Management

### Registrasi
- **Email + Password** (no Google OAuth, no social login)
- **No email verification** — langsung aktif setelah daftar
- Wajib isi: email, password, nama lengkap
- Opsional: bio

### Security Question (Lupa Password)
- Saat registrasi, user diminta memilih **1 pertanyaan khusus** dari daftar dan menuliskan jawabannya
- Saat "Lupa Password", user harus menjawab pertanyaan tersebut dengan benar untuk bisa reset password
- Contoh pertanyaan:
  - "Apa nama hewan peliharaan pertama kamu?"
  - "Apa nama kota kelahiran ibumu?"
  - "Apa makanan favorit kamu?"
  - "Apa judul lagu favorit kamu?"
  - "Apa merek HP pertama kamu?"
- Setelah jawaban benar → bisa set password baru

### Profil User
Tampilan berisi:
- **Foto/Avatar** — user bisa upload atau pakai default
- **Nama lengkap**
- **Email** (read-only atau bisa ganti dengan verifikasi ulang security question)
- **Bio** — teks bebas

### Role
| Role | Hak Akses |
|---|---|
| **User** | Akses materi, bookmark, progress tracking, edit profil sendiri |
| **Admin (Superadmin)** | Full CRUD semua user & materi, draft/publish, lihat statistik, akses panel admin |

---

## 4. 📚 Materi Management

### Struktur Hierarki
```
Kategori (misal: Python)
  └── Sub-Kategori (misal: Python Dasar)
        └── Materi (video YouTube + resource)
```

- **Kategori** — level 1, contoh: Python, SQL, Machine Learning, Statistics, Data Visualization
- **Sub-Kategori** — level 2, contoh: di bawah Python → "Dasar", "Lanjutan", "Web Scraping"
- **2 level cukup** — nggak perlu nested lebih dalam

### Urutan Materi — Hybrid (Opsi C)
- Ada **jalur silabus yang direkomendasikan** per sub-kategori (urutan nonton yang disarankan)
- User **tetap bisa buka materi lain** secara bebas — tidak ada yang terkunci
- Cocok: user punya panduan tapi tetap fleksibel

### Status Materi
| Status | Keterangan |
|---|---|
| **Draft** | Hanya terlihat di admin panel, belum muncul di halaman user |
| **Publish** | Muncul di halaman user |

### Detail Materi
- **Judul**
- **Deskripsi**
- **Embed link YouTube**
- **Tag** (untuk search & filter)
- **Resource pendukung** (file PDF, dataset, notebook — upload)
- **Kategori** & **Sub-Kategori**
- **Urutan** dalam sub-kategori
- **Status** (draft/publish)

### Progress Tracking
- User bisa klik **"Tandai Selesai"** pada setiap materi
- **Progress bar** per sub-kategori: *"3/8 materi selesai"*
- **Riwayat nonton**: daftar video terakhir yang ditonton
- **Next manual** — tidak auto-play, user klik sendiri next

### Fitur Lain
- **Search global** — cari materi berdasarkan judul/tag
- **Bookmark** — user bisa tandai materi favorit (ditampilkan di halaman profil/dashboard)

---

## 5. 🛠️ Admin Panel

### Dashboard
- Jumlah total user
- Jumlah user aktif (login dalam 7 hari terakhir)
- User baru minggu ini
- Total materi (draft vs publish)
- Statistik per kategori (popularitas)

### Manajemen User (Superadmin)
- Lihat daftar semua user
- Edit user (nama, email, role)
- Hapus user
- Ubah role (user ↔ admin)
- Lihat progress tiap user

### Manajemen Materi
- **CRUD Kategori:**
  - Tambah, edit, hapus kategori & sub-kategori
  - Urutkan tampilan kategori
- **CRUD Materi:**
  - Tambah materi (judul, deskripsi, link YouTube, resource, kategori, sub-kategori, urutan, tag)
  - Edit materi
  - Hapus materi
  - **Draft → Publish toggle**
  - Preview materi sebelum publish

---

## 6. 🎨 Tampilan

### Gaya
- LMS look-and-feel yang familiar (seperti Udemy, Coursera, Dicoding)
- **Layout:**
  - **Header** — logo, search bar, profil user
  - **Sidebar** — navigasi kategori
  - **Main content** — grid card untuk daftar materi
  - **Dashboard user** — progress, bookmark, riwayat
- **Mobile responsif**

### Warna
- Pakai **Tailwind CSS** — bisa kustomisasi tema
- Skema warna modern, nyaman dibaca

### Halaman yang Akan Dibuat
1. **Landing/Home** — daftar kategori, materi unggulan
2. **Register** — form registrasi + pilih security question
3. **Login** — form login
4. **Lupa Password** — input email → jawab security question → reset password
5. **Dashboard User** — progress, bookmark, riwayat nonton
6. **Kategori** — daftar sub-kategori dalam satu kategori
7. **Sub-Kategori** — daftar materi + progress bar
8. **Detail Materi** — video YouTube + deskripsi + resource + tombol selesai
9. **Profil User** — edit nama, avatar, bio, email
10. **Search Results** — hasil pencarian materi
11. **Admin Dashboard** — statistik keseluruhan
12. **Admin → Manage Users** — tabel user + aksi
13. **Admin → Manage Categories** — CRUD kategori & sub-kategori
14. **Admin → Manage Materials** — daftar materi + draft/publish toggle

---

## 7. 🚀 Deployment

### Platform
- **Railway.app**
- **Custom Domain** dari Railway (subdomain `*.railway.app` atau domain sendiri)
- **Docker** container untuk deploy

### Database
- **PostgreSQL** (Railway PostgreSQL plugin)
- Migration pakai **SQLAlchemy** + **Alembic**

### Persiapan
- Dockerfile untuk app FastAPI
- `railway.json` untuk konfigurasi deploy
- Environment variables: `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`

---

## 8. 📁 Struktur Folder (Rencana)

```
study-data-ikanx101/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings & env vars
│   ├── database.py          # DB connection & session
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py          # User, SecurityQuestion
│   │   ├── category.py      # Category, SubCategory
│   │   ├── material.py      # Material
│   │   ├── progress.py      # UserProgress
│   │   └── bookmark.py      # Bookmark
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── material.py
│   │   └── auth.py
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── categories.py
│   │   ├── materials.py
│   │   ├── progress.py
│   │   ├── bookmarks.py
│   │   └── admin.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── material_service.py
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── materials/
│   │   ├── profile/
│   │   └── admin/
│   └── static/              # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── img/
├── migrations/              # Alembic migrations
├── Dockerfile
├── docker-compose.yml       # Local dev
├── railway.json
├── requirements.txt
└── pyproject.toml
```

---

## 9. ⚙️ Fitur Tambahan (Nice-to-Have — Post Launch)

- Dark mode toggle
- Quiz/soal per materi
- Sertifikat kelar per kategori
- Forum diskusi tiap materi
- Notifikasi (email reminder belajar)
- Fitur export progress

---

## 10. ✅ Checklist Implementasi

- [ ] Setup project: FastAPI + Tailwind + HTMX
- [ ] PostgreSQL database + models (Alembic migration)
- [ ] Auth: Register, Login, JWT, Logout
- [ ] Security question flow: set saat register, verify saat lupa password
- [ ] Role-based access: user vs admin (superadmin)
- [ ] CRUD Kategori & Sub-Kategori (admin)
- [ ] CRUD Materi + draft/publish (admin)
- [ ] Embed YouTube + resource upload
- [ ] Dashboard user: progress, bookmark, riwayat
- [ ] Tandai selesai + progress bar
- [ ] Search & bookmark materi
- [ ] Profil user (nama, avatar, email, bio)
- [ ] Admin panel: statistik, manage user, manage materi
- [ ] Tampilan LMS (Tailwind, responsive, sidebar, card-grid)
- [ ] Dockerfile + railway.json
- [ ] Deploy ke Railway + custom domain
