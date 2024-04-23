import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading


class ChatClient:
    def __init__(self, host="127.0.0.1", port=12345):
        self.root = tk.Tk()
        self.root.title("Chat Client")

        self.host = host
        self.port = port
        self.socket = None

        self.setup_username()

    def setup_username(self):
        while True:
            self.username = simpledialog.askstring(
                "Username", "Enter your username:", parent=self.root
            )
            if self.username:
                if self.connect_to_server():
                    break
            else:
                messagebox.showinfo(
                    "Username Needed", "You must enter a username to continue."
                )
                continue  # Will ask for the username again

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            # Send username right after connecting
            self.socket.send(self.username.encode("utf-8"))

            # Wait for server response
            server_response = self.socket.recv(1024).decode("utf-8")
            if "Welcome" in server_response:
                self.chat_window()
                return True
            else:
                messagebox.showerror(
                    "Username Taken",
                    "This username is already taken, please try another one.",
                )
                self.socket.close()
                return False
        except Exception as e:
            print(f"Failed to connect to the server: {e}")
            messagebox.showerror(
                "Connection Failed", f"Failed to connect to the server: {e}"
            )
            self.root.quit()
            return False

    def chat_window(self):
        self.username_label = tk.Label(self.root, text=f"Username: {self.username}")
        self.username_label.pack(padx=20, pady=5)

        self.group_label = tk.Label(self.root, text="No group joined")
        self.group_label.pack(padx=20, pady=5)

        self.text_area = tk.Text(self.root)
        self.text_area.pack(padx=20, pady=20)
        self.text_area.config(
            state=tk.DISABLED
        )  # Set the text area to disabled to make it read-only

        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack(padx=20, pady=20, fill=tk.BOTH)

        self.message_var = tk.StringVar()
        self.message_entry = tk.Entry(self.entry_frame, textvariable=self.message_var)
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.send_button = tk.Button(
            self.entry_frame, text="Send", command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.message_entry.bind("<Return>", self.send_message)

        threading.Thread(target=self.receive_message, daemon=True).start()

    def send_message(self, event=None):
        message = self.message_var.get()
        if message:
            if message.startswith("/whisper") and len(message.split()) < 3:
                self.text_area.config(state=tk.NORMAL)
                self.text_area.insert(
                    tk.END, 'Usage: /whisper <username> "<message>"\n'
                )
                self.text_area.config(state=tk.DISABLED)
            elif message.startswith("/group"):
                # Split the command to handle different group actions
                parts = message.split(maxsplit=2)
                if len(parts) < 2 or (parts[1] in ["create", "join"] and len(parts) < 3):
                    self.text_area.config(state=tk.NORMAL)
                    self.text_area.insert(tk.END, "Usage: /group <create|join> <groupname>, /group <list|leave>\n")
                    self.text_area.config(state=tk.DISABLED)
                else:
                    self.socket.send(message.encode('utf-8'))
            else:
                self.socket.send(message.encode("utf-8"))
            self.message_var.set("")  # Clear input field after sending

    def receive_message(self):
        while True:
            try:
                message = self.socket.recv(1024).decode("utf-8")
                if message:
                    self.text_area.config(
                        state=tk.NORMAL
                    )  # Temporarily make the text area writable
                    if "Online Users:" in message:
                        self.text_area.insert(tk.END, message + "\n", "list")
                    elif "has joined the group" in message or "has left the group" in message:
                        # Display group messages in a different color or style
                        self.text_area.insert(tk.END, message + "\n", 'group')
                    elif "You joined the group" in message:
                        group_name = message.split("'")[1]  # Extract the group name from the message
                        self.group_label.config(text=f"Group: {group_name}")
                        self.text_area.delete('1.0', tk.END)  # Clear chat window
                        self.text_area.insert(tk.END, message + "\n", 'join')
                    elif "You left the group" in message:
                        self.group_label.config(text="No group joined")
                        self.text_area.delete('1.0', tk.END)  # Clear chat window
                        self.text_area.insert(tk.END, message + "\n", 'leave')
                    else:
                        self.text_area.insert(tk.END, message + "\n")
                    self.text_area.see(tk.END)  # Auto-scroll to the bottom
                    self.text_area.config(state=tk.DISABLED)  # Set it back to disabled
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.socket.close()
                break

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    client = ChatClient()
    client.run()
