"""r340 bm-c: respawn hung T-131 fund_history refresh (detached, zero-window, log-file stdio).

Diagnosis: pid 33316 alive but zero face-file writes for 30.8 min (pace 12.9 s/sym,
log tail frozen mid tqdm bar 23:11:56) = socket-level hang on a face pull.
Checkpoint is per-face per-symbol -- kill+respawn loses only the in-flight symbol.
r317 law: child stdio -> explicit log file (no pipe inheritance), close_fds=True.
"""
import os
import subprocess
import sys
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
LOG = os.path.join(ROOT, "data", "fund_history", "_refresh.log")


def main():
    # 1) verify + kill hung pid 33316 (exact cmdline match, r317 diagnostic order)
    import ctypes
    # use tasklist-free approach: psutil if available else skip check (already verified via CIM)
    killed = False
    try:
        import psutil
        p = psutil.Process(33316)
        cl = " ".join(p.cmdline())
        if "update_fund_history.py" in cl and "refresh" in cl:
            p.kill()
            p.wait(timeout=10)
            killed = True
    except Exception:
        pass
    if not killed:
        # fallback via CIM (exclude self-match by exact pid)
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "Stop-Process -Id 33316 -Force -ErrorAction SilentlyContinue; "
             "Start-Sleep -Milliseconds 500; "
             "(Get-Process -Id 33316 -ErrorAction SilentlyContinue) -eq $null"]
        ).decode().strip()
        killed = out.lower() == "true"
    print("kill_hung_pid_33316:", killed)

    # 2) respawn detached, stdio -> log file (append), zero window, close_fds
    with open(LOG, "ab") as lf:
        lf.write(f"\n[r340 respawn {time.strftime('%Y-%m-%dT%H:%M:%S')}] hung pid killed, checkpoint resume\n".encode())
        proc = subprocess.Popen(
            [sys.executable, "-X", "utf8", os.path.join(ROOT, "scripts", "update_fund_history.py"), "refresh"],
            cwd=ROOT,
            stdout=lf,
            stderr=lf,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW | getattr(subprocess, "DETACHED_PROCESS", 0),
            close_fds=True,
        )
    print("respawned_pid:", proc.pid)
    time.sleep(8)
    # 3) liveness + log-growth verification (r325 law: artifact-growth is the only evidence)
    rc = proc.poll()
    print("still_running_after_8s:", rc is None)
    with open(LOG, "rb") as f:
        f.seek(0, 2)
        print("log_size:", f.tell())


if __name__ == "__main__":
    main()
