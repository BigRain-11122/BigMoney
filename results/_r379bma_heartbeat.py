"""r379 bm-a heartbeat update: fresh stats + epoch int + clock_read
T-separator (R170/R178/R262 laws), post-write self-proof."""
import io, json, time, datetime

import psutil

p = r"fleet/machines/bm-a.json"
d = json.load(io.open(p, encoding="utf-8"))

now = datetime.datetime.now().astimezone()
cpu = psutil.cpu_percent(interval=2.0)
vm = psutil.virtual_memory()
ram_free = round(vm.free / 1e9, 1)
gpu_free = None
try:
    import subprocess
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=10)
    gpu_free = round(float(out.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass

epoch = int(time.time())
clock = now.isoformat(sep="T", timespec="seconds")

d.update({
    "machine_id": "bm-a",
    "last_seen": clock,
    "current_task": "r379 done: D-20260928-03(1) batch-3 slice-2 paper-family C single-writer guards (6 faces, 6 writers wired, lane_io selftest 9/9, non-host sim all-skip) + MSG-0420 W2B runner owner-review ACCEPTED + exporter roster-name gate landed (selftest 11/11); S6 30 legs rc=0 + reconcile 14/14 zero-drift",
    "cpu_cores": psutil.cpu_count(),
    "cpu_pct": cpu,
    "free_ram_gb": ram_free,
    "verdict": "green (red=false lane healthy; probe 04:15 py_low_board_clear legal-idle: board 0 open / pool ready=1 W2B bm-b lane ~10h burn + V2-P1 waiting defer-RAM-serialize-behind-W2B; audit v2.3 CLEAN flags=[])",
    "task": "round-closed",
    "round_no": 379,
    "round": 379,
    "loop_round": 379,
    "heartbeat_epoch_utc": epoch,
    "clock_read": clock,
})
if gpu_free is not None:
    d["gpu_free_vram_gb"] = gpu_free

json.dump(d, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# post-write self-proof: epoch must be JSON int (R170/R178), clock T-separated
d2 = json.load(io.open(p, encoding="utf-8"))
e = d2.get("heartbeat_epoch_utc")
assert isinstance(e, int) and not isinstance(e, bool), f"epoch type={type(e)}"
assert "T" in d2.get("clock_read", ""), d2.get("clock_read")
print(f"heartbeat verified: epoch={e} (int) clock={d2['clock_read']} "
      f"cpu={cpu}% ram_free={ram_free}GB gpu_free={gpu_free}GB")
