import tkinter as tk
from tkinter import simpledialog
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
        self.username = simpledialog.askstring(
            "Username", "Enter your username:", parent=self.root
        )
        if self.username:
            self.connect_to_server()
        else:
            self.root.quit()  # Exit if no username is entered

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            # Send username right after connecting
            self.socket.send(self.username.encode('utf-8'))
            self.chat_window()
        except Exception as e:
            print(f"Failed to connect to the server: {e}")
            self.root.quit()

    def chat_window(self):
      self.text_area = tk.Text(self.root)
      self.text_area.pack(padx=20, pady=20)
      self.text_area.config(state=tk.DISABLED)  # Set the text area to disabled to make it read-only

      self.message_var = tk.StringVar()
      self.message_entry = tk.Entry(self.root, textvariable=self.message_var)
      self.message_entry.pack(padx=20, pady=20, fill=tk.X)
      
      self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
      self.send_button.pack(padx=20, pady=20)

      threading.Thread(target=self.receive_message, daemon=True).start()


    def send_message(self):
      message = self.message_var.get()
      if message:
          if message.startswith("/whisper") and len(message.split()) < 3:
              self.text_area.config(state=tk.NORMAL)
              self.text_area.insert(tk.END, "Usage: /whisper <username> \"<message>\"\n")
              self.text_area.config(state=tk.DISABLED)
          else:
              self.socket.send(message.encode('utf-8'))
          self.message_var.set("")  # Clear input field after sending

    def receive_message(self):
      while True:
          try:
              message = self.socket.recv(1024).decode('utf-8')
              if message:
                  self.text_area.config(state=tk.NORMAL)  # Temporarily make the text area writable
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
