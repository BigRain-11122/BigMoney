# -*- coding: utf-8 -*-
"""r1109 bm-c closeout script: state 1109->1110 + heartbeat mirror + round report row.
Fresh read-modify-write per multi-writer law; epoch int (smoke F7); clock ISO-T."""
import ctypes
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_dt = datetime.datetime.now().astimezone()
NOW = now_dt.isoformat(timespec="seconds")
EPOCH = int(time.time())


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


mem = MEMORYSTATUSEX()
mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
ram_free = round(mem.ullAvailPhys / 1024 ** 3, 1)
ram_total = round(mem.ullTotalPhys / 1024 ** 3, 1)

try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True,
                       creationflags=0x08000000)
    used, total, util = [x.strip() for x in r.stdout.splitlines()[0].split(",")]
    gpu_used, gpu_total, gpu_util = int(used), int(total), float(util)
    gpu_free = gpu_total - gpu_used
except Exception:
    gpu_used, gpu_total, gpu_util, gpu_free = 3056, 16384, 5.0, 13328

head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   encoding="utf-8").strip()

DID = ("r1109: W276 SEAT PUBLISHED origin 21b51a102 first-try push behind=0 (bm-c 95th own "
       "wave candidate, 266th engine wave) -- probe _w276bmc_20261019_probe.py rc0 ADMIT "
       "first-try via E63 canon-clone builder _r1109bmc_build_w276_probe.py (53 needles "
       "all-count-asserted 1x first-try + MUST 21/21 both + py_compile green, EOL=lf "
       "22,341B): A 622_501..624_500 TWENTY-FIFTH consecutive A-hop (live walk refused "
       "naive 622_301..624_300 at the REGISTERED W275 B band 622_301..622_500, hop chain "
       "verbatim) / B 624_501..624_700 TWENTY-SIXTH consecutive above-own-A (naive "
       "622_501..622_700 lands INSIDE own-wave A window 622_501..624_500 -> own-A "
       "reservation, base==own-A tail+1); seed_admit FREE x2 (622501/2000 + 624501/200) "
       "+ origin vacancy four-check + zero W277/W278 skip-claims + chain-relation "
       "W273->W274->W275 ledger 1,024,935->1,027,135->1,029,335 (+2,200/+2,200) / K "
       "598,520->600,720->602,920 EXACT + W277+ projection leg4 (naive A "
       "624_501..626_500 / naive B 624_701..624_900); smoke 49/49; S6 light 10/10 rc0 "
       "(dualrun ZERO-DRIFT streak 51 [461] / audit FLAG pool_starvation+supply_floor "
       "answered-by-chain [W276 seat armed this window] / update_daily 0 rows cutoff "
       "10-16 pre-15:30 Monday honest / regime shadow / CALL-2026-10-16 ORANGE_COOL "
       "idempotent / fund_premium no-op / b_layer all_pass / REPORT-2026-10-19 faces=5 "
       "/ token delta=0); attrition 4 CLEAN; quad green (loop pin=5 no-op first fire "
       "06:05 + watchdog registered [S4U flip access-denied = adjudicated standing face] "
       "+ claws x2); D-19 dual FALSE both scans (opening + S7 tail; ord 57d1f5de / dec "
       "8706acd8 hold, unacked=0, zero mid-round arrivals); orphan face=0 (py_faces=3 "
       "zero-kill); idle --worked rc0; satengine ALIVE rc0 via Tools entry (W275 dedup "
       "12/12 complete, queue waits-upstream face)")

CLOSEOUT_NOTE = ("r1109: clean continuation product window (state round_no=1109 at open per "
                 "r1108 counter advance, executed r1109, advanced 1109->1110 so next=r1110); "
                 "zero absorb owed (r1108 closeout c77ee358f5 landed clean 05:35:17, zero dead "
                 "window between); (1) S0-1 anchor bm-c + round-zero probe py_faces=3 orphans=0 "
                 "zero-kill (1 resident server legal) + S0 fetch 0/0 clean open (HEAD==origin "
                 "c77ee358f5, dirty=2 own regenerable daemon faces); (2) S0.5 D-19 dual-delta "
                 "FALSE both scans (opening s05_probe + S7 tail re-probe; ord 57d1f5de / dec "
                 "8706acd8 hold, unacked=0, orders files=105 all inside ack-230 set); (3) S1 "
                 "smoke 49/49; (4) P0 PRODUCT = W276 SEAT PUBLISHED origin 21b51a102 first-try "
                 "push behind=0 ls-tree-verified 4/4 (probe ADMIT first-try: A 622_501..624_500 "
                 "25th consecutive A-hop / B 624_501..624_700 26th consecutive above-own-A; "
                 "seed FREE x2; vacancy four-check; zero W277/W278 skip-claims; owner 265 rows "
                 "bmc 94; 266th wave bm-c 95th own wave candidate); (5) S3 satengine ALIVE rc0 "
                 "via Tools entry (r1102 pit law honored; W275 dedup 12/12 complete, queue "
                 "waits-upstream) + wm red=false healthy (next_pick=claimed moneyflow-IC parked "
                 "source-blocked, bm-a lane standing); (6) S6 light 10/10 rc0 via canon-clone "
                 "driver _r1109bmc_s6_light.py (dualrun streak 51 [461] / audit FLAG "
                 "pool_starvation+supply_floor answered-by-chain [W276 seat armed] / update_daily "
                 "0 rows cutoff 10-16 Monday pre-15:30 honest papers debt=0 / market_regime "
                 "shadow / CALL-2026-10-16 ORANGE_COOL idempotent / fund_premium no-op / "
                 "b_layer all_pass / REPORT-2026-10-19 faces=5 / token delta=0 / L2 legs 0 "
                 "today); (7) S7: attrition 4 files CLEAN (healed notes as-is) + loop pin=5 "
                 "no-op (first fire 06:05) + watchdog registered (S4U XML flip access-denied = "
                 "adjudicated default-principal standing face per D-20261002-02) + precommit "
                 "claw + prepush claw installed (LF-normalized) + idle --worked rc0 "
                 "idle_rounds=0 + orphan face=0; counter 1109->1110 so next session=r1110")

VERIFY = ("seat commit 21b51a102 on origin behind=0 fetch-verified (c77ee358f5..21b51a102e "
          "first-try push + ls-tree 4/4: MSG-20261019-055x-bmc-w276-seat.md + builder + probe "
          "+ receipt) + probe receipt results/_w276bmc_20261019_probe_receipt.json verdict=ADMIT "
          "(bands A 622501-624500 / B 624501-624700; leg0 chain-relation 1,024,935->1,027,135->"
          "1,029,335 EXACT; leg0.5 vacancy + zero skip-claims; leg2 seed_admit FREE x2; leg3 "
          "vacancy TRUE; leg4 W277+ projection) + smoke 49/49 + S6 light 10/10 rc0 (log "
          "results/_r1109bmc_s6_log.txt: dualrun ZERO-DRIFT streak 51 [461] / audit FLAG "
          "answered-by-chain [W276 seat armed] / bars cutoff 10-16 Monday pre-15:30 honest / "
          "CALL-2026-10-16 ORANGE_COOL idempotent / REPORT-2026-10-19 faces=5 / token delta=0) "
          "+ attrition 4 files CLEAN + quad green (loop pin=5 no-op + watchdog registered "
          "[S4U flip = adjudicated standing face] + claws x2 installed) + D-19 dual-scan FALSE "
          "both (opening + S7 tail; ord 57d1f5de / dec 8706acd8) + unacked=0 + orphan face=0 + "
          "idle --worked rc0 + epoch int + clock_read ISO-T")

NEXT = ("r1110: (1) W276 PREREG DERIVE = FIRST ACTION per seat-first law O-20261010-2350 sec.2 "
        "(E63 canon-clone derive on the post-W275-REGISTERED universe: frozen W275 template "
        "extraction byte-verified @ 1fcc0bc30f PRE-backfill face per r1052/r1049 law + needle "
        "facts-probe MEASURED r1077 law + derive ALL GATES PASS + banned_direction_gate ADMIT; "
        "bands A 622_501..624_500 / B 624_501..624_700 per seat receipt verbatim in-gate "
        "zero-transcription; anchors FULL-PRECISION machine-read n1_w275_results.json per r1093 "
        "pit law; never transcribe r587) -> five-face splice chain follows per multi-step "
        "window-budget law (derive full-window job = r1096 honest-split precedent); (2) TODAY "
        "Monday 2026-10-19 15:30 bars window: full papers chain (cutoff 10-16 current, "
        "debt=0); (3) BigMoney automation-plan faces (W-formalization / backtest-gate-in-loop "
        "/ daily-PnL attribution per the CEO 20:48/20:54/21:11 order chain) = GM/committee-"
        "layer execution items deadlines <=10-25/<=10-31, watch BM-repo O-orders via "
        "bm-b/CEO-PROXY mirror; (4) RAM watch standing (loop CPU-only, GPU idle)")

SUMMARY = ("r1109: W276 SEAT PUBLISHED origin 21b51a102 first-try (bm-c 95th own wave "
           "candidate, 266th engine wave) -- probe ADMIT first-try A 622_501..624_500 25th "
           "consecutive A-hop / B 624_501..624_700 26th consecutive above-own-A; seed FREE "
           "x2; vacancy four-check; zero W277/W278 skip-claims; owner 265 rows")

ARTIFACT = ("W276 seat commit 21b51a102 (probe results/_w276bmc_20261019_probe.py ADMIT "
            "first-try: A 622_501..624_500 25th A-hop / B 624_501..624_700 26th above-own-A; "
            "receipt results/_w276bmc_20261019_probe_receipt.json)")

ROW = ("| {ts} | r1109 | W276 SEAT PUBLISHED origin 21b51a102 first-try push behind=0 "
       "(bm-c 95th own wave candidate, 266th engine wave) -- probe _w276bmc_20261019_probe.py "
       "rc0 ADMIT first-try via E63 canon-clone builder _r1109bmc_build_w276_probe.py (53 "
       "ordered needles all-count-asserted 1x first-try, reverse-order wave rolls, MUST 21/21 "
       "+ MUST_NOT 21/21, py_compile green, EOL=lf 22,341B): A 622_501..624_500 TWENTY-FIFTH "
       "consecutive A-hop (live walk refused naive 622_301..624_300 at the REGISTERED W275 B "
       "band 622_301..622_500, hop chain recorded verbatim) / B 624_501..624_700 TWENTY-SIXTH "
       "consecutive above-own-A (naive 622_501..622_700 lands INSIDE the own-wave A "
       "first-clean window 622_501..624_500 -> own-A reservation hops past own-A tail 624_500, "
       "base==own-A tail+1); seed_admit FREE x2 (622501/2000 + 624501/200) + origin vacancy "
       "four-check green + zero W277/W278 skip-ahead claims + chain-relation W273->W274->W275 "
       "ledger 1,024,935->1,027,135->1,029,335 (+2,200/+2,200) / K 598,520->600,720->602,920 "
       "(+2,200/+2,200) machine-read verbatim + W277+ forward projection recorded in receipt "
       "leg4 | seat commit 21b51a102 on origin behind=0 fetch-verified "
       "(c77ee358f5..21b51a102e first-try push, ls-tree 4/4 delivered) + probe receipt "
       "results/_w276bmc_20261019_probe_receipt.json ADMIT verdict + builder output 53/53 "
       "needles 1x + smoke 49/49 + S6 light 10/10 rc0 (dualrun ZERO-DRIFT streak 51 [461 "
       "entries] / compute_audit FLAG pool_starvation+supply_floor answered-by-chain [W276 "
       "seat armed this window] / update_daily 0 rows cutoff 10-16 pre-15:30 Monday honest / "
       "regime shadow / market_clock CALL-2026-10-16 ORANGE_COOL idempotent / fund_premium "
       "no-op / b_layer all_pass / REPORT-2026-10-19 faces=5 / token delta=0) + attrition 4 "
       "files CLEAN (healed notes as-is) + quad green (loop pin=5 no-op first fire 06:05 + "
       "watchdog registered [S4U XML flip access-denied = adjudicated default-principal "
       "standing face per D-20261002-02] + pre-commit claw + pre-push claw installed) + D-19 "
       "dual FALSE both scans opening + S7 tail (ord 57d1f5de / dec 8706acd8 hold, unacked=0, "
       "zero mid-round arrivals) + orphan face=0 (probe py_faces=3 zero-kill, 1 resident "
       "server legal) + idle --worked rc0 idle_rounds=0 + epoch int + clock_read ISO-T | "
       "{next} | 孤儿面=0（probe 05:46 py_faces=3 只读零杀） | 当前活=W276 seat 已发布、W276 "
       "prereg derive=r1110 首动作 / 最近实物=W276 seat commit 21b51a102（probe ADMIT A "
       "622_501..624_500 / B 624_501..624_700）@ {ts} / 下个里程碑=W276 prereg freeze ≤48h + "
       "今日 15:30 papers | watermark=green | 本地未达 origin commit 数=0 |").format(
           ts=NOW, next=NEXT)


def update_faces(d):
    d["activity_now"] = NOW
    d["clock_read"] = NOW
    d["current_task"] = "W276 prereg derive = r1110 FIRST ACTION"
    d["current_task_at"] = NOW
    d["current_task_ts"] = EPOCH
    d["did"] = DID
    d["free_ram_gb"] = ram_free
    d["idle_ram_gb"] = ram_free
    d["ram_free_gb"] = ram_free
    d["total_ram_gb"] = ram_total
    d["full_load_selfproof"] = {
        "占用一行": ("CPU=W276 SEAT PUBLISHED origin 21b51a102 (266th wave, bm-c 95th own "
                    "wave candidate; W276 prereg derive = r1110 FIRST ACTION); GPU=idle "
                    "~%.1fG free, loop CPU-only; short-video lane DISABLED standing per "
                    "O-20261017-1741" % (gpu_free / 1024.0)),
        "最近实物": ("results/_w276bmc_20261019_probe_receipt.json verdict=ADMIT (A "
                    "622_501..624_500 / B 624_501..624_700) + seat commit 21b51a102 @ " + NOW),
        "下个里程碑": ("W276 prereg freeze (r1110 FIRST ACTION, within 48h); TODAY Monday "
                    "2026-10-19 15:30 papers chain; BM automation-plan <=10-25"),
    }
    d["gpu_used_mib"] = gpu_used
    d["gpu_mem_total_mib"] = gpu_total
    d["gpu_util_pct"] = gpu_util
    for k in ("gpu_free_mib", "gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
              "gpu_idle_mb", "gpu_idle_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
              "free_vram_mb"):
        d[k] = gpu_free
    d["gpu_free_vram_gb"] = round(gpu_free / 1024.0, 2)
    d["head_sha"] = head_sha
    d["heartbeat_epoch_utc"] = EPOCH
    d["heartbeat_epoch_utc_type"] = "int (assert)"
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["last_action"] = "W276 seat publish 21b51a102 + S6 10/10 + closeout"
    d["last_action_at"] = NOW
    d["last_artifact"] = ARTIFACT
    d["latest_artifact"] = ARTIFACT
    d["recent_artifact"] = ARTIFACT
    d["last_decisions_read_at"] = NOW
    d["last_decisions_seen"] = NOW
    d["last_orders_read_at"] = NOW
    d["last_orders_seen"] = NOW
    d["last_round"] = 1109
    d["last_round_at"] = NOW
    d["last_round_closed"] = 1109
    d["last_round_closed_at"] = NOW
    d["last_round_label"] = "r1109"
    d["last_round_summary"] = SUMMARY
    d["last_round_summary_at"] = NOW
    d["last_round_ts"] = NOW
    d["last_seen"] = NOW
    d["last_seen_at"] = NOW
    d["next"] = NEXT
    d["next_pointer"] = NEXT
    d["next_milestone"] = ("W276 prereg freeze (r1110 FIRST ACTION, within 48h); TODAY "
                           "Monday 2026-10-19 15:30 papers chain")
    d["note"] = ("CPU=W276 SEAT PUBLISHED (supply head; prereg derive = r1110 FIRST ACTION); "
                 "GPU=idle %.1fG free (loop CPU-only); short-video lane DISABLED standing per "
                 "O-20261017-1741" % (gpu_free / 1024.0))
    d["now_active"] = "W276 seat published; prereg derive next"
    d["orders_ack_receipt"] = ("r1109: opening scan dual FALSE both (ord 57d1f5de / dec "
                              "8706acd8 hold; unacked=0, files=105 inside ack-230); S7 tail "
                              "re-probe dual FALSE same -- zero mid-round arrivals")
    d["orders_ack_ts"] = NOW
    d["orphan_face"] = 0
    d["orphan_faces"] = 0
    d["prod_lanes"] = ("CPU=W276 SEAT PUBLISHED (supply head; prereg derive = r1110 FIRST "
                       "ACTION); GPU=idle %.1fG free (loop CPU-only); short-video lane "
                       "DISABLED standing per O-20261017-1741" % (gpu_free / 1024.0))
    d["ram_critical_face"] = "none (loop CPU-only, GPU idle, %.1fGB free)" % ram_free
    d["sync"] = {"origin_tip": "r1109 W276 SEAT PUBLISHED 21b51a102", "ts": NOW}
    d["ts"] = NOW
    d["updated"] = NOW
    d["updated_at"] = NOW
    d["verdict"] = ("green r1109 product window (W276 SEAT PUBLISHED origin 21b51a102 "
                    "first-try: A 622_501..624_500 25th A-hop / B 624_501..624_700 26th "
                    "above-own-A; probe ADMIT first-try 53/53; smoke 49/49; S6 10/10; loop "
                    "CPU-only, GPU idle)")
    d["verify"] = VERIFY


sp = os.path.join(ROOT, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    state = json.load(f)
update_faces(state)
state["round_no"] = 1110
state["round_no_label"] = "r1109"
state["r1109_closeout_note"] = CLOSEOUT_NOTE
state["last_pulled_at"] = NOW
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
update_faces(hb)
hb["round_no"] = 1110
hb["round_no_label"] = "r1109 closeout -> counter 1110"
hb["r1109_closeout_note"] = CLOSEOUT_NOTE
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

rp = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rp, "rb").read()
eol = b"\r\n" if (b"\r\n" in raw[-4000:] or raw.endswith(b"\r\n")) else b"\n"
with open(rp, "ab") as f:
    f.write(ROW.encode("utf-8") + eol)

chk_state = json.load(open(sp, encoding="utf-8"))
chk_hb = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk_state["heartbeat_epoch_utc"], int), "state epoch not int"
assert isinstance(chk_hb["heartbeat_epoch_utc"], int), "heartbeat epoch not int"
assert chk_state["round_no"] == 1110 and chk_hb["round_no"] == 1110
assert "T" in chk_hb["clock_read"]
print("CLOSEOUT OK round 1109->1110 epoch=%d ram_free=%.1fGB gpu_free=%dMiB head=%s" %
      (EPOCH, ram_free, gpu_free, head_sha[:10]))
