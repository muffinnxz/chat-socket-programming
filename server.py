import socket
import threading
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

def client_thread(conn, addr, all_connections, clients, groups):
    try:
        # First message from the connection is the username
        username = conn.recv(1024).decode("utf-8").strip()
        if username:
            if username in clients:
                conn.send(
                    "Server: Username is already taken, please try again with a different username.".encode(
                        "utf-8"
                    )
                )
                conn.close()
                return
            clients[username] = conn
            broadcast(
                f"Server: {username} has joined the chat!",
                conn,
                all_connections,
                groups,
                include_self=False,
            )
        else:
            raise Exception("Username cannot be empty")

        conn.send("Server: Welcome to the chat room!".encode("utf-8"))
        print(f"User connected: {username} from {addr}")

        while True:
            message = conn.recv(1024).decode("utf-8")
            if message:
                if message.startswith("/whisper"):
                    handle_whisper(message, conn, clients, username)
                elif message.startswith("/list"):
                    # Handle listing users with error check
                    if message.strip() == "/list":
                        list_users(conn, clients)
                    else:
                        conn.send(
                            "Server: Invalid /list command. Use /list without any additional text.".encode(
                                "utf-8"
                            )
                        )
                elif message.startswith("/group"):
                    handle_group_command(message, conn, all_connections, clients, groups)
                elif message.startswith("/chatgpt"):
                    parts = message.split(maxsplit=1)
                    if len(parts) < 2 or not parts[1].strip():  # Check if there's a question part after the command
                        conn.send("Server: Usage: /chatgpt <question> - please provide a question.".encode('utf-8'))
                    else:
                        question = parts[1].strip()
                        response = get_ai_response(question)
                        conn.send(f"(private) {username}: {message}".encode('utf-8'))
                        conn.send(f"ChatGPT: {response}".encode('utf-8'))
                else:
                    print(f"Message received from {username}: {message}")
                    broadcast(f"{username}: {message}", conn, all_connections, groups)
            else:
                raise Exception("Client disconnected")
    except Exception as e:
        print(f"Error or disconnection with {username}: {e}")
        remove_connection(conn, all_connections, clients, groups)

def get_ai_response(question):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content

def handle_group_command(message, conn, all_connections, clients, groups):
    parts = message.split(maxsplit=2)
    command = parts[1]  # The part after "/group"

    if command == "create":
        group_name = parts[2].strip()
        if group_name in groups:
            conn.send("Server: Group already exists.\n".encode('utf-8'))
        else:
            groups[group_name] = [conn]  # Create new group with creator as first member
            conn.send(f"Server: Group '{group_name}' created successfully.\n".encode('utf-8'))
            conn.send(f"Server: You joined the group '{group_name}'.\n".encode('utf-8'))


    elif command == "list":
        group_list = "Available Groups: " + ", ".join(groups.keys()) + "\n"
        conn.send(group_list.encode('utf-8'))

    elif command == "join":
        new_group_name = parts[2].strip()
        if new_group_name not in groups:
            conn.send("Server: Group does not exist.\n".encode('utf-8'))
        else:
            # Remove from any current group
            for group_name, members in groups.items():
                if conn in members:
                    members.remove(conn)
                    broadcast(f"{get_username(conn, clients)} has left the group '{group_name}'.", conn, all_connections, groups, include_self=False)
                    if not members:  # Delete empty groups
                        del groups[group_name]
                    break
            # Add to new group
            groups[new_group_name].append(conn)
            conn.send(f"Server: You joined the group '{new_group_name}'.\n".encode('utf-8'))
            broadcast(f"{get_username(conn, clients)} has joined the group '{new_group_name}'.", conn, all_connections, groups, include_self=False)

    elif command == "leave":
        is_in_group = False
        # Find the group the user is in and remove them
        for group_name, members in groups.items():
            if conn in members:
                is_in_group = True
                members.remove(conn)
                conn.send(f"Server: You left the group '{group_name}'.\n".encode('utf-8'))
                broadcast(f"{get_username(conn, clients)} has left the group '{group_name}'.", conn, all_connections, groups, include_self=False)
                if not members:  # If no members left, delete the group
                    del groups[group_name]
                break
        if not is_in_group:
            conn.send("Server: You are not in any group.\n".encode('utf-8'))

def list_users(conn, clients):
    user_list = "Online Users: " + ", ".join(clients.keys())
    conn.send(user_list.encode("utf-8"))

def handle_whisper(message, sender_conn, clients, sender_username):
    parts = message.split(maxsplit=2)  # Split into command, username, message
    if len(parts) < 3:
        sender_conn.send(
            'Server: Invalid whisper command. Use /whisper <username> "<message>".'.encode(
                "utf-8"
            )
        )
        return
    _, target_username, msg = parts
    receiver_conn = clients.get(target_username)
    if receiver_conn:
        formatted_message = f"(whisper) {sender_username}: {msg}"
        receiver_conn.send(formatted_message.encode("utf-8"))
        sender_conn.send(formatted_message.encode("utf-8"))
    else:
        sender_conn.send(
            f"Server: No user named {target_username} found.".encode("utf-8")
        )


def get_username(conn, clients):
    for username, connection in clients.items():
        if connection == conn:
            return username
    return None


def broadcast(message, connection, all_connections, groups, include_self=True):
    sender_group = None
    # Determine if sender is in any group
    for group_name, members in groups.items():
        if connection in members:
            sender_group = group_name
            break

    if sender_group:
        # Send message only to members of the same group
        for client in groups[sender_group]:
            if client != connection or include_self:
                try:
                    formatted_message = f"({sender_group}) {message}"
                    client.send(formatted_message.encode('utf-8'))
                except Exception as e:
                    print(f"Error broadcasting message to group: {e}")
    else:
        # If the sender is not in any group, broadcast normally
        for client in all_connections:
            if client != connection or include_self:
                try:
                    client.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Error broadcasting message: {e}")


def remove_connection(conn, all_connections, clients, groups):
    if conn in all_connections:
        all_connections.remove(conn)
        username = None
        for user, connection in clients.items():
            if connection == conn:
                username = user
                broadcast(
                    f"Server: {username} has left the chat.",
                    conn,
                    all_connections,
                    groups,
                    include_self=False,
                )
                del clients[username]
                break
        conn.close()
        print(
            f"Connection with {username if username else 'Unknown'} has been removed."
        )


def main():
    host = "127.0.0.1"
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server started, waiting for connections...")
    all_connections = []
    clients = {}
    groups = {}  # This will map group names to a list of connections (members).

    while True:
        conn, addr = server_socket.accept()
        all_connections.append(conn)
        print(f"Connected to {addr}")

        # Start a new thread to handle the client; the first received message must be the username.
        threading.Thread(
            target=client_thread, args=(conn, addr, all_connections, clients, groups)
        ).start()


if __name__ == "__main__":
    main()
