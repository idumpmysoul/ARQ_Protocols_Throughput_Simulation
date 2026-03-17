import socket
import random
import time
import os

# Ambil parameter dari environment variable (agar bisa diatur oleh orchestrator)
PER = float(os.getenv(PER, 0.1))
DELAY = float(os.getenv(DELAY, 0.001))

# Port konfigurasi
SENDER_ADDR = (sender, 5000)
RECEIVER_ADDR = (receiver, 6000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((0.0.0.0, 7000)) # Channel listen di port 7000

print(f"Channel active with PER={PER}, DELAY={DELAY}")

while True:
    data, addr = sock.recvfrom(4096)
    
    # Simulasi Packet Loss
    if random.random() > PER:
        time.sleep(DELAY) # Simulasi Latensi kabel
        
        # Arahkan paket: Jika dari sender ke receiver, dan sebaliknya
        if addr[0] == socket.gethostbyname(sender):
            sock.sendto(data, RECEIVER_ADDR)
        else:
            sock.sendto(data, SENDER_ADDR)
