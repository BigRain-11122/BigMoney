"""Silent wrapper for the scheduled daily full cycle (pythonw = no console).

Runs run_daily.py under the same windowless pattern as run_tick_watch.py:
CREATE_NO_WINDOW spawn + all output appended to logs/daily_task.log.
User orders: 2026-09-20 everything SILENT; 2026-09-21 trade for real every
single day - this is the belt-and-braces 20:30 trigger behind the tick's
new-data autodetect (run_daily itself is single-flight via full_run.pid).
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, "logs", "daily_task.log")
PYW = sys.executable.replace("python.exe", "pythonw.exe")


def main():
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(ROOT, "logs", f"daily_{stamp}.out")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] MoneyQuantDaily trigger\n")
    with open(out, "wb") as fo:
        p = subprocess.Popen([PYW, os.path.join(ROOT, "run_daily.py")],
                             stdout=fo, stderr=subprocess.STDOUT,
                             cwd=ROOT,
                             creationflags=0x08000000)  # CREATE_NO_WINDOW
    # the full cycle can legitimately take hours (34y WF) - do NOT time it
    # out here; run_tick's police owns hang detection (360 min).
    p.wait()
    try:
        with open(out, "r", encoding="utf-8", errors="replace") as f:
            tail = f.read()[-4000:]
        if tail.strip():
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(tail)
    except Exception:  # noqa: BLE001
        pass
    finally:
        try:
            os.remove(out)
        except OSError:
            pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] done rc={p.returncode}\n")


if __name__ == "__main__":
    main()
