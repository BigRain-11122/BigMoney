import json, io, os, datetime
now = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
p = "state-bm-c.json"
d = json.load(io.open(p, encoding="utf-8"))
h = json.load(io.open(os.path.join("fleet","machines","bm-c.json"), encoding="utf-8"))
d["round_no"] = 1673
d["activity"] = "product"
d["activity_now"] = "CEO 页新增机队实况节：哪台机自己在写心跳、它管的车道现在谁在跑"
d["activity_now_round"] = 1673
for k in ("ts","clock_read","last_seen","heartbeat_epoch_utc","clock_read_source","clock_tz","ahead_origin","behind_origin"):
    if k in h: d[k] = h[k]
buf = json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True)
io.open(p, "w", encoding="utf-8", newline="\n").write(buf + "\n")
d2 = json.load(io.open(p, encoding="utf-8"))
print("state round_no", d2["round_no"], "ts", d2["ts"], "epoch_int", isinstance(d2.get("heartbeat_epoch_utc"), int))
