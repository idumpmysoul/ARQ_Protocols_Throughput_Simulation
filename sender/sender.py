import socket
import time
import os

PER = float(os.getenv('PER', 0.1))
PACKETS_TO_SEND = 1000
WINDOW_SIZE = 5
TIMEOUT = 0.1 

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5000))
sock.settimeout(TIMEOUT)

base = 0
next_seq_num = 0
acked = [False] * PACKETS_TO_SEND
start_time = time.time()

print(f"Sender: Simulasi dimulai untuk PER={PER}")

while base < PACKETS_TO_SEND:
    while next_seq_num < base + WINDOW_SIZE and next_seq_num < PACKETS_TO_SEND:
        try:
            sock.sendto(str(next_seq_num).encode(), ('channel', 7000))
            next_seq_num += 1
        except: break
    
    try:
        data, addr = sock.recvfrom(4096)
        msg = data.decode()
        if "ACK:" in msg:
            ack_id = int(msg.split(":")[1])
            if ack_id >= base and ack_id < PACKETS_TO_SEND:
                acked[ack_id] = True
                while base < PACKETS_TO_SEND and acked[base]:
                    base += 1
    except socket.timeout:
        next_seq_num = base 

duration = time.time() - start_time
throughput = PACKETS_TO_SEND / duration

# Jangan pakai 'with open', cukup print dengan tanda khusus agar mudah dicari
print(f"FINAL_RESULT:{PER}:{throughput}")
print("Sender: Simulasi selesai.")
