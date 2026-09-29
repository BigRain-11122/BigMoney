#!/usr/bin/env python
"""r460 bm-a closeout: state file bump + round report line + heartbeat."""
import json
import time
from datetime import datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

# --- state-bm-a.json: round_no 460 -> 461 + did/verify/next ---
state_path = ROOT + r"\state-bm-a.json"
with open(state_path, encoding="utf-8") as fh:
    st = json.load(fh)
assert st["round_no"] == 460, f"unexpected round_no {st['round_no']}"
st["round_no"] = 461
st["did"] = ("r460: (1) dead-session adoption: prior r460 session (06:28-06:51) died uncommitted "
             "while awaiting PoolWorker 06:52 fire -- full work verified green then landed: "
             "fill_ladder runner_args fail-closed gate (r444 no-arg-leg root fix, 6 selftest legs "
             "ALL PASS) + CODELY reorg (4 cold pointers to archive, 9,597B < 10,240B line) + "
             "r460 crash-fuse pit entry + S6 36-leg green + 2 read-only W6 forensics probes; "
             "(2) W6 verdict landed via bm-b burn (RRG-ROTATION-P1 0/4 judged-negative, family "
             "closed, ledger 355,375): 06:52 PoolWorker freeze root-caused = origin pending MSG-0805 "
             "(bm-b claim-collision heads-up names SLOT-6); bm-c stale-tree claim self-resolved per "
             "same-seed determinism (r460 verified: single verdict, no double ledger, head 355,375); "
             "(3) 15-UU rebase storm canon-resolved: classifier 9+6 manual classes, 6 ALL_FACES "
             "merge_lane_views resolve + reconcile (3 faces settle-lag drift, superset-both-parents "
             "verified), snapshots deep-ts take-local, twins same-side (REPORT/LIVE local 06:36:54 > "
             "origin 06:28:08), archive union 95|94->96 headings zero-loss, CODELY auto-merge r327 "
             "entry-level verify zero-loss; push LANDED 38ea8108b..19166f758; "
             "(4) dualrun ZERO-DRIFT streak 40/3; (5) orders 122/122 dual-scan zero-diff + decisions "
             "review clean + inbox MSG-0640 (SLOT-8 berth, bm-b) + MSG-0805 (W6 verdict+collision) "
             "both read/processed; (6) 5x HANDOVER overdue window R446-R460 entry filed (anchor "
             "355,375 live-read, r450/r455 missing rows disclosed, bm-c r255 misread corrected)")
st["verify"] = ("smoke 26/26; fill_ladder selftest ALL PASS (runner_args gate); attrition guard 4 "
                "ledgers CLEAN; dualrun ZERO-DRIFT 40/3; W6 verdict file+ledger verified "
                "(355,375=355,371+4 single-count); precommit claw parity True; IterLoop pin=8 "
                "no-op + watchdog Ready; orders 122/122; pool SLOT-6 done on origin (bm-b r449 + "
                "bm-c r257 harvest)")
st["next"] = ("r461: (1) W13 SUMN adoption freeze window OPEN (W12-JUDGE landed 06:06) -- bm-a "
              "berth per W13 draft checklist: frozen prereg whole-package + SEED_REGISTRY three "
              "keys 20323000/20323500/20324000 three-step reverify (r441 law) + REAL-DATA "
              "identity-face first-run three-command law (r446 surgical pit); (2) D-20260929-04(1) "
              "IntradayMarks Last-Run recheck (9:25 fire passed?); (3) SLOT-7 runner = bm-c lane "
              "watch; SLOT-8 freeze = bm-b lane watch; (4) 10-01 month-first-round trio + "
              "REGIME_GUARD v3 date-gate auto-activation hands-off; (5) S9C amend veto window to "
              "10-07; reconcile drift settle via next S6 producer runs")
st["last_round_at"] = "2026-09-30T07:30:00+08:00"
st["current_task"] = "r460 closed (dead-session adoption + W6 collision closeout + 15-UU storm + 5x HANDOVER); next = W13 freeze window"
st["updated"] = "2026-09-30T07:30:00+08:00"
with open(state_path, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
print("state bumped to", st["round_no"])

# --- round_reports-bm-a.md: one fixed-field line ---
rr = ROOT + r"\round_reports-bm-a.md"
line = ("2026-09-30T07:30:00+08:00 | r460 | dept:工程/舰队 | dead-session adoption landed "
        "(fill_ladder runner_args fail-closed gate selftest green + CODELY reorg + S6 36-leg) + "
        "W6 RRG-ROTATION verdict 0/4 judged-negative verified landed via bm-b (ledger 355,375 "
        "single-count, bm-c claim-collision self-resolved) + 15-UU rebase storm canon-resolved "
        "(push 19166f758) + 5x HANDOVER overdue window R446-460 filed | verify: smoke 26/26 + "
        "fill_ladder selftest + guard CLEAN + dualrun 40/3 + orders 122/122 | next: W13 freeze "
        "window (seeds three-step) + D-04(1) 9:25 recheck + 10-01 trio\n")
with open(rr, "a", encoding="utf-8", newline="") as fh:
    fh.write(line)
print("round report line appended")

# --- heartbeat fleet/machines/bm-a.json ---
hb_path = ROOT + r"\fleet\machines\bm-a.json"
with open(hb_path, encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = "2026-09-30T07:30:00+08:00"
hb["current_task"] = "r460 closed; W13 freeze window next"
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = datetime.now().astimezone().isoformat(timespec="seconds")
with open(hb_path, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
with open(hb_path, encoding="utf-8") as fh:
    back = json.load(fh)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat written; epoch int verified:", back["heartbeat_epoch_utc"])
