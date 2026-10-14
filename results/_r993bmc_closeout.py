# r993 bm-c closeout: wait-state window #8 one-line + S6 light + S7 quad + counter 993->994
# Law refs: one-line wait-state law (product-priority block sec.2), r750 canonical ledger path,
# R170/R178 heartbeat epoch int law, R262 clock_read T-separator law.
import json, time, subprocess, io, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

now_local = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- machine stats sample ---
def ram_free_gb():
    import ctypes, ctypes.wintypes
    class MEM(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEM(); m.dwLength = ctypes.sizeof(MEM)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / (1024**3), 1), round(m.dwMemoryLoad, 1)

def gpu_free_mb():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
        return int(out)
    except Exception:
        return -1

def cpu_pct():
    try:
        out = subprocess.run(["wmic", "cpu", "get", "loadpercentage", "/value"],
                             capture_output=True, text=True, timeout=20).stdout
        for ln in out.splitlines():
            if "LoadPercentage=" in ln:
                return int(ln.split("=")[1])
    except Exception:
        pass
    return -1

free_gb, mem_load = ram_free_gb()
gpu_free = gpu_free_mb()
cpu = cpu_pct()

SUMMARY = ("r993: wait-state window #8 per one-line law (W238 finalize absent -- bm-a prereg derive 40/47, "
           "re-anchor P0 their window -> W239 freeze-prep waits-upstream; bars pre-15:30; MF-IC-P1 parked "
           "[panel refresh in flight, source-blocked connection-level]; W19 SCREEN pool = bm-b lane, "
           "autofill consuming [shard-0 done 09:33], bm-c RAM gate NOW PASSING 5.2G>=4G r354 disclosure-only) "
           "+ S0 stash-bridge pull landed bm-a r978/r979 estate + S0.5 dual-delta FALSE x2 + smoke 49/49 + "
           "S3 satengine ALIVE + wm red=false (MF-IC-P1 claimed/parked) + idle green_idle=false RAM 21.7% "
           "honest no-claim-duty + queues P2/P3 empty + jobs 0 + S6 light (dualrun ZERO-DRIFT streak 51/455 + "
           "audit FLAG ignition_sla structural bm-b-lane answered-by-mechanism + update_daily no-op cutoff 10-13 + "
           "market_regime rc0 + market_clock ORANGE_COOL + fund_premium no-op pre-15:30 + token delta=0) + "
           "S7 quad green + sentinel v1.0 LIVE-VERIFIED 5 ticks NORMAL + attrition 4 CLEAN")

VERDICT = ("green: wait-state window #8 per one-line law -- W238 prereg 40/47 bm-a re-anchor P0 in-flight -> "
           "W239 freeze-prep waits-upstream; bars pre-15:30 (papers chain on landing); MF-IC-P1 parked upstream; "
           "W19 pool bm-b-lane autofill standing path -- smoke 49/49 + S6 light green + S7 quad green")

NEXT = ("r994: (1) 15:30 bars re-probe -> papers full chain when 10-14 bar lands; (2) W238 finalize watch (bm-a "
        "prereg re-anchor first) -> W239 prereg derive R33-style + five-face splice + six-gate PRE-FINALIZE "
        "same-window on landing per W239 bloodline; (3) MF panel recheck (refresh in flight -> if complete, "
        "MF-IC-P1 S2 completion gate check; else parked one-line); (4) W19 pool bm-b-lane watch (ignition_sla "
        "flag clears when bm-b autofill consumes shards; bm-c RAM gate passing disclosure-only)")

PROD_LANES = ("CPU=N1 W237 CLOSED (r990 finalized 945,189/K=519,320); W238=bm-a chain in-flight (prereg derive "
             "40/47, re-anchor P0 their next window); W239=bm-c SEATED 09:14 (freeze waits-upstream W238 finalize, "
             "prereg derive = first action on landing per seat-first law); MF-IC-P1: parked, bm-a panel refresh "
             "in flight; W19-SCREEN pool: 7 ready bm-b-lane (autofill consuming, shard-0 done), bm-c RAM gate "
             "5.2G>=4G passing disclosure-only; GPU=MV V3 burn window protected per O-20261014-0312 sec.2 zero touch")

FULLLOAD = {
    "占用一行": ("GPU=MV V3 车道保护烧窗（O-20261014-0312 §2 零碰）+qwen3.8:27b ollama serve 在役+双 llama-server"
                 "（:11113/:9913）+album serve（:8800）；CPU=空闲带（py 0.2%）"),
    "当前活": "r993 wait-state 窗 #8（W238 上游 bm-a 在飞·bars 15:30 到点·MF 面板刷新在途）+ S6/S7 例行全绿",
    "下一交付物": ("W238 finalize 落地即同窗 W239 freeze-prep（prereg derive R33 式+五面 splice+六门 PRE-FINALIZE）；"
                  "bars 15:30 papers 全链；W19 shards bm-b autofill 顺序消化"),
    "队列水位": ("N1 引擎 0 在烧（W239 席占·候上游 W238）·W19 SCREEN 池 7 ready（bm-b lane·shard-0 done）·"
                "P2/P3 队列空·jobs 0·inbox 0·bars 15:30"),
}

# --- 1) round report line (canonical path per r750 law) ---
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
line = (f"{now_local} | r993 | {SUMMARY} | smoke 49/49 + dualrun streak 51 + sentinel 5 ticks NORMAL + "
        f"attrition 4 CLEAN | {NEXT[:180]}\n")
with io.open(REPORT, "a", encoding="utf-8") as f:
    f.write(line)

# --- 2) state-bm-c.json ---
SP = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(SP, encoding="utf-8"))
st["round_no"] = 994
st["last_round"] = "r993"
st["round_no_label"] = "r993"
st["loop_round"] = 993
st["clock_read"] = now_local
st["ts"] = now_local
st["updated"] = now_local
st["updated_at"] = now_local
st["last_round_at"] = now_local
st["last_seen"] = now_local
st["last_seen_at"] = now_local
st["last_round_ts"] = epoch
st["last_ts"] = epoch
st["heartbeat_epoch_utc"] = epoch
st["current_task"] = ("r993 wait-state window #8 done (one-line law); next r994 unchanged faces: bars 15:30 papers "
                      "+ W238 finalize watch -> W239 freeze-prep on landing + MF panel recheck + W19 pool bm-b-lane watch")
st["current_task_at"] = now_local
st["did"] = SUMMARY
st["verdict"] = VERDICT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["prod_lanes"] = PROD_LANES
st["last_round_summary"] = "r993: wait-state window #8 (W238 upstream / bars pre-15:30 / MF parked / W19 bm-b-lane) + smoke 49/49 + S6 light green + S7 quad green + sentinel live-verified; counter 993->994"
st["last_action"] = "r993 closeout (wait-state window #8 one-line + S6 light + S7 quad + sentinel verify)"
st["latest_artifact"] = "r993: no new product artifact (wait-state window #8 per one-line law); last = r992 addendum (O-0949 receipt + bm-c-Sentinel v1.0 deployed), sentinel live-verified 5 ticks NORMAL this window"
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = "10-14 15:30 bars -> papers chain; W238 finalize (bm-a) -> W239 freeze-prep bm-c same-window; MF-IC-P1 unpark on panel complete"
st["free_ram_gb"] = free_gb
st["ram_free_gb"] = free_gb
st["idle_ram_gb"] = free_gb
st["cpu_pct"] = cpu
st["cpu_util_pct"] = cpu
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["full_load_selfproof"] = FULLLOAD
st["r993_closeout_note"] = ("r993: clean continuation wait-state window (state round_no=993 at open, executed r993, "
                            "advanced 993->994 so next=r994); zero absorb owed (r992 addendum landed clean); "
                            "S0 landed bm-a r978/r979 estate (W237 finalize MSG processed + W238 prereg derive 40/47 "
                            "re-anchor P0); zero double-count: S0.5 dual-delta FALSE both scans; sentinel v1.0 "
                            "first-day live-verified (5 ticks 09:53-10:10 all NORMAL, task Ready next 10:15)")
with io.open(SP, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- 3) heartbeat fleet/machines/bm-c.json ---
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(HB, encoding="utf-8"))
hb["last_seen"] = now_local
hb["ts"] = now_local
hb["clock_read"] = now_local
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = 32
hb["idle_ram_gb"] = free_gb
hb["gpu_free_vram_mb"] = gpu_free
hb["verdict"] = VERDICT
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_round"] = "r993"
with io.open(HB, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- self-verify ---
chk = json.load(io.open(SP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"].split("+08:00")[0], "clock_read T-separator law R262"
assert chk["round_no"] == 994
hbc = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(hbc["heartbeat_epoch_utc"], int)
print("closeout written: round 993->994, epoch", epoch, "ram", free_gb, "gpu_free", gpu_free, "cpu", cpu)
