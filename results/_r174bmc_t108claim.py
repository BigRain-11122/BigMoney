# -*- coding: utf-8 -*-
"""r174 bm-c one-off: T-2026-09-28-108 claim (O-20260928-1630 claim-and-start
same round; ticket open on origin at claim time -- fetched + verified)."""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-28-108-P0.json")
NOW = time.strftime("%Y-%m-%d %H:%M:%S")

with open(TICKET, encoding="utf-8-sig") as f:
    t = json.load(f)
if t.get("status") != "open":
    print(f"REFUSE: status={t.get('status')} (r239 collision)", file=sys.stderr)
    sys.exit(2)
t["status"] = "claimed"
t["claimed_by"] = ("bm-c (OS iteration loop, round 174; git fetch immediately "
                   "before claim per r239 collision law)")
t["claimed_at"] = NOW
t["progress_r174_bmc"] = (
    "SAME-ROUND START (O-1730) = D2 design-decision slice landed in-ticket + "
    "code build plan; lane-context honesty: bm-a = autofill/dispatcher "
    "machinery author (deepest context); this claim takes the D2 lead per "
    "same-round law, D-face co-execution welcome per O-1614 sec.3 parallel "
    "law (single science face = this ticket). D2 v0.1 design (recorded for "
    "the code slice): resident dispatcher = 30s light pre-check cycle "
    "(pool-face read local+origin via git show; ZERO writes when idle) -> "
    "invokes the EXISTING autofill tick engine only when a lane-compatible "
    "ready entry is visible (claim/launch/fuse/keepalive machinery reused "
    "NOT rewritten, zero-new-science-face); guards = git-quiescence skip "
    "(.git/index.lock + rebase/merge markers, D-20260928-02 family), >=60s "
    "invocation spacing, event-only logging (results/dispatcher_log.jsonl "
    "gitignored + dispatcher_state.<machine>.json machine-suffixed tracked "
    "face); ignition <=60s from ready-visible (acceptance per O-1630 sec.3; "
    "O-1614 sec.2 10-min SLA stays the audit v2.4 line until D2 lands, then "
    "tightens together). Host = schtasks 1-min repetition, pythonw.exe "
    "zero-window (U060), 2x30s inner cycles per invocation; register script "
    "idempotent per register_loop_task.ps1 precedent + Disabled-state "
    "self-heal (MSG-1622 root-cause: time-limit kill must never leave the "
    "task Disabled -- also being added to register_loop_task.ps1 this round "
    "under T-107). bm-c = first registration machine; bm-a/bm-b adoption = "
    "their rounds run the in-repo register script. D1 pool-directory switch "
    "= AFTER current pool drains (migration order frozen in ticket spec)."
)
tmp = TICKET + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(t, f, indent=1, ensure_ascii=False)
os.replace(tmp, TICKET)
print(json.dumps({"ticket": t["id"], "status": t["status"],
                  "claimed_by": "bm-c", "claimed_at": NOW}, ensure_ascii=False))
