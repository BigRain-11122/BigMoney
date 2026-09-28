# -*- coding: utf-8 -*-
"""r150 bm-c closing bookkeeping: state round_no, round report line,
heartbeat update (epoch int + clock_read T-format + self-verify)."""
import io
import json
import time
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone(timedelta(hours=8)))
stamp = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- state-bm-c.json: round_no 149 -> 150
st = json.load(io.open("state-bm-c.json", encoding="utf-8"))
assert st["round_no"] == 149, f"unexpected round_no {st['round_no']}"
st["round_no"] = 150
st["updated"] = stamp
st["last_round_ts"] = stamp
st["updated_at"] = now.strftime("%Y-%m-%d %H:%M")
st["note"] = (
    "r150: TRIAL_LABOR_W3 screen slice-2 claimed (MSG-0839 first-declare per bma "
    "MSG-0810 open invitation) and FULLY delivered: screen-prep/screen/screen-"
    "finalize trio in trial_labor_w3.py (gate columns + gate segmented survival "
    "stats per prereg sec.6 + tl2._finalize_math import + r354 RAM gate), "
    "selftest 59/59 double-run byte-identical, live prep PASS 16.9s (panel 48/48, "
    "anchors 6/6 faithful, census L1253/1127/875, gate na-window 199), pool "
    "TRIAL-LABOR-W3-SCREEN ready lane=null (3752 cells, tick claim next); S7 "
    "pool UU vs bmb keepalive resolved via union canon (_r150bmc_resolve_pool.py, "
    "commit 5010fc0b); S6 30 legs rc=0 pre-market no-op family; HANDOVER r150 "
    "5x line + CODELY batch-39 hot-cold integration + r150 pitlaw (conflict "
    "hunk cuts inside JSON top-level object, shared tail = closing brace)")
json.dump(st, io.open("state-bm-c.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
chk = json.load(io.open("state-bm-c.json", encoding="utf-8"))
assert chk["round_no"] == 150
print("state -> 150 OK")

# --- round_reports-bm-c.md: append one fixed-field line
rr = io.open("logs/iteration-loop/round_reports-bm-c.md",
             "r", encoding="utf-8", newline="").read()
assert rr.endswith("\n")
line = (
    f"{stamp} | r150 | dept:research+strategy: TRIAL_LABOR_W3 screen slice-2 "
    "claimed-and-delivered same round (MSG-0839 declare -> trio built "
    "gate-face+W2-caliber -> selftest 59/59 byte-identical -> prep PASS live "
    "16.9s gates 4/4 -> pool TRIAL-LABOR-W3-SCREEN ready 3752 cells -> S7 "
    "union-resolve vs bmb keepalive storm -> push 5010fc0b); S6 30 legs rc=0 "
    "pre-market no-op (audit CLEAN, WM py_low_board_clear, cutoff 09-24 "
    "mid-autumn correct, regime ORANGE shadow, clock ORANGE_COOL, lane guards "
    "honest no-op, fund_premium 15:30 armed bmc lane, scorecard/daily_scorecard/"
    "build_status stale-takeover derive per in-script STALE_MIN law, daily_report "
    "faces=4, token delta=0); smoke 25/25; orders 99/99 both-scan zero un-acked; "
    "HANDOVER r150 5x line + CODELY batch-39 integration + r150 pitlaw | "
    "evidence: scripts/trial_labor_w3.py + results/trial_labor_w3/prep_state."
    "json + pool entry + 5010fc0b + selftest 59/59 | next: W3-SCREEN tick claim "
    "-> burn -> finalize harvest round (survivors feed judge slice; gate-"
    "segmented survival reconcile vs prereg 5.4 bear>none>bull prediction, "
    "honest either way); fund_premium 15:30 first snapshot (bmc lane); V2-P1 "
    "stable-RAM relaunch watch (bmb post-W2B)\n")
io.open("logs/iteration-loop/round_reports-bm-c.md", "w",
        encoding="utf-8", newline="\n").write(rr + line)
assert line.strip() in io.open("logs/iteration-loop/round_reports-bm-c.md",
                               "r", encoding="utf-8").read()
print("round report appended OK")

# --- heartbeat fleet/machines/bm-c.json
hb_path = "fleet/machines/bm-c.json"
hb = json.load(io.open(hb_path, encoding="utf-8"))
hb["round_no"] = 150
hb["last_seen"] = stamp
hb["heartbeat_epoch_utc"] = epoch          # python int, JSON int type (R170/R178)
hb["clock_read"] = stamp                    # ISO 8601 with T separator (R262)
hb["current_task"] = (
    "r150: W3 screen slice-2 claimed+delivered (MSG-0839; pool TRIAL-LABOR-W3-"
    "SCREEN ready 3752 cells awaiting tick claim; finalize=next harvest round)")
hb["verdict"] = (
    "green: standing-line supply executed per TRIAL_LABOR_LAW sec.1 (W3 screen "
    "slice open per bma MSG-0810 invitation, MSG-first declare honored); zero "
    "other claimable (judge family RAM/physical-gated on bmb per frozen "
    "sec.9.1 ordering; census W2B bmb burning)")
hb["last_round_ts"] = stamp
hb["updated_at"] = stamp
hb["updated"] = stamp
hb["orders_ack"] = sorted(set(hb["orders_ack"]))
json.dump(hb, io.open(hb_path, "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
chk = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print(f"heartbeat OK: epoch={chk['heartbeat_epoch_utc']} (int), "
      f"clock={chk['clock_read']}, round={chk['round_no']}")
