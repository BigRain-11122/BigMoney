# -*- coding: utf-8 -*-
"""r282 bm-b heartbeat write (R170/R178/R262 laws: epoch=JSON int via int(time.time()),
clock_read=astimezone().isoformat() T-separated; post-write self-proof)."""
import io
import json
import time
import datetime as dt
import os
import ctypes


def ram_idle_gb():
    class Mem(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = Mem()
    m.dwLength = ctypes.sizeof(Mem)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / 1e9, 1), round(m.ullTotalPhys / 1e9, 1), m.dwMemoryLoad


def cpu_pct():
    import psutil
    return round(psutil.cpu_percent(interval=0.4), 1)


p = "fleet/machines/bm-b.json"
d = json.load(io.open(p, encoding="utf-8"))
avail, total, _ = ram_idle_gb()
now = dt.datetime.now().astimezone()
d["machine_id"] = "bm-b"
d["role"] = "compute-node"
d["last_seen"] = now.isoformat()
d["heartbeat_epoch_utc"] = int(time.time())
d["clock_read"] = now.isoformat()
d["current_task"] = ("T-87 supply lane: first-pull pass in flight (450/5228, on_track, ETA Sun 06:47); "
                     "r282 re-probe #2 + S6 26 legs green + rebase UU per r281 recipe")
d["cpu_cores"] = os.cpu_count()
d["free_ram_gb"] = avail
d["total_ram_gb"] = total
d["cpu_util_pct"] = cpu_pct()
d["round_no"] = 282
d["verdict"] = "green"
io.open(p, "w", encoding="utf-8", newline="").write(json.dumps(d, ensure_ascii=False, indent=1))

# post-write self-proof (smoke F7 face)
d2 = json.load(io.open(p, encoding="utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in d2["clock_read"], "clock_read must be T-separated"
print("heartbeat ok: epoch=", d2["heartbeat_epoch_utc"], "clock=", d2["clock_read"])
