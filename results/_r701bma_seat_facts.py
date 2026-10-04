# r701 seat-time facts: live ledger head + RAM face + W117/W118 product counts
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import perpetual_faces  # bootstrap: same import order as the W119 probe (path fixup)
import science_gates
import glob

head = science_gates.ledger_head()
print("ledger_head", head)
lh = science_gates.active_voids() if hasattr(science_gates, "active_voids") else None
print("voids", lh)

# upstream product counts
for w in (116, 117, 118):
    n = len(glob.glob(os.path.join(ROOT, "results", "p2cal_ext", f"n1_w{w}", "shard-*.json")))
    print(f"n1_w{w}_shards", n)

# W117 finalize armed note
p117 = os.path.join(ROOT, "results", "_r684bma_w117_finalize_rehearsal.json")
if os.path.exists(p117):
    j = json.load(open(p117, encoding="utf-8"))
    print("w117_rehearsal_verdict", j.get("verdict"), "| armed", j.get("armed", j.get("note", "")))

import ctypes, ctypes.wintypes
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.wintypes.DWORD), ("dwMemoryLoad", ctypes.wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
print("ram_avail_gb", round(m.ullAvailPhys / 1e9, 2), "load_pct", m.dwMemoryLoad)
