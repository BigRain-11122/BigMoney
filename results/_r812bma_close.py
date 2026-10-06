# -*- coding: utf-8 -*-
"""r812 bm-a S7 closeout: round report append + state bump + heartbeat refresh.
Per multi-writer law: fresh-read-modify-write via python (no replace tool on shared ledgers)."""
import json, time, os, sys
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
now = datetime.now(timezone(timedelta(hours=8)))
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# --- 1. round report append (bm-a lane file) ---
rr_path = "logs/iteration-loop/round_reports-bm-a.md"
line = ("| 2026-10-07T07:47 | r812 | S0 dead-r811 rebase estate landed (30-face UU x2 waves per bigmoney-conflict-resolve skill: "
        "ALL_FACES laneviews-union + twins take-newer-same-side + host-guard :3: + satengine daemon :3:; push raced twice, "
        "churn-absorb-5 clean-tree; origin delivery 15d26411b self-verified behind-0) + S0.5 orders 0-unacked/inbox empty/DEC sha MATCH "
        "+ S1 smoke 48/48 + **S3 P0 W169 finalize one-pass (r381 recovery-first law): ledger 775,012->777,212 EXACT r811 projection hit, "
        "pool K=369,720, skill_line 1.1838->1.1839, product results/perpetual_faces/n1_w169_results.json + default-wave selftest PASS** "
        "+ W170 seat published=reserved (r565 law, MSG-0738: A 388_804..390_803 staircase 29th E36 + B 390_804..391_003 mutual-exclusion "
        "walk, pre-seat probe _r812bma_w170_probe.py rc0 ADMIT = the r811 MANDATORY W170+ re-derive, W171+ projection disclosed; "
        "4-item payload pushed 0f00fa424 behind-0) + S6 38/38 rc0 (dualrun streak 51 ZERO-DRIFT; watermark loaded_ok; "
        "compute_audit FLAG supply_gap+supply_floor pool ready 2<floor 3 -> W170 freeze = next-round P0 refill; data cutoffs 2026-09-30 "
        "pre-holiday honest no-op regime; daily_report/LIVE-2026-10-07/dashboard re-derived on host guard) "
        "| evidence: n1_w169_results.json + _r812bma_w170_probe_receipt.json + git 0f00fa424 | next: W170 freeze edits (prereg + "
        "N1_BANDS[170] + WAVE_CONFIGS[170] + materializer + ignition) refills engine lane + pool supply floor |")
with open(rr_path, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("round report appended:", rr_path)

# --- 2. state bump 811 -> 812 ---
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
prev = st.get("round_no")
st["round_no"] = 812
st["last_round"] = "r812"
st["last_round_at"] = iso
st["last_round_ts"] = EPOCH
st["last_action"] = "W169 finalize one-pass + W170 seat published; next W170 freeze"
st["did"] = ("r812 recovery round: S0 dead-r811 rebase estate landed (30-face UU x2 waves resolver, origin 15d26411b) + "
             "S3 P0 W169 finalize one-pass (ledger 775,012->777,212 exact r811 projection hit, pool K=369,720, "
             "skill_line 1.1838->1.1839) + W170 seat published=reserved (A 388_804..390_803 staircase 29th + "
             "B 390_804..391_003, probe ADMIT, payload 0f00fa424) + S6 38/38 rc0 (dualrun streak 51; "
             "supply_gap flag -> W170 freeze next-round P0) | did: S0 estate-resolve+finalize+seat+S6+closeout")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"state round_no {prev} -> 812")

# --- 3. heartbeat refresh (epoch int law R170/R178; clock_read T-sep law R262) ---
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = iso
hb["ts"] = iso
hb["clock_read"] = iso
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = "r812 done: W169 finalize + W170 seat; next W170 freeze"
hb["verdict"] = "green"
import psutil
hb["cpu_cores"] = psutil.cpu_count(logical=True)
vm = psutil.virtual_memory()
hb["idle_ram_gb"] = round(vm.available / 1e9, 1)
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat refreshed, epoch int self-verified:", chk["heartbeat_epoch_utc"])

# --- 4. S7 second orders sweep (double-scan law) ---
import glob
ack = set(hb.get("orders_ack", []))
orders = sorted(glob.glob("fleet/orders/O-*.md"))
unacked = [os.path.basename(o) for o in orders if os.path.basename(o) not in ack]
print("S7 second sweep unacked:", unacked if unacked else "0")
assert not unacked, f"late-order arrival: {unacked}"
print("CLOSEOUT OK r812")
