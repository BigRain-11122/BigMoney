"""Silent watchdog wrapper for the OS tick (run via pythonw.exe = no console).

Spawns run_tick.py (also pythonw, fully windowless), enforces the 9-minute
hard timeout, kills the process tree on overrun, appends all output to
logs/tick.log. User order 2026-09-20: everything must be SILENT - no popups.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, "logs", "tick.log")
PYW = sys.executable.replace("python.exe", "pythonw.exe")


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def kill_tree(pid):
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                   capture_output=True)


def main():
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(ROOT, "logs", f"tick_{stamp}.out")
    with open(out, "wb") as fo:
        p = subprocess.Popen([PYW, os.path.join(ROOT, "run_tick.py")],
                             stdout=fo, stderr=subprocess.STDOUT,
                             cwd=ROOT,
                             creationflags=0x08000000)  # CREATE_NO_WINDOW
    try:
        p.wait(timeout=540)
    except subprocess.TimeoutExpired:
        log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] WATCHDOG: killing hung tick pid={p.pid}")
        kill_tree(p.pid)
    try:
        with open(out, "r", encoding="utf-8", errors="replace") as f:
            content = f.read().strip()
        if content:
            log(content)
        else:
            log(f"[{time.strftime('%H:%M:%S')}] (tick produced no output)")
    except Exception:
        pass
    finally:
        try:
            os.remove(out)
        except Exception:
            pass


if __name__ == "__main__":
    main()
