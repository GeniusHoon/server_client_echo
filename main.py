import multiprocessing
import time
from server import ServerApp
from client import ClientApp

def run_server():
    """Initializes and runs the server application."""
    server_app = ServerApp()
    server_app.mainloop()

def run_client():
    """
    Waits a moment for the server to initialize, then starts the client application.
    """
    time.sleep(1)  # Give the server a moment to start and bind the port
    client_app = ClientApp()
    client_app.mainloop()

if __name__ == "__main__":
    # Using multiprocessing to run server and client in separate processes
    # is necessary because each has its own blocking Tkinter mainloop.
    
    # Set start method to 'spawn' for compatibility with GUI libraries on macOS and Windows
    try:
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        # set_start_method can only be called once
        pass

    print("Starting server and client...")

    server_proc = multiprocessing.Process(target=run_server)
    client_proc = multiprocessing.Process(target=run_client)

    server_proc.start()
    print("Server process started.")
    
    client_proc.start()
    print("Client process started.")

    # Wait for the processes to complete. 
    # The script will end when both the server and client windows are closed.
    server_proc.join()
    client_proc.join()

    print("Server and client processes have finished.")
