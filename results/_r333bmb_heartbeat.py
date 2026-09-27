# r333 bm-b heartbeat updater (R170/R178/R262 laws: epoch JSON int, clock_read T-sep ISO)
import json, time, datetime, psutil, subprocess

P = r"fleet\machines\bm-b.json"
d = json.load(open(P, encoding="utf-8"))
now = datetime.datetime.now().astimezone()
epoch = int(time.time())
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / 2**30, 1)
cpu = psutil.cpu_percent(interval=1)
gpu_free_mb = None
try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,name", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True).stdout.strip().splitlines()[0]
    parts = [x.strip() for x in q.split(",")]
    gpu_free_mb = int(float(parts[0]))
    gpu_name = parts[1]
except Exception:
    gpu_name = d.get("gpu_model", "").split("(")[0].strip()

d.update({
    "last_seen": now.isoformat(timespec="microseconds" if now.microsecond else "seconds"),
    "heartbeat_epoch_utc": epoch,
    "clock_read": now.isoformat(),
    "current_task": "SINA_CONSTRUCT_P1 ignition face delivered (script+freeze+seed pushed f5acd8fa; bm-a census burn unblocked per MSG-1615 two-condition) + W2-A burn monitoring (4 workers full-throttle since 15:40, first ckpt block pending) + Mon T-91/T-87 chains pre-armed",
    "cpu_cores": 16,
    "total_ram_gb": round(vm.total / 2**30, 1),
    "free_ram_gb": ram_free_gb,
    "idle_ram_gb": ram_free_gb,
    "free_ram_mb": int(vm.available / 2**20),
    "idle_ram_mb": int(vm.available / 2**20),
    "cpu_util_pct": round(cpu, 1),
    "cpu_pct": round(cpu, 1),
    "round_no": 333,
    "round": 333,
    "loop_round": 333,
    "verdict": "healthy",
})
if gpu_free_mb is not None:
    d["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 2)
    d["gpu_idle_vram_gb"] = round(gpu_free_mb / 1024, 2)
    d["gpu_free_vram_mb"] = gpu_free_mb
    d["gpu_idle_vram_mb"] = gpu_free_mb
    d["gpu_model"] = f"{gpu_name} ({8192 - gpu_free_mb}MiB used @{now.isoformat()})"

with open(P, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

# self-verify (smoke F7 face): strict reload, epoch int, clock_read T-sep
chk = json.load(open(P, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"].split("+")[0], "clock_read T-sep"
assert chk["round_no"] == 333
print("heartbeat OK: epoch=%d int, clock=%s, ram_free=%.1fGB, gpu_free=%sMB, cpu=%.1f%%, ack=%d" % (
    chk["heartbeat_epoch_utc"], chk["clock_read"], chk["free_ram_gb"],
    chk.get("gpu_free_vram_mb"), chk["cpu_util_pct"], len(chk["orders_ack"])))
