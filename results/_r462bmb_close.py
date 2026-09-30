# r462 bm-b closing writer: round_no bump + round report + heartbeat (S5/S7)
import json, time, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 1. state.json round bump 461 -> 462
st = json.load(open("state.json", encoding="utf-8"))
assert st.get("round_no") == 461, st.get("round_no")
st["round_no"] = 462
st["last_round_at"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
json.dump(st, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state round_no -> 462")

# 2. round report line
now = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
row = (now + " | r462 bm-b | WATERMARK: green (13:36 probe rc0 py_low_board_clear lawful: board 0 open + pool 139/139 done + "
       "bandit 0 open [moneyflow IC claimed-parked EM source, bm-a lane] + RW-5 freeze in effect = lawful idle freeze face) | "
       "CURRENT-ACTIVE: r462 in-session maintenance round -- S0 stash-pop UU marks collision resolved per canon (union 40+40->41 "
       "zero-loss, resolver results/_r462bmb_stash_pop_marks_union.py, fresh r462 pitlaw) + CODELY hot-cold reorg 10614->10040B "
       "(r269+r459 verbatim->archive, results/_r462bmb_codely_reorg.py, zero-loss 7/7) | LAST-ARTIFACTS: marks-20260930.jsonl "
       "tick 18 positions @13:37 (4.3s) + docs/daily_report/REPORT-2026-09-30.md regenerated + docs/live_usage/LIVE-2026-09-30.md "
       "(ORANGE cap50 COOL) regenerated + market_clock CALL-2026-09-28 ORANGE_COOL sleeves=4 | NEXT-MILESTONE: 15:30 post-close "
       "unlock today (>=15:35 rounds: 09-30 bars -> live.paper/t35/prospect accrue, bar-gated legs fire post-close rounds); "
       "RW-1~4 unfreeze <=48h (bm-a T-127, 2026-10-02) then W14 prereg window opens -- within 48h | EVIDENCE: smoke 27/27 + "
       "S6 38-leg all rc0 NON-GREEN=NONE (dualrun ZERO-DRIFT 51/3 @139 BEFORE compute_audit order held + regime ORANGE breadth "
       "0.83 + lhb 30min-guard no-op + minute_feed throttle 16min<20min honest no-op + foreign-lane honest no-ops 10x + "
       "fundamental 2.0h fresh-skip + lane_io guards honest skips) + attrition CLEAN 4 ledgers (2 healed) + claw LF-normalized "
       "installed + loop pin=2 no-op first fire 13:42 + watchdog re-registered first fire 13:40 + orders 127/127 zero-diff "
       "both-scans + decisions.md absent-on-tree zero-action + inbox 2 unread both non-bm-b addressees (MSG-1322 bmc->bma, "
       "MSG-1332 bma->bmc, left for recipients, zero bm-b action face) + heartbeat epoch int self-verified | NEXT-POINTER: "
       "r463 = in-session freeze watch; >=15:35 round = post-close unlock legs (09-30 bars); 2026-10-01 first round fires "
       "month-first trio (science_audit/monthly_briefing/self_review) + REGIME_GUARD v3 date-gate auto-activates hands-off "
       "[via bm-b]\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(row)
print("round report appended")

# 3. heartbeat
epoch = int(time.time())
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
hb["current_task"] = "r462 in-session maintenance: S0 stash-pop marks UU canon-resolved + CODELY reorg under 10KB + S6 38-leg green"
hb["round_no"] = 462
hb["round"] = 462
hb["loop_round"] = 462
hb["last_round_at"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
assert isinstance(hb["heartbeat_epoch_utc"], int)
json.dump(hb, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# self-verify
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat epoch int verified:", chk["heartbeat_epoch_utc"], "clock:", chk["clock_read"])
