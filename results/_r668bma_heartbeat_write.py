"""r668 bm-a S7 heartbeat write (fleet/machines/bm-a.json): epoch int +
clock T-sep + strict json proof."""
import json
import time

P = "fleet/machines/bm-a.json"
epoch = int(time.time())
clock = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
d = json.load(open(P, encoding="utf-8"))
d["machine_id"] = "bm-a"
d["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
d["last_run"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
d["last_round"] = "r668"
d["round_no"] = 669
d["current"] = ("THEME-JUDGE-P1 burn in flight (daemon-claimed 09:51:37; "
                "burn_state.json = completion marker); fund trio NULLS "
                "bm-b keepalive (QUALITY self-adopt live 09:36:12); T-166 "
                "fund-statement backfill staging->panel promotion pending")
d["current_task"] = d["current"]
d["verdict"] = ("green: r668 = T-167 s3 runner built+selftest 15/15+real-"
                "probe green+pool entered+daemon claimed same minute; S6 "
                "37/37 rc0; smoke 48/48")
d["heartbeat_epoch_utc"] = epoch
d["clock_read"] = clock
d["task"] = "OS iteration loop r668 (T-2026-10-04-167-P1 s3)"
import psutil
d["cpu_pct"] = psutil.cpu_percent(interval=0.5)
d["cpu_util_pct"] = d["cpu_pct"]
d["cores"] = psutil.cpu_count()
d["cpu_cores"] = d["cores"]
d["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
d["idle_ram_gb"] = d["free_ram_gb"]
try:
    import GPUtil
    g = GPUtil.getGPUs()[0]
    d["gpu_free_vram_gb"] = round(g.memoryFree / 1024, 1)
    d["gpu_model"] = g.name
except Exception:
    pass
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
chk = json.load(open(P, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock T-sep"
print(json.dumps({"epoch_int": chk["heartbeat_epoch_utc"],
                  "clock": chk["clock_read"],
                  "ack_count": len(chk.get("orders_ack", []))},
                 ensure_ascii=False))
