# r796 bm-b heartbeat bookkeeping (lineage: results/_r7768bmb_bookkeeping.py pattern)
# Single-instant capture: epoch int + clock_read T-separated ISO + same-instant ts fields.
import json, os, subprocess, sys, time
from datetime import datetime

P = "fleet/machines/bm-b.json"
now = datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")   # 2026-10-07THH:MM:SS+08:00 (T separator, offset)
epoch = int(time.time())
assert isinstance(epoch, int)

cpu_cores = os.cpu_count() or 0
free_ram_gb = round(__import__("psutil").virtual_memory().available / 1e9, 2)
gpu_mb = 0
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    gpu_mb = int(float(out.stdout.strip().splitlines()[0]))
except Exception:
    gpu_mb = 0

VERDICT = ("green: golden-week steady-state guard round r796; trio Q/D burns alive "
           "(Q 1941/2000 eta ~08:00 honest-corrected rate 0.353/min, D 1610/2000 eta ~10-08 01:40, V 2000 COMPLETE); "
           "orders 163/163; smoke 48/48; QA r796 5/5; satengine alive rc0 idle; boards 0 open; CODELY <=cap compliant")
CURRENT_TASK = ("r796 closed; next = Q first-to-2000 ~10-07 08:00 same-window pool dual-flip per r668 / "
                 "trio finalize when Q+D both 2000 (D ~10-08 01:40) / "
                 "market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3 first new bar enforce)")
LAST_ACTION = ("r796: S0 daemon-ticks commit + pull --rebase clean (4 absorbed) + orders 163/163 double-scan zero-delta "
               "+ group dual-face zero-delta (decisions 77FFC880 / orders F1B0CC59 both MATCH) + smoke 48/48 "
               "+ S6 chain 35/35 rc0 + QA r796 5/5 + S7 quartet 4/4 + attrition CLEAN")
NOW_ACTIVE = ("FUND trio NULLS judgment batch in-flight: Q 1941/2000 (rate 0.353/min measured @05:13, ETA ~08:00 "
              "honest-corrected) / D 1610/2000 (rate 0.318/min, ETA ~10-08 01:40) / V 2000/2000 COMPLETE; "
              "G1 pending Q+D, G2+G3 green, G4 PENDING r638 fallback armed; finalize window 10-05..10-09")
LATEST = ("qa/smoke-r796.md 5/5 + qa/equity-curve-r796.png (93 trades determinism=True) + "
          "results/_r796bmb_s6_chain.log (35 legs all rc0 05:07-05:12) @2026-10-07T05:2x")
NEXT_MS = ("trio Q first-to-2000 ~10-07 08:00 same-window pool dual-flip per r668 law + trio finalize when Q+D both "
           "complete (~10-08 01:40, G4 r638 fallback armed) + post-trio-close O-20260906-2358... O-20261006-2358 "
           "self-claim <=1h + market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3) — within 48h window")

with open(P, encoding="utf-8-sig") as fh:
    h = json.load(fh)
h.update({
    "last_seen": clock, "heartbeat_epoch_utc": epoch, "clock_read": clock,
    "cpu_cores": cpu_cores, "free_ram_gb": free_ram_gb,
    "gpu_free_vram_gb": round(gpu_mb / 1024.0, 3), "gpu_free_vram_mb": gpu_mb,
    "verdict": VERDICT, "current_task": CURRENT_TASK,
    "round_no": 796, "round": 796,
    "last_round_at": clock, "last_action": LAST_ACTION,
    "now_active": NOW_ACTIVE, "latest_artifact": LATEST, "next_milestone": NEXT_MS,
    "task": "r796 closed; see state.next",
    "ts": clock, "updated": clock,
})
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, indent=1, ensure_ascii=False)
    fh.write("\n")

# self-verify: epoch int + clock T-separator (smoke F7 contract)
with open(P, encoding="utf-8-sig") as fh:
    v = json.load(fh)
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in v["clock_read"] and "+08:00" in v["clock_read"], "clock_read must be T-separated ISO with offset"
print("HEARTBEAT OK epoch=%d clock=%s ram=%.2fGB gpu=%dMB" % (epoch, clock, free_ram_gb, gpu_mb))
