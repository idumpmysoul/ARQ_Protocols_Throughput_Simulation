import subprocess
import os
import matplotlib.pyplot as plt

# Range PER yang akan diuji
pers = [0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
results = []

# Bersihkan hasil lama
if os.path.exists("results/output.txt"):
    os.remove("results/output.txt")

for per in pers:
    print(f"Running simulation for PER={per}...")
    # Jalankan docker-compose dengan environment variable PER
    env = os.environ.copy()
    env["PER"] = str(per)
    subprocess.run(["docker-compose", "up", "--abort-on-container-exit"], env=env)

# Baca hasil
per_data = []
thr_data = []
with open("results/output.txt", "r") as f:
    for line in f:
        p, t = line.strip().split(",")
        per_data.append(float(p))
        # Normalisasi throughput (misal dibagi max throughput yang didapat)
        thr_data.append(float(t))

# Normalisasi sederhana agar S berada di antara 0-1
max_t = max(thr_data)
s_data = [t/max_t for t in thr_data]

# Plotting
plt.plot(per_data, s_data, 'bo-')
plt.xscale('log')
plt.xlabel('Packet Error Ratio')
plt.ylabel('Normalized Throughput (S)')
plt.title('Data Nyata dari Infrastruktur Docker ARQ')
plt.show()
