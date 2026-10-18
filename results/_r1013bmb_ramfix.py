import ctypes, json

class MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

m = MS()
m.dwLength = ctypes.sizeof(MS)
ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free = round(m.ullAvailPhys / 1024**3, 1)
p = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-b.json"
hb = json.load(open(p, encoding="utf-8"))
hb["free_ram_gb"] = free
json.dump(hb, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("api_ok=%s free_gb=%s" % (bool(ok), free))
