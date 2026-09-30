"""r479 bm-b: park refresh-window-collision pool entries + claim/launch P2NULL-KLIFT-K2200-S2.

- Park EXCLUSION-MARGINAL-P1-RUN + CROSS-START-ROBUSTNESS-P1-FACEB-RUN (ready->waiting)
  in BOTH shared + bm-b lane pool files (W14 vocabulary-legal precedent; r479 lesson:
  refresh-window burn = park first, then clear). astock universe refresh spawned
  21:09:13 (pid 47564) in-flight; both burns consume the astock panel -> every autofill
  tick relaunches -> honest gate exit counted as false crash. Unpark = post-settle round.
- External worker claim O-2210 for P2NULL-KLIFT-K2200-S2 (CEO O-20260930-2054 sec.1
  e-item; lane_owner=null; est ~5.5min; core48 prefixed files, refresh-window safe).
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARK_NOTE = (
    "r479 bm-b park 21:36: astock universe refresh in-flight since 21:09:13 "
    "(spawn pid 47564); this burn consumes the astock panel -> mid-refresh "
    "launches die at in-runner FAIL-CLOSED gates as false crashes (FACEB 20:40 "
    "precedent, r479 lesson park-first). Unpark=waiting->ready by bm-b round "
    "after panel refresh settles (verify refresh process exit + panel complete)."
)

PARK_IDS = ["EXCLUSION-MARGINAL-P1-RUN", "CROSS-START-ROBUSTNESS-P1-FACEB-RUN"]
POOL_FILES = [
    os.path.join(ROOT, "results", "runnable_pool.json"),
    os.path.join(ROOT, "results", "runnable_pool.bm-b.json"),
]


def park_entries():
    flipped = []
    for pf in POOL_FILES:
        if not os.path.exists(pf):
            continue
        with open(pf, encoding="utf-8") as fh:
            pool = json.load(fh)
        changed = False
        for e in pool.get("entries", []):
            if e.get("id") in PARK_IDS and e.get("status") == "ready":
                e["status"] = "waiting"
                e["parked_note"] = PARK_NOTE
                e["parked_by"] = "bm-b (OS iteration loop r479)"
                e["parked_at"] = "2026-09-30T21:36+08:00"
                changed = True
                flipped.append((os.path.basename(pf), e["id"]))
        if changed:
            with open(pf, "w", encoding="utf-8") as fh:
                json.dump(pool, fh, indent=1, ensure_ascii=False)
    return flipped


def launch_s2():
    log = os.path.join(ROOT, "results", "_r479bmb_p2null_s2.log")
    cmd = [
        sys.executable,
        os.path.join(ROOT, "scripts", "p2_null_calibration_ext.py"),
        "--shard", "2", "--nshards", "4",
    ]
    with open(log, "w", encoding="utf-8") as lh:
        p = subprocess.Popen(
            cmd, cwd=ROOT, stdout=lh, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            | getattr(subprocess, "DETACHED_PROCESS", 0x00000008),
        )
    return p.pid, log


def write_claim(pid):
    d = os.path.join(ROOT, "results", "pool_claims", "P2NULL-KLIFT-K2200-S2")
    os.makedirs(d, exist_ok=True)
    claim = {
        "machine_id": "bm-b",
        "state": "claimed",
        "pid": pid,
        "heartbeat": "2026-09-30T21:36:30+08:00",
        "started": "2026-09-30T21:36:30+08:00",
    }
    path = os.path.join(d, "p2null-klift-s2-0of1.bm-b.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(claim, fh, indent=1)
    return path


if __name__ == "__main__":
    flips = park_entries()
    for f in flips:
        print("PARKED", f)
    pid, log = launch_s2()
    print("LAUNCHED s2 pid", pid, "log", log)
    cp = write_claim(pid)
    print("CLAIM", cp)
    time.sleep(3)
    with open(log, encoding="utf-8", errors="replace") as fh:
        head = fh.read(400)
    print("LOG-HEAD:", head)
