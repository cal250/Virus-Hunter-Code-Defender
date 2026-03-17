import socket
import sys
import time
import re
import threading
from queue import Queue

def data_collector(conn, output_queue):
    """Background thread to collect data from the socket."""
    while True:
        try:
            conn.settimeout(1.0)
            raw_data = conn.recv(16384)
            if not raw_data:
                break
            
            response = raw_data.decode("utf-8", errors="replace")
            
            # Split data by heartbeats
            if "[HEARTBEAT]" in response:
                # Handle heartbeat silently
                response = response.replace("[HEARTBEAT]", "").strip()
            
            if response:
                output_queue.put(response)
                
        except socket.timeout:
            continue
        except Exception as e:
            # print(f"[Debug] Collector Error: {e}")
            break

def main():
    host = "0.0.0.0"
    port = 5050
    
    print("========================================")
    print(" VIRUS HUNTER: MAJESTIC COMMAND CENTER ")
    print("========================================")
    print(f"[*] Awaiting connection on {host}:{port}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        return

    while True:
        try:
            conn, addr = server.accept()
            print(f"\n[+] SECURE LINK ESTABLISHED: {addr[0]}:{addr[1]}")
            print("[*] Privileged Shell Active. Full system access enabled.")
            print("[*] Controls: 'quit' to close, any other text to execute.")
            print("----------------------------------------")

            output_queue = Queue()
            collector_thread = threading.Thread(target=data_collector, args=(conn, output_queue), daemon=True)
            collector_thread.start()
            
            current_path = "v-hunter"
            
            while True:
                # Drain the queue for any pending output (like initial greeting)
                while not output_queue.empty():
                    msg = output_queue.get()
                    
                    # Update path if info is in message
                    path_tags = re.findall(r"\[PATH: (.*)\]", msg)
                    if path_tags:
                        current_path = path_tags[-1].strip()
                        msg = re.sub(r"\[PATH: .*\]", "", msg).strip()
                    
                    dir_match = re.search(r"\[DIRECTORY CHANGED\] -> (.*)", msg)
                    if dir_match:
                        current_path = dir_match.group(1).strip()
                        
                    if "Secure Shell Active" in msg:
                        p_match = re.search(r"Current Path: (.*)", msg)
                        if p_match: current_path = p_match.group(1).strip()
                        
                    if msg: print(msg)

                # Custom prompt based on current path
                prompt_display = os.path.basename(current_path) if current_path != "v-hunter" else "system"
                cmd = input(f"operator@{prompt_display} $ ").strip()
                
                if not cmd:
                    if not collector_thread.is_alive():
                        print("[!] Connection lost.")
                        break
                    continue
                
                try:
                    conn.send((cmd + "\n").encode("utf-8"))
                    if cmd.lower() == "quit":
                        break
                    
                    # Wait for output with a reasonable timeout
                    start_time = time.time()
                    timeout = 10.0
                    while time.time() - start_time < timeout:
                        if not output_queue.empty():
                            break
                        if not collector_thread.is_alive():
                            break
                        time.sleep(0.1)
                        
                except Exception as e:
                    print(f"[!] Transmission error: {e}")
                    break
            
            conn.close()
            print("[*] Secure link terminated. Awaiting new connection...")
        except KeyboardInterrupt:
            break

    server.close()
    print("\n[*] Command Center shutdown.")

if __name__ == "__main__":
    import os 
    main()
