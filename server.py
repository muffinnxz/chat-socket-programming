import socket
import threading

def client_thread(conn, addr, all_connections, clients):
    try:
        # First message from the connection is the username
        username = conn.recv(1024).decode('utf-8').strip()
        if username:
            if username in clients:
                # If username is already taken, notify the client and close the connection
                conn.send("Server: Username is already taken, please try again with a different username.".encode('utf-8'))
                conn.close()
                return  # Exit the thread for this connection
            clients[username] = conn
            broadcast(f"Server: {username} has joined the chat!", conn, all_connections, include_self=False)
        else:
            raise Exception("Username cannot be empty")
        
        conn.send("Server: Welcome to the chat room!".encode('utf-8'))
        print(f"User connected: {username} from {addr}")

        while True:
            message = conn.recv(1024).decode('utf-8')
            if message:
                if message.startswith("/whisper"):
                    handle_whisper(message, conn, clients, username)
                else:
                    print(f"Message received from {username}: {message}")
                    broadcast(f"{username}: {message}", conn, all_connections)
            else:
                raise Exception("Client disconnected")
    except Exception as e:
        print(f"Error or disconnection with {username}: {e}")
        remove_connection(conn, all_connections, clients)

def handle_whisper(message, sender_conn, clients, sender_username):
    parts = message.split(maxsplit=2)  # Split into command, username, message
    if len(parts) < 3:
        sender_conn.send("Server: Invalid whisper command. Use /whisper <username> \"<message>\".".encode('utf-8'))
        return
    _, target_username, msg = parts
    receiver_conn = clients.get(target_username)
    if receiver_conn:
        formatted_message = f"(whisper) {sender_username}: {msg}"
        receiver_conn.send(formatted_message.encode('utf-8'))
        sender_conn.send(formatted_message.encode('utf-8'))
    else:
        sender_conn.send(f"Server: No user named {target_username} found.".encode('utf-8'))

def get_username(conn, clients):
    for username, connection in clients.items():
        if connection == conn:
            return username
    return None

def broadcast(message, connection, all_connections, include_self=True):
    for client in all_connections:
        if client != connection or include_self:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message: {e}")

def remove_connection(conn, all_connections, clients):
    if conn in all_connections:
        all_connections.remove(conn)
        username = None
        for user, connection in clients.items():
            if connection == conn:
                username = user
                broadcast(f"Server: {username} has left the chat.", conn, all_connections, include_self=False)
                del clients[username]
                break
        conn.close()
        print(f"Connection with {username if username else 'Unknown'} has been removed.")

def main():
    host = '127.0.0.1'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server started, waiting for connections...")
    all_connections = []
    clients = {}

    while True:
        conn, addr = server_socket.accept()
        all_connections.append(conn)
        print(f"Connected to {addr}")
        
        # Start a new thread to handle the client; the first received message must be the username.
        threading.Thread(target=client_thread, args=(conn, addr, all_connections, clients)).start()

if __name__ == "__main__":
    main()