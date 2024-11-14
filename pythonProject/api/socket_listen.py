import socket
import json

UDP_IP = "0.0.0.0"
UDP_PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received message from {addr}")
    try:
        json_data = json.loads(data.decode('utf-8'))
        print(f"Received JSON data: {json_data}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
