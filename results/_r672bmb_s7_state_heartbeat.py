import json, io, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

now = datetime.datetime.now()
iso = now.isoformat(timespec="seconds") + "+08:00"
epoch = int(time.time())

# --- state.json: round_no +1, timestamps (programmatic write + json.loads self-verify, r645 law) ---
sp = ROOT + r"\state.json"
d = json.load(io.open(sp, encoding="utf-8"))
assert d.get("machine_id") == "bm-b", "identity anchor: state.json machine_id != bm-b"
d["round_no"] = 672
d["round_no_label"] = "r672"
d["last_round_at"] = iso
d["ts"] = iso
d["updated"] = iso
d["last_seen"] = iso
d["clock_read"] = iso
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
d2 = json.loads(io.open(sp, encoding="utf-8").read())
assert d2["round_no"] == 672 and isinstance(epoch, int)
print("state.json r672 written + reparse OK")

# --- heartbeat fleet/machines/bm-b.json: epoch int + T-form clock (R170/R178/R262 laws) ---
hp = ROOT + r"\fleet\machines\bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["round_no"] = 672
h["current_task"] = ("r672: trio NULLS burn watch (V/Q/D ~38/30/22pct, ETA 10-06/07/08) "
                     "+ S6 38/38 golden-week + finalize rehearsal re-run (MSG-1720 fix verify)")
h["cpu_cores"] = 16
h["verdict"] = "healthy burning"
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
h2 = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"] and ":" in h2["clock_read"]
print("heartbeat written: epoch=%d clock=%s" % (h2["heartbeat_epoch_utc"], h2["clock_read"]))
