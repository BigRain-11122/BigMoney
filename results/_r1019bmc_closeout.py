"""r1019 closeout: round report row + heartbeat fix (real RAM free)."""
import ctypes
import datetime
import json


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_uint),
        ("dwMemoryLoad", ctypes.c_uint),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


m = MEMORYSTATUSEX()
m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
ram_free_gb = round(m.ullAvailPhys / 2 ** 30, 1)
ram_total_gb = round(m.ullTotalPhys / 2 ** 30, 1)
print("ram free=%.1fGB total=%.1fGB" % (ram_free_gb, ram_total_gb))

# ---- heartbeat fix: free_ram_gb must be RAM, not disk ----
hb = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
hb["free_ram_gb"] = ram_free_gb
open("fleet/machines/bm-c.json", "w", encoding="utf-8", newline="").write(
    json.dumps(hb, ensure_ascii=False, indent=1))
print("heartbeat free_ram_gb fixed ->", ram_free_gb)
