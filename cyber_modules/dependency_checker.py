"""Dependency management for System Defender - Mission Lockdown.

This module intentionally keeps behavior safe for classroom demos.
It installs only the explicit, user-approved dependencies.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from typing import Iterable

_MODULE_TO_PIP_PACKAGE = {
    # On many platforms (especially newer Python versions), pygame-ce is the reliable wheel,
    # but it still imports as `pygame`.
    "pygame": "pygame-ce",
}

def _is_installed(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def _install_package(package: str) -> bool:
    """Attempt to install a package via pip. Returns True on success."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        return True
    except Exception:
        return False


def ensure_dependencies(packages: Iterable[str]) -> None:
    """Ensure required packages are installed.

    If a package is missing, we try to install it automatically. If the
    installation fails, we raise RuntimeError to allow the caller to exit
    cleanly with a clear message.
    """
    missing = [p for p in packages if not _is_installed(p)]
    if not missing:
        return

    print("[Dependency Checker] Missing packages:", ", ".join(missing))
    for module_name in missing:
        pip_pkg = _MODULE_TO_PIP_PACKAGE.get(module_name, module_name)
        print(f"[Dependency Checker] Installing {pip_pkg} (for import '{module_name}')...")
        ok = _install_package(pip_pkg)
        if not ok:
            raise RuntimeError(
                f"Failed to install {pip_pkg}. Please run: {sys.executable} -m pip install {pip_pkg}"
            )

