import socket
import time
import os

PER = float(os.getenv('PER', 0.1))
PACKETS_TO_SEND = 1000
WINDOW_SIZE = 50       # Large window to approach SR-ARQ theoretical throughput
TIMEOUT = 0.05         # Tuned to ~3x channel DELAY (0.001s) to avoid spurious retransmits

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5000))
sock.settimeout(TIMEOUT)

base = 0
next_seq_num = 0
acked = [False] * PACKETS_TO_SEND
start_time = time.time()

print(f"Sender: Simulation started for PER={PER}", flush=True)

while base < PACKETS_TO_SEND:
    # Fill the window
    while next_seq_num < base + WINDOW_SIZE and next_seq_num < PACKETS_TO_SEND:
        try:
            sock.sendto(str(next_seq_num).encode(), ('channel', 7000))
            next_seq_num += 1
        except Exception:
            break

    # Wait for ACK
    try:
        data, addr = sock.recvfrom(4096)
        msg = data.decode().strip()
        if "ACK:" in msg:
            ack_id = int(msg.split(":")[1])
            if 0 <= ack_id < PACKETS_TO_SEND:
                acked[ack_id] = True
                # Slide base forward over all consecutively acked packets
                while base < PACKETS_TO_SEND and acked[base]:
                    base += 1
    except socket.timeout:
        # Selective retransmit: only resend un-acked packets in the window
        for seq in range(base, min(base + WINDOW_SIZE, PACKETS_TO_SEND)):
            if not acked[seq]:
                try:
                    sock.sendto(str(seq).encode(), ('channel', 7000))
                except Exception:
                    pass

duration = time.time() - start_time
throughput = PACKETS_TO_SEND / duration

print(f"FINAL_RESULT:{PER}:{throughput:.4f}", flush=True)
print(f"Sender: Done. Duration={duration:.2f}s, Throughput={throughput:.2f} pkt/s", flush=True)
