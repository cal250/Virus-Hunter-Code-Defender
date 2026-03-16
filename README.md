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
1. **Start the Listener** (Optional but required for Level 2):
   ```bash
   python tools/listener.py
   ```
2. **Launch the Game**:
   ```bash
   python game/main_game.py
   ```
   - Use **WASD** to move.
   - Use **Space** to shoot your antivirus beam.
   - Use **E** to interact with terminals.
3. **Follow Mission Objectives** in the HUD.

## Cleanup
After playing, run the cleanup tool to remove any simulated persistence artifacts:
```bash
python tools/cleanup_tool.py
```
