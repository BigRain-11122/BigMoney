# -*- coding: utf-8 -*-
"""r897 bm-b supervisor: relaunch r894/r895 group-repo pushes with stall-kill-restart.

Empirics (20:44 + 21:38 live-fire x2): write-tree on the blob:none partial-clone
group repo triggers a ~2.9k-object promisor lazy fetch; the night ssh route stalls
bulk packs indefinitely while single-round-trip calls pass; and the scripts'
internal subprocess timeouts fail to kill the real git.exe chain (shim-orphan
family). Supervisor caps each attempt at STALL_CAP sec, kills the WHOLE tree via
taskkill /T, sweeps residual group-repo git orphans, then retries on a fresh
connection. Route fluctuates minute-scale; a healthy window lands the pack and
the rest of the script run is all-local. G1-G4 anti-wipe guards unchanged.
"""
import json, os, subprocess, sys, time

BIGM = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RECEIPT = os.path.join(BIGM, "results", "_r897bmb_supervisor_receipt.json")
SCRIPTS = [
    ("r894_gsoft", os.path.join(BIGM, "results", "_r894bmb_gsoft_closeout.py")),
    ("r895_pool_scored", os.path.join(BIGM, "results", "_r895bmb_pool_scored_push.py")),
]
STALL_CAP = 600
MAX_ATTEMPTS = 4

PS_SWEEP = ("$ws = Get-CimInstance Win32_Process -Filter \"Name='git.exe'\"; "
            "$ws | Where-Object {$_.CommandLine -like '*-C C:\\Fluxgroup\\FluxGroup *' "
            "-or $_.CommandLine -like '*fetch.negotiationAlgorithm=noop*'} | "
            "ForEach-Object { taskkill /F /T /PID $_.ProcessId 2>$null }; 'swept'")


def sweep():
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", PS_SWEEP],
                       capture_output=True, timeout=60)
    except Exception:
        pass


def main():
    receipt = {"start": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"), "attempts": []}

    def flush():
        json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    final = {}
    for tag, path in SCRIPTS:
        for i in range(1, MAX_ATTEMPTS + 1):
            t0 = time.time()
            p = subprocess.Popen([sys.executable, path], cwd=BIGM,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            rc = None
            while True:
                try:
                    rc = p.wait(timeout=20)
                    break
                except subprocess.TimeoutExpired:
                    if time.time() - t0 > STALL_CAP:
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                                       capture_output=True)
                        time.sleep(3)
                        sweep()
                        rc = "STALL-KILLED"
                        break
            receipt["attempts"].append(
                {"tag": tag, "attempt": i, "rc": rc, "sec": round(time.time() - t0, 1)})
            flush()
            if rc == 0:
                break
            time.sleep(10)
        final[tag] = rc
        receipt["final"] = final
        flush()
    receipt["done"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    flush()
    return 0 if all(v == 0 for v in final.values()) else 3


if __name__ == "__main__":
    sys.exit(main())
