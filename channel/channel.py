import socket
import random
import time
import os

PER = float(os.getenv('PER', 0.1))
DELAY = float(os.getenv('DELAY', 0.001))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 7000))

print(f"Channel active with PER={PER}", flush=True)

sender_ip = None
receiver_ip = None

while True:
    try:
        data, addr = sock.recvfrom(4096)

        # Resolve lazily so DNS is ready after containers start
        if sender_ip is None:
            try:
                sender_ip = socket.gethostbyname('sender')
            except Exception:
                pass
        if receiver_ip is None:
            try:
                receiver_ip = socket.gethostbyname('receiver')
            except Exception:
                pass

        # Drop packet with probability PER
        if random.random() < PER:
            continue

        time.sleep(DELAY)

        if addr[0] == sender_ip:
            sock.sendto(data, ('receiver', 6000))
        else:
            sock.sendto(data, ('sender', 5000))

    except Exception:
        continue
