import ctypes, json

p = json.load(open(r"results/runnable_pool.json", encoding="utf-8"))
e = p.get("entries", [])
if isinstance(e, dict):
    items = [(k, v) for k, v in e.items()]
else:
    items = [(v.get("id", f"idx{i}"), v) for i, v in enumerate(e)]
ready = []
for k, v in items:
    st = v.get("status") if isinstance(v, dict) else None
    if st == "ready":
        ready.append(k)
print("pool total:", len(items), "ready:", len(ready))
for r in ready[:18]:
    print(" -", r[:80])

class M(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]

m = M()
m.dwLength = ctypes.sizeof(M)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
print(f"RAM load {m.dwMemoryLoad}% avail {m.ullAvailPhys/1e9:.1f}GB")
