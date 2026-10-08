"""r774 bm-c closeout probe: EngineTick idle face + ctypes RAM + CPU load."""
import ctypes
import datetime
import json

R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
f = json.load(open(R + r"\results\idle_trigger.bm-c.json", encoding="utf-8"))
keys = ["ts", "verdict", "ram_idle_pct", "idle_ram_gb", "vram_free_mb",
        "idle_rounds", "agenda_starved", "inflight_batches", "green", "tier"]
print("IDLE_FACE", json.dumps({k: f.get(k) for k in keys if k in f},
                              ensure_ascii=False)[:600])
print("IDLE_FACE_ALL_KEYS", sorted(f.keys())[:20])


class M(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
                ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
                ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64),
                ("ullAvailExtendedVirtual", ctypes.c_uint64)]


m = M()
m.dwLength = ctypes.sizeof(M)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
print("RAM_FREE_GB", round(m.ullAvailPhys / 1073741824, 1),
      "RAM_TOTAL_GB", round(m.ullTotalPhys / 1073741824, 1),
      "MEMLOAD_PCT", m.dwMemoryLoad)
print("now", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
