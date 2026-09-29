import json
import time
import socket
import psutil

p = "fleet/machines/bm-a.json"
hb = json.load(open(p, encoding="utf-8"))
epoch = int(time.time())
assert isinstance(epoch, int)
hb["last_seen"] = "2026-09-29T15:2x+08:00"
hb["current_task"] = "r433 closed: T-101-V4-A2 prescreen verdict (1/10 survive + D6 REJECT 0.9424); next=r434 survivor corr-source prereg"
hb["cpu_cores"] = 32
mem = psutil.virtual_memory()
hb["idle_ram_gb"] = round(mem.available / 1e9, 1)
gpu_free = 24 - 10.849
hb["gpu_free_vram_gb"] = round(gpu_free, 1)
hb["verdict"] = "r433: product increment delivered (v4 prescreen batch live-fire, verdict face in results/t101_v4_a2_prescreen.json); S6 all-green; board clear legal-idle"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
json.dump(hb, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(p, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO8601"
print("heartbeat ok epoch=", chk["heartbeat_epoch_utc"], "type=", type(chk["heartbeat_epoch_utc"]).__name__)
print("orders_ack count:", len(chk.get("orders_ack", [])))
