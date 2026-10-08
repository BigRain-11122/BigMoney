"""r781 bm-c close-facts probe: RAM/VRAM/CPU snapshot + compute_audit flag
extract + attrition-independent facts -> results/_r781bmc_close_facts.json."""
import ctypes
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# RAM via GlobalMemoryStatusEx
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


mem = MEMORYSTATUSEX()
mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
ram_total_gb = mem.ullTotalPhys / (1024 ** 3)
ram_free_gb = mem.ullAvailPhys / (1024 ** 3)
ram_free_pct = round(100.0 * mem.ullAvailPhys / mem.ullTotalPhys, 1)

# VRAM via nvidia-smi
vram_free_mb = -1
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, timeout=20)
    vram_free_mb = int(p.stdout.decode("utf-8", "replace").strip().splitlines()[0])
except Exception as e:
    print("VRAM probe fail:", str(e)[:120])

# CPU via wmic-free performance snapshot (1s)
cpu_pct = -1.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
except Exception:
    class PDH:
        pass
    # fallback: load percentage via WMI through powershell-free path is
    # complex; use GetSystemTimes delta instead
    import time
    kernel32 = ctypes.windll.kernel32

    class FILETIME(ctypes.Structure):
        _fields_ = [("lo", ctypes.c_ulong), ("hi", ctypes.c_ulong)]
    idle1, kern1, user1 = FILETIME(), FILETIME(), FILETIME()
    kernel32.GetSystemTimes(ctypes.byref(idle1), ctypes.byref(kern1),
                             ctypes.byref(user1))
    time.sleep(1.0)
    idle2, kern2, user2 = FILETIME(), FILETIME(), FILETIME()
    kernel32.GetSystemTimes(ctypes.byref(idle2), ctypes.byref(kern2),
                            ctypes.byref(user2))

    def ft_to_int(ft):
        return (ft.hi << 32) | ft.lo
    idle_d = ft_to_int(idle2) - ft_to_int(idle1)
    kern_d = ft_to_int(kern2) - ft_to_int(kern1)
    user_d = ft_to_int(user2) - ft_to_int(user1)
    total = kern_d + user_d
    cpu_pct = round(100.0 * (total - idle_d) / total, 1) if total else -1.0

# compute_audit flags extract (machine-local face)
flags = None
load_state = None
try:
    with open(os.path.join(REPO, "results", "compute_audit.bm-c.json"),
              encoding="utf-8") as fh:
        audits = json.load(fh)
    last = audits[-1] if isinstance(audits, list) else audits
    flags = last.get("flags")
    load_state = last.get("load_state")
except Exception as e:
    print("audit read fail:", str(e)[:120])

facts = {
    "round": 781,
    "ram_total_gb": round(ram_total_gb, 1),
    "ram_gb": round(ram_free_gb, 1),
    "ram_free_pct": ram_free_pct,
    "vram_mb": vram_free_mb,
    "cpu_pct": cpu_pct,
    "compute_audit_flags": flags,
    "compute_audit_load_state": load_state,
}
out = os.path.join(REPO, "results", "_r781bmc_close_facts.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1)
print(json.dumps(facts, indent=1))
