# -*- coding: utf-8 -*-
# r595 bm-b S7: inbox W115 seat processed-move + orders full-set diff (r367 law) + heartbeat
# dynamic-field-only update with orders_ack +2 (r583 law: load -> touch dynamic -> carry lists verbatim).
import os
import io
import json
import time
import datetime as dt
import shutil

# 1) inbox: W115 seat broadcast processed (informational, no action for bm-b engine lane under
#    O-2115 supply-priority; N1 deprioritized vs new-direction family furnaces)
src = "fleet/inbox/MSG-20261002-2130-bmc-w115-seat.md"
dst = "fleet/inbox/processed/MSG-20261002-2130-bmc-w115-seat.md"
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox: W115 seat -> processed (awareness noted, no action)")

# 2) orders full-set diff: every O-*.md on disk vs heartbeat orders_ack (r367: no name-sort windows)
orders_dir = "fleet/orders"
on_disk = sorted(f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md"))
with io.open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
ack = list(hb.get("orders_ack", []))
pending = [o for o in on_disk if o not in ack]
print("orders on-disk=%d acked=%d pending=%s" % (len(on_disk), len(ack), pending))

# 3) heartbeat dynamic-field-only update (r583 law; R170/R178: epoch must be JSON int; R262: T-sep clock)
new_ack = [o for o in on_disk if o not in ack]  # this round acks O-2100 + O-2115 (handled in-report)
hb["orders_ack"] = ack + new_ack
now = dt.datetime.now().astimezone()
hb["last_seen"] = now.isoformat(timespec="seconds")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now.isoformat(timespec="seconds")
hb["current_task"] = "T-145 slice (a) PIT audit probe delivered + dispatch to bm-c; next = (b) unlock eval on PIT PASS"
hb["verdict"] = "round 595 ok: S0 surgery healed r594 deletions (claw first live save), r594 re-landed at origin; T-145 claimed+started; S6 33 legs rc0; smoke 47/47"
tmp = "fleet/machines/bm-b.json.tmp"
with io.open(tmp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
os.replace(tmp, "fleet/machines/bm-b.json")
with io.open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
print("heartbeat ok: epoch=%d clock=%s orders_ack=%d (pending now 0)"
      % (chk["heartbeat_epoch_utc"], chk["clock_read"], len(chk["orders_ack"])))
