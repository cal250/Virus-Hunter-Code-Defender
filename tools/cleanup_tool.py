"""Cleanup tool for System Defender - Mission Lockdown.

Removes simulated persistence artifacts created by the game.
"""

from __future__ import annotations

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cyber_modules.persistence import remove_persistence

def main() -> int:
    removed, path = remove_persistence()
    if removed:
        print(f"[Cleanup] Removed simulated persistence marker: {path}")
    else:
        print(f"[Cleanup] No persistence marker found at: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

