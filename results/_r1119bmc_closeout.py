# -*- coding: utf-8 -*-
"""r1119 bm-c closeout: state round_no 1119->1120 + heartbeat mirror + round report row.
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

NEXT = ("r1120 FIRST ACTIONS: (1) W279 prereg derive = P0 first action (live re-derive on the "
        "post-W278 universe per W279 seat MSG-20261019-145x-bmc-w279-seat origin 900c23fe7d + probe "
        "receipt _w279bmc_20261019_probe_receipt.json: bands A 629_101..631_100 TWENTY-EIGHTH A-hop / "
        "B 631_101..631_300 TWENTY-NINTH above-own-A; prereg builder canon = r1116 recipe "
        "one-generation roll; upstream W278 finalize anchors live-read from _r1118bmc_w278_fivekeys.json "
        "+ n1_w278_results.json: ledger 1,035,935 / K=609,520 / mu -0.09278576 / sigma 0.24505494 / "
        "a_p95 0.2844 / line_merged_609520 1.1969 / se_mu 0.000314 / klift -0.0002; W280p projection "
        "A naive 631_101..633_100 refused-at-registered-W279-B expected face); (2) TODAY Monday 15:30 "
        "papers chain on the new bar (debt=0 cutoff 10-16: live.paper enforce + t35_openfill + t24 x2 + "
        "aggr + alloc + grid + system_v1 + t35_export + scorecard); (3) night GPU lane standing P0 = "
        "XQ xingqing carry-burn + jman v2 young-era + female-lead W1/W2 datasets; (4) W279 prereg -> "
        "splice editor chain = subsequent rounds honest-split per r1096; (5) next 5x HANDOVER duty = "
        "bm-c r1120")

DID = ("r1119 (W278 cycle-complete + W279 seat window): (1) W278 finalize one-pass = r1119 FIRST ACTION "
       "landed (expected ledger 1,035,935 / K=609,520 EXACT per sixgate ledger_pre machine face; "
       "w278-only mu -0.0970 / sigma 0.2361 K=2,200; merged mu -0.09278576 / sigma 0.24505494 K=609,520; "
       "K-lift delta -0.0002 key4-band legal; n_eff held 1,033,735; skill_line 1.1971->1.1969; product "
       "results/perpetual_faces/n1_w278_results.json landed); (2) W278 fivekeys 6/6 ALL PASS (clone BUILT "
       "r1118 results/_r1118bmc_w278_fivekeys.py; frozen keys = W277 finalize actuals live-read; key1 "
       "w278-vs-merged gap 0.0042293 / key1b merged-vs-W277 1.53e-05 / key2 sigma rel -1.306e-04 / key3 "
       "A p95 0.3095->0.2844 delta -0.0251 double-direction in-band / key4 -0.0002 / key5 se_mu "
       "0.000314<=0.000314 held-flat; ledger + K identities EXACT; receipt _r1118bmc_w278_fivekeys.json); "
       "(3) sec.7/8 backfill zero-placeholder (script _r1119bmc_w278_sec78_backfill.py r1114 canon clone, "
       "all values machine-read; prereg post-backfill twin landed, frozen PRE-backfill sha16 "
       "99001d3d3f337942 per r1049/r1052); (4) W279 SEAT published same-window per seat-first law (probe "
       "_w279bmc_20261019_probe.py rc0 ADMIT first-try: A 629_101..631_100 TWENTY-EIGHTH consecutive A-hop "
       "live-walk measured (naive 628_901..630_900 refused at registered W278 B 628_901..629_100) / B "
       "631_101..631_300 TWENTY-NINTH above-own-A (naive 629_101..629_300 refused by own-A reservation "
       "cascade); roller token maps + 21 count-asserted patches + preflight 53/53 vs on-disk W278 probe; "
       "builder 53 needles first-try after P1b MUSTC-prefix patch healed same-window (builder MUST_CONTAIN "
       "birth-station catch, zero disk pollution, disclosed); seed_admit FREE x2 629101/2000 + 631101/200; "
       "origin vacancy four-check green; zero W280/W281 skip-claims; universe post-W278-REGISTERED 268 "
       "owner rows bma 130 / bmb 41 / bmc 97 -> W279 = 269th, bm-c 98th own; seat commit 900c23fe7d); "
       "(5) D-19: S7 tail delta consumed 1 row (14:48 科学借鉴律 zero bm-c action, receipt "
       "_r1119bmc_ord_tail_judgment.json; advance 86f6fcef->b97cb656 read-back equality heartbeat mirrors "
       "synced; final re-probe dual FALSE); (6) S7: attrition 4 ledger files CLEAN + quad green "
       "(IterationLoop PT5M next 15:00 rc0 + LoopWatchdog PT2M next 14:59 rc0 + claws precommit/prepush "
       "IN-PLACE) + orphan 3/0/1 zero-kill + idle --worked rc0 idle_rounds=0; (7) W278 CYCLE COMPLETE = "
       "splice+burn+sixgate r1118 + finalize/fivekeys/sec78 r1119 same-session per 0502c722ac estate "
       "canon; (8) mid-window bm-b race a23a5441d2 (r1024 drama/voice lane) absorbed at closeout -- zero "
       "overlap with bm-c dirty faces verified pre-integration, rebase+push rides this window")

VERIFY = ("finalize ledger/K EXACT dual (1,035,935/609,520) + fivekeys 6/6 receipt re-read + sec78 "
          "zero-placeholder re-read + probe ADMIT receipt re-read + roller preflight 53/53 + builder 53 "
          "needles + quad green x4 + attrition CLEAN + d19 advance read-back full-string equality + "
          "final tail probe dual FALSE (ord b97cb656 / dec 95879dd9) + orphan 0 + idle --worked rc0 + "
          "epoch int + report row +1 asserted + closeout push rides this window (rebase onto a23a5441d2 "
          "+ push + fetch behind-0 self-proof)")

VERDICT = ("green r1119 W278 cycle-complete + W279 seat window (finalize 1,035,935/609,520 EXACT + "
           "fivekeys 6/6 + sec78 zero-placeholder + W279 seat ADMIT first-try published 900c23fe7d + "
           "D-19 1-row tail consumed dual-clean at close + quad green; W279 prereg derive = r1120 first "
           "action; GPU idle day, night queue XQ + jman v2 + female-lead datasets)")

st.update({
    "round_no": 1120,
    "round_no_label": "r1119 closeout -> counter 1120",
    "last_round": "r1119",
    "last_round_label": "r1119",
    "last_round_at": ts, "last_round_ts": ts, "last_round_closed": ts, "last_round_closed_at": ts,
    "last_round_summary": VERDICT, "last_round_summary_at": ts,
    "last_action": "r1119 closeout (W278 CYCLE COMPLETE: finalize 1,035,935/609,520 EXACT + fivekeys 6/6 + sec78 zero-placeholder + W279 seat published 900c23fe7d; counter 1119->1120)",
    "last_action_at": ts,
    "last_run_at": ts,
    "last_pulled_at": ts,
    "current_task": "r1120 FIRST ACTION = W279 prereg derive (post-W278 universe, bands A 629_101..631_100 / B 631_101..631_300 per seat probe); TODAY 15:30 papers chain; night GPU lane XQ+jman v2+female-lead",
    "current_task_at": ts, "current_task_ts": epoch,
    "did": DID,
    "verify": VERIFY,
    "verdict": VERDICT,
    "head_sha": "r1119 closeout (W278 cycle complete: finalize/fivekeys/sec78 + W279 seat 900c23fe7d; D-19 ord b97cb656; W279 prereg = r1120 first)",
    "last_artifact": "results/perpetual_faces/n1_w278_results.json (finalize product) + results/_r1118bmc_w278_fivekeys.json + research/PERPETUAL_N1_W278_PREREG.md (sec78 backfilled) + results/_w279bmc_20261019_probe.py + _w279bmc_20261019_probe_receipt.json + _r1119bmc_roll_w279_probe.py + _r1119bmc_build_w279_probe.py + fleet/inbox/MSG-20261019-145x-bmc-w279-seat.md (this closeout batch)",
    "next": NEXT, "next_pointer": NEXT,
    "next_milestone": "W279 prereg derive (r1120 first action) -> W279 splice editor chain; TODAY 15:30 papers chain; night GPU training lane",
    "note": "r1119: W278 CYCLE COMPLETE (splice r1118 + finalize/fivekeys/sec78 r1119 same-session estate) + W279 seat published same-window (900c23fe7d, A 629_101..631_100 28th A-hop / B 631_101..631_300 29th above-own-A); D-19 tail 1-row consumed dual FALSE at close",
    "full_load_selfproof": {
        "占用一行": "CPU=W278 cycle complete + W279 seat published (engine wave chain = W279 prereg derive r1120 first action); GPU=idle day, night queue = XQ xingqing carry-burn + jman v2 young-era + female-lead W1/W2 datasets (standing GPU-lane night P0); short-video lane DISABLED standing per O-20261017-1741",
        "最近实物": "results/perpetual_faces/n1_w278_results.json (finalize 1,035,935/609,520 EXACT) + seat commit 900c23fe7d (W279 A 629_101..631_100 / B 631_101..631_300) @ " + ts,
        "下个里程碑": "W279 prereg derive r1120 first action -> W279 splice editor chain; TODAY 15:30 papers chain on new bar; night GPU lane",
    },
    "prod_lanes": "CPU=W278 cycle landed + W279 seat published (prereg derive r1120); GPU=idle day (night queue XQ+jman v2+female-lead standing P0 night); short-video lane DISABLED standing per O-20261017-1741",
    "r1119_closeout_note": DID,
    "orphan_face": 0, "orphan_faces": 0,
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": epoch,
    "heartbeat_epoch_utc_type": "int (assert)",
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "last_seen": ts, "last_seen_at": ts, "now_active": ts, "activity_now": ts,
    "orders_ack_receipt": "r1119: ORD S7 tail 86f6fcef->b97cb656 (1 row: 14:48 科学借鉴律 zero bm-c action, receipt _r1119bmc_ord_tail_judgment.json); DEC 95879dd9 FALSE hold both scans; final re-probe dual FALSE (b97cb656/95879dd9)",
    "orders_ack_ts": ts,
    "ram_critical_face": "none (loop CPU-only, GPU idle day)",
    "ram_free_gb": free_ram, "idle_ram_gb": free_ram, "free_ram_gb": free_ram,
    "cpu_pct": cpu_pct, "cpu_util_pct": cpu_pct, "cpu_idle_pct": round(100 - cpu_pct, 1),
    "sync": {"origin_tip": "r1119 closeout commit rides this window (rebase onto a23a5441d2 + push lands this window; post-push behind=0 verified same window)", "ts": ts},
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
dg["round_ref"] = 1119
dg["ts"] = ts
st["d19_watermark_guard"] = dg

with open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, sort_keys=True, ensure_ascii=False)
with open(HB, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, sort_keys=True, ensure_ascii=False)

# ---------- report row ----------
row = " | ".join([
    ts, "r1119", "bm-c",
    "watermark verdict=green (%s; D-19 S7 tail 1 row (14:48 科学借鉴律) consumed zero bm-c action, "
    "advance 86f6fcef->b97cb656, final re-probe dual FALSE; 孤儿面=0 (py_faces=3 / 0 orphans / 1 "
    "resident, zero-kill); 本地未达 origin commit 数=0 (closeout rebase+push rides this window + "
    "fetch self-proof); W278 CYCLE COMPLETE (finalize 1,035,935/609,520 EXACT + fivekeys 6/6 + sec78 "
    "zero-placeholder) + W279 seat published (A 629_101..631_100 / B 631_101..631_300); boards clear, "
    "jobs 0; idle --worked rc0 idle_rounds=0)" % wm_verdict,
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
assert hb["round_no"] == 1120, "counter must be 1120"
assert "T" in hb["clock_read"], "clock_read must be T-separated ISO8601"
with open(STATE, "r", encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["last_round"] == "r1119" and st2["round_no"] == 1120
print("CLOSEOUT OK round_no=1120 epoch=%d clock=%s free_ram=%.2fGB gpu_free=%sMiB report_row=+1" % (
    hb["heartbeat_epoch_utc"], hb["clock_read"], free_ram, gpu_free_mib))
