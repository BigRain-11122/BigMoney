# -*- coding: utf-8 -*-
"""r1098 bm-c closeout script (canon clone family): updates state-bm-c.json
(canonical fields, round_no 1098->1099), appends the round_reports-bm-c.md row
(CANONICAL ROOT path per r750 law), updates heartbeat fleet/machines/bm-c.json,
read-back asserts (epoch int / clock_read ISO-T / round_no)."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

# --- light resource sample (CPU via psutil if present; RAM via ctypes; GPU via nvidia-smi hidden) ---
cpu_pct = None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    cpu_pct = None

free_ram_gb = None
try:
    import ctypes

    class MemStat(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]
    ms = MemStat()
    ms.dwLength = ctypes.sizeof(MemStat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    free_ram_gb = round(ms.ullAvailPhys / 1e9, 2)
except Exception:
    free_ram_gb = None

gpu_free_mb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    gpu_free_mb = int(r.stdout.strip().splitlines()[0])
except Exception:
    gpu_free_mb = None

# --- state update ---
sp = os.path.join(ROOT, "state-bm-c.json")
s = json.load(open(sp, encoding="utf-8"))
assert s["round_no"] == 1098, f"counter drift: state round_no={s['round_no']} (expect 1098)"

DID = ("r1098: W272 SEAT PUBLISHED origin f608ff1cee (push first-try behind=0, incl engine ledger append c4c5bfa4ff rebased) -- "
       "probe _w272bmc_20261018_probe.py rc0 ADMIT FIRST-TRY: A 613_701..615_700 (staircase-affects-A TWENTY-FIRST consecutive A-hop; naive 613_501..615_500 REFUSED at registered W271 B 613_501..613_700, live walk 1-hop) / "
       "B 615_701..615_900 (own-A reservation cascade TWENTY-SECOND consecutive above-own-A, base==own-A tail+1; naive 613_701..613_900 lands INSIDE own-A window); seed_admit rc0 FREE x2 (A base=613701 span=2000 / B base=615701 span=200); "
       "origin vacancy four-check green (no seat/row/configs/prereg) + zero W273/W274 skip-claims; leg0 chain-relation W269->W270->W271 ledger 1,016,135->1,018,335->1,020,535 (+2,200/+2,200) / K 589,720->591,920->594,120 (+2,200/+2,200) OK; owner 261 rows -> W272=262nd wave, bm-c 91st own wave candidate; "
       "E63 canon-clone builder _r1098bmc_build_w272_probe.py 50 ordered exact needles ALL count-asserted + MUST/MUST_NOT audit + py_compile green (2 same-window needle heals disclosed: docstring single-line '(seat MSG-' form + self-burn sha 6c1aee751d 9->10char transcription caught fail-closed; dbg evidence _r1098bmc_dbg_docstring.txt); "
       "seat MSG-20261018-191x-bmc-w272-seat.md landed fleet/inbox/; "
       "+ W272 PREREG PREP machine-frozen per r971/r1026 prep precedent (honest split per r1096 multi-step window-budget law: _w271bmc_prereg_derive.py = 48,523B full-window clone job): "
       "frozen face extraction results/_w272bmc_w271_frozen_face.txt 23,336B sha256_16 f8b4a755d81bfbe5 == r1097 pin, blob a5aad2251d04d082 @ f75b18c862 PRE-backfill (r1049/r1052 law) + "
       "anchors key-paths dump + derive handoff facts results/_r1098bmc_w272_derive_facts.json (W271 finalize anchors FULL-PRECISION live-read: merged mu -0.09276411835992728 / sigma 0.24509039950538597 / K-lift +0.0001 / ledger 1,020,535 / K 594,120; r1093 pit law cited); "
       "S0.5: ORD delta consumed BOTH scans (opening c8b328c1->1768e8a4 18:51 bm-d hardware row + S7-tail 1768e8a4->f3a0cbad 3 rows: 19:01 bm-d memory-price backfill + 15:1x CEO meta-criticism C-20261018-05 via bm-a + 19:1x MV V5.8 final-review order BigStream lane -- ALL zero BigMoney/bm-c obligation, judgment evidence results/_r1098bmc_ord_judgment.json); DEC 4cfdd17c FALSE hold all scans; unacked=0 both scans; "
       "S1 smoke 49/49; satengine ALIVE rc0; S6 light 10/10 rc0 (driver _r1098bmc_s6_light.py; ONE clone defect disclosed+fixed same-window: r1096-canon DONE-line astimezone(timespec=) crashed AFTER all 10 legs rc=0 logged, DONE marker appended post-hoc, driver healed in-place); "
       "S7: attrition 4 CLEAN + idle --worked rc0 idle_rounds->0 + quad green (loop pin=5 no-op next-fire 19:25 + watchdog S4U flip access-denied = adjudicated default-principal standing face D-20261002-02 + claws x2 installed) + orphan face=2 zero-kill (legal resident faces family); "
       "S0: rebase 1 engine self-commit c4c5bfa4ff over bm-a r1064 chain x4 clean; tail dual-scan mid-round ORD caught+consumed same-window")

VERIFY = ("W272 seat push f608ff1cee first-try behind=0 fetch-verified (519b94c7dc..f608ff1cee) + probe receipt ADMIT on disk (results/_w272bmc_20261018_probe_receipt.json) + frozen face byte-identity vs r1097 pin (23,336B sha256_16 f8b4a755d81bfbe5) + "
          "ORD watermarks advanced read-back (1768e8a4 + f3a0cbad via d19 --advance two-face, mirrors synced) + DEC hold 4cfdd17c + S6 log 10x rc=0 read-back + smoke 49/49 + attrition CLEAN + idle_rounds=0 + heartbeat epoch int + clock_read ISO-T read-back + 本地未达 origin commit 数=0")

VERDICT = ("green r1098 product window (W272 seat published origin f608ff1cee FIRST-TRY + prereg prep facts machine-frozen; prereg derive = r1099 FIRST ACTION per r1096 window-budget honest-split law; "
           "CEO 15:1x meta-criticism row answered-by-product this window (standing product-first law P-2026-09-29-07); loop CPU-only, GPU=MV PACK-A per O-20261018-1810 sec.2)")

NEXT = ("r1099: (1) W272 PREREG DERIVE = FIRST ACTION (full window budget per r1096 honest-split law; SUB source = W271 prereg frozen face @ f75b18c862 PRE-backfill [HEAD twin = post-backfill, NOT used per r1049/r1052 law]; "
        "facts machine-frozen results/_r1098bmc_w272_derive_facts.json: frozen face 23,336B sha256_16 f8b4a755d81bfbe5 extracted results/_w272bmc_w271_frozen_face.txt; bands A 613_701..615_700 / B 615_701..615_900 per seat receipt f608ff1cee; "
        "anchors FULL-PRECISION machine-read from n1_w271_results.json per r1093 pit law [merged mu -0.09276411835992728 / sigma 0.24509039950538597 / K-lift +0.0001 / ledger head 1,020,535 / K 594,120]; "
        "needle probe MEASURED r1077 law (clone _w271bmc_needle_probe.py); derive canon-clone _w271bmc_prereg_derive.py [pre-author consumed-label forms per r1059]; banned_direction_gate ADMIT; freeze research/PERPETUAL_N1_W272_PREREG.md + push); "
        "(2) splice chain = r1100 FIRST ACTION after prereg freeze (five-face editor derive needs full window); "
        "(3) Monday 10-20 15:30 bars window: full papers chain (weekend 10-18/19 no bars, cutoff 10-16 current, debt=0); "
        "(4) RAM watch standing (MV PACK-A GPU lane; loop CPU-only); (5) watchdog S4U manual re-pass backlog face (adjudicated default-principal standing)")

CLOSEOUT_NOTE = ("r1098: clean continuation window (state round_no=1098 at open per r1097 counter advance, executed r1098, advanced 1098->1099 so next=r1099); zero absorb owed (r1097 closeout landed clean 18:48:20, zero dead window between); "
                 "zero double-count: S0.5 opening dual-scan consumed the 18:51 row (ORD c8b328c1->1768e8a4) + S7 tail re-scan caught+consumed 3 more rows (1768e8a4->f3a0cbad, group orders.md hot-moving bm-a hardware+MV window disclosed); DEC 4cfdd17c FALSE hold both scans; "
                 "products: W272 seat estate f608ff1cee + prereg prep facts; prereg derive deferred to r1099 FIRST ACTION with machine-frozen facts per r1096 honest-split law (derive clone = 48,523B full-window job)")

ARTIFACT = ("W272 seat estate origin f608ff1cee (probe _w272bmc_20261018_probe.py + receipt ADMIT + seat MSG-20261018-191x-bmc-w272-seat.md + E63 builder) + prereg prep facts results/_r1098bmc_w272_derive_facts.json + frozen face results/_w272bmc_w271_frozen_face.txt (23,336B sha256_16 f8b4a755d81bfbe5 @ f75b18c862)")

s.update({
    "round_no": 1099,
    "last_round": "r1098",
    "last_round_label": "r1098",
    "last_round_at": NOW_ISO,
    "last_round_closed": NOW_ISO,
    "last_round_closed_at": NOW_ISO,
    "last_round_summary": DID[:2000],
    "last_action": "r1098 closeout (W272 seat published + prereg prep; counter 1098->1099)",
    "last_action_at": NOW_ISO,
    "head_sha": "r1098 closeout (W272 seat published + prereg prep; counter 1098->1099)",
    "clock_read": NOW_ISO,
    "ts": NOW_ISO,
    "now_active": NOW_ISO,
    "activity_now": NOW_ISO,
    "updated": NOW_ISO,
    "updated_at": NOW_ISO,
    "current_task": "r1099 FIRST ACTION: W272 prereg derive (facts frozen results/_r1098bmc_w272_derive_facts.json)",
    "current_task_at": NOW_ISO,
    "current_task_ts": EPOCH,
    "did": DID,
    "verify": VERIFY,
    "verdict": VERDICT,
    "next": NEXT,
    "next_pointer": NEXT,
    "next_milestone": "W272 prereg derive freeze (r1099 FIRST ACTION, within 48h); splice chain r1100; Monday 10-20 15:30 papers chain",
    "latest_artifact": ARTIFACT,
    "last_artifact": ARTIFACT,
    "recent_artifact": ARTIFACT,
    "r1098_closeout_note": CLOSEOUT_NOTE,
    "idle_rounds": 0,
    "agenda_starved": False,
    "orphan_face": 2,
    "orphan_faces": 2,
    "heartbeat_epoch_utc": EPOCH,
    "prod_lanes": "CPU=engine W272 prereg derive armed (r1099 FIRST ACTION on post-W271-REGISTERED universe, seat bands A 613_701..615_700 / B 615_701..615_900 @ f608ff1cee); GPU=MV PACK-A i2v lane per O-20261018-1810 sec.2 (CEO full-mobilization resume standing; loop CPU-only); short-video lane DISABLED standing per O-20261017-1741",
    "full_load_selfproof": {"占用一行": "CPU=W272 seat PUBLISHED + prereg prep frozen (r1099 derive armed); GPU=MV PACK-A i2v burn in flight (gen-only standing, loop CPU-only); short-video lane DISABLED standing per O-20261017-1741"},
})
if cpu_pct is not None:
    s["cpu_pct"] = cpu_pct
    s["cpu_util_pct"] = cpu_pct
if free_ram_gb is not None:
    s["free_ram_gb"] = free_ram_gb
    s["idle_ram_gb"] = free_ram_gb
    s["ram_free_gb"] = free_ram_gb
if gpu_free_mb is not None:
    s["gpu_free_vram_mib"] = gpu_free_mb
    s["gpu_free_vram_mb"] = gpu_free_mb
    s["gpu_free_mb"] = gpu_free_mb
    s["gpu_idle_vram_mb"] = gpu_free_mb
    s["gpu_idle_mb"] = gpu_free_mb
s["sync"] = {"origin_tip": "r1098 W272 SEAT PUBLISHED f608ff1cee landed (push first-try, behind=0); closeout commit rides this window", "ts": NOW_ISO}

json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- round report row (CANONICAL ROOT path, r750 law) ---
rp = os.path.join(ROOT, "round_reports-bm-c.md")
row = ("| %s | r1098 | W272 SEAT PUBLISHED origin f608ff1cee (probe ADMIT first-try: A 613_701..615_700 21st A-hop / B 615_701..615_900 22nd above-own-A, seed FREE x2, vacancy 4-check; E63 50-needle builder count-asserted, 2 heals disclosed) "
       "+ W272 prereg PREP machine-frozen (frozen face f8b4a755d81bfbe5 23,336B @ f75b18c862 + derive facts json; derive=48,523B full-window job -> r1099 FIRST ACTION per r1096 honest-split law) "
       "+ ORD 4 rows consumed zero-action (18:51/19:01 bm-d hardware + 15:1x CEO meta-criticism via bm-a + 19:1x MV V5.8 BigStream) + DEC hold "
       "| smoke 49/49 + S6 10/10 rc0 (DONE-line clone defect disclosed+healed) + attrition CLEAN + quad green + idle_rounds 0 + watermark green (next_pick chain-armed) | "
       "r1099: W272 prereg derive FIRST ACTION (facts _r1098bmc_w272_derive_facts.json) -> splice r1100; Monday 10-20 15:30 papers chain | watermark=green | 本地未达 origin commit 数=0 |") % NOW_ISO
with open(rp, "a", encoding="utf-8") as f:
    f.write(row + "\n")

# --- heartbeat update ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h.update({
    "last_seen": NOW_ISO,
    "last_seen_at": NOW_ISO,
    "ts": NOW_ISO,
    "clock_read": NOW_ISO,
    "heartbeat_epoch_utc": EPOCH,
    "last_round": "r1098",
    "verdict": VERDICT,
    "current_task": "r1099 FIRST ACTION: W272 prereg derive (facts frozen results/_r1098bmc_w272_derive_facts.json)",
    "did": DID,
    "verify": VERIFY,
    "next": NEXT,
    "next_pointer": NEXT,
    "latest_artifact": ARTIFACT,
    "idle_rounds": 0,
    "agenda_starved": False,
    "last_orders_sha": s["last_orders_sha"],
    "last_decisions_sha": s["last_decisions_sha"],
})
if cpu_pct is not None:
    h["cpu_pct"] = cpu_pct
if free_ram_gb is not None:
    h["free_ram_gb"] = free_ram_gb
if gpu_free_mb is not None:
    h["gpu_free_vram_mib"] = gpu_free_mb
    h["gpu_free_vram_mb"] = gpu_free_mb
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- read-back asserts (R170/R178/R262 law) ---
s2 = json.load(open(sp, encoding="utf-8"))
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(s2["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(h2["heartbeat_epoch_utc"], int), "heartbeat epoch must be int"
assert "T" in s2["clock_read"] and "T" in h2["clock_read"], "clock_read must be ISO-T"
assert s2["round_no"] == 1099, "round_no must be 1099 after advance"
assert s2["last_orders_sha"] == h2["last_orders_sha"], "heartbeat ORD mirror drift"
assert s2["last_decisions_sha"] == h2["last_decisions_sha"], "heartbeat DEC mirror drift"
print("CLOSEOUT OK | round_no=1099 | epoch=%d (int) | clock=%s | cpu=%s ram_free=%s gpu_free=%s | report row appended (canonical root path)" % (
    EPOCH, NOW_ISO, cpu_pct, free_ram_gb, gpu_free_mb))
