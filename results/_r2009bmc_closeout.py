"""r2009 closeout: update this machine's own state face and heartbeat fields.

Under a CONTENTION window this round only lands NEW files plus the machine's own
single-writer records (state-<id>.json / heartbeat), never a shared code or data face.
"""
import datetime
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
FIELDS = os.path.join(ROOT, "results", "_r2009bmc_heartbeat_fields.json")

now = datetime.datetime.now().astimezone().replace(microsecond=0)
iso = now.isoformat()
epoch = int(time.time())

DID = ("product: scripts/etf_book_nobond_ticket.py + results/etf_book_nobond_ticket.json + "
       "research/ETF_BOOK_NOBOND_TICKET.md -- the production candidate's order ticket "
       "(5-name bond-free + 8% vol target): today's scale 0.7350 / cash 26.50%, three capital "
       "sizes with whole lots and a 5 CNY ticket floor, and the 975 CNY one-lot floor whose "
       "round-trip commission is 5.13% of capital")
NEXT = ("(a) attach this face to the S6 chain + two smoke legs once the contention window closes; "
        "(b) the ticket prices lots but not impact: read etf_book_capacity_at_size at these "
        "sizes and say whether 13-15% of NAV per name is placeable")

with open(STATE, encoding="utf-8") as f:
    st = json.load(f)

prev_round = st.get("round_no")
prev_done = st.get("rounds_done")
if isinstance(prev_round, int) and prev_round >= 2009:
    print("round_no already", prev_round, "-- refusing to rewind")
else:
    st["round_no_prev"] = prev_round
    st["round_no"] = 2009
    if isinstance(prev_done, int):
        st["rounds_done"] = prev_done + 1

st["did"] = DID
st["did_round"] = 2009
st["activity"] = "product"
st["activity_now"] = ("r2009: the production candidate's order ticket -- 73.5% invested, 26.5% "
                      "cash, three capital sizes in whole lots")
st["activity_now_round"] = 2009
st["current"] = st["activity_now"]
st["current_task"] = st["activity_now"]
st["current_task_at"] = iso
st["current_task_short"] = "r2009 nobond ticket"
st["last_round"] = 2009
st["last_round_at"] = iso
st["next"] = NEXT
st["next_pointer"] = NEXT
st["clock_read"] = iso
st["heartbeat_epoch_utc"] = epoch
st["ts"] = iso
st["last_seen"] = iso
st["last_orders_sha"] = "99e8e77d093cc13df12a599cd9ba1c5aa2d87fe942380a5f002242c31a07a42c"
st["last_orders_read_at"] = iso
st["last_orders_note"] = (
    "r2009: group docs/orders.md raw-blob sha256 99e8e77d (was aad2632e at the watermark) -- "
    "the new tail is MacBook 主控/养号/移交 rows plus one fleet-wide 2026-11-22 22:31 order "
    "(local-first compute, cloud needs local_checked + why_not_local evidence). No quant-line "
    "work order. This round ran entirely on local CPU with zero cloud calls, so the fleet-wide "
    "order is satisfied by construction; fleet/orders diff is CLEAN (116 files / 329 acks / 0 unacked)")
st["last_decisions_checked_at"] = iso
st["contention"] = {
    "evidence": "results/_repo_write_contention.bm-c.json",
    "rc": 3,
    "verdict": "CONTENTION",
    "round": 2009,
    "note": ("3 hosts alive (pid 51252 resident ACP host, pid 67160 interactive since 20:05, this "
             "host). New-file faces only this round; no shared code/data face and no S6 chain run"),
}
st["orphan_note"] = "orphan face probe: py_faces 8, orphans 0"

with open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

fields = {
    "last_seen": iso,
    "ts": iso,
    "clock_read": iso,
    "heartbeat_epoch_utc": epoch,
    "round": 2009,
    "round_no": 2009,
    "busy": False,
    "cur_task": "r2009 nobond ticket (5-name bond-free book at 73.5% invested)",
    "current_task": st["activity_now"],
    "current_task_at": iso,
    "health": "ok",
}
with open(FIELDS, "w", encoding="utf-8") as f:
    json.dump(fields, f, ensure_ascii=False, indent=1)

print("state updated: round_no", st.get("round_no"), "rounds_done", st.get("rounds_done"))
print("fields written", FIELDS)

hb = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "heartbeat_write.py"),
                     "apply", "--fields", FIELDS], capture_output=True, text=True)
print("heartbeat rc", hb.returncode)
print((hb.stdout or "").strip()[:800])
print((hb.stderr or "").strip()[:400])
