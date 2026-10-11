import json, time, datetime
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+" if now.utcoffset() >= datetime.timedelta(0) else "-") + now.strftime("%H:%M")
epoch = int(time.time())

# state round_no +1
sp = "state-bm-c.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 883
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# heartbeat
hp = r"fleet\machines\bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = iso
h["current_task"] = "W18 shard-0 screen burn in-flight (pid 46804, autofill-relit) + r883 S0 rebase/relay closeout"
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["ts"] = iso
h["verdict"] = "green-idle (RAM 2.2G free; shard-0 burn ramping; watermark insufficient_history transitional)"
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# verify epoch is int
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("state round_no=883; heartbeat epoch:", epoch, "iso:", iso, "| epoch-type:", type(chk["heartbeat_epoch_utc"]).__name__)
