# ARQ Protocol Infrastructure Simulation (Docker-Based)

Proyek ini mensimulasikan protokol ARQ (Automatic Repeat Request) menggunakan infrastruktur jaringan nyata yang diwadahi oleh Docker. Simulasi ini tidak hanya memplot rumus matematis, tetapi menjalankan mesin protokol nyata (Sender, Channel Emulator, dan Receiver) untuk mengamati performa throughput terhadap gangguan jaringan.

## Arsitektur Sistem
1. **Sender Service**: Menjalankan logika ARQ (Selective Reject) menggunakan socket UDP.
2. **Channel Service**: Berperan sebagai network emulator yang memberikan latensi (delay) dan menjatuhkan paket secara acak (Packet Error Ratio/PER).
3. **Receiver Service**: Endpoint tujuan yang menerima paket dan mengirimkan ACK kembali ke Sender.

## Prasyarat
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- [Python 3.x](https://www.python.org/downloads/) installed on your host machine.
- Library Python: `matplotlib` (untuk plotting hasil).

## Cara Menjalankan

### 1. Persiapan Awal
Pastikan Docker sudah aktif di komputer Anda. Install library untuk plotting:
```bash
pip install matplotlib
```

### 2. Menjalankan Simulasi Otomatis
Gunakan script `orchestrator.py` untuk menjalankan seluruh rangkaian pengujian (dari PER 0.01 hingga 1.0):
```bash
python orchestrator.py
```
Script ini akan secara otomatis:
- Mengonfigurasi parameter jaringan pada Docker.
- Menjalankan kontainer menggunakan `docker-compose`.
- Mengumpulkan data throughput dari setiap percobaan.
- Menghasilkan grafik hasil akhir.

### 3. Melihat Hasil Manual
Data mentah hasil simulasi disimpan di folder `results/output.txt` dalam format CSV (`PER, Throughput`).

## Parameter Simulasi
- **Packet Size**: 1514 Bytes.
- **Capacity**: 6 Mbps.
- **Latency**: 1ms.
- **Target Packets**: 1000 sukses per titik data.

---

### Bagian 4: Cara Menjalankan Pertama Kali

Setelah semua file siap, ikuti langkah ini:

1.  **Buka Terminal** dan masuk ke folder `arq_simulation`.
2.  **Uji Coba Satu Kali (Dry Run):**
    Coba jalankan Docker secara manual untuk melihat apakah kontainer bisa saling "berbicara":
    ```bash
    export PER=0.1 && docker compose up --build
    ```
    *(Jika di Windows PowerShell, gunakan `$env:PER=0.1; docker-compose up --build`)*
3.  **Lihat Log:** Perhatikan log di terminal. Kamu harus melihat `channel` membuang paket dan `sender` melakukan retransmisi.
4.  **Jalankan Orchestrator:**
    Jika uji coba manual sukses, tekan `Ctrl+C` untuk berhenti, lalu jalankan simulasi penuh:
    ```bash
    python orchestrator.py
    ```

**Tips Troubleshooting:**
- Jika `orchestrator.py` gagal menjalankan docker, pastikan perintah di dalam script menggunakan `docker-compose` atau `docker compose` (sesuaikan dengan versi yang terinstall di PC-mu).
- Jika grafik tidak muncul, pastikan kamu menjalankan terminal di lingkungan yang mendukung GUI (seperti VS Code atau Terminal bawaan, bukan lingkungan remote murni).
