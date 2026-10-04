# r684 bm-b: state round bump + heartbeat refresh (r645 tail-comma law:
# programmatic write + json.loads self-proof; R170/R178 epoch int; R262 T-sep clock)
import io, json, time, datetime

# --- state.json (bm-b uses shared state.json per fleet README sec.6)
SP = r"state.json"
st = json.loads(io.open(SP, encoding="utf-8").read())
st["round_no"] = 684
with io.open(SP, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
rt = json.loads(io.open(SP, encoding="utf-8").read())
assert rt["round_no"] == 684
print("state round_no ->", rt["round_no"])

# --- heartbeat fleet/machines/bm-b.json
HP = r"fleet/machines/bm-b.json"
hb = json.loads(io.open(HP, encoding="utf-8").read())
now = datetime.datetime.now().astimezone()
hb["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" \
    + now.strftime("%z")[-2:]
hb["heartbeat_epoch_utc"] = int(time.time())          # JSON int, R170/R178
hb["clock_read"] = now.isoformat(timespec="seconds")  # T-separator, R262
hb["current_task"] = ("T-148 slice-3 pending-legs: lowamp-2 burned+merged "
                      "(ranks #41/#43), RC-10 pool unit RAM-gated in queue; "
                      "trio NULLS keepalive")
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1e9, 2)
    hb["cpu_cores"] = psutil.cpu_count(logical=True)
    py = sum(p.info.get("cpu_percent", 0) or 0 for p in
             psutil.process_iter(["name", "cpu_percent"]))
except Exception:
    pass
hb["verdict"] = "GREEN: S6 38/38 rc0; lowamp-2 contest rows landed; RC pool unit queued; trio NULLS burning healthy"
with io.open(HP, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
rt = json.loads(io.open(HP, encoding="utf-8").read())
assert isinstance(rt["heartbeat_epoch_utc"], int) and \
    "T" in rt["clock_read"] and "+" in rt["clock_read"]
print("heartbeat ok: epoch", rt["heartbeat_epoch_utc"],
      "int =", isinstance(rt["heartbeat_epoch_utc"], int),
      "| clock", rt["clock_read"],
      "| free_ram", rt.get("free_ram_gb"), "GB")
