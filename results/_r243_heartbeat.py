"""r243 heartbeat: fleet/machines/bm-a.json update (own file, single writer).

heartbeat_epoch_utc MUST be a JSON int (python int(time.time()) directly —
R170/R178 double-violation law); clock_read = local ISO with UTC offset (T-04).
"""
import io
import json
import time
import datetime
import psutil

P = "fleet/machines/bm-a.json"
hb = json.load(io.open(P, encoding="utf-8"))

vm = psutil.virtual_memory()
gpus = [g for g in [None]]
try:
    import torch
    free = total = None
    if torch.cuda.is_available():
        free, total = torch.cuda.mem_get_info(0)
    vram_free_mb = round(free / 1e6, 1) if free else None
    vram_total_mb = round(total / 1e6, 1) if total else None
except Exception:
    vram_free_mb = vram_total_mb = None

hb["last_seen"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
hb["current_task"] = ("R243 done: T-77 slice-4 GPU lane flip+launch "
                      "(3 torch-core live-fire fixes; relaunch pid56984 "
                      "in flight, harvest next round); hot-cold reorg "
                      "50.7KB->11.4KB zero-loss")
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["idle_ram_gb"] = round(vm.available / 1e9, 1)
hb["gpu_free_vram_mb"] = vram_free_mb
hb["gpu_total_vram_mb"] = vram_total_mb
hb["verdict"] = "GREEN py_low_board_clear"
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = datetime.datetime.now().astimezone().isoformat(
    timespec="seconds")

io.open(P, "w", encoding="utf-8", newline="").write(
    json.dumps(hb, ensure_ascii=False, indent=1))
back = json.load(io.open(P, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), \
    type(back["heartbeat_epoch_utc"])
print("heartbeat ok; epoch int =", back["heartbeat_epoch_utc"],
      "| clock =", back["clock_read"],
      "| gpu free MB =", back["gpu_free_vram_mb"])
