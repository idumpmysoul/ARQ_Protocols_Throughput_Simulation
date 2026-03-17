import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((0.0.0.0, 6000))

expected_packets = 1000
received_count = 0
received_ids = set()

while received_count < expected_packets:
    data, addr = sock.recvfrom(4096)
    packet_id = int(data.decode())
    
    if packet_id not in received_ids:
        received_ids.add(packet_id)
        received_count += 1
    
    # Kirim ACK kembali melalui channel
    sock.sendto(f"ACK:{packet_id}".encode(), (channel, 7000))

print("Receiver finished.")
