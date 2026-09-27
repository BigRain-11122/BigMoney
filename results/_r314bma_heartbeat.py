import json
import io
import time
import datetime as dt

p = "fleet/machines/bm-a.json"
m = json.load(io.open(p, encoding="utf-8-sig"))

now = dt.datetime.now().astimezone()
epoch = int(time.time())

m["last_seen"] = now.isoformat(timespec="seconds")
m["clock_read"] = now.isoformat(timespec="seconds")   # T-separator law (R262)
m["heartbeat_epoch_utc"] = epoch                      # int type law (R170/R178)
m["round_no"] = 314
m["current_task"] = ("R314 done: T-72 A1 deep-window amendment (d1b2d20a) + full-universe 250td "
                     "deep repull IN FLIGHT ETA~14:40 + T-91 Monday preflight green + MSG bm-b "
                     "MF_IC_P1 contingency; R315 next: repull terminal verdict + Monday s3 window")

# machine face (single sample, same fields as prior rounds)
import psutil
m["cpu_cores"] = psutil.cpu_count(logical=True)
m["cpu_pct"] = psutil.cpu_percent(interval=1.0)
m["cpu_util_pct"] = m["cpu_pct"]
vm = psutil.virtual_memory()
m["free_ram_gb"] = round(vm.available / 1024**3, 1)
m["free_ram_mb"] = round(vm.available / 1024**2)
m["total_ram_gb"] = round(vm.total / 1024**3, 1)
try:
    import subprocess
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True,
                         timeout=10).stdout.strip().splitlines()[0]
    tot, used = [float(x) for x in out.split(",")]
    m["gpu_total_vram_mb"] = tot
    m["gpu_free_vram_gb"] = round((tot - used) / 1024, 2)
    m["gpu_idle_vram_gb"] = m["gpu_free_vram_gb"]
except Exception:
    pass

m["verdict"] = ("py_low_with_work_cands legal-occupied (work = sina_mf 250td deep repull in flight, "
                "network-paced; audit CLEAN; pool 1 ready = bm-c lane)")
m["task"] = m["current_task"]

with io.open(p, "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=1)

# self-verify: epoch int + json round-trip + clock T-separator (smoke F7 faces)
chk = json.load(io.open(p, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO8601"
print("heartbeat ok: epoch", chk["heartbeat_epoch_utc"], type(chk["heartbeat_epoch_utc"]).__name__,
      "| clock", chk["clock_read"], "| round", chk["round_no"])
