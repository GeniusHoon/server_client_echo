import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

HOST = '127.0.0.1'
PORT = 65432

class ServerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Server")
        self.geometry("400x300")

        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.log_area.configure(state='disabled')

        self.server_socket = None
        self.client_connection = None
        self.running = False

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.start_server()

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, log_message + '\n')
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)

    def start_server(self):
        self.running = True
        # 1. Create a socket using IPv4 address family and TCP protocol.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reusing the address to avoid "Address already in use" errors.
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 2. Bind the socket to the specified host and port.
        self.server_socket.bind((HOST, PORT))
        # 3. Enable the server to accept connections, with a queue of up to 5 waiting.
        self.server_socket.listen()
        self.log(f"Server listening on {HOST}:{PORT}")

        self.server_thread = threading.Thread(target=self.accept_clients, daemon=True)
        self.server_thread.start()

    def accept_clients(self):
        try:
            while self.running:
                # 4. Block and wait for an incoming connection.
                # When a client connects, create a new socket 'conn' for the connection.
                conn, addr = self.server_socket.accept()
                self.client_connection = conn
                self.log(f"Connected by {addr}")
                # Start a new thread to handle this client's communication.
                handler_thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                handler_thread.start()
        except OSError:
            # This will happen when the socket is closed while accept() is blocking.
            if self.running:
                self.log("Server socket was closed unexpectedly.")
        finally:
            self.log("Server accept loop has stopped.")


    def handle_client(self, conn, addr):
        try:
            with conn:
                while self.running:
                    # 5. Receive data from the client (up to 1024 bytes).
                    data = conn.recv(1024)
                    if not data:
                        # If no data is received, the client has closed the connection.
                        break
                    decoded_data = data.decode()
                    self.log(f"Received from {addr}: {decoded_data}")
                    # 6. Echo the received data back to the same client.
                    conn.sendall(data)
                    self.log(f"Echoed back to {addr}: {decoded_data}")
        except ConnectionResetError:
            self.log(f"Connection with {addr} was reset.")
        finally:
            # 7. The connection is closed automatically by the 'with' statement.
            self.log(f"Connection with {addr} closed.")
            if self.client_connection == conn:
                self.client_connection = None


    def on_closing(self):
        self.running = False
        # To unblock the server_socket.accept() call
        try:
            # Create a dummy connection to the server to unblock the accept call
            dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dummy_socket.connect((HOST, PORT))
            dummy_socket.close()
        except Exception as e:
            self.log(f"Error during shutdown: {e}")

        if self.server_socket:
            self.server_socket.close()
            self.log("Server socket closed.")
            
        if self.client_connection:
            self.client_connection.close()
            self.log("Client connection closed.")

        self.destroy()

if __name__ == "__main__":
    app = ServerApp()
    app.mainloop()