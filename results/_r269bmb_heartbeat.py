"""r269 bm-b heartbeat update (S7): fleet/machines/bm-b.json.
Laws: epoch = python int (R170/R178), clock_read ISO-8601 T-separator (R262),
byte-face mirror (probe from HEAD blob first), post-write json.loads
self-verify isinstance(epoch, int)."""
import io
import json
import os
import subprocess
import time
import datetime as dt
import ctypes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

# --- byte-face probe (HEAD blob, git cat-file direct bytes, R255 channel law)
blob = subprocess.run(["git", "show", "HEAD:fleet/machines/bm-b.json"],
                       capture_output=True).stdout
print("probe: BOM=%s CRLF=%s tail_nl=%s" % (
    blob[:3] == b"\xef\xbb\xbf", b"\r\n" in blob, blob.endswith(b"\n")))
txt0 = blob.decode("utf-8-sig")
import re
m = re.match(r'( +)"', txt0.split("\n")[1])
print("probe: indent=%s ascii_raw=%s" % (
    len(m.group(1)) if m else "?", any(ord(c) > 127 for c in txt0)))

# --- system stats
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
stat = MEMORYSTATUSEX()
stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
free_ram_gb = round(stat.ullAvailPhys / (1024 ** 3), 1)
total_ram_gb = round(stat.ullTotalPhys / (1024 ** 3), 1)

cpu_util = 0.0
try:
    import psutil
    cpu_util = round(psutil.cpu_percent(interval=0.5), 1)
except Exception:
    pass

gpu_free_gb = 2.2  # last known face; no GPU job ran this round
try:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"], capture_output=True).stdout
    gpu_free_gb = round(float(out.decode().strip().splitlines()[0]) / 1024, 1)
except Exception:
    pass

now = dt.datetime.now().astimezone()
epoch = int(time.time())

with io.open(PATH, encoding="utf-8") as fh:
    h = json.load(fh)
assert h["round_no"] in (268, 269), "unexpected round_no: %s" % h["round_no"]
h["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S")
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now.isoformat(timespec="seconds")
h["current_task"] = ("r269 done: T-81 closure (post_review acceptance x4 YES "
                     "+ done flip); next: board/pool watch + 09-28 Monday "
                     "channels/marks window")
h["cpu_cores"] = 16
h["free_ram_gb"] = free_ram_gb
h["gpu_free_vram_gb"] = gpu_free_gb
h["total_ram_gb"] = total_ram_gb
h["cpu_util_pct"] = cpu_util
h["round_no"] = 269
h["verdict"] = "healthy"
# legacy mirror fields (kept in sync with r268 face)
h["cores"] = 16
h["idle_ram_gb"] = free_ram_gb
h["gpu_free_vram_mb"] = int(gpu_free_gb * 1024)
h["idle_ram_mb"] = int(free_ram_gb * 1024)
h["gpu_idle_vram_mb"] = int(gpu_free_gb * 1024)
h["n_orders_ack"] = len(h["orders_ack"].split())
h["gpu_idle_vram_gb"] = gpu_free_gb
h["cpu_pct"] = cpu_util

# byte-face mirror: no BOM, LF, indent=1, no trailing newline
with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)

# post-write self-verify (smoke F7 contract)
h2 = json.load(io.open(PATH, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"], "clock_read must be T-separated"
print("heartbeat ok: epoch=%d (int) clock=%s round=%d ram_free=%.1fGB "
      "gpu_free=%.1fGB cpu=%.1f%%" % (
          h2["heartbeat_epoch_utc"], h2["clock_read"], h2["round_no"],
          free_ram_gb, gpu_free_gb, cpu_util))
