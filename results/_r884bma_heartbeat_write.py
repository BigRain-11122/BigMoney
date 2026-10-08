# r884 bm-a heartbeat write (own single-writer file)
import json, time, datetime, os

P = "fleet/machines/bm-a.json"
d = json.load(open(P, encoding="utf-8"))

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

ram_free_pct, vram_free_gb, cpu_pct = None, None, None
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_pct = round(vm.available * 100 / vm.total, 1)
    cpu_pct = round(psutil.cpu_percent(interval=0.5), 1)
except Exception:
    pass
try:
    out = os.popen(
        "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits"
    ).read().strip().splitlines()
    if out:
        vram_free_gb = round(float(out[0]) / 1024, 2)
except Exception:
    pass

d["last_seen"] = now
d["ts"] = now
d["clock_read"] = now
d["heartbeat_epoch_utc"] = epoch
d["current_task"] = ("W186 finalize landed (ledger 816,528); W187 chain unopened; "
                     "10-08 late-bar self-heal watch")
d["cpu_cores"] = 32
if cpu_pct is not None:
    d["cpu_pct"] = cpu_pct
if ram_free_pct is not None:
    d["ram_free_pct"] = ram_free_pct
if vram_free_gb is not None:
    d["gpu_vram_free_gb"] = vram_free_gb
d["verdict"] = "green"
d["idle_rounds"] = 0
d["agenda_starved"] = False

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("heartbeat written epoch=", epoch, "int=", isinstance(d["heartbeat_epoch_utc"], int),
      "ram_free=", ram_free_pct, "vram_free=", vram_free_gb, "cpu=", cpu_pct)
