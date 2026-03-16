import socket
import sys

def main():
    host = "0.0.0.0"
    port = 5050
    
    print("========================================")
    print(" VIRUS HUNTER: COMMAND LISTENER ")
    print("========================================")
    print(f"[*] Listening on {host}:{port}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(1)
    except Exception as e:
        print(f"[!] Error binding to port: {e}")
        return

    conn, addr = server.accept()
    print(f"[*] Connection received from {addr[0]}:{addr[1]}")
    print("[*] Type 'quit' to close connection.")
    print("----------------------------------------")

    # Receive initial banner
    try:
        banner = conn.recv(1024).decode("utf-8")
        print(banner)
    except:
        pass

    while True:
        try:
            cmd = input("shell> ").strip()
            if not cmd:
                continue
            
            conn.send((cmd + "\n").encode("utf-8"))
            
            if cmd.lower() == "quit":
                break
            
            # Non-blocking receive for output
            conn.settimeout(2.0)
            try:
                response = conn.recv(4096).decode("utf-8")
                print(response)
            except socket.timeout:
                print("[!] Timeout waiting for response.")
            finally:
                conn.settimeout(None)
                
        except (KeyboardInterrupt, EOFError):
            conn.send(b"quit\n")
            break
        except Exception as e:
            print(f"[!] Connection error: {e}")
            break

    conn.close()
    server.close()
    print("[*] Listener closed.")

if __name__ == "__main__":
    main()
