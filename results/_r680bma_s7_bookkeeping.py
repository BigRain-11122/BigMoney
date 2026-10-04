"""r680 bm-a S7 bookkeeping: state round_no, heartbeat, inbox archive, orders double-scan.
Programmatic json writes + json.loads self-verify (r645 law)."""
import json
import os
import glob
import shutil
import time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
clock = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- state: round_no 679 -> 680 ---
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
assert st["round_no"] == 679, f"unexpected round_no {st['round_no']}"
st["round_no"] = 680
st["last_round"] = "r680"
st["next"] = ("r680 done -> r681: fund trio NULLS finalize window 10-05..09 (bm-b canonical; "
              "V786/Q613/D457 of 2000 @14:0x); piece-4 excess-CFO prereg gate = trio finalize -> "
              "D6 corr measured (mktcap caliber leg: GM P1 pending); next-wave candidate drafting "
              "10-06+ (LHB board-level closed r680; seat-axis untested residue; remaining in-house "
              "testable candidates = limit-up relay axis + style rotation axis)")
with open(sp, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
json.loads(open(sp, encoding="utf-8").read())
print("state round_no ->", json.load(open(sp, encoding="utf-8"))["round_no"])

# --- heartbeat ---
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = clock
hb["current_task"] = ("r680: LHB board-level family cheap-census closure (external scan 5 claims "
                      "vs in-house 266k rows; T+1 open-gap eats apparent edge; family closed, "
                      "no burn needed) + S6 37/37 rc0")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
with open(hp, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
d2 = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in d2["clock_read"] and d2["clock_read"] == clock
print("heartbeat epoch", d2["heartbeat_epoch_utc"], "clock", d2["clock_read"])

# --- inbox: process MSG-2026-10-04-1332-bmc-all ---
msg = "fleet/inbox/MSG-2026-10-04-1332-bmc-all.md"
if os.path.exists(msg):
    os.makedirs("fleet/inbox/processed", exist_ok=True)
    shutil.move(msg, "fleet/inbox/processed/" + os.path.basename(msg))
    print("inbox processed:", os.path.basename(msg))

# --- orders double-scan (S7 tail) ---
ack = set(json.load(open(hp, encoding="utf-8")).get("orders_ack", []))
files = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
missing = [f for f in files if f not in ack]
print("orders double-scan:", len(files), "total,", len(missing), "unacked", missing)
assert not missing
