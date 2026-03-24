import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 6000))

received_ids = set()
print("Receiver ready and waiting...")

# Biarkan berjalan terus, orchestrator yang akan mematikan via sender exit
while True:
    try:
        data, addr = sock.recvfrom(4096)
        packet_id = data.decode()
        
        if packet_id not in received_ids:
            received_ids.add(packet_id)
            if len(received_ids) % 100 == 0:
                print(f"Receiver: Progress {len(received_ids)}/1000")
        
        # Kirim balik ACK
        sock.sendto(f"ACK:{packet_id}".encode(), ('channel', 7000))
    except Exception as e:
        pass # Diam saja jika ada error saat shutdown
