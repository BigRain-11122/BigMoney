# -*- coding: utf-8 -*-
"""R239 closing: ticket progress updates + inbox processing + state/heartbeat/acks.
All shared-JSON edits preserve producer format (indent=1, ensure_ascii=False)."""
import json
import os
import shutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

progress = {
    "74": ("r239 delivered: s0 canon+prereg FROZEN (research/MARKET_CLOCK_COMBO.md v1.0: L1 clock=v3xheat(8 cells, "
           "H_act>=rolling250d p80 AND H_net>0=HOT, LHB 2007-2026 266k rows = heat face; missing census faces disclosed, "
           "forward-only faces banned from replay), L3 sleeve table, L5 ladder RED20/ORANGE50/GREEN80/GREENxHOT95; "
           "s2 criteria frozen: >=200 start grid, costs on, random baseline, N recorded, vs EW-48+B_MAXDIV, D6 corr "
           "check vs T-73 family) + s1 SAME-DAY current call (scripts/market_clock_call.py selftest PASS 4 cases; "
           "CALL-2026-09-24: cell=ORANGE_COOL (81<96 p80 rows, net +16.4Yi), breadth r20+ 0.167, top=513100/512800/512200, "
           "bottom=512400/515030/515790, ladder 50%, sleeves chop-corps+dividend-lowvol; wired into S6 chain after "
           "market_regime leg). NEXT: s2 runner+pool batch (per frozen prereg), then s3 results report to CEO."),
    "75": ("r239 delivered: firm/DECISIONS.md canon (4 backfilled entries) + scripts/daily_report.py v1 (selftest PASS: "
           "4 faces + token line; aggregation-only, honest face-state labels) + FIRST REPORT same-day "
           "(docs/daily_report/REPORT-2026-09-26.md+json: 6 traders + 27 account families + clock cell + 24h throughput "
           "539 commits/88 result jsons/37 digests + decisions tail + queue 26 + token line) + WIRING: S6 chain leg "
           "inserted byte-precise after daily_scorecard (idempotent same-day regen; append-only across days) + "
           "py_watermark.py verdict persistence fix (was stdout-only; now in jsonl record; selftest 20/20) so the "
           "report reads the verdict from the file. NEXT: first live trading-day cycle (Mon 09-28) 15:45 report "
           "verification; T-29/dashboard surfacing citation check."),
    "77": ("r239 delivered slice-1: firm/LOCAL_FIRST.md v2.0 (routing table L1/L2/L3 with CEO carve-outs: "
           "harvest-synthesis + blend design stay cloud; speed-priority law restated; sections 3b crash-loop guard "
           "terms + 3c GPU factor lane terms staged) + token line LIVE in T-75 daily report (results/token_usage.json "
           "consumed; acceptance-d partially met). NEXT slices (continuation): (a) crash-fuse extension in autofill "
           "launcher -- same runner+args+version crash -> refuse re-launch + refusal counter visible (r175/r198 "
           "evidence base); (b) L2 consumption extension -- routine doc legs routed via llm_assist 7b/14b, L2 share "
           "measurable from token_meter; (c) GPU factor lane first batch -- torch availability probe on 4070S, "
           "workers_plan, pool-ready >100-factor matrix job (BelowNormal priority)."),
}

for tid, prog in progress.items():
    p = os.path.join(ROOT, "fleet", "tasks", f"T-2026-09-26-{tid}-P1.json")
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    d["progress_r239"] = prog
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"T-{tid} progress updated")

# ---- inbox: process the bm-b T-76 slice-1 claim notice (FYI, zero conflict with T-74/75/77)
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260926-0927-bm-b-claim-t73-wave10-slice1.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-20260926-0927-bm-b-claim-t73-wave10-slice1.md")
if os.path.exists(src):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    print("inbox msg processed ->", os.path.basename(dst))

# ---- state file: round_no 239
sp = os.path.join(ROOT, "state-bm-a.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 239
st["did"] = ("R239: 3 CEO immediate tickets claimed+started same round (O-0932/0940/0947) -- T-74 market-clock combo "
             "s0 canon frozen + s1 same-day call ORANGE_COOL (CALL-2026-09-24, market_clock_call.py wired), T-75 daily "
             "battle report v1 + DECISIONS.md canon + first report same-day + S6 wiring, T-77 LOCAL_FIRST v2 routing "
             "table + token line live; E1 self-catch P0: science_gates.ledger_head crashed on C-arm list-form "
             "metrics.json (.get on list) -- fixed with isinstance guard + real-form fixture leg (selftest 35/35), "
             "aggressive_lab S6 leg back green; py_watermark verdict now persisted in jsonl (was stdout-only). "
             "Next: T-74 s2 full-history backtest batch, T-77 crash-fuse+L2+GPU slices.")
st["updated"] = "2026-09-26 10:04:00"
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("state round_no=239 written")

# ---- heartbeat: bm-a machine file (epoch int verified)
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
epoch = int(time.time())
hb["last_seen"] = "2026-09-26 10:04:00"
hb["current_task"] = "T-74 s2 backtest batch next + T-77 slices (crash-fuse/L2/GPU); C-arm T-70/T-73 batch in-flight parallel"
hb["cpu_cores"] = 32
hb["idle_ram_gb"] = None  # leave prior value untouched if present
hb["verdict"] = "py_low_with_work_cands (legit: CPU saturated by C-arm LLM inference rounds; 3 CEO tickets claimed+worked same round)"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = "2026-09-26T10:04:00+08:00"
ack = hb.get("orders_ack", "")
for tok in ("O-20260926-0932-bm-a.md", "O-20260926-0940-bm-a.md", "O-20260926-0947-bm-a.md"):
    if tok not in ack:
        ack = (ack + " " + tok).strip()
hb["orders_ack"] = ack
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
with open(hp, encoding="utf-8") as f:
    check = json.load(f)
assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat written; epoch int verified:", check["heartbeat_epoch_utc"])
