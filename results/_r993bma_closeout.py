# -*- coding: utf-8 -*-
"""r993 bm-a closeout: state + heartbeat + round report (fresh-read-modify-write per multi-writer law)."""
import json, io, time, datetime

sys = __import__("sys")
sys.stdout.reconfigure(encoding="utf-8")

NOW = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
EPOCH = int(time.time())
TS = NOW[:19] + "+08:00" if "+08:00" not in NOW else NOW

DID = ("r993: S0 rebase storm canon-resolved (19-UU shared-regen batch deep-ts resolve + md twin pair-alignment per E68 + "
       "r864 add-A continue law; 4 stale stashes cleared per r642 clean-tree law, shas receipted) + push b4b4ec77b "
       "BEHIND=0 + S0.5 D19 dual-delta consumed (ORD 542f99a9 / DEC c61d7884 zero BigMoney directives; probe "
       "decisions_changed flag quirk noted, sha256 equality governs) + S1 smoke 49/49 + S2 boards empty (queue probe "
       "CLEAR T22/E14) + W240 finalize one-pass LANDED (sixgate PRE-FINALIZE fourteenth consecutive ALL PASS -> "
       "finalize 950,135+2,200=952,335 EXACT / K=525,920 -> five-key ALL PASS -> sec78 backfill placeholders=0) + "
       "S6 chain core (dualrun ZERO-DRIFT streak 25 / compute_audit pool_starvation=W241 supply standing / watermark "
       "py_low_board_clear legal-idle / update_daily retry honest no-op bars-10-14-pending-upstream cutoff 10-13 / "
       "scorecard 83.2s + clock ORANGE_COOL + LHB no-op disclosure-window + token delta=0) + E68 card appended")

TASK = ("r993: W240 own-wave finalize LANDED (sixgate PRE-FINALIZE 14th consecutive ALL PASS -> finalize one-pass "
        "950,135+2,200=952,335 EXACT -> five-key ALL PASS -> sec78 backfill; W241 waits-upstream DISARMED by this "
        "finalize per chain-order M12)")

CUR = ("r993: W240 finalize landed (952,335/K 525,920 five-key ALL PASS) + S6 quick legs landed 17:1x (dualrun streak "
       "25 / compute_audit pool_starvation flag / scorecard+clock regenerated) + E68 twin-pair law card; W241 "
       "materialization (seat+derive+freeze in post-W240 universe) = next-round opening product per de-throttle zero-gap")

NEXT = ("r994: W241 seat probe + prereg derive + five-face freeze (post-W240 universe re-derive MANDATORY per W240 "
        "sec.5.5: A naive 547_501..549_500 / B naive 541_004..541_203 CLEAN hops=0 pre-W240 projection, B must reserve "
        "W240 A window, seed-gap inherited) + engine self-burn 12/12 + S6 full chain bars retry + CEO-PROXY orders scan")

VERDICT = ("green (wm-red=false; satengine ALIVE rc0 idle queue0 pool_starvation=W241 supply standing next product; "
           "orphan 0/43; W240 finalize LANDED 952,335/K 525,920 five-key ALL PASS this round; dualrun streak 25)")

VERIFY = ("green (sixgate receipt ALL PASS 14th consecutive + finalize identity 950,135+2,200=952,335 EXACT + "
          "five-key ALL PASS + sec78 placeholders=0 + smoke 49/49 + attrition guard CLEAN rc0 + idle --worked 0 + "
          "push b4b4ec77b behind=0 verified)")

ART = "results/perpetual_faces/n1_w240_results.json (finalize product 952,335/K 525,920, 17:1x)"

# --- state-bm-a.json ---
SP = "state-bm-a.json"
d = json.load(io.open(SP, encoding="utf-8"))
d["round_no"] = 993
d["last_round"] = 993
d["last_round_at"] = TS
d["last_round_closed"] = TS
d["ts"] = TS
d["updated"] = TS
d["did"] = DID
d["task"] = TASK
d["current"] = CUR
d["current_task"] = CUR
d["now_active"] = CUR
d["next"] = NEXT
d["last_action"] = "r993 W240 finalize closeout"
d["last_artifact"] = ART
d["latest_artifact"] = ART
d["recent_artifact"] = ART
d["verdict"] = VERDICT
d["verify"] = VERIFY
d["heartbeat_epoch_utc"] = EPOCH
d["last_heartbeat_epoch_utc"] = EPOCH
d["heartbeat_epoch_utc_type_int"] = True
d["clock_read"] = TS
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["orphan_face"] = 0
d["orphan_faces"] = 0
d["push_verified"] = {"ts": TS, "note": "r993: closeout push this round (see sync)", "origin_tip": "pending"}
io.open(SP, "w", encoding="utf-8", newline="").write(json.dumps(d, indent=1, ensure_ascii=False))

# --- heartbeat fleet/machines/bm-a.json ---
HP = "fleet/machines/bm-a.json"
h = json.load(io.open(HP, encoding="utf-8"))
h["active"] = True
h["round_no"] = 993
h["loop_round"] = 993
h["last_round"] = 993
h["last_seen"] = TS
h["ts"] = TS
h["updated"] = TS
h["clock_read"] = TS
h["heartbeat_epoch_utc"] = EPOCH
h["last_heartbeat_epoch_utc"] = EPOCH
h["heartbeat_epoch_utc_type_int"] = True
h["current"] = CUR
h["current_task"] = CUR
h["now_active"] = CUR
h["did"] = DID
h["task"] = TASK
h["next"] = NEXT
h["last_action"] = "r993 W240 finalize closeout"
h["last_artifact"] = ART
h["latest_artifact"] = ART
h["recent_artifact"] = ART
h["verdict"] = VERDICT
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["next_milestone"] = "W240 finalize LANDED this round; W241 materialization next round; month exam 10-31; C-20261014-01 revisit 10-16"
io.open(HP, "w", encoding="utf-8", newline="").write(json.dumps(h, indent=1, ensure_ascii=False))

# --- round report append (canonical face = ROOT round_reports-bm-a.md per r899 note) ---
RP = "round_reports-bm-a.md"
line = (f"{TS} | r993 | {DID} | evidence: results/_w240bma_sixgate_prereg.json ALL PASS + "
        f"results/perpetual_faces/n1_w240_results.json ledger 952,335/K 525,920 + results/_w240bma_fivekey_receipt.json "
        f"five-key ALL PASS + sec78 placeholders=0 + smoke 49/49 + dualrun streak 25 + push b4b4ec77b | next: {NEXT}\n")
t = io.open(RP, encoding="utf-8").read()
if not t.endswith("\n"):
    t += "\n"
io.open(RP, "a", encoding="utf-8", newline="").write(line)

# verify writes
d2 = json.load(io.open(SP, encoding="utf-8"))
h2 = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int) and isinstance(h2["heartbeat_epoch_utc"], int)
assert d2["round_no"] == 993 and h2["round_no"] == 993
print("STATE+HEARTBEAT+REPORT-OK round=993 epoch=", EPOCH)
