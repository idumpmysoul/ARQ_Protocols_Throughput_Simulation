import subprocess
import os
import time

# 1. Pastikan folder results ada
if not os.path.exists("results"):
    print("Membuat folder results...")
    os.makedirs("results")

pers = [0.01, 0.1, 0.5] # Test dengan 3 titik dulu
output_path = "results/output.txt"

# 2. Hapus file lama agar tidak tercampur data lama
if os.path.exists(output_path):
    os.remove(output_path)

for per in pers:
    print(f"--- Menjalankan Simulasi PER: {per} ---")
    
    # Set environment variable untuk Docker
    env = os.environ.copy()
    env["PER"] = str(per)
    
    # Jalankan Docker Compose
    # Gunakan 'docker-compose' (dengan strip) jika versi lama, 
    # atau 'docker', 'compose' jika versi baru.
    process = subprocess.run(["docker-compose", "up", "--build", "--abort-on-container-exit"], env=env)
    
    if process.returncode != 0:
        print(f"Peringatan: Docker Compose keluar dengan error pada PER {per}")

# 3. BERI JEDA agar OS sempat sinkronisasi file dari Docker
time.sleep(2)

# 4. CEK SEBELUM BUKA (Baris yang tadi error)
if not os.path.exists(output_path):
    print(f"\nERROR KRITIS: File '{output_path}' tidak ditemukan!")
    print("Kemungkinan penyebab:")
    print("1. Volume mapping di docker-compose.yml salah.")
    print("2. Script sender.py di dalam Docker gagal menulis ke folder /results.")
    print("3. Kontainer sender mati sebelum sempat menulis file.")
else:
    with open(output_path, "r") as f:
        print("\nBerhasil membaca data:")
        print(f.read())
