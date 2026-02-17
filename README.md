# 🎵 LightMusic API

Backend API untuk aplikasi pemutar musik Android **LightMusic**, dibangun di atas [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/) — unofficial API untuk YouTube Music.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-green?style=flat-square)](https://flask.palletsprojects.com)
[![ytmusicapi](https://img.shields.io/badge/ytmusicapi-1.11.5-red?style=flat-square)](https://ytmusicapi.readthedocs.io)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple?style=flat-square)](https://railway.app)

---

## 📋 Daftar Isi

- [Tentang](#tentang)
- [Stack](#stack)
- [Instalasi](#instalasi)
- [Autentikasi ytmusicapi](#autentikasi-ytmusicapi)
- [Menjalankan Lokal](#menjalankan-lokal)
- [API Endpoints](#api-endpoints)
- [Deploy ke Railway](#deploy-ke-railway)
- [Struktur Folder](#struktur-folder)

---

## Tentang

LightMusic API adalah REST API yang membungkus **ytmusicapi** dan **yt-dlp** untuk menyediakan:

- 🔍 Pencarian lagu, artis, album dari YouTube Music
- 🎵 Metadata detail lagu
- 📡 Stream URL audio langsung
- 📥 Download file audio (.m4a)
- 🎤 Lirik lagu
- 📊 Chart musik per negara

> **Catatan:** ytmusicapi adalah library tidak resmi yang mengemulasi request browser YouTube Music. Tidak berafiliasi dengan Google atau YouTube.

---

## Stack

| Komponen | Teknologi |
|---|---|
| Framework | Flask |
| Music API | ytmusicapi |
| Audio Extract | yt-dlp |
| Deploy | Railway |
| Runtime | Python 3.10+ |

---

## Instalasi

### Prasyarat

- Python 3.10 atau lebih baru
- pip
- Git

### Clone & Setup

```bash
# Clone repository
git clone https://github.com/username/lightmusic-api.git
cd lightmusic-api

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### requirements.txt

```
flask
ytmusicapi
yt-dlp
flask-caching
python-dotenv
gunicorn
requests
```

---

## Autentikasi ytmusicapi

ytmusicapi mendukung dua mode: **publik** (tanpa login) dan **autentikasi** (dengan akun YouTube).

### Mode Publik (Tanpa Login)

Cukup untuk search, chart, metadata, dan stream. Tidak perlu setup apapun:

```python
from ytmusicapi import YTMusic
ytm = YTMusic()  # langsung bisa dipakai
```

### Mode Autentikasi — Browser Headers

Diperlukan untuk akses library pribadi, playlist, dan histori.

1. Buka **https://music.youtube.com** dan pastikan sudah login
2. Tekan `Ctrl+Shift+I` → tab **Network**
3. Filter request dengan kata `/browse`
4. Klik salah satu request → tab **Headers** → copy semua **Request Headers**
5. Jalankan perintah ini:

```python
import ytmusicapi
ytmusicapi.setup(filepath="browser.json", headers_raw="<PASTE HEADERS DI SINI>")
```

6. File `browser.json` akan dibuat. Gunakan saat inisialisasi:

```python
from ytmusicapi import YTMusic
ytm = YTMusic("browser.json")
```

> Kredensial ini valid selama sesi browser YouTube Music aktif (sekitar 2 tahun selama tidak logout).

### Mode Autentikasi — OAuth

Direkomendasikan untuk penggunaan jangka panjang. Memerlukan Google Cloud Console.

```bash
# Mulai flow OAuth dari terminal
ytmusicapi oauth
```

```python
from ytmusicapi import YTMusic, OAuthCredentials

ytm = YTMusic(
    'oauth.json',
    oauth_credentials=OAuthCredentials(
        client_id="CLIENT_ID_KAMU",
        client_secret="CLIENT_SECRET_KAMU"
    )
)
```

> Lihat panduan lengkap: [OAuth authentication](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html)

---

## Menjalankan Lokal

```bash
# Pastikan virtual environment aktif
python app.py
```

Server berjalan di: `http://localhost:5000`

Test endpoint:
```
http://localhost:5000/
http://localhost:5000/search?q=dewa19
http://localhost:5000/charts?country=ID
```

---

## API Endpoints

Base URL lokal: `http://localhost:5000`  
Base URL production: `https://lightmusic.up.railway.app`

---

### `GET /`

Info API dan daftar endpoint.

**Response:**
```json
{
  "Sumber": "https://ytmusicapi.readthedocs.io/en/stable/index.html",
  "app": "LightMusic API",
  "dev": "natgul",
  "endpoints": [
    "GET /search?q=query&type=songs",
    "GET /song/\u003Cvideo_id\u003E",
    "GET /stream/\u003Cvideo_id\u003E",
    "GET /lyrics/\u003Cvideo_id\u003E",
    "GET /charts?country=ID"
  ],
  "version": "1.0"
}
```

---

### `GET /search`

Cari lagu, artis, atau album dari YouTube Music.

**Query Parameters:**

| Parameter | Tipe | Wajib | Default | Keterangan |
|---|---|---|---|---|
| `q` | string | ✅ | - | Kata kunci pencarian |
| `type` | string | ❌ | `songs` | `songs` / `artists` / `albums` / `playlists` |
| `limit` | integer | ❌ | `20` | Jumlah hasil (max 40) |

**Contoh Request:**
```
GET /search?q=dewa19&type=songs&limit=10
```

**Contoh Response:**
```json
{
  "status": "success",
  "message": "Ditemukan 10 hasil",
  "data": [
    {
      "id": "kXQRVbRfF4s",
      "title": "Separuh Nafas",
      "artist": "Dewa 19",
      "album": "Bintang Lima",
      "duration": "4:32",
      "thumbnail": "https://lh3.googleusercontent.com/..."
    }
  ]
}
```

---

### `GET /song/<video_id>`

Ambil detail metadata sebuah lagu.

**Contoh Request:**
```
GET /song/kXQRVbRfF4s
```

**Contoh Response:**
```json
{
  "status": "success",
  "data": {
    "id": "kXQRVbRfF4s",
    "title": "Separuh Nafas",
    "artist": "Dewa 19",
    "duration": 272,
    "thumbnail": "https://...",
    "description": "..."
  }
}
```

---

### `GET /stream/<video_id>`

Ambil URL stream audio. URL ini expire dalam beberapa jam.

**Contoh Request:**
```
GET /stream/kXQRVbRfF4s
```

**Contoh Response:**
```json
{
  "status": "success",
  "data": {
    "stream_url": "https://rr1---sn-...googlevideo.com/videoplayback?...",
    "mimeType": "opus",
    "bitrate": 131526,
    "ext": "webm",
    "duration": 272,
    "title": "Separuh Nafas"
  }
}
```

---

### `GET /play/<video_id>`

**Proxy audio stream langsung.** Cocok dipakai di Flutter `just_audio` — tidak perlu extract URL di sisi client.

```
GET /play/kXQRVbRfF4s
```

Penggunaan di Flutter:
```dart
await audioPlayer.setUrl('https://lightmusic.up.railway.app/play/kXQRVbRfF4s');
```

---

### `GET /lyrics/<video_id>`

Ambil lirik lagu.

**Contoh Request:**
```
GET /lyrics/kXQRVbRfF4s
```

**Contoh Response:**
```json
{
  "status": "success",
  "data": {
    "lyrics": "Masih seperti dulu...",
    "source": "YouTube Music"
  }
}
```

---

### `GET /charts`

Top chart lagu per negara.

**Query Parameters:**

| Parameter | Tipe | Default | Keterangan |
|---|---|---|---|
| `country` | string | `ID` | Kode negara ISO 3166-1 alpha-2 |

**Contoh Request:**
```
GET /charts?country=ID
```

**Contoh Response:**
```json
{
  "status": "success",
  "data": {
    "country": "ID",
    "top_songs": [
      {
        "id": "abc123",
        "title": "Judul Lagu",
        "artist": "Nama Artis",
        "thumbnail": "https://...",
        "rank": 1
      }
    ]
  }
}
```

---

## Deploy ke Railway

### 1. Buat Procfile

```
web: gunicorn app:app
```

### 2. Push ke GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/username/lightmusic-api.git
git push -u origin main
```

### 3. Deploy

1. Buka [railway.app](https://railway.app) → login dengan GitHub
2. **New Project** → **Deploy from GitHub repo**
3. Pilih repo `lightmusic-api`
4. Tunggu build selesai
5. **Settings** → **Networking** → **Generate Domain**

### 4. Environment Variables (Opsional)

Jika menggunakan cookies untuk autentikasi yt-dlp, tambahkan di Railway:

```
YT_COOKIES = <isi file cookies.txt>
```

---

## Struktur Folder

```
lightmusic-api/
├── app.py                  ← Entry point Flask
├── Procfile                ← Konfigurasi Railway
├── requirements.txt
├── .env                    ← Environment variables (tidak di-commit)
├── cookies.txt             ← YouTube cookies (tidak di-commit)
│
├── routes/
│   ├── search.py           ← GET /search
│   ├── song.py             ← GET /song/:id
│   ├── stream.py           ← GET /stream/:id & /play/:id
│   ├── lyrics.py           ← GET /lyrics/:id
│   └── charts.py           ← GET /charts
│
├── services/
│   └── ytmusic.py          ← Wrapper ytmusicapi
│
└── utils/
    └── response.py         ← Format response JSON standar
```

---

## Referensi

- [ytmusicapi Documentation](https://ytmusicapi.readthedocs.io/en/stable/)
- [ytmusicapi GitHub](https://github.com/sigma67/ytmusicapi)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [Flask Documentation](https://flask.palletsprojects.com)

---

## Lisensi

MIT License — bebas digunakan untuk keperluan pribadi maupun komersial.
