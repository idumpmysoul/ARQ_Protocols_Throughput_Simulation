import socket
import time
import os

PER = float(os.getenv(PER, 0.1))
PACKETS_TO_SEND = 1000
WINDOW_SIZE = 5
TIMEOUT = 0.05 # 50ms timeout

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((0.0.0.0, 5000))
sock.settimeout(TIMEOUT)

base = 0
next_seq_num = 0
acked = [False] * PACKETS_TO_SEND

start_time = time.time()

while base < PACKETS_TO_SEND:
    # Kirim paket dalam window
    while next_seq_num < base + WINDOW_SIZE and next_seq_num < PACKETS_TO_SEND:
        sock.sendto(str(next_seq_num).encode(), (channel, 7000))
        next_seq_num += 1
    
    try:
        # Tunggu ACK
        data, addr = sock.recvfrom(4096)
        ack_id = int(data.decode().split(":")[1])
        if ack_id >= base:
            acked[ack_id] = True
            # Geser window
            while base < PACKETS_TO_SEND and acked[base]:
                base += 1
    except socket.timeout:
        # Jika timeout, kirim ulang paket base saja (Selective Reject)
        next_seq_num = base 

end_time = time.time()
throughput = (PACKETS_TO_SEND) / (end_time - start_time)

# Simpan hasil ke file yang bisa dibaca Orchestrator
with open("/results/output.txt", "a") as f:
    f.write(f"{PER},{throughput}\n")
