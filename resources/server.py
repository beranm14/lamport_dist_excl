import socket
import signal
import sys


def signal_handler(signal, frame):
    s.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 4  # Normally 1024, but we want fast response

global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

while 1:
    conn, addr = s.accept()
    print('Connection address:', addr)
    data = b''
    while 1:
        new_data = conn.recv(BUFFER_SIZE)
        data = data + new_data
        print(new_data[-1:])
        if new_data[-1:] == b'\x00':
            break
        print("received data:", data)
    conn.send(data)  # echo
    print("Data sent:", data)

conn.close()
