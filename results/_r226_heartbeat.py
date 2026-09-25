# -*- coding: utf-8 -*-
"""r226 (bm-b) heartbeat update: fleet/machines/bm-b.json
epoch = python int(time.time()) written as JSON int (R170/R178 law,
self-verified post-write)."""
import datetime
import json
import platform

epoch = int(__import__("time").time())          # JSON int, not str

# RAM sample (idle MB)
idle_ram_mb = None
try:
    import ctypes
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
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    idle_ram_mb = round(m.ullAvailPhys / (1024 * 1024))
except Exception:
    pass

# GPU idle VRAM sample (nvidia-smi if present)
gpu_idle_vram_mb = None
try:
    import subprocess
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, timeout=15)
    vals = [int(x) for x in p.stdout.decode().split() if x.strip().isdigit()]
    if vals:
        gpu_idle_vram_mb = vals[0]
except Exception:
    pass

P = "fleet/machines/bm-b.json"
raw = open(P, "rb").read()
crlf = raw.count(b"\r\n") > 0
d = json.loads(raw.decode("utf-8-sig"))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
d["last_seen"] = now[:19]
d["current_task"] = ("r226 done: P-1e batch closed 4/4 (harvest+flip+finalize: "
                     "survivors 2/7 stv+coin_team, ledger 183292, prereg 7/8 "
                     "backfilled, shelf +2); idle: 09-28 relay / corr spec")
d["cpu_cores"] = 16
d["idle_ram_mb"] = idle_ram_mb
d["gpu_idle_vram_mb"] = gpu_idle_vram_mb
d["verdict"] = "green"
d["heartbeat_epoch_utc"] = epoch                       # int, R170/R178 law
d["clock_read"] = now
orders_ack = d.get("orders_ack")
out = json.dumps(d, ensure_ascii=False, indent=2)
with open(P, "wb") as f:
    if crlf:
        f.write(out.replace("\n", "\r\n").encode("utf-8"))
    else:
        f.write(out.encode("utf-8"))

chk = json.load(open(P, encoding="utf-8-sig"))
e = chk.get("heartbeat_epoch_utc")
assert isinstance(e, int) and not isinstance(e, bool), f"epoch type={type(e)}"
print(f"heartbeat written: epoch={e} (int verified) idle_ram={idle_ram_mb}MB "
      f"gpu_idle_vram={gpu_idle_vram_mb}MB clock={now}")
print("orders_ack preserved:", len(orders_ack.split()) if isinstance(orders_ack, str) else len(orders_ack or []), "tokens")
