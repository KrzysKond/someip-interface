import socket
import json

def send_json_data(json_data, remote_ip, remote_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = json.dumps(json_data).encode('utf-8')
        sock.sendto(message, (remote_ip, remote_port))
        print("Sent JSON data to remote:", remote_ip, remote_port)
        sock.close()
    except Exception as e:
        print(f"Error sending data: {e}")
