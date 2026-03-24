import socket
import random
import time
import os

PER = float(os.getenv('PER', 0.1))
DELAY = float(os.getenv('DELAY', 0.001))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 7000)) 

print(f"Channel active with PER={PER}")

while True:
    try:
        data, addr = sock.recvfrom(4096)
        if random.random() > PER:
            time.sleep(DELAY)
            # Arahkan paket
            if addr[0] == socket.gethostbyname('sender'):
                sock.sendto(data, ('receiver', 6000))
            else:
                sock.sendto(data, ('sender', 5000))
    except Exception:
        continue # Abaikan error jika salah satu host hilang saat shutdown
