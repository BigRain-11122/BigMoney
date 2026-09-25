"""r221 close: heartbeat update for fleet/machines/bm-b.json (own file only).
Fields per S7: last_seen / current_task / cpu cores / free RAM / GPU free
VRAM / verdict / heartbeat_epoch_utc (python int, self-verified) /
clock_read (local ISO with UTC offset)."""
import json, io, time, datetime, subprocess

try:
    import psutil
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    cpu_pct = psutil.cpu_percent(interval=1)
except Exception:
    ram_free, cpu_pct = None, None

gpu_free_gb = None
try:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    if out:
        gpu_free_gb = round(float(out[0]) / 1024.0, 1)
except Exception:
    pass

p = "fleet/machines/bm-b.json"
d = json.load(io.open(p, encoding="utf-8"))
d["last_seen"] = "2026-09-26 03:41"
d["current_task"] = ("r221: P-1e runner first-fire fix landed (M_close "
                     "close-only KeyError, r198 family); autofill fires 4 "
                     "shards from 03:40; r222 = harvest + pool flip + finalize")
d["cpu_cores"] = 16
if ram_free is not None:
    d["free_ram_gb"] = ram_free
    d["idle_ram_gb"] = ram_free
if cpu_pct is not None:
    d["cpu_util_pct"] = cpu_pct
if gpu_free_gb is not None:
    d["gpu_free_vram_gb"] = gpu_free_gb
    d["gpu_free_vram_mb"] = int(gpu_free_gb * 1024)
d["round_no"] = 221
d["verdict"] = "green"
epoch = int(time.time())
assert isinstance(epoch, int)
d["heartbeat_epoch_utc"] = epoch
d["clock_read"] = datetime.datetime.now().astimezone().isoformat()

payload = json.dumps(d, ensure_ascii=False, indent=1)
parsed = json.loads(payload)
assert isinstance(parsed["heartbeat_epoch_utc"], int), "epoch must be int"
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(payload)
print("heartbeat ok: epoch", epoch, "| ram_free", ram_free,
      "| cpu", cpu_pct, "| gpu_free_gb", gpu_free_gb)