import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

class ClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client")
        self.geometry("400x400")

        # Connection Frame
        conn_frame = tk.Frame(self)
        conn_frame.pack(pady=5, padx=10, fill=tk.X)

        tk.Label(conn_frame, text="Host:").pack(side=tk.LEFT, padx=(0, 5))
        self.host_entry = tk.Entry(conn_frame)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(conn_frame, text="Port:").pack(side=tk.LEFT, padx=(5, 5))
        self.port_entry = tk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, "65432")
        self.port_entry.pack(side=tk.LEFT)

        self.connect_button = tk.Button(conn_frame, text="Connect", command=self.connect_action)
        self.connect_button.pack(side=tk.LEFT, padx=(5, 0))
        
        self.disconnect_button = tk.Button(conn_frame, text="Disconnect", command=self.disconnect_action, state='disabled')
        self.disconnect_button.pack(side=tk.LEFT, padx=(5, 0))

        # Chat Log
        self.chat_log = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.chat_log.pack(padx=10, pady=(5, 10), fill=tk.BOTH, expand=True)
        self.chat_log.configure(state='disabled')

        # Message Frame
        msg_frame = tk.Frame(self)
        msg_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.msg_entry = tk.Entry(msg_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", self.send_message)
        self.msg_entry.configure(state='disabled')

        self.send_button = tk.Button(msg_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        self.send_button.configure(state='disabled')
        
        self.client_socket = None
        self.running = False

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, log_message + '\n')
        self.chat_log.configure(state='disabled')
        self.chat_log.see(tk.END)

    def connect_action(self):
        host = self.host_entry.get()
        port_str = self.port_entry.get()
        if not port_str.isdigit():
            self.log("Error: Port must be a number.")
            return
        port = int(port_str)

        try:
            # 1. Create a socket using IPv4 address family and TCP protocol.
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 2. Connect to the server at the specified host and port.
            self.client_socket.connect((host, port))
            self.running = True

            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')
            self.host_entry.config(state='disabled')
            self.port_entry.config(state='disabled')
            self.msg_entry.config(state='normal')
            self.send_button.config(state='normal')
            
            self.log(f"Connected to {host}:{port}")

            # Start a thread to listen for incoming messages from the server.
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()

        except ConnectionRefusedError:
            self.log("Connection refused. Is the server running?")
        except Exception as e:
            self.log(f"Failed to connect: {e}")

    def disconnect_action(self):
        self.close_connection()

    def receive_messages(self):
        try:
            while self.running:
                # 4. Block and wait to receive data from the server (the echo).
                data = self.client_socket.recv(1024)
                if not data:
                    # If no data is received, the server has closed the connection.
                    self.log("Server closed the connection.")
                    self.close_connection()
                    break
                self.log(f"Server echo: {data.decode()}")
        except (ConnectionResetError, ConnectionAbortedError):
            if self.running:
                self.log("Connection to server was lost.")
                self.close_connection()
        except OSError:
            # This can happen if the socket is closed while recv is blocking.
            pass

    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message and self.client_socket:
            try:
                self.log(f"You: {message}")
                # 3. Send the encoded message to the server.
                self.client_socket.sendall(message.encode())
                self.msg_entry.delete(0, tk.END)
            except Exception as e:
                self.log(f"Error sending message: {e}")
                self.close_connection()

    def close_connection(self):
        # 5. Close the connection.
        if self.running:
            self.running = False
            if self.client_socket:
                try:
                    # Politely inform the other side we're closing the connection.
                    self.client_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.client_socket.close()
                self.client_socket = None
                self.log("Connection closed.")

        self.connect_button.config(state='normal')
        self.disconnect_button.config(state='disabled')
        self.host_entry.config(state='normal')
        self.port_entry.config(state='normal')
        self.msg_entry.config(state='disabled')
        self.send_button.config(state='disabled')

    def on_closing(self):
        self.close_connection()
        self.destroy()

if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()
