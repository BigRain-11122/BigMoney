# autofill_state conflict: r161 recipe (launches ts-union + last_tick newest)
import json, subprocess

def stage(n):
    return subprocess.run(["git", "show", f":{n}:results/autofill_state.json"],
                          capture_output=True).stdout.decode("utf-8-sig")

mine = json.loads(stage(3))   # my replayed commit (245f47ee)
orig = json.loads(stage(2))   # origin base (bm-a newest)
lo, lt = mine.get("launches", []), orig.get("launches", [])
seen = {}
for r in lo + lt:
    seen[(r.get("ts"), r.get("machine"), r.get("entry"), r.get("shard"), r.get("pid"))] = r
launches = sorted(seen.values(), key=lambda r: r.get("ts", ""))
cko, ckt = mine.get("last_tick", {}), orig.get("last_tick", {})
mine_newer = (cko.get("ts", "") or "") >= (ckt.get("ts", "") or "")
last_tick = cko if mine_newer else ckt
base = mine if mine_newer else orig
union = {k: v for k, v in base.items() if k not in ("launches", "last_tick")}
union["launches"] = launches
union["last_tick"] = last_tick
with open("results/autofill_state.json", "w", encoding="utf-8") as f:
    json.dump(union, f, ensure_ascii=False, indent=1)
print("launches", len(lo), "+", len(lt), "->", len(launches))
print("last_tick:", last_tick.get("ts"), last_tick.get("machine"),
      last_tick.get("entry", ""), last_tick.get("verdict"))
print("tail:", [(r["ts"], r["machine"], r.get("entry", ""), r.get("verdict"))
                for r in launches[-4:]])
