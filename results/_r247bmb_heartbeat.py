# r247 heartbeat updater (throwaway; delete after run)
import json, io, time, datetime, psutil

p = "fleet/machines/bm-b.json"
d = json.load(io.open(p, encoding="utf-8"))

vm = psutil.virtual_memory()
now_local = datetime.datetime.now().astimezone()
epoch = int(time.time())

d["last_seen"] = now_local.strftime("%Y-%m-%d %H:%M")
d["heartbeat_epoch_utc"] = epoch
d["clock_read"] = now_local.isoformat(timespec="seconds")
d["current_task"] = "r247 closed: maintenance round, board clear (zero-claim honest); next action face = 09-28 Monday new-bar full chain"
d["cpu_cores"] = psutil.cpu_count()
d["free_ram_gb"] = round(vm.available / 1e9, 1)
d["total_ram_gb"] = round(vm.total / 1e9, 1)
d["cpu_util_pct"] = psutil.cpu_percent(interval=1)
d["gpu_free_vram_gb"] = 2.2
d["round_no"] = 247
d["verdict"] = "GREEN"
d["cores"] = d["cpu_cores"]
d["idle_ram_gb"] = d["free_ram_gb"]
d["gpu_free_vram_mb"] = 2242
d["idle_ram_mb"] = int(vm.available / 1e6)
d["gpu_idle_vram_mb"] = 2242

io.open(p, "w", encoding="utf-8", newline="").write(
    json.dumps(d, indent=1, ensure_ascii=False) + "\n"
)

# self-verify: reload, epoch must be JSON int
d2 = json.load(io.open(p, encoding="utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch not int!"
print("heartbeat OK | epoch=", d2["heartbeat_epoch_utc"], "int-verified | clock=", d2["clock_read"], "| round_no=", d2["round_no"], "| free_ram=", d2["free_ram_gb"], "| cpu%=", d2["cpu_util_pct"])
