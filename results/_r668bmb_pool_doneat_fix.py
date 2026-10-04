# r668 fix: pool entry done_at was future-stamped (estimate); set to real flip-window time
import json, io

p = "results/runnable_pool.json"
d = json.load(io.open(p, encoding="utf-8"))
e = [x for x in d["entries"] if x["id"] == "THEME-JUDGE-P1"][0]
assert e.get("done_at") == "2026-10-04T11:57:30+08:00", "unexpected done_at: %r" % e.get("done_at")
e["done_at"] = "2026-10-04T11:50:30+08:00"
with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
chk = json.loads(io.open(p, encoding="utf-8").read())
e2 = [x for x in chk["entries"] if x["id"] == "THEME-JUDGE-P1"][0]
assert e2["status"] == "done" and e2["done_at"] == "2026-10-04T11:50:30+08:00"
print("pool done_at normalized; entry reparse PASS")
