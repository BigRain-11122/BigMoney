# -*- coding: utf-8 -*-
"""r410 bm-b heartbeat update (epoch int law R170/R178 + T-separator clock law R262)."""
import io
import json
import time
from datetime import datetime, timezone, timedelta

p = "fleet/machines/bm-b.json"
hb = json.load(io.open(p, encoding="utf-8"))
tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
epoch = int(time.time())

hb["machine_id"] = "bm-b"
hb["role"] = hb.get("role", "compute-node")
hb["joined"] = hb.get("joined", "2026-09-23")
hb["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["current_task"] = (
    "round 410 done: TRIAL_LABOR_W6 runner slice landed (trial_labor_w6.py selftest 80/80 + grammar "
    "FROZEN 2d395f5f8e7d16cb 193,536 combos + pool TRIAL-LABOR-W6-GENERATE ready; T-117 sec.9 open "
    "slice, claim MSG-0450 receipted) -- next: autofill generate burn -> SCREEN entry -> judge trio "
    "(RAM sequencing); astock repull in-flight, rev_osc waits panel"
)
hb["round_no"] = 410
hb["loop_round"] = 410
hb["round"] = 410
hb["verdict"] = (
    "healthy: smoke 26/26; S3 standing-line W6 runner slice landed (selftest 80/80 hermetic, grammar "
    "sha constructively distinct W1-W5, pool entry ready consumer_plan carried); S6 37 legs rc=0; "
    "orders 122/122 double-scan; pit-law batch-84 + CODELY reorg hot 7,966B zero-loss; supply standing "
    "(W6 generate burn next via autofill + astock repull in-flight + V3 runner bm-c gap)"
)
hb["orders_ack"] = hb.get("orders_ack", [])
hb["n_orders_ack"] = len(hb["orders_ack"])

io.open(p, "w", encoding="utf-8", newline="").write(
    json.dumps(hb, ensure_ascii=False, indent=1) + "\n")

# self-verification: epoch must be a JSON int, clock must be T-separated
chk = json.load(io.open(p, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"], "clock not T-separated"
assert chk["round_no"] == 410
print("heartbeat OK: epoch=", chk["heartbeat_epoch_utc"],
      "type=", type(chk["heartbeat_epoch_utc"]).__name__,
      "clock=", chk["clock_read"])
