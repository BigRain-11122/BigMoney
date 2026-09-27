# -*- coding: utf-8 -*-
"""r365 bm-a T-95 claim (CEO immediate law O-20260924-1730: claim-and-start same round).
O-2255 landed on origin 23:54:13 mid-round (caught at post-push S7 true-close double-scan,
local tree was pre-rebase blind at 23:5x scan -- r239-family blind window, disclosed).
Fetch-verified origin T-95 open at claim instant."""
import json
import io
import datetime

now = datetime.datetime.now().astimezone()
claimed_at = now.isoformat(timespec="seconds")

p = "fleet/tasks/T-2026-09-27-95-P1.json"
d = json.load(io.open(p, encoding="utf-8"))
assert d.get("status") == "open", f"ticket not open: {d.get('status')}"
d["status"] = "claimed"
d["claimed_by"] = "bm-a (OS iteration loop, round 365 post-push S7 catch; CEO immediate-law claim-and-start same round per O-20260924-1730; git fetch immediately before claim per r239 collision law, origin T-95 verified open)"
d["claimed_at"] = claimed_at
d["claim_note"] = "v2 simplification batch: s1 prereg FREEZE this round (DECISION_CHAIN_LEDGER v1 row + r318 four-ring localization consumed as spec inputs); s2 runner-reuse pool entry next round; overnight burn legal per O-2320"
io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")

# orders_ack: append O-2255 token (full filename with .md suffix, r220 law)
hb_p = "fleet/machines/bm-a.json"
hb = json.load(io.open(hb_p, encoding="utf-8"))
ack = hb.get("orders_ack", [])
import os
tokens = sorted(f for f in os.listdir("fleet/orders") if f.startswith("O-"))
for t in tokens:
    if t not in ack:
        ack.append(t)
hb["orders_ack"] = ack
hb["current_task"] = "r365 closeout: T-95 claimed (CEO O-2255 decision-chain v2 simplification batch, s1 prereg freeze in progress); prior: 5x HANDOVER + Sunday green maintenance"
hb["last_seen"] = claimed_at
import time
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = claimed_at
io.open(hb_p, "w", encoding="utf-8").write(json.dumps(hb, ensure_ascii=False, indent=2) + "\n")

hb2 = json.load(io.open(hb_p, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
assert "T" in hb2["clock_read"]
print("claimed_at:", claimed_at)
print("orders_ack count:", len(hb2["orders_ack"]))
print("newly-acked:", [t for t in hb2["orders_ack"] if "2255" in t])
