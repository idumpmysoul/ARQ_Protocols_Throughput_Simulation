# ARQ Protocol Network Testbed (Docker-Based Simulation)

Proyek ini adalah emulator jaringan berbasis kontainer untuk mensimulasikan protokol **Automatic Repeat Request (ARQ)**. Berbeda dengan simulasi matematis biasa, sistem ini menjalankan **infrastruktur nyata** di mana paket data benar-benar dikirim melalui *network stack* sistem operasi menggunakan socket UDP.

## 🚀 Fitur Utama
- **Real Traffic Simulation**: Data dikirim antar kontainer terpisah (Sender, Channel, Receiver).
- **Network Emulation**: Kontainer `channel` secara aktif memberikan latensi (delay) dan menjatuhkan paket secara acak berdasarkan *Packet Error Ratio* (PER).
- **Log-Based Data Capture**: Menggunakan teknik *stdout interception* untuk mengumpulkan data throughput tanpa hambatan izin akses file (*file permission*) di Linux.
- **Automated Orchestration**: Melakukan pengujian otomatis untuk berbagai tingkat gangguan jaringan (PER).

## 🏗️ Arsitektur Sistem
1.  **Sender (Logic Engine)**: Mengimplementasikan protokol ARQ (saat ini: *Selective Reject*). Mengelola nomor urut, *timer retransmission*, dan *sliding window*.
2.  **Channel (Network Emulator)**: Bertindak sebagai perantara (*Man-in-the-Middle*). Memberikan latensi (1ms) dan membuang paket berdasarkan probabilitas PER yang ditentukan.
3.  **Receiver (The Sink)**: Menerima paket, mendeteksi paket duplikat, dan menghasilkan ACK untuk dikirim kembali ke Pengirim.

## 📋 Prasyarat
- **Docker** & **Docker Compose** (Versi terbaru V2 direkomendasikan).
- **Python 3.x** pada mesin host.
- Library Python: `matplotlib` (untuk visualisasi grafik).

## 📂 Struktur Proyek
```text
arq_simulation/
├── channel/        # Kode Emulator Jaringan & Dockerfile
├── receiver/       # Kode Endpoint Penerima & Dockerfile
├── sender/         # Kode Logika Protokol & Dockerfile
├── results/        # Folder output data mentah (CSV)
├── orchestrator.py # Script utama pengatur simulasi
└── README.md       # Dokumentasi proyek
```

## 🛠️ Cara Menjalankan

### 1. Persiapan Folder
Pastikan Anda berada di folder utama proyek dan beri izin akses pada folder hasil:
```bash
chmod -R 777 results/
```

### 2. Jalankan Simulasi Otomatis
Gunakan orchestrator untuk menjalankan seluruh skenario (PER 0.01, 0.1, 0.5):
```bash
python3 orchestrator.py
```
*Script ini akan membangun image Docker, menjalankan kontainer, menangkap log output dari Sender, dan menyimpan data ke `results/output.txt`.*

### 3. Visualisasi Hasil
Data mentah disimpan di `results/output.txt` 
Silakan input data mentah ke Google Colab berikut : https://colab.research.google.com/drive/1MqfSBydWb3wPP63s8PxfGgRcCMCL0wb1?usp=sharing
