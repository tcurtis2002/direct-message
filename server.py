import socket
import threading

clients = []

def handle_client(conn, addr):
    print(f"🟢 New connection: {addr}")
    while True:
        try:
            msg = conn.recv(1024)
            if not msg:
                break
            broadcast(msg, conn)
        except:
            clients.remove(conn)
            conn.close()
            break

def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            client.send(message)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen()
    print("🚀 Server started on port 5555. Waiting for clients...")

    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start_server()