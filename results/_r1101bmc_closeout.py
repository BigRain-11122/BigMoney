# -*- coding: utf-8 -*-
"""r1101 bm-c closeout: state round_no 1101->1102 + heartbeat mirror + round report row.
Fresh-read-modify-write per r1006 multi-writer law. Metrics via psutil + nvidia-smi
(CREATE_NO_WINDOW). Epoch MUST be JSON int (R170/R178). clock_read MUST be ISO-T (R262).
Round report row goes to the CANONICAL root path round_reports-bm-c.md (r750 law).
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

now = datetime.datetime.now().astimezone()
NOW = now.isoformat(timespec="seconds")          # 2026-10-18T21:2x:xx+08:00 (T-sep)
EPOCH = int(time.time())

# ---- metrics -----------------------------------------------------------------
cpu_pct = None
free_ram = None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    free_ram = round(psutil.virtual_memory().available / (1024 ** 3), 2)
except Exception as e:
    print("metric fallback (psutil):", e)

gpu_free_mib = None
gpu_used_mib = None
gpu_total_mib = None
gpu_util = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.used,memory.total,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True,
                       creationflags=CNW)
    m = r.stdout.strip().splitlines()[0].split(",")
    gpu_free_mib = int(m[0].strip())
    gpu_used_mib = int(m[1].strip())
    gpu_total_mib = int(m[2].strip())
    gpu_util = int(m[3].strip())
except Exception as e:
    print("metric fallback (nvidia-smi):", e)

DID = ("r1101: W273 SEAT PUBLISHED origin 39e1bb32f1 first-try push behind=0 (bm-c 92nd own wave "
       "candidate, 263rd engine wave) -- probe _w273bmc_20261018_probe.py rc0 ADMIT first-try via E63 "
       "canon-clone builder _r1101bmc_build_w273_probe.py (53 ordered needles all-count-asserted, "
       "reverse-order wave rolls, MUST/MUST_NOT audit + py_compile green; triple-label heal canon "
       "rolled one generation per r1100 heal note): A 615_901..617_900 TWENTY-SECOND consecutive "
       "A-hop (live walk refused naive 615_701..617_700 at the REGISTERED W272 B band "
       "615_701..615_900, hops=1, 1-hop live trace recorded) / B 617_901..618_100 TWENTY-THIRD "
       "consecutive above-own-A (naive 615_901..616_100 lands INSIDE the own-wave A first-clean "
       "window 615_901..617_900 -> own-A reservation hops past 617_900, base==own-A tail+1); "
       "seed_admit_gate rc0 FREE x2 (base=615901 span=2000 checked=2000 / base=617901 span=200 "
       "checked=200) + origin vacancy four-check green (no seat/row/configs/prereg on origin) + "
       "zero W274/W275 skip-ahead claims + W274+ forward projection recorded in receipt leg4; "
       "chain-relation anchors W270->W271->W272 ledger 1,018,335->1,020,535->1,022,735 "
       "(+2,200/+2,200) / K 591,920->594,120->596,320 (+2,200/+2,200) machine-read verbatim")

VERIFY = ("seat commit 39e1bb32f1 on origin behind=0 fetch-verified (42dcc66c81..39e1bb32f1 "
          "first-try push) + probe receipt results/_w273bmc_20261018_probe_receipt.json ADMIT "
          "verdict + builder output 53/53 needles 1x + smoke 49/49 + S6 light 10/10 rc0 "
          "(dualrun ZERO-DRIFT streak 51 [461 entries] / compute_audit FLAG pool_starvation+supply_floor "
          "structural answered-by-chain [W273 seat armed this window] / py_watermark py_low_board_clear "
          "legal [bars_present=false weekend, board clear] / bars cutoff 10-16 weekend honest / "
          "regime ORANGE 6th day shadow / market_clock CALL-2026-10-16 ORANGE_COOL idempotent / "
          "REPORT-2026-10-18 faces=5 / token delta=0) + attrition 4 files CLEAN (healed notes as-is) + "
          "quad green (loop pin=5 no-op first fire 21:25 + watchdog registered [S4U XML flip "
          "access-denied = adjudicated default-principal standing face per D-20261002-02] + "
          "pre-commit claw + pre-push claw installed) + idle --worked rc0 idle_rounds->0 + "
          "watermark advanced d923d08918->f99c9c6d->2e2276ca both via d19 dual-face read-back OK "
          "mirrors synced + final probe FALSE both + epoch int + clock_read ISO-T")

NEXT = ("r1102: (1) W273 PREREG DERIVE = FIRST ACTION (E63 canon-clone derive on the post-W272 "
        "universe: frozen W272 template extraction byte-verified @ c049a57623 PRE-backfill face per "
        "r1052/r1049 law + needle facts-probe MEASURED r1077 law + derive ALL GATES PASS + banned "
        "gate ADMIT; bands A 615_901..617_900 / B 617_901..618_100 per seat receipt verbatim "
        "in-gate zero-transcription; anchors FULL-PRECISION machine-read n1_w272_results.json per "
        "r1093 pit law; never transcribe r587) -> five-face splice chain follows per multi-step "
        "window-budget law (derive full-window job = r1096 honest-split precedent); (2) Monday "
        "10-20 15:30 bars window: full papers chain (weekend 10-18/19 no bars, cutoff 10-16 current, "
        "debt=0); (3) BigMoney automation-plan faces (W-formalization/backtest-gate-in-loop/daily-PnL "
        "attribution per 20:48/20:54/21:11 CEO order chain) = GM/committee-layer execution items, "
        "deadlines <=10-25/<=10-31, watch for BM-repo O-order via bm-b/CEO-PROXY mirror; (4) RAM "
        "watch standing (MV PACK-A GPU lane in flight, loop CPU-only)")

NOTE = ("r1101: product window (state round_no=1101 at open per r1100 counter advance, executed "
        "r1101, advanced 1101->1102 so next=r1102); zero absorb owed (r1100 closeout + postscript "
        "42dcc66c81 landed clean 20:56:58, zero dead window between); zero double-count: S0.5 "
        "opening scan consumed 1 row (d923d08918->f99c9c6d, 20:54 CEO 子公司全量梳理勘正令 -- "
        "BigMoney seat already dispatched at 20:48, zero new bm-c obligation) + S7 tail re-scan "
        "caught+consumed 1 more row (f99c9c6d->2e2276ca, 21:11 CEO 九司自动化建设方案呈报令 -- plan "
        "file landed by bm-a interactive window, BigMoney execution-phase items = GM/committee layer "
        "with <=10-25/<=10-31 deadlines, zero immediate bm-c action; W-wave loop operating = the live "
        "product the plan describes); DEC 4cfdd17c FALSE hold both scans; unacked=0 both scans "
        "(orders_ack_scan CLEAN 103/228/0 zero face divergence); d19 --advance dual-face x2 "
        "(opening f99c9c6d + tail 2e2276ca) read-back OK; final probe FALSE both faces")

VERDICT = ("green r1101 product window (W273 SEAT PUBLISHED one-window ADMIT first-try: A "
           "615_901..617_900 22nd consecutive A-hop / B 617_901..618_100 23rd consecutive "
           "above-own-A per live walk; probe E63 canon-clone clean-at-build, zero heals needed, "
           "zero transcription; prereg derive armed = r1102 FIRST ACTION; loop CPU-only, "
           "GPU=MV PACK-A per CEO weekend production standing)")

CURRENT_TASK = "r1102 FIRST ACTION: W273 prereg derive (E63 canon-clone on post-W272 universe, never transcribe r587)"

CLOSEOUT_NOTE = ("r1101: (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=0 zero-kill "
                 "(resident ComfyUI listener legal face) + S0 fetch 0/0 clean open (r1100 postscript "
                 "42dcc66c81 == origin; daemon live-face watermark_red.json 21:06:03 regenerable "
                 "disclosed); (2) S0.5 opening ORD delta consumed d923d08918->f99c9c6d (1 row = 20:54 "
                 "CEO 子公司全量梳理勘正令, nine-seat full-count erratum, BigMoney seat already "
                 "dispatched 20:48 = zero bm-c action) + DEC 4cfdd17c hold + orders_ack_scan CLEAN "
                 "103/228/0 zero face divergence unacked=0; (3) smoke 49/49; (4) P0 PRODUCT = W273 "
                 "SEAT PUBLISHED origin 39e1bb32f1 first-try (probe ADMIT first-try via E63 builder "
                 "53-needle all-count-asserted; bands A 615_901..617_900 / B 617_901..618_100 live "
                 "walk; seed FREE x2; vacancy four-check; zero skip-claims; W274+ projection); "
                 "(5) S6 light 10/10 rc0 (dualrun streak 51 / audit FLAG answered-by-chain / "
                 "py_low_board_clear legal / ORANGE 6th day / token delta=0); (6) S7 tail dual-scan "
                 "caught+consumed 21:11 九司方案呈报令 row (zero bm-c action, GM-layer execution) + "
                 "final probe FALSE both; (7) quad green (watchdog S4U flip = adjudicated "
                 "default-principal standing face) + attrition 4 CLEAN + idle --worked + seat MSG "
                 "swept to processed; counter 1101->1102")

PROD_LANES = ("CPU=W273 SEAT PUBLISHED origin 39e1bb32f1 (supply head; prereg derive = r1102 FIRST "
              "ACTION); GPU=MV PACK-A i2v lane per O-20261018-1810 sec.2 (CEO full-mobilization "
              "resume standing; loop CPU-only); short-video lane DISABLED standing per O-20261017-1741")

ORD_NOTE = ("r1101: ORD d923d08918->f99c9c6d consumed at open + f99c9c6d->2e2276ca consumed at tail "
            "(content-sha1 pinned r977; 2 rows = CEO 20:54 全量梳理勘正令 + 21:11 九司建设方案呈报令, "
            "both zero bm-c action -- BigMoney seat dispatched at 20:48 [W 波循环正式化 via "
            "bm-b/CEO-PROXY mirror], plan execution-phase = GM/committee layer <=10-25/<=10-31); "
            "dec 4cfdd17c hold both scans")

ACK_RECEIPT = ("r1101: S0.5 opening + S7-tail dual-scan consumed group-tree ORD rows (2 rows total: "
               "20:54 CEO 子公司全量梳理勘正令 + 21:11 CEO 九司自动化建设方案呈报令 -- both "
               "nine-seat group-level dispatches, BigMoney seat already dispatched at 20:48, ZERO "
               "new bm-c obligation this window); repo O-files unacked=0 both scans (ack scan CLEAN "
               "103/228/0 zero face divergence); d19 --advance dual-face x2 read-back OK heartbeat "
               "mirrors synced")

DEC_NOTE = "r1101: DEC delta FALSE at open+tail both (raw-blob sha256 4cfdd17c hold; zero rows owed)"

ARTIFACT = ("W273 seat publish commit 39e1bb32f1 (probe receipt results/_w273bmc_20261018_probe_receipt.json "
            "ADMIT A 615_901..617_900 / B 617_901..618_100; builder _r1101bmc_build_w273_probe.py "
            "53-needle)")

fields = {
    "clock_read": NOW, "round_no": 1102, "round_no_label": "r1101 closeout -> counter 1102",
    "last_round": "r1101", "last_round_label": "r1101", "last_round_at": NOW, "last_round_ts": NOW,
    "last_seen": NOW, "last_seen_at": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "activity_now": NOW, "now_active": NOW, "last_action_at": NOW, "current_task_at": NOW,
    "current_task": CURRENT_TASK, "did": DID, "note": NOTE, "verify": VERIFY,
    "next_pointer": NEXT, "next": NEXT, "verdict": VERDICT,
    "last_action": "r1101 closeout (W273 seat published; counter 1101->1102)",
    "head_sha": "r1101 closeout (W273 seat published; counter 1101->1102)",
    "latest_artifact": ARTIFACT, "recent_artifact": ARTIFACT, "last_artifact": ARTIFACT,
    "last_round_summary": DID, "last_round_summary_at": NOW,
    "next_milestone": "W273 prereg derive/freeze (r1102 FIRST ACTION, within 48h); Monday 10-20 15:30 papers chain",
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": EPOCH, "current_task_ts": EPOCH,
    "last_round_closed": NOW, "last_round_closed_at": NOW,
    "last_orders_read_at": NOW, "last_decisions_read_at": NOW,
    "last_orders_seen": NOW, "last_decisions_seen": NOW,
    "last_orders_sha_note": ORD_NOTE, "last_decisions_read_note": DEC_NOTE,
    "orders_ack_receipt": ACK_RECEIPT, "orders_ack_ts": NOW,
    "r1101_closeout_note": CLOSEOUT_NOTE, "prod_lanes": PROD_LANES,
    "orphan_face": 0, "orphan_faces": 0,
    "codely_live_count": 1,
}
if cpu_pct is not None:
    fields["cpu_pct"] = cpu_pct
    fields["cpu_util_pct"] = cpu_pct
    fields["cpu_idle_pct"] = round(100 - cpu_pct, 1)
if free_ram is not None:
    fields["free_ram_gb"] = free_ram
    fields["idle_ram_gb"] = free_ram
    fields["ram_free_gb"] = free_ram
if gpu_free_mib is not None:
    fields["gpu_free_vram_mib"] = gpu_free_mib
    fields["gpu_free_mib"] = gpu_free_mib
    fields["gpu_idle_vram_mib"] = gpu_free_mib
    fields["gpu_idle_mib"] = gpu_free_mib
    fields["gpu_free_vram_mb"] = gpu_free_mib
    fields["gpu_free_mb"] = gpu_free_mib
    fields["gpu_idle_vram_mb"] = gpu_free_mib
    fields["gpu_idle_mb"] = gpu_free_mib
    fields["gpu_vram_free_mb"] = gpu_free_mib
    fields["gpu_free_vram_gb"] = round(gpu_free_mib / 1024, 2)
    fields["free_vram_mb"] = gpu_free_mib
    fields["gpu_used_vram_mib"] = gpu_used_mib
    fields["gpu_mem_used_mib"] = gpu_used_mib
    fields["gpu_total_vram_mib"] = gpu_total_mib
    fields["gpu_mem_total_mib"] = gpu_total_mib
    fields["gpu_util_pct"] = gpu_util

state = json.load(open(STATE, encoding="utf-8"))
state.update(fields)
dg = state.get("d19_watermark_guard") or {}
if isinstance(dg, dict):
    dg["round_ref"] = 1101
    dg["ts"] = NOW
    state["d19_watermark_guard"] = dg
state["sync"] = {"origin_tip": "r1101 closeout (W273 seat published; closeout commit rides this window)", "ts": NOW}
state["full_load_selfproof"] = {"占用一行": PROD_LANES}
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

heart = json.load(open(HEART, encoding="utf-8"))
heart.update(fields)
hdg = heart.get("d19_watermark_guard") or {}
if isinstance(hdg, dict):
    hdg["round_ref"] = 1101
    hdg["ts"] = NOW
    heart["d19_watermark_guard"] = hdg
heart["sync"] = state["sync"]
heart["full_load_selfproof"] = state["full_load_selfproof"]
with open(HEART, "w", encoding="utf-8", newline="\n") as f:
    json.dump(heart, f, ensure_ascii=False, indent=1)

# post-write assertions (R170/R178 epoch int + R262 clock_read T-sep)
for path in (STATE, HEART):
    d = json.load(open(path, encoding="utf-8"))
    assert isinstance(d["heartbeat_epoch_utc"], int) and not isinstance(d["heartbeat_epoch_utc"], bool), path
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$", d["clock_read"]), path
    assert d["round_no"] == 1102, path
print("state+heartbeat updated; epoch=%d clock_read=%s cpu=%s ram=%s gpu_free=%sMiB" %
      (EPOCH, NOW, cpu_pct, free_ram, gpu_free_mib))

# ---- round report row (canonical root path, r750 law) ---------------------------
ROW = ("| %s | r1101 | %s | %s | %s | 孤儿面=0 零击杀（probe 21:06 py_faces=5 只读·resident legal）| "
       "当前活=W273 prereg derive（r1102 FIRST ACTION）/ 最近实物=W273 seat commit 39e1bb32f1（probe ADMIT "
       "A 615_901..617_900 / B 617_901..618_100）/ 下个里程碑=W273 prereg freeze ≤48h + 周一 10-20 15:30 "
       "papers | watermark=green | 本地未达 origin commit 数=0 |" % (NOW, DID, VERIFY, NEXT))
with open(REPORT, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + ROW + "\n")
print("round report row appended ->", REPORT)

# ---- sweep own seat MSG to processed -------------------------------------------
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20261018-211x-bmc-w273-seat.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-20261018-211x-bmc-w273-seat.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("seat MSG swept -> processed/")
print("CLOSEOUT OK")
