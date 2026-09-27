# -*- coding: utf-8 -*-
"""r360 bm-a S7 closeout: state round_no->360, round-report line append,
heartbeat refresh (epoch int + T-separator clock per F7 laws)."""
import io
import json
import subprocess
import sys
import time
import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# ---------- 1. state-bm-a.json ----------
sp = "state-bm-a.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 360
st["did"] = ("R360: 5x HANDOVER reconciliation round (launch-eve green window): S0 clean-tree up-to-date "
             "(HEAD==origin/main 1d05757d) + S0.5 orders 96/96 double-scan zero-unacked + decisions zero-new-actionable "
             "(D-20260927-10 non-BigMoney HQ-executed; council C-01 seat-3 opinion F-20260927-02 already issued r326, "
             "window continues 09-29 12:00) + smoke 25/25 + S2 board zero-open + post_review 3192 rows 15 NO all "
             "same-id-later-YES zero-unresolved + pool real-read watch-face (r359 pit-law): 80 entries, W2-A ready "
             "lane=bm-b (bmb r341-344 burn+fold window, r344 close 22:04:52 landed), W2-B waiting with d8_receipt "
             "dep-1 stamped, dep-2=W2-A finalize -- restore converged both sides + S6 30/30 rc=0 Sunday no-op family "
             "zero-masked (+3 new-bar-gated legal skips) + 5x HANDOVER duty LANDED: R360 promote (R356-360 window: "
             "launch-eve green + W2B silent-loss fix, ledger 286,551 real-read flat, product list zero-drift) + "
             "R355 demote inline + R350 tail dropped-preserved-in-git + S7 schtasks 4/4 + claw IDENTICAL")
st["verify"] = ("smoke 25/25 + S6 30/30 rc=0 zero-masked + orders 96/96 both scans + post_review 0 unresolved + "
                "HANDOVER read-back asserts (promote/demote/drop) + ledger 286,551 flat INTERNAL_BALANCE=0 + "
                "schtasks 4/4 + claw IDENTICAL")
st["next"] = ("Mon 09-28 09:15 T-91 s3 auto-fire (IntradayMarks 09:25; first bar ~15:30 -> live.paper enforce + "
              "t35 open-fill verify + exports; sysv1 marks via bm-b BARS evening); bm-b W2-A finalize re-check + "
              "W2-B sequence (dep-2 only: W2-A finalize -> probe once -> run); MF/AH EM self-heal watch; "
              "council vote-record 09-29 12:00 window close; next 5x=R365 HANDOVER")
st["last_round_at"] = NOW
st["current_task"] = "r360 closed: 5x HANDOVER R360 promote landed, S6 30/30, T-91 armed for Mon 09:15"
st["updated"] = NOW
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1) + "\n")

# ---------- 2. round report line ----------
RLINE = (
    NOW + " | R360 bm-a (dept:总经办·舰队·launch-eve 5x reconciliation) | "
    "WM first-line verdict: GREEN (red=false @22:20 probe py_low_board_clear n=3 span 18.6min legal-idle board-clear; "
    "audit v2.3 22:20 CLEAN py 0.2% flags=[] load_state pool-supply-gap pool_ready=1=W2A-owned-by-bmb) | "
    "did: S0 clean-tree up-to-date (HEAD==origin/main 1d05757d, zero divergence both directions) + S0.5 orders 96/96 "
    "double-scan zero-unacked + decisions zero-new-actionable (D-20260927-10 non-BigMoney HQ-executed zero-action; "
    "council C-20260927-01 seat-3 opinion ALREADY ISSUED F-20260927-02 by bm-a r326 per commit-time canon = zero "
    "re-issue anti-dup, window continues to 09-29 12:00) + S1 smoke 25/25 + S2 board zero-open (job_list empty; "
    "fleet tickets 0 open / 30 claimed-done; T-91 mine armed) + post_review 3192 rows 15 NO all same-id-later-YES "
    "zero-unresolved + pool watch-face real-read (r359 pit-law): 80 entries verified in-file, W2-A ready lane=bm-b "
    "(bmb r341-344 burn+fold window; their r344 close 22:04:52 landed with W2B fold-loss also found+restored their "
    "side = converge), W2-B waiting d8_receipt dep-1 stamped in row (dep-2 = W2-A finalize) + S6 30/30 rc=0 Sunday "
    "no-op family zero-masked (+3 new-bar-gated legal skips: live.paper/t35_open_fill/t24_prospect_paper; daily "
    "0-new cutoff 09-24 + regime ORANGE shadow #10 breadth 0.77 + scorecard 6strat/28trader/7port + clock "
    "CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 + lhb no-op + heat weekend + futures/repo/options "
    "cutoff-covered zero-network + MF rank-pass spawn 22:20 self-heal + sina_mf covered + lane-guards "
    "astock/rev_osc/alloc/fund_premium stdout-no-op + ths same-day idempotent + ah spawn-throttled 10.4s same EM "
    "family + fundamental 0.7h fresh-skip + b_layer gates pass + t24_promo 0/22 honest NOT-ELIGIBLE legs 0/0/0 + "
    "aggr/alloc/grid/sysv1 no-op marks@cutoff T-91 ARMED + t35 export 09-24 regen 6traders 18pos equity 5,996,645 + "
    "daily_scorecard + daily_report REPORT-2026-09-27 regen faces=4 token=1 + build_status + token_meter L2 1-leg "
    "crash-fuse 1) + 5x HANDOVER duty LANDED (R355 pattern 4f6bc885): L4 promote R360 (R356-360 window = launch-eve "
    "green window + W2B pool-row silent-loss fix window; ledger _r295bmb_ledger_scan real-read 286,551 flat "
    "INTERNAL_BALANCE_FAIL=0 DUP_BATCH_CONFLICTS=0 GAP-19 same spectrum; product list zero-drift) + R355 demote "
    "inline + R350 tail dropped-preserved-in-git + S7 schtasks 4/4 (IterationLoop Running / Watchdog 22:50 / "
    "Autofill 22:30 / IntradayMarks Mon 09-28 09:25 Ready = T-91 armed) + claw IDENTICAL + zero memory append "
    "(nothing passed four-question gate) + inbox 1 msg = my outbound to bm-b (their pickup duty) | "
    "verify: smoke 25/25 + S6 30/30 rc=0 zero-masked + orders 96/96 both scans + post_review 0 unresolved + "
    "HANDOVER read-back asserts promote/demote/drop + ledger 286,551 flat + schtasks 4/4 + claw IDENTICAL | "
    "next: Mon 09-28 09:15 T-91 s3 auto-fire (IntradayMarks 09:25; first bar ~15:30 -> live.paper enforce + t35 "
    "open-fill verify + exports; sysv1 marks via bm-b BARS evening); bm-b W2-A finalize re-check + W2-B sequence "
    "(dep-2 only: W2-A finalize -> probe once -> run); MF/AH EM self-heal watch; council vote-record 09-29 12:00 "
    "window close; next 5x=R365 HANDOVER")
with io.open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(RLINE + "\n")

# ---------- 3. heartbeat ----------
hp = "fleet/machines/bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = NOW
hb["current_task"] = "r360 closed+pushing: 5x HANDOVER R360 promote, S6 30/30, T-91 armed Mon 09:15"
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["round_no"] = 360
hb["round"] = 360
hb["loop_round"] = 360
hb["verdict"] = "loaded_ok_maintenance_green"
hb["task"] = "idle-round-done"
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")

# self-proof: epoch must be int, clock must be T-separated ISO
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock not T-separated"
print("closeout OK round=360 epoch=", EPOCH, "clock=", NOW)
