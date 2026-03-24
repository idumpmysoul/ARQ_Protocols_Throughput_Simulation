import subprocess
import os
import time

# List untuk menampung data sementara
all_data = []

pers = [0.01, 0.1, 0.5]
output_path = "results/output.txt"

# Pastikan folder results ada
if not os.path.exists("results"):
    os.makedirs("results")

for per in pers:
    print(f"\n--- Menjalankan Simulasi PER: {per} ---")
    env = os.environ.copy()
    env["PER"] = str(per)
    
    # Menjalankan Docker dan menangkap output terminalnya
    cmd = ["docker", "compose", "up", "--build", "--exit-code-from", "sender"]
    
    # subprocess.Popen memungkinkan kita membaca log secara real-time
    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in process.stdout:
        print(line, end="") # Tetap tampilkan log di terminal kamu
        if "FINAL_RESULT:" in line:
            # Jika menemukan tanda khusus, ambil datanya
            # Format: FINAL_RESULT:PER:THROUGHPUT
            data_part = line.split("FINAL_RESULT:")[1].strip()
            per_val, thr_val = data_part.split(":")
            all_data.append(f"{per_val},{thr_val}")

    process.wait()

# Setelah semua simulasi selesai, simpan SEMUA data ke file
print("\n--- Menyimpan Hasil Akhir ---")
with open(output_path, "w") as f:
    for entry in all_data:
        f.write(entry + "\n")

print(f"File '{output_path}' berhasil dibuat dengan {len(all_data)} data point.")

# Panggil fungsi plotting (jika ada di file yang sama atau import)
# ... kode plotting kamu di sini ...
