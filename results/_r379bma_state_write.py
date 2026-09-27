import io, json, datetime

p = r"state-bm-a.json"
d = json.load(io.open(p, encoding="utf-8"))
prev = d.get("round_no")
d["round_no"] = 379
d["round"] = 379
d["loop_round"] = 379
d["ts"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(d, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# read-back self-proof (r128 law: S7 single-write face verified same-window)
d2 = json.load(io.open(p, encoding="utf-8"))
assert d2["round_no"] == 379, d2["round_no"]
assert isinstance(d2["round_no"], int)
print(f"state write-back verified: round_no {prev} -> {d2['round_no']} (int)")
