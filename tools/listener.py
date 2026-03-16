import socket
import sys
import time

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
            print("[*] Controls: 'quit' to close, any other text to execute.")
            print("----------------------------------------")

            conn.settimeout(None)
            
            while True:
                cmd = input("operator@v-hunter ~ $ ").strip()
                if not cmd:
                    # Optional: send a ping to check if still alive
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
                    conn.settimeout(5.0)
                    response = conn.recv(8192).decode("utf-8")
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
    main()
