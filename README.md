# **Penjelasan Kode**

# 01 — Cara Menjalankan & Logika Kode Simulasi ARQ

## Prasyarat

Sebelum menjalankan simulasi, pastikan perangkat sudah terinstal:

| Perangkat | Versi Minimum | Keterangan |
|---|---|---|
| Docker Desktop / Docker Engine | 24.x | Runtime container |
| Docker Compose | v2 (sudah bundled di Docker Desktop) | Orkestrasi multi-container |
| Python | 3.9+ | Menjalankan `orchestrator.py` |

Verifikasi instalasi dengan perintah berikut di terminal:

```bash
docker --version
docker compose version
python3 --version
```

---

## Struktur Direktori

```
ARQ_Protocols_Throughput_Simulation/
├── docker-compose.yml       ← Definisi semua service container
├── orchestrator.py          ← Script utama yang menjalankan simulasi berulang
├── results/
│   └── output.txt           ← Hasil throughput tiap nilai PER
├── channel/
│   ├── Dockerfile
│   └── channel.py           ← Simulasi kanal dengan packet loss
├── receiver/
│   ├── Dockerfile
│   └── receiver.py          ← Penerima paket, mengirim ACK
└── sender/
    ├── Dockerfile
    └── sender.py            ← Pengirim paket, menerapkan SR-ARQ
```

---

## Cara Menjalankan

### Langkah 1 — Clone atau siapkan direktori

Pastikan semua file sudah berada di struktur direktori di atas.

### Langkah 2 — Jalankan orchestrator

Masuk ke folder root proyek, lalu jalankan:

```bash
cd ~/Documents/ARQ_Protocols_Throughput_Simulation
python3 orchestrator.py
```

Orchestrator akan otomatis menjalankan Docker Compose sebanyak 6 kali (satu per nilai PER), lalu menyimpan hasil ke `results/output.txt`.

### Langkah 3 — Lihat hasil

```bash
cat results/output.txt
```

Format file output adalah `PER,throughput_pkt_per_detik`, contoh:

```
0.01,487.23
0.05,401.55
0.1,312.44
0.2,198.67
0.3,130.21
0.5,56.83
```

### Langkah 4 — Plot grafik di Google Colab

1. Buka https://colab.research.google.com/drive/1MqfSBydWb3wPP63s8PxfGgRcCMCL0wb1?usp=sharing
2. Jalankan semua cell dari atas ke bawah
3. Pada cell upload, unggah file `results/output.txt`
4. Grafik akan muncul dan tersimpan sebagai `arq_throughput.png`

---

## Logika Kode — Penjelasan Per Komponen

### `channel.py` — Simulasi Kanal Tidak Sempurna

Channel adalah jantung dari simulasi ini. Tugasnya adalah meniru perilaku kanal komunikasi nyata yang bisa menjatuhkan (drop) paket secara acak.

```python
PER = float(os.getenv('PER', 0.1))   # Packet Error Ratio, diambil dari env variable
DELAY = float(os.getenv('DELAY', 0.001))  # Propagation delay buatan (1 ms)
```

Channel mendengarkan di port `7000`. Setiap paket yang masuk akan:

1. Dicek apakah harus di-drop: `if random.random() < PER` — jika nilai acak lebih kecil dari PER, paket dibuang begitu saja.
2. Jika lolos, ditunda selama `DELAY` detik untuk mensimulasikan propagation delay.
3. Diteruskan ke arah yang tepat — jika datang dari sender, dikirim ke receiver (port 6000), dan sebaliknya.

```python
if addr[0] == sender_ip:
    sock.sendto(data, ('receiver', 6000))
else:
    sock.sendto(data, ('sender', 5000))
```

Channel menggunakan **lazy DNS resolution** — IP sender dan receiver baru di-resolve saat paket pertama kali masuk, bukan saat startup, sehingga tidak terjadi error DNS jika container lain belum sepenuhnya siap.

---

### `receiver.py` — Penerima Paket

Receiver mendengarkan di port `6000`. Logikanya sederhana:

1. Menerima paket dari channel.
2. Mencatat ID paket ke dalam `set` (sehingga duplikat diabaikan otomatis).
3. Mengirim ACK kembali ke channel: `ACK:{packet_id}`.

```python
received_ids = set()
...
if packet_id not in received_ids:
    received_ids.add(packet_id)
...
sock.sendto(f"ACK:{packet_id}".encode(), ('channel', 7000))
```

Receiver berjalan terus-menerus (`while True`) dan hanya berhenti ketika container-nya dihentikan oleh Docker.

---

### `sender.py` — Implementasi Selective Reject (SR) ARQ

Ini adalah komponen paling penting. Sender mengimplementasikan **Sliding Window** dengan logika **Selective Reject**, yaitu hanya mengirim ulang paket yang benar-benar hilang, bukan seluruh window.

```python
PACKETS_TO_SEND = 1000
WINDOW_SIZE = 50    # Window besar agar mendekati throughput teoritis SR-ARQ
TIMEOUT = 0.05      # ~3x delay kanal, menghindari timeout palsu
```

**Mekanisme Sliding Window:**

```python
# Isi window dengan paket baru
while next_seq_num < base + WINDOW_SIZE and next_seq_num < PACKETS_TO_SEND:
    sock.sendto(str(next_seq_num).encode(), ('channel', 7000))
    next_seq_num += 1
```

Sender terus mengisi window hingga `WINDOW_SIZE` paket sedang dalam perjalanan secara bersamaan (in-flight).

**Penerimaan ACK dan penggeseran base:**

```python
acked[ack_id] = True
while base < PACKETS_TO_SEND and acked[base]:
    base += 1
```

Base window hanya bergeser maju jika paket di posisi `base` sudah di-ACK. Ini adalah perilaku khas SR-ARQ — window tidak bergerak sampai paket paling awal dikonfirmasi.

**Selective retransmit saat timeout:**

```python
except socket.timeout:
    for seq in range(base, min(base + WINDOW_SIZE, PACKETS_TO_SEND)):
        if not acked[seq]:
            sock.sendto(str(seq).encode(), ('channel', 7000))
```

Inilah perbedaan utama SR-ARQ vs Go-Back-N. Saat timeout, sender hanya mengirim ulang paket yang `acked[seq] == False`, bukan seluruh window dari awal.

---

### `orchestrator.py` — Pengulang Simulasi Otomatis

Orchestrator menjalankan simulasi secara berulang untuk setiap nilai PER yang berbeda:

```python
pers = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5]
```

Untuk setiap iterasi:

1. Menjalankan `docker compose down` terlebih dahulu untuk memastikan tidak ada container sisa dari run sebelumnya.
2. Menjalankan `docker compose up --build --exit-code-from sender` — simulasi dianggap selesai ketika container sender exit.
3. Membaca stdout secara real-time dan mencari token `FINAL_RESULT:PER:THROUGHPUT`.
4. Menyimpan semua data ke `results/output.txt` setelah semua iterasi selesai.

---

### `docker-compose.yml` — Jaringan Antar Container

```yaml
services:
  channel:
    build: ./channel
    environment:
      - PER=${PER:-0.1}
      - DELAY=${DELAY:-0.001}

  receiver:
    build: ./receiver
    depends_on:
      - channel

  sender:
    build: ./sender
    environment:
      - PER=${PER:-0.1}
    volumes:
      - "./results:/results"
    depends_on:
      - channel
      - receiver
```

Docker Compose secara otomatis membuat **Docker network** internal sehingga ketiga container bisa saling berkomunikasi menggunakan nama hostname (`sender`, `receiver`, `channel`) tanpa perlu mengetahui IP secara manual. Nilai `PER` diteruskan sebagai environment variable dari host ke dalam container.

---

## Mengapa Kode Ini Menjadi Contoh yang Baik?

### 1. Isolasi yang nyata dengan Docker
Setiap komponen (sender, channel, receiver) berjalan dalam container terpisah. Ini mencerminkan arsitektur jaringan nyata di mana setiap node adalah entitas independen yang berkomunikasi lewat kanal fisik.

### 2. Kanal yang realistis
`channel.py` mensimulasikan dua karakteristik kanal nyata sekaligus: **packet loss** (PER) dan **propagation delay** (DELAY). Tanpa channel sebagai perantara, simulasi tidak akan mencerminkan kondisi jaringan yang sebenarnya.

### 3. Implementasi SR-ARQ yang akurat
Sliding window + selective retransmit adalah implementasi yang benar dari protokol SR-ARQ. Sender tidak membuang-buang bandwidth dengan mengirim ulang seluruh window seperti Go-Back-N, melainkan hanya menambal paket yang benar-benar hilang.

### 4. Kontrol variabel yang bersih
Nilai PER diinjeksikan sebagai environment variable, sehingga kode simulasi tidak perlu diubah sama sekali antar run. Orchestrator cukup mengubah satu variabel dan Docker Compose meneruskannya ke semua container yang membutuhkan.

### 5. Hasil terukur dan dapat diplot
Output `FINAL_RESULT` dicetak ke stdout dengan format yang konsisten, sehingga mudah di-parse dan diplot menjadi grafik perbandingan dengan kurva teoritis.
