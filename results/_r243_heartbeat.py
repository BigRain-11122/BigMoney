# r243 heartbeat update (bm-b) -- epoch MUST be JSON int (R170/R178 law)
import io, json, time

hp = r"fleet\machines\bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
now = time.strftime("%Y-%m-%d %H:%M:%S")
h["last_seen"] = now
h["round_no"] = 243
h["current_task"] = ("r243 closed: T-78 s5a CN-GRID-SLEEVE prereg frozen "
                     "(commit db8ac757) + engine/grid_sleeve.py v1 selftest "
                     "8/8; s5b runner+pool next")
h["cpu_cores"] = 16
h["free_ram_gb"] = 11.0
h["gpu_free_vram_gb"] = 2.2
h["verdict"] = "GREEN"
epoch = int(time.time())
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S")
# orders_ack unchanged: 79/79 all acked (re-verified by caller after write)
io.open(hp, "w", encoding="utf-8", newline="").write(
    json.dumps(h, ensure_ascii=False, indent=1) + "\n")
d = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(d["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat ok epoch-int:", d["heartbeat_epoch_utc"], d["clock_read"])
