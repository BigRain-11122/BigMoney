# r424 bm-a fix: malformed NOW timestamp ("10:2%d" template trap, seconds=19 -> "10:219")
# correct all three faces with real localtime ISO-8601.
import json, time, io

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())
print("correct NOW:", NOW)

sp = "state-bm-a.json"
s = json.load(open(sp, encoding="utf-8"))
assert s["round_no"] == 424
bad = s.get("updated", "")
if "10:219" in bad or bad.count(":") != 3:
    s["updated"] = NOW
    json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("state updated fixed:", bad, "->", NOW)
else:
    print("state updated ok:", bad)

hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
for k in ("last_seen", "clock_read"):
    bad = h.get(k, "")
    assert isinstance(bad, str)
    if "10:219" in bad or bad.count(":") != 3:
        h[k] = NOW
        print("heartbeat", k, "fixed:", bad, "->", NOW)
h["heartbeat_epoch_utc"] = int(time.time())
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
back = json.load(open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int)
assert back["clock_read"].count(":") == 3 and "T" in back["clock_read"]
print("heartbeat epoch=%d int ok" % back["heartbeat_epoch_utc"])

rp = "logs/iteration-loop/round_reports-bm-a.md"
lines = io.open(rp, encoding="utf-8", newline="").read().splitlines(True)
hits = [i for i, l in enumerate(lines) if l.startswith("2026-09-29T10:2x:00+08:00 | r424 bm-a")]
assert len(hits) == 1, hits
i = hits[0]
lines[i] = lines[i].replace("2026-09-29T10:2x:00+08:00", NOW, 1)
io.open(rp, "w", encoding="utf-8", newline="").write("".join(lines))
back_line = io.open(rp, encoding="utf-8", newline="").read().splitlines(True)[i]
assert back_line.startswith(NOW) and "r424 bm-a" in back_line
print("round report ts fixed:", NOW)
