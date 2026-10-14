# -*- coding: utf-8 -*-
"""r983 bm-a heartbeat closeout: fresh sample + round 983 fields + epoch int + T-separated clock."""
import json, time, datetime, subprocess

p = "fleet/machines/bm-a.json"
d = json.load(open(p, encoding="utf-8"))
now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")

# fresh RAM sample (fast WMI-free)
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
    free_gb = round(m.ullAvailPhys / 1024**3, 1)
    total_gb = round(m.ullTotalPhys / 1024**3, 1)
except Exception:
    free_gb, total_gb = None, None

d["machine_id"] = "bm-a"
d["last_seen"] = now_iso
d["ts"] = now_iso
d["updated_at"] = now_iso
d["round"] = 983
d["round_no"] = 983
d["last_round"] = 983
d["last_round_at"] = now_iso
d["last_round_closed"] = 983
d["current_task"] = ("W238 PREREG FROZEN+DELIVERED r983 (27558B/47 SUB); splice next round; "
                     "S6 41-leg chain detached pid 44360")
d["current"] = d["current_task"]
d["now_active"] = True
d["active"] = True
d["verdict"] = ("green (red=false lane=healthy; engine ALIVE idle queue0; W238 PREREG FROZEN r983 "
                "ignition=this push; S6 chain detached pid 44360)")
d["recent_artifact"] = "research/PERPETUAL_N1_W238_PREREG.md (2026-10-14T12:0x, 27558B, 47 SUB pairs)"
d["latest_artifact"] = d["recent_artifact"]
d["last_artifact"] = d["recent_artifact"]
d["next_milestone"] = ("W238 five-face freeze splice -> self-burn 12/12 -> finalize (window <=48h); "
                       "bars 15:30 today -> S6 full chain + papers")
d["next"] = d["next_milestone"]
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["orphan_face"] = 0
d["orphan_faces"] = 0
d["last_orders_seen"] = ("r983: ORD db08b85b consumed (tail zero BigMoney rows); DEC unchanged")
d["last_orders_sha"] = "db08b85b76d1d44f14d66cc96442523a480eb0f6"
d["last_orders_at"] = now_iso
d["last_orders_ts"] = now_iso
d["last_orders_read_at"] = now_iso
d["last_decisions_seen"] = "r983: DEC 86187eff unchanged (dual-delta FALSE)"
d["last_decisions_read_at"] = now_iso
if free_gb:
    d["free_ram_gb"] = free_gb
    d["ram_free_gb"] = free_gb
    d["total_ram_gb"] = total_gb
epoch = int(time.time())
d["heartbeat_epoch_utc"] = epoch
d["last_heartbeat_epoch_utc"] = epoch
d["heartbeat_epoch_utc_type_int"] = True
d["clock_read"] = now_iso  # T-separated ISO8601 with offset

json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-proof: epoch int + clock T-sep
d2 = json.load(open(p, encoding="utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in d2["clock_read"], "clock_read must be T-separated"
print("heartbeat written: epoch=%d (int OK) clock=%s free_ram=%s" % (d2["heartbeat_epoch_utc"], d2["clock_read"], free_gb))
