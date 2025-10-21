import socket
import threading

def receive_messages(sock):
    while True:
        data = sock.recv(1024)
        print("\nFriend:", data.decode())

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5555))

threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

while True:
    msg = input("You: ")
    sock.send(msg.encode())