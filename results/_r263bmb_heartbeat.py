"""r263 bm-b: heartbeat update (five-face probe first, then epoch-int heartbeat per R170/R178 law)."""
import ctypes
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
path = "fleet/machines/bm-b.json"
raw = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True).stdout
print("BOM:", raw[:3] == b"\xef\xbb\xbf", "| CRLF:", raw.count(b"\r\n"), "LF:", raw.count(b"\n"), "| tail_nl:", raw.endswith(b"\n"), "| esc:", b"\\u" in raw)
txt = raw.decode("utf-8-sig" if raw[:3] == b"\xef\xbb\xbf" else "utf-8")
first_field = next(l for l in txt.splitlines() if '"' in l)
print("indent_sample:", repr(first_field[:20]))

with open(path, encoding="utf-8") as f:
    h = json.load(f)

# free RAM via ctypes GlobalMemoryStatusEx
class MEM(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
mem = MEM()
mem.dwLength = ctypes.sizeof(MEM)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
free_ram_gb = round(mem.ullAvailPhys / 1024 ** 3, 1)

# GPU free VRAM via nvidia-smi
gpu_free = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], capture_output=True, timeout=20)
    gpu_free = int(out.stdout.decode().strip().splitlines()[0])  # MiB
except Exception as e:  # noqa: BLE001
    gpu_free = None

epoch = int(time.time())
h["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
h["current_task"] = "T-76 face (d) #95/#96 paramfreeze deep-read delivered; round 263 closeout"
h["cpu_cores"] = 16
h["free_ram_gb"] = free_ram_gb
h["gpu_free_vram_mb"] = gpu_free
h["verdict"] = "py_low_board_clear legal idle (board closed, pool all-done, research-face round)"
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] + ":" + time.strftime("%z")[3:]
with open(path, "w", encoding="utf-8", newline="\r\n" if raw.count(b"\r\n") > 0 else "\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1 if first_field.startswith(' "') else 2)
    f.write("\n" if raw.endswith(b"\n") else "")

with open(path, encoding="utf-8") as f:
    check = json.load(f)
e = check.get("heartbeat_epoch_utc")
assert isinstance(e, int) and not isinstance(e, bool), f"epoch type violation: {type(e)}"
print("heartbeat OK: epoch int", e, "| free_ram", free_ram_gb, "GB | gpu_free", gpu_free, "MiB | clock", check.get("clock_read"))
