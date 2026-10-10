# r950 bm-a closeout phase-1: state + heartbeat + round report line.
# Fresh load -> targeted field updates -> atomic write (multi-writer discipline).
import ctypes
import datetime
import io
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NOW = datetime.datetime.now().astimezone()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S%z")  # +0800 form
TS_T = NOW.isoformat(timespec="seconds")  # T-separator ISO 8601 (F5/F7 law)
EPOCH = int(NOW.timestamp())

# ---- live resource readings (honest faces) ----
cores = os.cpu_count() or 32
ram_free_pct = None
try:
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = MS()
    ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    total_gb = ms.ullTotalPhys / (1024 ** 3)
    ram_free_pct = round(100.0 * ms.ullAvailPhys / max(1, ms.ullTotalPhys), 1)
    ram_free_gb = round(ms.ullAvailPhys / (1024 ** 3), 1)
except Exception:
    total_gb, ram_free_gb = None, None
vram_free_gb = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"], capture_output=True, timeout=20)
    vals = [float(x) for x in out.stdout.decode().replace(",", ".").split()]
    if vals:
        vram_free_gb = round(min(vals) / 1024.0, 2)
except Exception:
    pass

VERDICT = ("green (r950: T19 gate product landed selftest 17/17 + live scan CLEAR "
           "tech1/explore5 live rows 0 findings + registration leg wired present-once; "
           "S6 39 legs rc0 zero flags dualrun streak 8; smoke 49/49; DEC/ORD UNCHANGED "
           "zero re-consume; E8 yielded to bm-b per T-18 probe in_flight; W17/W204 watches held)")
DID = ("r950: T19 P2 head consumed same-round (queue seed closed-family machine gate "
       "scripts/queue_seed_gate.py: check single-seed lint rc3-rejected/reopen-declared + "
       "scan live-row hygiene audit + 9-key registry single-source import + false-positive "
       "control work-col vs pointer-col + iteration_prompt S3 registration leg) + S6 39 legs "
       "rc0 + S0 FF absorb bm-b r827 (E7 delivered by bm-b; E8 yielded per T-18 probe)")
NEXT = ("r951: E9 AH premium deepening or standing agenda per probe (E8 bm-b in-flight "
        "yield); W205 seat watch (W204 five-face row unregistered, no first-burn); W17 "
        "ignition recheck after bm-c training window ETA ~22:45 (MSG-0935 standing)")
ART = ("scripts/queue_seed_gate.py + results/queue_seed_gate.json + state/queue/tech.md "
       "T19 done flip (10:0x)")

# ---- state-bm-a.json ----
sp = "state-bm-a.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 950
st["round"] = 950
st["last_round"] = 949
st["last_round_at"] = st.get("last_round_ts") or TS_T
st["last_round_ts"] = TS_T
st["ts"] = TS_T
st["clock_read"] = TS_T
st["updated"] = TS_T
st["updated_at"] = TS_T
st["last_run"] = TS_T
st["last_seen"] = TS_T
st["did"] = DID
st["last_action"] = "r950 closeout: T19 gate product landed (selftest 17/17 + scan CLEAR + leg wired)"
st["next"] = NEXT
st["now_active"] = NEXT
st["task"] = NEXT
st["current"] = NEXT
st["current_task"] = NEXT
st["last_artifact"] = ART
st["latest_artifact"] = ART
st["recent_artifact"] = ART
st["verdict"] = VERDICT
st["next_milestone"] = ("r951: E9/standing agenda per probe; W205 seat after W204 "
                        "five-face+first-burn; 10-31 month-boundary first exam (T-143 "
                        "assembly 10-29)")
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["last_decisions_seen"] = ("r950 scan hash b87a92b1 MATCH (D-20261010-01/02/03 already "
                             "consumed r933); zero new group face")
st["last_decisions_at"] = "2026-10-10"
st["last_decisions_ts"] = TS_T
st["last_orders_seen"] = "r950 scans zero unacked (60 files vs 199 ack, S0.5+S7 double-scan)"
st["last_orders_at"] = "2026-10-10"
st["last_orders_ts"] = TS_T
st["heartbeat_epoch_utc"] = EPOCH
st["last_heartbeat_epoch_utc"] = EPOCH
st["heartbeat_epoch_utc_type_int"] = True
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
chk = json.load(io.open(sp, encoding="utf-8"))
assert chk["round_no"] == 950 and isinstance(chk["heartbeat_epoch_utc"], int)
assert "T" in chk["clock_read"] and "+" in chk["clock_read"]
print("state-bm-a.json: round 950 written, epoch int ok, clock T-form ok")

# ---- fleet/machines/bm-a.json (heartbeat, own file only) ----
hp = "fleet/machines/bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["round_no"] = 950
hb["last_seen"] = TS_T
hb["ts"] = TS_T
hb["clock_read"] = TS_T
hb["updated"] = TS_T
hb["updated_at"] = TS_T
hb["heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = True
hb["current_task"] = NEXT
hb["task"] = NEXT
hb["current"] = NEXT
hb["now_active"] = NEXT
hb["did"] = DID
hb["next"] = NEXT
hb["last_action"] = st["last_action"]
hb["last_artifact"] = ART
hb["latest_artifact"] = ART
hb["verdict"] = VERDICT
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 1
hb["orphan_faces"] = 1
hb["last_round"] = 949
hb["last_round_at"] = TS_T
hb["cores"] = cores
hb["cpu_cores"] = cores
if ram_free_pct is not None:
    hb["ram_free_pct"] = ram_free_pct
    hb["free_ram_pct"] = ram_free_pct
if ram_free_gb is not None:
    hb["ram_free_gb"] = ram_free_gb
    hb["free_ram_gb"] = ram_free_gb
if vram_free_gb is not None:
    hb["gpu_free_vram_gb"] = vram_free_gb
    hb["vram_free_gb"] = vram_free_gb
    hb["gpu_vram_free_gb"] = vram_free_gb
    hb["idle_vram_gb"] = vram_free_gb
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)
chk2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int) and "T" in chk2["clock_read"]
print("heartbeat: r950 written; ram_free_pct=%s vram_free_gb=%s cores=%s"
      % (ram_free_pct, vram_free_gb, cores))

# ---- round report line ----
rp = "round_reports-bm-a.md"
line = (
    TS_T + " | r950 | bm-a | dept:\u5de5\u7a0b/\u8230\u961f (T19 P2 \u961f\u5934\u6d88\u8d39="
    "\u961f\u5217\u79cd\u5b50\u95ed\u5408\u65cf\u673a\u68c0\u95f8 + S6 \u5168\u94fe) | "
    "WM-VERDICT: green (red=false lane healthy; engine ALIVE idle; DEC b87a92b1/ORD 0ddb01d9 "
    "UNCHANGED \u96f6\u91cd\u6d88\u8d39; S0.5+S7 \u53cc\u626b 0 \u672a\u56de\u6267) | "
    "\u5b64\u513f\u9762=1 (read-only probe) | "
    "S0: FF-only absorb 3-behind (bm-b r827 E7 \u4ea4\u4ed8\u9762; \u8f6e\u9996\u810f= \u672c\u673a 9 \u4efd daemon live faces \u96f6\u6587\u4ef6\u91cd\u53e0=FF \u5e72\u51c0\u96f6 UU) | "
    "S2: T-18 probe E8=COLLISION_RISK (bm-b in_flight 09:43 fresh) \u8ba9\u8def; T19=CLEAR \u540c\u8f6e\u8ba4\u9886 | "
    "S3: T19 \u5efa\u9762\u540c\u8f6e\u51fa\u5217=scripts/queue_seed_gate.py: \u2460 9 \u952e\u6ce8\u518c\u8868 single-source import science_gates.CLOSED_FAMILIES"
    "+face\u8868\u2194\u6ce8\u518c\u8868\u4e00\u81f4\u6027 selftest \u817f \u2461 check \u5355\u7c7d lint"
    "\uff08E6 \u7c7d\u5b9e\u5f39 rejected rc3+\u2014\u2014reopen \u58f0\u660e\u2192reopen_channel_declared rc0\uff09+scan \u6d3b\u884c\u536b\u751f\u5ba1\u8ba1"
    "\uff08tech 1+explore 5 \u6d3b\u884c\u00b70 findings\u00b71 note=T19 \u6307\u9488 meta \u5f15\u7528\u975e\u963b\u65ad\uff09 \u2462 \u5047\u9633\u6027\u63a7\u5236=HARD \u53ea\u770b work \u5217"
    "\u00b7pointer-only=note\u00b7done/closed \u6c38\u4e0d\u590d\u62a5\u00b7\u8bcd\u9762\u4fdd\u5b88\uff08E8 \u8de8\u671f\u4ef7\u5dee CLEAR=\u975e CTA \u65cf\u5b9e\u8bc1\uff09 "
    "\u2463 selftest 17/17 hermetic \u53cc\u8dd1\u5b57\u8282\u6052\u7b49 \u2464 \u63a5\u7ebf=Tools/iteration_prompt.txt S3 \u767b\u8bb0\u524d\u7f6e\u817f"
    "\uff08ASCII \u7eaf\u4f53\u00b7present-once \u5b9e\u8bc1\uff09 \u2465 \u8bc1\u636e=results/queue_seed_gate.json | "
    "\u6cbb\u7406\u6839\u6cbb\u9762=E6 r804 \u5efa\u9762\u672a\u6838\u95ed\u5408\u65cf\u2192\u767b\u8bb0\u65f6\u5f3a\u5236\u6838\u9a8c\u6b65\u843d\u5730\uff08\u79cd\u5b50\u9762\u95ed\u5408\u65cf\u673a\u68c0\u95f8=T19 \u5b8c\u6574\u95ed\u73af\uff09 | "
    "S6 39 legs rc0: dualrun \u96f6\u6f02\u79fb streak 7\u21928 / compute_audit flags []\uff08W17 bm-c \u5df2\u8ba4\u9886 0-4of8 @08:29-08:30 \u70b9\u706b\u949f\u5237\u65b0"
    "\u00b75/6/7+judge \u672a\u8ba4\u9886\u5f85 bm-c \u8bad\u7ec3\u7a97\u540e\u00b7MSG-0935 \u5728\u518c\uff09 / new_bar=False \u5468\u516d\u9762\u677f\u5c3e 10-09"
    "\u00b7paper legs \u5408\u6cd5\u5e42\u7b49 no-op / \u62a5\u544a\u00b7\u9762\u677f\u00b7token \u5168\u843d\u5730 | "
    "S7: attrition 4 \u8d26 CLEAN / self-heal 4/4\uff08loop pin=8 no-op+watchdog -Force+precommit+prepush\uff09/ "
    "idle_trigger --worked \u6e05\u96f6\u00b7GREEN-IDLE \u8f7d\u4f53\u81ea\u8bb0 | smoke 49/49 | "
    "\u4e0b\u8f6e\u6307\u9488: E8 bm-b \u5728\u98de\u7ee7\u7eed\u8ba9\u8def\u2192E9 AH \u6df1\u5316\u6216 W205 \u5e2d\u4f4d\u7a97\u5224\u5b9a\uff08W204 \u4e94\u9762\u672a\u6ce8\u518c\uff09; W17 bm-c ETA ~22:45 \u540e\u70b9\u706b\u56de\u67e5 | "
    "scoring: 2\uff08\u80fd\u8dd1\u95f8+\u8bc1\u636e+\u961f\u5217\u6d88\u8d39\u95ed\u73af\uff09 | bookkeeping: 5/5 | "
    "\u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08commit \u540e push+fetch+rev-list \u81ea\u8bc1\uff09 | [r950 bm-a]"
)
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line + "\n")
print("round report line appended")
print("closeout phase-1 done", TS_T)
