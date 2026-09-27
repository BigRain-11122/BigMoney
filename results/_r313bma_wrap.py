# -*- coding: utf-8 -*-
"""R313 bm-a wrap: round-report line + state + heartbeat (r72 long-line law: python not PS)."""
import json, os, subprocess, time

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ROUND = 313

REPORT_LINE = (
    NOW + " | R313 bm-a (dept:工程+舰队) | "
    "WM first-line verdict: red=false lane healthy; probe 10:54 py_low_board_clear n=2 span 16.2min avg 0.3% LEGAL-idle "
    "(board 0 open tickets 0 bandit 0; pool_ready 1 = bm-c lane T19-PHANTOM-P1 not ours to grind; audit v2.3 CLEAN flags[] "
    "load_state pool-supply-gap starvation-candidate false) | "
    "did: (A) S0 CRASH RECOVERY = round main face: inherited orphan mid-rebase from r312-closeout crashed session "
    "(fb2795fc replay onto bm-b r316 chain 7ce3e12e, 16 UU, zero commands remaining) -> resolved per bigmoney-conflict-resolve "
    "skill push-rejection batch exception (NOT read-only retreat): classifier 11 classified + 5 UNKNOWN manual-classified "
    "(daily-report pair + memory-archive + scorecard pair = derive/append-ledger faces) -> 13 take-new-theirs byte-copies "
    "(ts-verified newer: 10:30-10:40 vs 10:14-10:36) + compute_audit history ts-union 202+201->203 zero-loss latest 10:38:13 + "
    "memory-archive section union (mid_a r316bm-b 6 lines + mid_b r312bm-a 13 lines minus 4 byte-identical dup entries -> 824 lines, "
    "both batch headers kept, zero-loss assert) + CODELY memory-union 8911B<10KB (both machines' live entries verbatim + both "
    "八批 index clauses + r312 bm-a fetch-law entry) -> resolvers results/_r313bma_resolve*.py x5 -> GIT_EDITOR=true continue LANDED; "
    "wave-2: push rejected (bm-c r75 + autofill tick in-window third-writer) -> pull --rebase 2 UU -> autofill_state "
    "mixed-dict+ledger union (50+50->51 unique->cap50 ts-asc write-back r245 + last_tick whole-dict ts-compare kept ours 10:40:02 "
    "r140 + CRLF mirror r223/r234) + token_usage take-new-theirs -> continue -> push LANDED b7eed90d; post-push tree clean main==origin "
    "(B) S0.5 both-scans: orders 96/96 zero unacked (round-start set-diff + wrap rescan); decisions.md zero NEW rows since 03:14 batch "
    "(D-20260927-04/05 receipts standing re-confirmed reasonable-accept per audit gate; 05② full-file orders scan = existing R13 canon, "
    "05③ conflict-marker pre-commit self-adopt re-executed clean this round); inbox zero unprocessed for bm-a "
    "(C) S6 full chain rc=0 Sunday no-new-bar posture (cutoff 09-24 Mid-Autumn Fri holiday: audit CLEAN / wm py_low_board_clear / "
    "daily 0-new / regime ORANGE shadow d2 trigger breadth 0.77 / scorecard 6-28-7 S2A4 / clock ORANGE_COOL sleeves4 activated0 / "
    "lhb 30min-guard / heat weekend / fut+opt cutoff-covered / mf rank-throttle 15.9min in-flight / smf fresh / astock+sigexport "
    "bm-b-lane honest no-op / ths same-day / ah spawn-throttle 15min in-flight / fundprem bm-c-lane / fundamental 13.2h fresh / "
    "b-layer 5222 gates-all-pass / aggr+grid+sysv1 idempotent no-op ARMED Monday / t35 export 09-24 idempotent 18 positions / "
    "daily_scorecard 6 traders / daily_report faces=4 token=1 / build_status 10factors 432combos / token delta=-171 L2 1 leg) | "
    "VERIFIED: smoke 25/25; post_review 2849 rows 0 x-rows; schtasks alive per R49 schtasks-not-CIM law (IterationLoop Running + "
    "Watchdog Ready next 11:20) | "
    "NEXT: Monday 09-28 open window = new-bar full chain + T-91 s3 auto-fire 09:15 (SIG/BARS-09-28 -> sysv1 replay -> first cohort "
    "entries + marks -> three report faces); bm-b harvest verdicts standing (X2/PROS finalize); 10-01 month trio standing; "
    "pool 1 ready = bm-c lane not ours"
)

with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(REPORT_LINE + "\n")
print("report line appended")

# state
state = {
    "round_no": ROUND,
    "did": "R313: crash-recovery round -- orphan r312-closeout rebase taken over + 16-UU canon-resolved (13 take-new-theirs + "
           "compute_audit union 203 + archive union 824L + CODELY union 8911B) + wave-2 2-UU (autofill_state union + token take-new) "
           "-> push LANDED b7eed90d; S6 chain rc=0 Sunday no-new-bar",
    "verdict": "py_low_board_clear legal-idle (pool 1 ready = bm-c lane; board 0; audit CLEAN)",
    "next": "R314: Monday 09-28 window = new-bar chain + T-91 s3 auto-fire 09:15; bm-b harvest verdicts standing; 10-01 month trio standing",
    "ts": NOW, "last_round_ts": NOW, "updated_at": NOW, "last_run": NOW, "last_round_at": NOW,
    "last_round": 312, "updated": NOW, "last_seen": NOW,
    "current_task": "R314 next: Monday window watch + supply line (MF_IC_P1 EM unblock)",
    "task": "R313: crash recovery + push-collision double-resolve + S6 wrap",
}
with open("state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
print("state written round_no=", ROUND)

# heartbeat
hb_path = "fleet/machines/bm-a.json"
with open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
orders = sorted(fn for fn in os.listdir("fleet/orders") if fn.startswith("O-") and fn.endswith(".md"))
hb["orders_ack"] = orders  # full-filename list whole-rewrite per r312 bm-b canon
assert set(orders) <= set(hb["orders_ack"]) and len(set(hb["orders_ack"]) & set(orders)) == len(orders)
hb["last_seen"] = NOW
hb["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())
hb["heartbeat_epoch_utc"] = epoch
assert isinstance(epoch, int)
hb["round_no"] = ROUND
hb["current_task"] = "R313 done: crash-recovery landed b7eed90d; R314 next: Monday window + supply line"
hb["verdict"] = "py_low_board_clear legal-idle (pool 1 ready = bm-c lane T19-PHANTOM-P1; audit CLEAN)"
hb["task"] = "R313: crash recovery + push-collision double-resolve (16+2 UU canon) + S6 wrap"
with open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(hb_path, encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat written: epoch=%d clock=%s ack=%d" % (chk["heartbeat_epoch_utc"], chk["clock_read"], len(chk["orders_ack"])))
