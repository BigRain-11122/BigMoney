"""r860 bm-a: W16-SCREEN completion takeover (W13/W14 observing-round law).

1. Tombstone the false-crash SCREEN sig (burn COMPLETED 373/373 at
   03:37:07, runner exited clean; trial-labor runners write no
   worker-claim file so the daemon harvest never lands this half --
   W13 shard-note documented gap; false-crash from the 25-min confirm).
2. Write the worker-claim file so the daemon harvest flips the shard
   + entry done (W14-SCREEN bm-c precedent format).
"""
import json
import os
import datetime

FUSE = r"results/crash_fuse.json"
SIG = "scripts/trial_labor_w16.py|screen,--shard,0,--shards,1"
CLAIM_DIR = os.path.join("results", "pool_claims", "TRIAL-LABOR-W16-SCREEN")
CLAIM = os.path.join(CLAIM_DIR, "w16-screen-0of1.bm-a.json")

# --- 1. tombstone false-crash sig ---------------------------------------
f = json.load(open(FUSE, encoding="utf-8"))
sigs = f.setdefault("sigs", {})
cleared = f.setdefault("cleared", {})
assert SIG in sigs, "SCREEN fused sig present"
reg = sigs.pop(SIG)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
cleared[SIG] = {
    "crashes": int(reg.get("count", 1)),
    "old_code_sha256": reg.get("code_sha256"),
    "cleared_by": "bm-a",
    "cleared_ts": now,
    "reason": ("r860 bm-a false-crash tombstone: SCREEN burn COMPLETED "
               "373/373 cells 03:37:07, runner exited clean (launch log "
               "'shard 0of1 complete'); trial-labor runners write no "
               "worker-claim file so the daemon harvest cannot land "
               "(W13 shard-note documented gap) -> 25-min confirm "
               "counted a false crash; completion takeover by observing "
               "round r860 per W13/W14 precedent"),
    "entry": reg.get("entry"),
    "shard": reg.get("shard"),
}
tmp = FUSE + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(f, fh, ensure_ascii=False, indent=1)
os.replace(tmp, FUSE)
f2 = json.load(open(FUSE, encoding="utf-8"))
assert SIG not in f2["sigs"] and SIG in f2["cleared"]
print("SCREEN sig tombstoned (false-crash documented)")

# --- 2. worker claim file (W14-SCREEN format) -----------------------------
os.makedirs(CLAIM_DIR, exist_ok=True)
claim = {
    "machine_id": "bm-a",
    "state": "closed",
    "pid": 85632,
    "heartbeat": "2026-10-08T03:37:07+08:00",
    "outcome": "ok",
    "exit_code": 0,
    "started": "2026-10-08T03:32:01+08:00",
    "closed_at": "2026-10-08T03:37:07+08:00",
    "result_ref": ("runner rc=0, 373/373 cells checkpoint complete "
                   "(artifacts results/trial_labor_w16/ + screen-finalize "
                   "LANDED r860: w16_screen.json + w16_screen_cells.csv)"),
}
with open(CLAIM, "w", encoding="utf-8") as fh:
    json.dump(claim, fh, ensure_ascii=False, indent=1)
c2 = json.load(open(CLAIM, encoding="utf-8"))
assert c2["state"] == "closed" and c2["outcome"] == "ok"
print("claim file written:", CLAIM)
