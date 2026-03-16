"""Persistence simulation for System Defender - Mission Lockdown.

IMPORTANT: This does NOT touch real OS startup folders or registry.
It only writes a marker file to a local, simulated startup folder
inside the project directory for safe demonstrations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple


SIMULATED_STARTUP_DIR = Path(__file__).resolve().parent / "simulated_startup"
PERSISTENCE_MARKER = SIMULATED_STARTUP_DIR / "system_defender_autorun.txt"


def create_persistence() -> Tuple[bool, Path]:
    """Create a simulated persistence marker.

    Returns (created, marker_path).
    """
    SIMULATED_STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    if PERSISTENCE_MARKER.exists():
        return False, PERSISTENCE_MARKER

    PERSISTENCE_MARKER.write_text(
        "System Defender - Mission Lockdown\n"
        "Simulated autorun entry for educational demo.\n",
        encoding="utf-8",
    )
    return True, PERSISTENCE_MARKER


def remove_persistence() -> Tuple[bool, Path]:
    """Remove the simulated persistence marker."""
    if not PERSISTENCE_MARKER.exists():
        return False, PERSISTENCE_MARKER

    PERSISTENCE_MARKER.unlink()
    return True, PERSISTENCE_MARKER

