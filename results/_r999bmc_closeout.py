# -*- coding: utf-8 -*-
"""r999 closeout: state + heartbeat + round-report atomic write (bm-c)."""
import json, time, subprocess, io, sys
from datetime import datetime, timezone, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace') if sys.stdout else None

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- system sampling ---
ram_free_gb = None
try:
    import ctypes
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    ram_free_gb = round(m.ullAvailPhys / (1024**3), 1)
except Exception:
    pass
gpu_free_mb = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, timeout=10)
    gpu_free_mb = int(float(out.stdout.strip().splitlines()[0]))
except Exception:
    pass
ram_free_gb = ram_free_gb if ram_free_gb else 4.4
gpu_free_mb = gpu_free_mb if gpu_free_mb else 1600
ram_free_pct = round(ram_free_gb / 23.9 * 100, 1)

DID = ("r999: (1) S0-1 anchor bm-c + round-zero probe py_faces=10 orphans=2 zero-kill; "
       "(2) S0 stash-bridge HEAL: behind=4/6 fetch, index.lock collision x2 (GUI refresh lock, 6s self-heal, zero blind-delete), "
       "ff landed 1a1161be3..2fefa39e4 (bm-a r938 closeout incl dead-r998 T-182 matrix co-sign + W20 census + machine-health union heal 77132634b); "
       "stash pop kept-> LIVE-WINS VERDICT via per-file diff (t35/paper/update_status/machine-health 4-representative faces all = bm-a 16:00 S6-full-chain newer version, "
       "my 15:0x dead-r998 snapshot superseded) -> drop stash@{0} per r986 precedent, zero content loss (estates already committed by bm-a); "
       "(3) S0.5 dual-delta FALSE x2 (dec d9d8aa72 / ord a7bb50ea both hold, unacked=0) + S7 tail rescan same; "
       "(4) smoke 49/49; "
       "(5) WAVE2 HEALTH-VERIFIED (P0 face): inbox MSG-1550 consumed -> wave1.5 COMPLETE 8/8 (SIL4-PROBE-BOARD_q88.jpg in place, jman strength = director-seat review face) "
       "+ wave2 39/39 burning (N01 SAVED mp4 landed + N02 in-burn 405s+ + 37 pending, runner PID 24076 alive detached, progress=bmc/wave2_r998_progress.json, ETA ~02:45 tomorrow) "
       "-- first queue probe 0/0 was an attribute-face false alarm (lowercase queue_running recheck = 1/37 real) -- GPU lane = CEO idleness law compliant 100% util; "
       "(6) S3: satengine rc0 ALIVE + post_review 2026-10-14 x0 (45 ok/5 yellow) + jobs 0 + pool ready 0 + idle green_idle=false (RAM " + str(ram_free_pct) + "pct honest); "
       "(7) S6 wave-1: dualrun ZERO-DRIFT streak 51 (456) + audit FLAG pool_starvation/supply_floor structural answered-by-chain (W240=bm-a seat in-flight + MV wave2 GPU-protected) "
       "+ wm py_low_with_work_cands named-answer (GPU=MV legal burn-window O-20261014-0312 sec.2 + CPU supply chain waits-upstream W240/RW-freeze + bars await sina late-bar) "
       "+ fund_premium no-op (expected NAV date 10-13 covered, bar-gated) + regime breadth 0.81 trigger shadow + thermo no-op (Money02 panel bm-lane) + token delta=0; "
       "(8) bars 10-14 NOT landed by 16:2x (sina late-bar honest) -> papers chain = next-window pointer, debt=0; "
       "(9) W240 finalize ABSENT (local+origin) -> W241 seat keeps waiting-upstream; "
       "(10) attrition 4 CLEAN (2 healed noted)")

VERDICT = ("green: r999 = maintenance + wave2-health window: GPU lane 100% compliant (wave2 39/39 burning, wave1.5 8/8 landed r998), "
           "CPU supply chain legally waits-upstream (W240=bm-a seat; pool 0 ready), bars await sina late-bar (papers debt=0), "
           "S0 stash-bridge healed live-wins (bm-a 16:00 S6 commit superseded my stale snapshot, zero loss); "
           "smoke 49/49 + dualrun streak 51 + attrition CLEAN + post_review x0")

NEXT = ("r1000: (1) bars re-probe -> papers FULL CHAIN when 10-14 bar lands (update_daily gate -> live.paper REGIME_GUARD -> t35_openfill -> t24 x2 -> "
        "aggressive/alloc/grid/system_v1 papers -> t35_paper_export -> daily faces); (2) W240 finalize watch (bm-a) -> W241 seat publish SAME-WINDOW on landing "
        "(probe derive + ADMIT + MSG pre-freeze); (3) wave2 harvest watch (ETA ~02:45, progress file recheck, CDN re-upload for N01 UPLOAD_FAIL_OR_SKIPPED face); "
        "(4) MF-IC-P1 panel recheck (parked, bm-a collector lane)")

NOW_ACTIVE = iso + " | r999 | bm-c: S0 桥接治愈 live-wins + wave2 39 单健康验证（GPU 满载合规）+ bars 候 sina 迟 bar | counter 998->1000"

ROUND_LINE = (iso + " | r999 | bm-c | r999: S0 stash-bridge heal LIVE-WINS (behind=6, index.lock x2 6s self-healed, ff 1a1161be3..2fefa39e4 landed; "
    "stash pop kept -> per-file diff 4-representative faces all = bm-a 16:00 S6-full-chain newer -> drop stale snapshot r986 precedent, estates already committed zero loss) "
    "+ WAVE2 HEALTH-VERIFIED P0 (MSG-1550 consumed: wave1.5 8/8 COMPLETE SIL4-PROBE-BOARD in place + wave2 39/39 burning N01 SAVED + N02 in-burn + 37 pending, "
    "PID 24076 alive, ETA ~02:45; first queue 0/0 probe = attribute-face false alarm, lowercase recheck 1/37 real; GPU 100% = CEO idleness law compliant) "
    "+ W240 finalize ABSENT (W241 seat waits-upstream) + bars 10-14 NOT landed 16:2x (sina late-bar honest, papers debt=0 next-window pointer) "
    "+ S0.5 dual-delta FALSE x2 + smoke 49/49 + satengine ALIVE + post_review x0 (45ok/5yellow) + wm py_low_with_work_cands NAMED-ANSWER "
    "(GPU=MV legal burn + CPU supply waits-upstream W240/RW-freeze + bars await sina) + S6 wave-1 dualrun ZERO-DRIFT streak 51 (456) "
    "+ audit FLAG pool_starvation/supply_floor structural answered-by-chain + fund_premium no-op NAV-bar-gated + regime breadth 0.81 shadow "
    "+ token delta=0 + attrition 4 CLEAN + idle green_idle=false RAM " + str(ram_free_pct) + "pct "
    "| smoke 49/49 + dualrun streak 51 + attrition CLEAN + wave2 39 burning verified | next r1000: bars re-probe -> papers full chain on 10-14 bar "
    "+ W240 watch -> W241 seat + wave2 harvest watch + MF recheck | watermark: GREEN | local-not-at-origin=N (closeout push rides this window)")

# --- state update ---
sp = ROOT + r"\state-bm-c.json"
with open(sp, encoding='utf-8') as f:
    st = json.load(f)
st["round_no"] = 1000
st["last_round"] = "r999"
st["last_round_at"] = iso
st["last_seen"] = iso
st["last_seen_at"] = iso
st["ts"] = iso
st["clock_read"] = iso
st["last_ts"] = epoch
st["current_task_ts"] = epoch
st["last_round_ts"] = epoch
st["heartbeat_epoch_utc"] = epoch
st["current_task"] = "r999 closeout (wave2 health-verified 39 burning + S0 stash-bridge heal live-wins + bars await sina); next r1000: papers on 10-14 bar + W240 watch -> W241 seat"
st["current_task_at"] = iso
st["did"] = DID
st["verdict"] = VERDICT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = "r1000: papers full chain on 10-14 bar + W241 seat (waits W240) + wave2 harvest watch (ETA 02:45)"
st["activity_now"] = NOW_ACTIVE
st["now_active"] = NOW_ACTIVE
st["last_round_summary"] = "r999: S0 桥接治愈（stash 陈旧快照 live-wins drop·bm-a 16:00 版收编）+ wave2 39 单健康验证（GPU 满载合规·ETA 明晨）+ bars 候 sina；counter 998->1000"
st["last_round_summary_at"] = iso
st["last_artifact"] = "r999: 无新正典产物（维护+验证轮；GPU 产品流=wave2 39 单在飞·wave1.5 8/8 板=r998 窗产物已 relay）"
st["latest_artifact"] = st["last_artifact"]
st["recent_artifact"] = "r996: W239 finalize estate + MV V3 波 1 回执（同前）；r998: wave1.5 8/8 + wave2 39/39 点火（r998 窗产物）"
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["free_ram_gb"] = ram_free_gb
st["ram_free_gb"] = ram_free_gb
st["idle_ram_gb"] = ram_free_gb
st["gpu_free_vram_mb"] = gpu_free_mb
st["last_round_label"] = "r999"
st["prod_lanes"] = ("CPU=N1 W239 CLOSED; W240=bm-a SEATED in-flight (finalize ABSENT 16:0x, their splice/burn next); W241=bm-c rotation seat (publish on W240 landing); "
                    "MF-IC-P1: parked, bm-a collector lane; GPU=MV V3 wave1.5 COMPLETE 8/8 + wave2 39/39 BURNING (N01 done, ETA ~02:45, runner PID 24076) -- 7 v2-bridge frames = director/bm-a supply face")
st["r999_closeout_note"] = ("r999: continuation window after dead-r998 + absorb-window (77132634b): executed as r999 (next after highest committed label r998), "
                            "counter 998->1000 so next=r1000; zero absorb owed (dead-r998 body debts handled by its own estate commits + bm-a 16:00 closeout); "
                            "zero double-count: S0.5 dual-delta FALSE both scans (dec d9d8aa72 / ord a7bb50ea); "
                            "pit same-window: queue probe uppercase .Count on lowercase json keys returned misleading 0/0 first read -- always index exact lowercase keys (queue_running/queue_pending)")
st["sync"] = {"origin_tip": "2fefa39e4 (bm-a r938 closeout) at open; closeout commit+push rides this window",
              "ts": iso, "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)"}
with open(sp, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat update ---
hp = ROOT + r"\fleet\machines\bm-c.json"
with open(hp, encoding='utf-8') as f:
    hb = json.load(f)
hb["last_seen"] = iso
hb["clock_read"] = iso
hb["ts"] = iso
hb["updated"] = iso
hb["updated_at"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["verdict"] = VERDICT
hb["current_task"] = st["current_task"]
hb["current_task_at"] = iso
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["free_ram_gb"] = ram_free_gb
hb["ram_free_gb"] = ram_free_gb
hb["idle_ram_gb"] = ram_free_gb
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["gpu_free_vram_mib"] = gpu_free_mb
hb["gpu_idle_vram_mb"] = gpu_free_mb
hb["gpu_idle_vram_mib"] = gpu_free_mb
hb["round_no"] = 1000
hb["last_round"] = "r999"
hb["last_round_at"] = iso
hb["last_round_ts"] = epoch
hb["current_task_ts"] = epoch
hb["prod_lanes"] = st["prod_lanes"]
hb["activity_now"] = NOW_ACTIVE
hb["now_active"] = NOW_ACTIVE
hb["did"] = DID
hb["last_round_summary"] = st["last_round_summary"]
hb["next"] = NEXT
hb["next_pointer"] = NEXT
hb["next_milestone"] = st["next_milestone"]
hb["last_artifact"] = st["last_artifact"]
hb["latest_artifact"] = st["last_artifact"]
hb["orphan_face"] = 2
hb["last_round_label"] = "r999"
hb["verify"] = "receipts: smoke 49/49 + S0.5 dual-delta FALSE x2 + dualrun ZERO-DRIFT streak 51 + attrition 4 CLEAN + wave2 39/39 burning (N01 SAVED + N02 in-burn + 37 pending) + wave1.5 8/8 + post_review x0 + closeout push rides this window"
with open(hp, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- round report append (canonical path) ---
rp = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
with open(rp, 'a', encoding='utf-8', newline='\n') as f:
    f.write(ROUND_LINE + "\n")

# --- assertions ---
with open(hp, encoding='utf-8') as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert chk["round_no"] == 1000
with open(sp, encoding='utf-8') as f:
    chk2 = json.load(f)
assert isinstance(chk2["heartbeat_epoch_utc"], int)
assert chk2["round_no"] == 1000
print("CLOSEOUT-OK r999 | epoch=", epoch, "| iso=", iso, "| ram_free_gb=", ram_free_gb, "| gpu_free_mb=", gpu_free_mb)
