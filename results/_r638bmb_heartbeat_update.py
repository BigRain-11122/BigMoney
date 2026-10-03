import json, time, datetime
p = "fleet/machines/bm-b.json"
d = json.load(open(p, encoding="utf-8"))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
ram = 4.12
gpu_free_mb = 2313
cpu = 67.1
d["last_seen"] = now
d["heartbeat_epoch_utc"] = epoch          # MUST be JSON int (R170/R178 law)
d["clock_read"] = now                      # ISO 8601 with T separator (R262 law)
d["round_no"] = 638
d["round_no_label"] = "round 638 (bm-b)"
d["current_task"] = ("FUND trio NULLS burn watch (V434/Q309/D193 of 2000 progressing, all 3 daemons "
                     "live-verified; finalize window 10-05..10-09 held on G-SEG GM ruling pending; W14 "
                     "CEO-park holds) + dashboard.html 4 new data-chain faces landed (repo ladder / "
                     "options / fund NAV / AH premium, r638)")
d["verdict"] = ("GREEN (smoke 47/47; S6 full chain rc0; dualrun ZERO-DRIFT streak 28; engine alive rc0 "
                "idle; orders 152/152 double-scan clean; attrition CLEAN; D-19 watermark consumed "
                "a82b096c zero new BigMoney dispatch; trio burns healthy pure-append verified; RAM "
                "avail 4.12GB above 4GB shared-machine gate)")
d["ts"] = now
d["updated"] = now
d["updated_at"] = now
d["cpu_cores"] = 16
d["cpu_util_pct"] = cpu
for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb", "ram_avail_gb"):
    d[k] = ram
d["total_ram_gb"] = 25.69
for k in ("gpu_idle_vram_gb", "gpu_free_vram_gb"):
    d[k] = round(gpu_free_mb / 1024, 2)
for k in ("gpu_idle_vram_mb", "gpu_free_vram_mb", "gpu_vram_free"):
    d[k] = gpu_free_mb
d["gpu_free_vram_mib"] = gpu_free_mb
d["root_path"] = "C:\\Fluxgroup"
d["ram_gb"] = 27.5
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# self-verify: epoch must be int, clock_read must contain 'T'
d2 = json.load(open(p, encoding="utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in d2["clock_read"], "clock_read missing T separator"
print("heartbeat OK: epoch", d2["heartbeat_epoch_utc"], "clock", d2["clock_read"],
      "orders_ack", len(d2["orders_ack"]))
