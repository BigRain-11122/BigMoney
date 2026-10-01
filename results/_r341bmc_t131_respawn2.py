"""r341 bm-c: T-131 fund_history refresh 2nd respawn (pid 24584 dead).

Forensics: log frozen 2026-10-01 23:45:03, tail ends mid tqdm bar with NO
traceback = hard death (kill/OS crash), not a source error; per-face
per-symbol checkpoint intact -> respawn loses only the in-flight symbol.
r317 law: child stdio -> explicit log file, close_fds=True, detached.
"""
import os
import subprocess
import sys
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
LOG = os.path.join(ROOT, "data", "fund_history", "_refresh.log")
DATA_DIR = os.path.join(ROOT, "data", "fund_history")


def face_count():
    n = 0
    for _d, _s, files in os.walk(DATA_DIR):
        n += sum(1 for f in files if f.endswith(".json"))
    return n


def main():
    # 1) verify ZERO live refresher processes (cmdline match; psutil
    #    process_iter excludes self by construction -- no cmdline overlap)
    live = []
    try:
        import psutil
        for p in psutil.process_iter(["pid", "cmdline"]):
            cl = " ".join(p.info.get("cmdline") or [])
            if "update_fund_history.py" in cl and "refresh" in cl:
                live.append((p.info["pid"], cl[:80]))
    except ImportError:
        pass
    print("live_refreshers:", live)
    if live:
        print("ABORT: refresher already running -- dual-collector guard")
        return 1
    pre = face_count()
    print("pre_face_count:", pre)
    # 2) respawn detached, stdio -> log file (append), zero window
    with open(LOG, "ab") as lf:
        lf.write(("\n[r341 respawn2 %s] pid 24584 dead (log frozen "
                  "23:45:03, no traceback = hard death); checkpoint resume\n"
                  % time.strftime("%Y-%m-%dT%H:%M:%S")).encode("utf-8"))
        proc = subprocess.Popen(
            [sys.executable, "-X", "utf8",
             os.path.join(ROOT, "scripts", "update_fund_history.py"),
             "refresh"],
            cwd=ROOT, stdout=lf, stderr=lf, stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
            | getattr(subprocess, "DETACHED_PROCESS", 0),
            close_fds=True)
    print("respawned_pid:", proc.pid)
    time.sleep(8)
    print("still_running_after_8s:", proc.poll() is None)
    print("post_face_count:", face_count())
    return 0


if __name__ == "__main__":
    sys.exit(main())
