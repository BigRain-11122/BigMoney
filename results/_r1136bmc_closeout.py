# -*- coding: utf-8 -*-
"""r1136 bm-c closeout state/heartbeat writer (round counter 1136->1137)."""
import datetime
import json
import os
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
DEC_SHA = "6c5f3444a495fe8f17544731351e0e4d392991070b875075e9a85597e711760e"

NOTE = (
    "r1136: (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 zero-kill + origin 0/0 clean; "
    "(2) zero absorb owed (r1135 closeout landed clean); "
    "(3) PRODUCT = W282 SEAT published (results/_w282bmc_20261020_probe.py -> "
    "_w282bmc_20261020_probe_receipt.json verdict=ADMIT on the post-W281-REGISTERED 271-owner universe): "
    "A 635_701..637_700 32nd consecutive A-hop walk (naive 635_501..637_500 refused at start by registered "
    "W281 B 635_501..635_700; A base == prior-B tail+1 EXACT) / B 637_701..637_900 33rd consecutive "
    "above-own-A (own-A reservation cascade, base==own-A tail 637_700+1); 7/7 relation asserts true, "
    "seed_admit_gate FREE x2 (base=635701 span=2000 / base=637701 span=200), 271-row mutual-exclusion asserts pass; "
    "MSG-20261020-0345-bmc-w282-seat @ALL published; "
    "(4) S0.5/D-19: decisions watermark consumed d5336c87->6c5f3444 (D-20261019-07..09 + D-20261020-01..03 "
    "read in full; zero new BigMoney execution owed -- D-20261019-02 leg-1 bm-c self-removal already landed r1116, "
    "D-20261020-* execute-commander = HQ/night shifts); orders unacked=0 (all 107 local O-*.md acked); "
    "(5) S1 smoke 49/49; satengine rc0 alive (burns_active=[], queue=[]); "
    "(6) S6 light 10/10 rc0 (dualrun/compute_audit/py_watermark/update_daily/regime/clock/fund_premium/"
    "b_layer/daily_report/token delta=0); "
    "(7) S7 attrition 4 ledger files CLEAN (3 historical shrink notes healed) + loop pin=5 no-op + watchdog "
    "re-registered (S4U flip access-denied -> default principal regression face logged) + both claws installed "
    "MATCH + idle --worked rc0 (idle_rounds 0); orphan face=0 at close."
)

UPD = {
    "round_no": 1137,
    "round_no_label": "r1136 closeout -> counter 1137",
    "last_decisions_sha": DEC_SHA,
    "activity_now": "W282 seat published; next = W282 prereg derive (banned_direction_gate ADMIT -> freeze -> splice -> engine burn 12/12 -> sixgate -> finalize 1,044,735 / K 618,320)",
    "current_task": "r1136 closeout (W282 seat product window)",
    "current_task_at": NOW,
    "current_task_ts": NOW,
    "recent_artifact": "results/_w282bmc_20261020_probe_receipt.json",
    "ts": NOW,
    "updated": NOW,
    "updated_at": NOW,
    "last_seen": NOW,
    "clock_read": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "idle_rounds": 0,
    "agenda_starved": False,
    "verdict": ("green r1136 product window: W282 SEAT ADMIT (A 635_701..637_700 32nd A-hop / "
                "B 637_701..637_900 own-A reservation, gates FREE x2); next = r1137 W282 prereg derive"),
    "verify": ("smoke 49/49 | satengine rc0 | S6 10/10 rc0 | attrition 4 CLEAN | orphan face=0 | "
               "seed_admit_gate FREE x2 | 271-row mutual exclusion | decisions watermark consumed"),
    "r1136_closeout_note": NOTE,
}

for rel in ("state-bm-c.json", os.path.join("fleet", "machines", "bm-c.json")):
    path = os.path.join(REPO, rel)
    d = json.load(open(path, encoding="utf-8"))
    d.update(UPD)
    open(path, "w", encoding="utf-8", newline="\n").write(
        json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    back = json.load(open(path, encoding="utf-8"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
    assert back["round_no"] == 1137
    print("updated", rel, "round_no=", back["round_no"], "epoch_int=", isinstance(back["heartbeat_epoch_utc"], int))