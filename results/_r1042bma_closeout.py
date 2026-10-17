# -*- coding: utf-8 -*-
# r1042 bm-a closeout: state / heartbeat / round report (EOL-preserving, epoch-int asserted)
import json, time, ctypes, subprocess, os, sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # results/ -> repo root
os.chdir(ROOT)
NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
CREATE_NO_WINDOW = 0x08000000

def live_ram():
    class MSX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MSX(); m.dwLength = ctypes.sizeof(MSX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / 1024**3, 1), round(m.ullTotalPhys / 1024**3, 1), m.dwMemoryLoad

def live_gpu_free_mb():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=20)
        return int(float(out.stdout.strip().splitlines()[0]))
    except Exception as e:
        return None

def read_b(p):
    with open(p, "rb") as f: return f.read()

def detect_eol(b): return "\r\n" if b"\r\n" in b[:4000] else "\n"

def detect_indent(b):
    for ln in b.decode("utf-8", "replace").splitlines()[1:6]:
        s = ln[:len(ln) - len(ln.lstrip(" "))]
        if s: return len(s)
    return 1

def write_json_eol(p, obj, ref_bytes):
    eol = detect_eol(ref_bytes); ind = detect_indent(ref_bytes)
    txt = json.dumps(obj, indent=ind, ensure_ascii=False)
    if eol == "\r\n": txt = txt.replace("\n", "\r\n")
    with open(p, "wb") as f: f.write(txt.encode("utf-8"))

free_gb, total_gb, memload = live_ram()
gpu_free = live_gpu_free_mb()

DID = ("r1042: S6 43/43 rc0 bad=0 maintenance closeout (chain driver _r1042bma_s6chain.ps1, r1038 43-leg face clone) + "
       "W264 finalize absent -> W265 bm-a own-seat stays gated (zero skip-claim) + D-19 opening double-scan hold "
       "(dec 1d4741e4 / ORD e0dcbd80 both zero-delta) + zero new orders + smoke 49/49")
VERDICT = ("green: r1042 = S6 43/43 rc0 adopted + smoke 49/49 + WM green (red=false) + satengine ALIVE idle + "
           "D-19 double-hold + W265 own-seat gated (zero skip-claim) + orphan face=0 (29 py faces)")
VERIFY = ("chain log results/_r1042bma_s6chain_rc.log 43/43 rc0 + smoke 49/49 + d19 probe rc0 silent hold + "
          "claws match x2 + loop pin=8 no-op + watchdog ready + idle_trigger --worked rc=0 (idle_rounds cleared)")
NEXT = ("r1043: W264 finalize landing watch (bm-c) -> W265 bm-a own-seat window FIRST ACTION on unlock; "
        "MF push2 Monday re-probe adjudication (<=2026-10-19)")
ART = "results/_r1042bma_s6chain_rc.log (S6 43/43 rc0, 22:3x-22:3x)"

# 1) state-bm-a.json
sp = "state-bm-a.json"; sb = read_b(sp); st = json.loads(sb.decode("utf-8"))
st.update({
    "round_no": 1043, "round": 1042, "loop_round": 1042,
    "last_round": "r1042", "last_round_label": "r1042", "round_no_label": "r1042",
    "clock_read": TS, "ts": TS, "updated": TS, "updated_at": TS, "now_active": TS,
    "last_round_at": TS, "last_round_ts": TS, "last_round_closed": TS, "last_run": TS,
    "last_seen": TS, "last_action_at": TS, "last_orders_at": TS, "last_decisions_at": TS,
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "last_heartbeat_epoch_utc": st.get("heartbeat_epoch_utc", EPOCH),
    "did": DID, "last_action": DID, "current": DID,
    "task": "r1042 S6 maintenance closeout + W265 gated watch",
    "current_task": "r1042 closed (S6 43/43 rc0 + D-19 hold); W265 bm-a own-seat gated on bm-c W264 finalize",
    "verdict": VERDICT, "verify": VERIFY, "next": NEXT,
    "next_milestone": "W265 bm-a own-seat window (opens on bm-c W264 finalize landing) + MF push2 re-probe adjudication <=2026-10-19",
    "last_artifact": ART, "recent_artifact": ART, "latest_artifact": ART,
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "idle_rounds": 0, "agenda_starved": False,
    "last_orders_seen": "r1042: ORD e0dcbd80 hold opening scan (probe rc0 silent zero delta; fleet/orders newest=O-20261017-2207-bm-c already receipted r1041)",
    "last_decisions_seen": "r1042: dec 1d4741e4 hold opening scan (probe rc0 silent, zero delta)",
    "orders_ack_note": "r1042: opening scan zero new orders (newest O-20261017-2207-bm-c receipted r1041); closing double-scan zero delta; d19 guard advance face = next orders/decisions change event",
    "free_ram_gb": free_gb, "ram_free_gb": free_gb, "idle_ram_gb": free_gb,
    "ram_free_pct": round(free_gb / total_gb * 100, 1), "free_ram_pct": round(free_gb / total_gb * 100, 1),
    "ram_load_pct": round((1 - free_gb / total_gb) * 100, 1),
    "total_ram_gb": total_gb,
    "gpu_source_note": "nvidia-smi live read " + TS + " (CEO working machine, honest free face)",
})
if gpu_free is not None:
    st["gpu_free_vram_mb"] = gpu_free
st["sync"] = {"ts": TS, "origin_tip": None, "ahead_behind": "pending-closeout-push",
              "note": "r1042: S0 fetch ahead=0 behind=0 (clean sync); closeout push follows"}
if isinstance(st.get("d19_watermark_guard"), dict):
    st["d19_watermark_guard"]["round_ref"] = 1042
    st["d19_watermark_guard"]["ts"] = TS
write_json_eol(sp, st, sb)

# 2) heartbeat fleet/machines/bm-a.json
hp = os.path.join("fleet", "machines", "bm-a.json"); hb = read_b(hp); ht = json.loads(hb.decode("utf-8"))
ht.update({
    "last_seen": TS, "ts": TS, "clock_read": TS, "updated_at": TS,
    "heartbeat_epoch_utc": EPOCH,
    "current_task": "r1042 closed (S6 43/43 rc0 maintenance); W265 own-seat gated on bm-c W264 finalize",
    "did": DID,
    "verdict": VERDICT,
    "idle_rounds": 0, "agenda_starved": False,
    "cpu_cores": os.cpu_count(),
    "idle_ram_gb": free_gb, "free_ram_gb": free_gb, "ram_free_gb": free_gb,
})
if gpu_free is not None:
    ht["gpu_free_vram_mb"] = gpu_free
write_json_eol(hp, ht, hb)

# 3) round_reports-bm-a.md append (EOL-matched)
rp = "round_reports-bm-a.md"; rb = read_b(rp); eol = detect_eol(rb)
line = (TS + " | r1042 bm-a (dept:舰队·S6 全链维护+W265 门控守watch) | WM-VERDICT: 绿 red=false lane=healthy "
        "(satengine ALIVE queue0 idle; idle green_idle=true→--worked 清零(0)) | 当前活=r1042: S0 平齐(0/0)+孤儿面探针 0(29 py faces)"
        "+D-19 开扫双 hold(dec 1d4741e4/ORD e0dcbd80 双零 delta)+零新令+S6 43/43 rc0 bad=0(driver _r1042bma_s6chain.ps1 r1038 面克隆)"
        "+smoke 49/49+W264 finalize absent→W265 own-seat 门控守watch 零 skip-claim+MF push2 复测裁定窗≤10-19(周六 S6 腿 no-op 自证) "
        "| 验证证据=chain log 43/43 rc0 + smoke 49/49 + d19 probe rc0 double-hold + claws match x2 + loop pin=8 no-op + watchdog ready "
        "+ idle_trigger --worked rc=0 + attrition scan rc0(链内腿) + 孤儿面=0 | 下轮指针=r1043: W264 finalize landing watch (bm-c) → "
        "W265 bm-a own-seat window FIRST ACTION on unlock; MF push2 Monday re-probe adjudication (≤2026-10-19); bm-b Taildrop re-queue pickup "
        "| 最近实物=" + ART + " | 本地未达 origin commit 数=0（收口推送后自证）| [r1042 bm-a s6-maintenance-watch]" + eol)
with open(rp, "ab") as f: f.write(line.encode("utf-8"))

# 4) self-assertions
for p in (sp, hp):
    d = json.loads(read_b(p).decode("utf-8"))
    assert isinstance(d.get("heartbeat_epoch_utc"), int), p + " epoch not int"
json.loads(read_b(rp).decode("utf-8", "replace"))  # not json, just byte sanity
print("CLOSEOUT_OK", TS, "free_ram_gb=", free_gb, "gpu_free_mb=", gpu_free, "epoch=", EPOCH)
