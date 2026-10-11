import json, time, datetime
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # 2026-10-11T18:xx:xx+0800
iso = iso[:-2] + ":" + iso[-2:]            # +08:00
epoch = int(time.time())
hp = r"fleet\machines\bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
h["clock_read"] = iso
h["ts"] = iso
h["last_seen"] = iso
h["heartbeat_epoch_utc"] = epoch
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("fixed clock_read/ts/last_seen:", iso, "| epoch:", chk["heartbeat_epoch_utc"])
