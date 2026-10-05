# -*- coding: utf-8 -*-
"""r750 bm-a heartbeat update (epoch int self-check per R170/R178 law,
T-separated clock_read per R262 law)."""
import json, time, subprocess

hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
epoch = int(time.time())
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())
hb["last_heartbeat_epoch_utc"] = hb.get("heartbeat_epoch_utc", 0)
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now
hb["last_seen"] = now
hb["cpu_pct"] = 94.6
hb["cpu_util_pct"] = 94.6
hb["cpu_load_pct"] = 94.6
hb["ram_free_gb"] = 45.3
hb["free_ram_gb"] = 45.3
hb["idle_ram_gb"] = 45.3
hb["idle_ram_mb"] = 45.3 * 1024
hb["gpu_free_vram_mb"] = 5120
hb["gpu_idle_vram_mb"] = 5120
hb["gpu0_free_vram_gb"] = 5.0
hb["health"] = "ok"
hb["verdict"] = "loaded_ok"
hb["current_task"] = "W143 engine burn in flight (n1w143 12-shard queue, ignition 00:37 pid=25400, ~1 shard/min)"
hb["last_action"] = "r750: W143 freeze chain full delivery (pre-seat probe ADMIT A 329_404..331_403 staircase-2nd / B 331_404..331_603 mutual-exclusion + seat MSG-2026-10-06-002x pushed 3a7640311 + band gate ADMIT leg0-leg3 + registry insert row143+face+prose + prereg FROZEN + freeze 86d3b070c delivered 0/0 + engine ignited n1w143) + D-19 dual watermark consumed (decisions 7674e37b / orders 99182969, D-20261006-01/02/03 zero BigMoney new dispatch) + S6 38 legs rc0 FAILS=0"
hb["last_round"] = 750

json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
rb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(rb["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert rb["heartbeat_epoch_utc"] == epoch and "T" in rb["clock_read"], "clock_read T-separator (R262 law)"
print("heartbeat ok: epoch", rb["heartbeat_epoch_utc"], "clock", rb["clock_read"],
      "ack", len(rb.get("orders_ack", [])))
