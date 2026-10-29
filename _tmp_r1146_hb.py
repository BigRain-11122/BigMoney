import ctypes
import json
import os
import sys
import time
from ctypes import wintypes

ROOT = os.path.dirname(os.path.abspath(__file__))


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


def _ft(ft):
    return (ft.dwHighDateTime << 32) | ft.dwLowDateTime


def cpu_pct(sample_sec=0.4):
    idle1, kern1, user1 = FILETIME(), FILETIME(), FILETIME()
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle1), ctypes.byref(kern1), ctypes.byref(user1))
    time.sleep(sample_sec)
    idle2, kern2, user2 = FILETIME(), FILETIME(), FILETIME()
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle2), ctypes.byref(kern2), ctypes.byref(user2))
    di = _ft(idle2) - _ft(idle1)
    dt = (_ft(kern2) - _ft(kern1)) + (_ft(user2) - _ft(user1))
    if dt <= 0:
        return None
    return round(100.0 * (1.0 - float(di) / float(dt)), 1)


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", wintypes.DWORD), ("dwMemoryLoad", wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def mem():
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return (round(m.ullAvailPhys / (1024.0 ** 3), 1), int(m.dwMemoryLoad))


ram_free_gb, ram_load_pct = mem()
now = time.time()
clock_read = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now)) + time.strftime("%z", time.localtime(now))
clock_read = clock_read[:-2] + ":" + clock_read[-2:]

fields = {
    "round": 1146,
    "round_no": 1146,
    "last_seen": clock_read,
    "ts": clock_read,
    "clock_read": clock_read,
    "heartbeat_epoch_utc": int(now),
    "current_task": "r1146: cash placement reconciliation on the CEO book page",
    "verdict": "ok",
    "cpu_cores": os.cpu_count(),
    "cpu_pct": cpu_pct(),
    "ram_free_gb": ram_free_gb,
    "ram_load_pct": ram_load_pct,
    "idle_rounds": 0,
    "agenda_starved": False,
}

sys.path.insert(0, os.path.join(ROOT, "Tools"))
import heartbeat_write  # noqa: E402

v, rc = heartbeat_write.write(ROOT, fields)
print("heartbeat rc=%s %s" % (rc, json.dumps({k: v.get(k) for k in
      ("machine_id", "ack_before", "ack_after", "applied", "warnings", "error")},
      ensure_ascii=False)))

sp = os.path.join(ROOT, "state-bm-a.json")
with open(sp, encoding="utf-8-sig") as fh:
    st = json.load(fh)
st["round_no"] = 1146
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("state round_no -> 1146")