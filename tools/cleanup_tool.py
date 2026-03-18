"""Cleanup tool for System Defender - Mission Lockdown.

Removes simulated persistence artifacts created by the game.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cyber_modules.persistence import remove_persistence, SIMULATED_STARTUP_DIR

def main() -> int:
    removed, path = remove_persistence()
    if removed:
        print("[Cleanup] Persistence cleanup completed.")
        if not path.exists():
            print(f"[Cleanup] Marker removed: {path}")
        else:
            print(f"[Cleanup] Marker still present: {path}")
        if not SIMULATED_STARTUP_DIR.exists():
            print(f"[Cleanup] Removed directory: {SIMULATED_STARTUP_DIR}")
        else:
            remaining = [p.name for p in SIMULATED_STARTUP_DIR.iterdir()] if SIMULATED_STARTUP_DIR.is_dir() else []
            if remaining:
                print(f"[Cleanup] Remaining files in {SIMULATED_STARTUP_DIR}: {', '.join(remaining)}")
    else:
        print("[Cleanup] No persistence artifacts were removed (nothing found).")
        print(f"[Cleanup] Marker path checked: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

