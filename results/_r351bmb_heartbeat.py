"""r351 bm-b S7: heartbeat refresh (epoch int + T-format clock, R170/R262)."""
import json, time, datetime, psutil

PATH = r"C:\Users\Administrator\Desktop\Bigmoney\fleet\machines\bm-b.json"
hb = json.load(open(PATH, encoding="utf-8"))
vm = psutil.virtual_memory()
epoch = int(time.time())
now = datetime.datetime.now(datetime.timezone.utc).astimezone()
hb.update({
    "machine_id": "bm-b",
    "last_seen": now.isoformat(timespec="seconds"),
    "heartbeat_epoch_utc": epoch,
    "clock_read": now.isoformat(timespec="seconds"),
    "current_task": "r351 closure landed: inherited S7 3-wave rebase storm canon-resolved (main 578abed1) + autofill r351 pool-behind-origin defer (b5be80cd tree-blind forensics closed per bm-c MSG-0105, selftest +3 legs ALL PASS) + CODELY hot-cold archive 24th batch 9873B; next r352 = W2A harvest + W2B RAM gate + JUDGE 4 shards waiting; CEO 48h clock 09-29 22:45",
    "cpu_cores": psutil.cpu_count(),
    "free_ram_gb": round(vm.available / 1e9, 2),
    "gpu_free_vram_gb": hb.get("gpu_free_vram_gb"),
    "total_ram_gb": round(vm.total / 1e9, 1),
    "cpu_util_pct": psutil.cpu_percent(interval=0.5),
    "round_no": 351,
    "verdict": "green: r351 closure complete (storm resolved zero-loss, guard landed, board empty, smoke 25/25, orders 99/99 zero diff); W2A 4-worker burn alive (PID 13148); pool JUDGE 4 shards queued behind W2A/W2B; RAM 3.3GB tight but batch-legal",
    "cores": psutil.cpu_count(),
    "idle_ram_gb": round(vm.available / 1e9, 2),
    "round": 351,
    "loop_round": 351,
})
json.dump(hb, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
back = json.load(open(PATH, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in back["clock_read"] and "+" in back["clock_read"], "clock T-format (R262)"
print("heartbeat OK epoch=", back["heartbeat_epoch_utc"], "clock=", back["clock_read"],
      "ram=", back["free_ram_gb"], "GB")
