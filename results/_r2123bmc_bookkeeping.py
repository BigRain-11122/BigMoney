"""Round 2123 closeout bookkeeping: state round_no + heartbeat.

State and heartbeat are per-machine faces (bm-c); nothing else is written here.
"""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- state: bump round_no, keep every other key intact
sp = "state-bm-c.json"
with open(sp, encoding="utf-8") as fh:
    state = json.load(fh)
before = state.get("round_no")
state["round_no"] = 2123
state["round_note_r2123"] = (
    "amended the 2026-11-23 zt day slice (late-completion superset, 143->146 rows) "
    "so the pool collector's overlap gate passes again; published the generation "
    "r2115-r2122 left uncommitted (470 faces)"
)
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
print("state round_no %s -> %s keys=%d" % (before, state["round_no"], len(state)))

# ---- heartbeat: same shape the smoke F7 leg reads (int epoch, T-separated clock)
hp = "fleet/machines/bm-c.json"
with open(hp, encoding="utf-8") as fh:
    hb = json.load(fh)
now = time.time()
iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(now))
hb["last_seen"] = iso
hb["ts"] = iso
hb["clock_read"] = iso
hb["heartbeat_epoch_utc"] = int(now)
hb["current_task"] = "r2123: zt day-slice amendment (late-completion superset) + publish the uncommitted generation"
hb["verdict"] = "product: pool overlap gate unblocked with evidence; collection pass at the next 30-min window"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["did_r2123"] = "zt-pool-2026-11-23-late-completion-amendment"
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

with open(hp, encoding="utf-8") as fh:
    back = json.load(fh)
print("heartbeat epoch int:", isinstance(back["heartbeat_epoch_utc"], int), "clock:", back["clock_read"])
