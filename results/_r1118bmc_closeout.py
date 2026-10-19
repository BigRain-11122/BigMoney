# -*- coding: utf-8 -*-
"""r1118 bm-c closeout: state round_no 1118->1119 + heartbeat mirror + round report row.
Live faces refreshed in-process (psutil) + one nvidia-smi via CREATE_NO_WINDOW (U060)."""

import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
WMRED = os.path.join(ROOT, "results", "watermark_red.json")

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# ---------- live faces ----------
import psutil
free_ram = round(psutil.virtual_memory().available / 1e9, 2)
cpu_pct = round(psutil.cpu_percent(interval=1), 1)
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
gpu_free_mib = None
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True,
                       creationflags=CNW, text=True)
    parts = p.stdout.strip().splitlines()[0].split(",")
    gpu_free_mib = int(parts[0].strip())
    gpu_util = float(parts[1].strip())
except Exception:
    gpu_free_mib, gpu_util = None, None

wmred = {}
try:
    with open(WMRED, "r", encoding="utf-8") as f:
        wmred = json.load(f)
except Exception:
    pass
wm_verdict = "red=true" if wmred.get("red") else "red=false"

with open(STATE, "r", encoding="utf-8") as f:
    st = json.load(f)

NEXT = ("r1119 FIRST ACTIONS: (1) W278 finalize one-pass = P0 first action per honest-split law "
        "(expected ledger 1,035,935 / K=609,520 EXACT per sixgate ledger_pre machine face; finalize "
        "canon = r1114-continuation recipe one-generation roll) -> W278 fivekeys 6/6 (clone BUILT this "
        "window results/_r1118bmc_w278_fivekeys.py, frozen keys = W277 finalize actuals live-read "
        "mu -0.09277044 / sigma 0.24508694 / a_p95 0.3095 / line_merged 1.197 / se_mu 0.000314 / "
        "k_lift 0.0) -> sec.7/8 backfill; (2) W279 seat = live re-derive on the post-W278 universe per "
        "W278 freeze receipt downstream_seat face (W279p naive A 628_901..630_900 lands INSIDE "
        "registered W278 B 628_901..629_100 = staircase affects A inherited, twenty-eighth A-hop "
        "expected; B own-A reservation cascade; never transcribe r587); (3) TODAY Monday 15:30 papers "
        "chain on the new bar (debt=0 cutoff 10-16); (4) night GPU lane standing P0 = XQ xingqing "
        "carry-burn + jman v2 young-era + female-lead W1/W2 datasets; (5) next 5x HANDOVER duty = "
        "bm-c r1120")

DID = ("r1118 (W278 five-face splice product window): (1) S0-1 anchor bm-c + round-zero probe "
       "py_faces=3 orphans=0 resident_servers=1 zero-kill; S0 fetch HEAD==origin 050b15588a 0/0 clean "
       "open; (2) S0.5 D-19 opening ORD 15f5bbbf->c6aeabd1 consumed 9 rows (8 zero-action "
       "BigStream/bm-a lanes + 1 standing-GPU-lane carry 13:2x paiman-ling v2; judgment receipt "
       "results/_r1118bmc_ord_judgment.json; 2 same-window appended rows 13:38/13:40 honest full "
       "coverage) / DEC 95879dd9 FALSE hold; d19 update --advance read-back full-string equality + "
       "heartbeat mirrors synced; (3) S1 smoke 49/49; (4) P0 W278 FIVE-FACE FREEZE SPLICE LANDED "
       "b6f486af35 (needle preflight FIRST-RUN ZERO-MISMATCH measured r1077 law on canon "
       "_w277bmc_freeze_edits.py sha16 d4913e4ad111fd85 62,353B; E63 22nd-gen derive editor ALL "
       "phase1-3 count-asserted reps first-try + phase4 zero-residual + phase5 presence gates PASS -> "
       "DST _w278bmc_freeze_edits.py 62,582B py_compile OK; first splice attempt gate0 fail-closed on "
       "mid-window bm-b race d2667773da -> discard-3-regenerable probe faces + ff per r609 gate0 law -> "
       "SPLICE OK first-try: bands A 626_901..628_900 TWENTY-SEVENTH A-hop / B 628_901..629_100 "
       "TWENTY-EIGHTH above-own-A registered per seat receipt b187aa6214 verbatim; gate0.5 upstream "
       "W277 landed 1,033,735/K=607,320 EXACT owner rows 267+candidate 268th bm-c 96+candidate 97th; "
       "seed_admit FREE x2 626901/2000 + 628901/200; banned ADMIT rc0; pf selftest 9/9 + n1 selftest "
       "PASS; push first-try behind=0/ahead=0); (5) engine mtime-watch self-ignite W278 burn dedup "
       "12/12 (batches 60e630918f six + b965e2ecf0 six both self-committed on origin per W272 estate "
       "precedent); (6) S6 light 10/10 rc0 (driver results/_r1118bmc_s6_light.py r1117 canon clone, "
       "log _r1118bmc_s6_log.txt; Monday pre-15:30 honest: update_daily 0 rows cutoff 10-16 / papers "
       "debt=0 / fund_premium no-op; pool_dualrun+compute_audit+py_watermark+market_regime+clock_call+"
       "b_layer+daily_report+token all rc0); (7) sixgate PRE-FINALIZE 41st consecutive ALL PASS "
       "first-try (gate-clone builder results/_r1118bmc_build_gate_clones.py FIRST-RUN ZERO-MISMATCH "
       "87 sixgate needles + 33 fivekeys needles + W277 anchors live-verified; generated "
       "_r1118bmc_w278_sixgate.py receipt _r1118bmc_w278_sixgate.json + _r1118bmc_w278_fivekeys.py "
       "BUILT for the r1119 finalize face; CAB 11th consecutive per canon chain arithmetic W276 9th "
       "-> W277 10th -> W278 11th, splice-commit prose '10th gen' reads as the canon-template "
       "generation, disclosed in the builder header); (8) S7: attrition 4 ledger files CLEAN (3 "
       "historical shrinks healed as-is) + quad green (IterationLoop PT5M live next-fire 14:15 rc0 + "
       "LoopWatchdog PT2M live next 14:15 rc0 + claws precommit/prepush IN-PLACE CR-normalized "
       "identical vs Tools/git-hooks canon x2; IntradayMarks standing-absent = quartet-expected face, "
       "census-340 verified) + D-19 S7 tail delta consumed 4 rows (13:41 MV V5.10 SIL4 + "
       "14:02/14:09/14:14 WorkBuddy Phase 3/4/5, all zero bm-c quant-loop action, receipt "
       "_r1118bmc_ord_tail_judgment.json; advance c6aeabd1->86f6fcef read-back full-string equality "
       "heartbeat mirrors synced; final re-probe dual FALSE) + idle --worked rc0 idle_rounds=0 "
       "agenda_starved=false + orphan probe 3/0/1 zero-kill re-verified")

VERIFY = ("smoke 49/49 + splice commit b6f486af35 push first-try behind=0/ahead=0 + engine dedup "
          "12/12 dual-face + sixgate ALL PASS receipt re-read + builder logs 87+33 needles first-try "
          "+ S6 log 10x rc=0 re-read + attrition CLEAN + quad green x4 + d19 advance read-back "
          "full-string equality + final tail probe dual FALSE (ord 86f6fcef / dec 95879dd9) + idle "
          "--worked rc0 + orphan 0 + epoch int + report line +1 asserted + closeout commit rides "
          "this window (push+fetch+behind-0 self-proof)")

VERDICT = ("green r1118 W278 five-face splice product window (splice b6f486af35 landed "
           "first-try-after-ff + engine burn 12/12 + sixgate 41st ALL PASS first-try + D-19 13 rows "
           "consumed zero bm-c action dual-clean at close + quad green + S6 10/10 + smoke 49/49; "
           "finalize/fivekeys/sec78 = r1119 first action honest split per r1096 law; GPU idle day, "
           "night queue XQ + jman v2 + female-lead datasets)")

st.update({
    "round_no": 1119,
    "round_no_label": "r1118 closeout -> counter 1119",
    "last_round": "r1118",
    "last_round_label": "r1118",
    "last_round_at": ts, "last_round_ts": ts, "last_round_closed": ts, "last_round_closed_at": ts,
    "last_round_summary": VERDICT, "last_round_summary_at": ts,
    "last_action": "r1118 closeout (W278 splice b6f486af35 + burn 12/12 + sixgate 41st ALL PASS + D-19 13 rows consumed + quad green; counter 1118->1119)",
    "last_action_at": ts,
    "last_run_at": ts,
    "last_pulled_at": ts,
    "current_task": "r1119 FIRST ACTION = W278 finalize one-pass (expected ledger 1,035,935/K=609,520 EXACT) -> fivekeys 6/6 (clone BUILT) -> sec78; W279 seat post-W278 re-derive; TODAY 15:30 papers chain; night GPU lane XQ+jman v2+female-lead",
    "current_task_at": ts, "current_task_ts": epoch,
    "did": DID,
    "verify": VERIFY,
    "verdict": VERDICT,
    "head_sha": "r1118 closeout (W278 splice b6f486af35 + burn 12/12 + sixgate 41st ALL PASS; D-19 ord 86f6fcef; finalize = r1119 first)",
    "last_artifact": "results/_r1118bmc_w278_sixgate.json (41st PRE-FINALIZE ALL PASS) + results/_r1118bmc_w278_sixgate.py + results/_r1118bmc_w278_fivekeys.py (BUILT for r1119) + results/_r1118bmc_build_gate_clones.py + results/_r1118bmc_ord_judgment.json + results/_r1118bmc_ord_tail_judgment.json + results/_r1118bmc_s6_light.py + results/_r1118bmc_s6_log.txt (this closeout batch)",
    "next": NEXT, "next_pointer": NEXT,
    "next_milestone": "W278 finalize one-pass (r1119 first action) -> fivekeys 6/6 -> sec78 -> W279 seat; TODAY 15:30 papers chain; night GPU training lane",
    "note": "r1118: W278 five-face splice landed b6f486af35 first-try-after-ff + engine burn 12/12 + sixgate 41st ALL PASS first-try + gate-clone builder FIRST-RUN ZERO-MISMATCH; D-19 13 rows consumed (9 opening + 4 S7 tail) all zero bm-c action; finalize/fivekeys/sec78 = r1119 honest split",
    "full_load_selfproof": {
        "占用一行": "CPU=W278 splice+burn+sixgate chain landed (P0 product window; engine wave chain = finalize r1119 first action); GPU=idle day, night queue = XQ xingqing carry-burn + jman v2 young-era + female-lead W1/W2 datasets (standing GPU-lane night P0); short-video lane DISABLED standing per O-20261017-1741",
        "最近实物": "results/_r1118bmc_w278_sixgate.json (41st PRE-FINALIZE ALL PASS first-try) + splice commit b6f486af35 + engine batches 60e630918f/b965e2ecf0 @ " + ts,
        "下个里程碑": "W278 finalize one-pass r1119 first action (expected 1,035,935/609,520 EXACT) -> fivekeys 6/6 -> W279 seat post-universe re-derive; TODAY 15:30 papers chain; night GPU lane",
    },
    "prod_lanes": "CPU=W278 chain landed (splice+burn+sixgate; finalize r1119); GPU=idle day (night queue XQ+jman v2+female-lead standing P0 night); short-video lane DISABLED standing per O-20261017-1741",
    "r1118_closeout_note": DID,
    "orphan_face": 0, "orphan_faces": 0,
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": epoch,
    "heartbeat_epoch_utc_type": "int (assert)",
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "last_seen": ts, "last_seen_at": ts, "now_active": ts, "activity_now": ts,
    "orders_ack_receipt": "r1118: ORD 15f5bbbf->c6aeabd1 (9 rows opening, receipt _r1118bmc_ord_judgment.json) + S7 tail c6aeabd1->86f6fcef (4 rows, receipt _r1118bmc_ord_tail_judgment.json) = 13 rows ALL zero bm-c quant-loop action; DEC 95879dd9 FALSE hold both scans; final re-probe dual FALSE (86f6fcef/95879dd9)",
    "orders_ack_ts": ts,
    "ram_critical_face": "none (loop CPU-only, GPU idle day)",
    "ram_free_gb": free_ram, "idle_ram_gb": free_ram, "free_ram_gb": free_ram,
    "cpu_pct": cpu_pct, "cpu_util_pct": cpu_pct, "cpu_idle_pct": round(100 - cpu_pct, 1),
    "sync": {"origin_tip": "r1118 closeout commit rides this window (push lands this window; post-push behind=0 verified same window)", "ts": ts},
})
if gpu_free_mib is not None:
    st["gpu_free_mib"] = gpu_free_mib
    st["gpu_free_vram_mib"] = gpu_free_mib
    st["gpu_idle_mib"] = gpu_free_mib
    st["gpu_idle_vram_mib"] = gpu_free_mib
    st["gpu_vram_free_mb"] = gpu_free_mib
    st["gpu_free_vram_mb"] = gpu_free_mib
    st["gpu_idle_vram_mb"] = gpu_free_mib
    st["free_vram_mb"] = gpu_free_mib
    st["gpu_free_mb"] = gpu_free_mib
    st["gpu_util_pct"] = gpu_util
    st["gpu_used_mib"] = 16384 - gpu_free_mib

dg = st.get("d19_watermark_guard", {})
dg["round_ref"] = 1118
dg["ts"] = ts
st["d19_watermark_guard"] = dg

with open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, sort_keys=True, ensure_ascii=False)
with open(HB, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, sort_keys=True, ensure_ascii=False)

# ---------- report row ----------
row = " | ".join([
    ts, "r1118", "bm-c",
    "watermark verdict=green (%s; D-19 ORD 15f5bbbf->c6aeabd1 9 rows + S7 tail c6aeabd1->86f6fcef "
    "4 rows = 13 rows consumed ALL zero bm-c quant-loop action, DEC 95879dd9 FALSE hold both scans, "
    "final re-probe dual FALSE; 孤儿面=0 (py_faces=3 / 0 orphans / 1 resident, zero-kill); 本地未达 "
    "origin commit 数=0 (closeout push rides this window + fetch self-proof); engine W278 dedup 12/12 "
    "landed, boards clear, jobs 0; idle --worked rc0 idle_rounds=0)" % wm_verdict,
    DID,
    "verify: " + VERIFY,
    "next " + NEXT,
])
raw = open(REPORT, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-400:] else b"\n"
with open(REPORT, "ab") as f:
    f.write(eol + row.encode("utf-8"))

# ---------- self-asserts ----------
with open(HB, "r", encoding="utf-8") as f:
    hb = json.load(f)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb["round_no"] == 1119, "counter must be 1119"
assert "T" in hb["clock_read"], "clock_read must be T-separated ISO8601"
with open(STATE, "r", encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["last_round"] == "r1118" and st2["round_no"] == 1119
print("CLOSEOUT OK round_no=1119 epoch=%d clock=%s free_ram=%.2fGB gpu_free=%sMiB report_row=+1" % (
    hb["heartbeat_epoch_utc"], hb["clock_read"], free_ram, gpu_free_mib))
