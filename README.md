# Virus Hunter: Code Defender

A high-quality 2D arcade-style cybersecurity game for educational purposes.

## Warning
This project demonstrates real cybersecurity concepts (reverse shells, persistence) and should **ONLY** be tested in a controlled virtual machine or lab environment.

## Features
- **Level 1: System Scan**: Automatic dependency verification.
- **Level 2: Network Node**: Real-time reverse shell communication with a listener.
- **Level 3: Persistence Simulation**: Demonstrates how malware maintains access.
- **Level 4: Final Cleanup**: System restoration and secure exit.

## Installation
1. Ensure you have Python 3.8+ installed.
2. The game will automatically attempt to install `pygame-ce` if it's missing.

## How to Play

### Local Connection (Single PC)
1. **Start the Listener**:
   ```bash
   python tools/listener.py
   ```
2. **Launch the Game**:
   ```bash
   python game/main_game.py
   ```

### Remote Connection (Two PCs)
By default, the game is configured to search for a listener at **10.12.73.251**.

1. **On the Listener PC (10.12.73.251)**:
   - Ensure the listener is running: `python tools/listener.py`.
   - Ensure **Port 5050** is open in the firewall.
2. **On the Game PC**:
   - Simply launch the game: `python game/main_game.py`.
   - It will automatically attempt to link to the global listener.

### Changing the Listener IP
If you need to connect to a different listener address, use the `--host` argument:
```bash
python game/main_game.py --host <NEW_IP_ADDRESS>
```

> [!TIP]
> **Firewall Note**: If the connection fails, verify connectivity with `ping 10.12.73.251`. Ensure the listener PC is reachable on the local network.

## Controls
- **WASD**: Move Antivirus Avatar
- **Space**: High-velocity Plasma Bolt
- **E**: Interact with Terminals
- **Esc**: Emergency Exit

## Cleanup
After playing, run the cleanup tool to remove any simulated persistence artifacts:
```bash
python tools/cleanup_tool.py
```
