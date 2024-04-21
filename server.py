import socket
import threading

def client_thread(conn, addr, all_connections):
    """
    Handle messages from a client.
    """
    conn.send("Server: Welcome to the chat room!".encode('utf-8'))  # Server welcome message
    while True:
        try:
            # Receiving message from the client
            message = conn.recv(1024).decode('utf-8')
            if message:
                print(f"Message received from {addr}: {message}")
                # Broadcasting message to all clients
                broadcast(f"{message}", conn, all_connections)
            else:
                # Remove connection if no message is received
                remove_connection(conn, all_connections)
                break
        except Exception as e:
            print(f"Error handling message from {addr}: {e}")
            remove_connection(conn, all_connections)
            break

def broadcast(message, connection, all_connections):
    """
    Broadcast messages to all clients including the sender for testing purposes.
    """
    for client in all_connections:
        try:
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error broadcasting to a client: {e}")
            remove_connection(client, all_connections)

def remove_connection(conn, all_connections):
    """
    Remove a client connection from the list.
    """
    if conn in all_connections:
        print(f"Removing connection {conn.getpeername()}")
        conn.close()
        all_connections.remove(conn)

def main():
    host = '127.0.0.1'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server started, waiting for connections...")
    all_connections = []

    while True:
        conn, addr = server_socket.accept()
        all_connections.append(conn)
        print(f"Connected to {addr}")
        threading.Thread(target=client_thread, args=(conn, addr, all_connections)).start()

if __name__ == "__main__":
    main()