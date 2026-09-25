# r201: autofill_state 3-source union (r161 recipe + worktree extension)
# context: r200 session's rebase stopped UU; 20:00:01 tick overwrote WT file with
# fresh state (marker parse fail -> fresh default), so WT now holds the ONLY copy of
# the 20:00:01 SHARD-2 launch record (pid 14112). Union stages + WT, last_tick newest.
import json, subprocess

def stage(n):
    return subprocess.run(["git", "show", f":{n}:results/autofill_state.json"],
                          capture_output=True).stdout.decode("utf-8-sig")

mine = json.loads(stage(3))   # my replayed commit (245f47ee side)
orig = json.loads(stage(2))   # origin base (bm-a 8009faf5 side)
with open("results/autofill_state.json", encoding="utf-8") as f:
    cur = json.load(f)        # post-conflict tick write (20:00:01 SHARD-2 launch)
sources = [mine, orig, cur]

seen = {}
for src in sources:
    for r in src.get("launches", []):
        assert r.get("ts") and r.get("machine"), f"launch record missing key fields: {r}"
        seen[(r.get("ts"), r.get("machine"), r.get("entry"), r.get("shard"), r.get("pid"))] = r
launches = sorted(seen.values(), key=lambda r: r.get("ts", ""))

ticks = [s.get("last_tick") or {} for s in sources]
last_tick = max(ticks, key=lambda t: t.get("ts", ""))
base = next(s for s in sources if (s.get("last_tick") or {}) is last_tick)

union = {k: v for k, v in base.items() if k not in ("launches", "last_tick")}
for s in (mine, orig):  # fill any top-level keys WT-fresh write may have dropped
    for k, v in s.items():
        if k not in ("launches", "last_tick") and k not in union:
            union[k] = v
union["launches"] = launches
union["last_tick"] = last_tick

out = json.dumps(union, ensure_ascii=False, indent=1)
json.loads(out)  # round-trip validation (r185: parse-validate BEFORE write-back)
for line in out.splitlines():
    assert not line.startswith(("<<<<<<<", "=======", ">>>>>>>")), "marker line present"

with open("results/autofill_state.json", "w", encoding="utf-8") as f:
    f.write(out)
print("launches", [len(s.get("launches", [])) for s in sources], "->", len(launches))
print("last_tick:", last_tick.get("ts"), last_tick.get("machine"),
      last_tick.get("entry", ""), last_tick.get("verdict"))
print("tail:", [(r["ts"], r["machine"], r.get("entry", ""), r.get("verdict"))
                for r in launches[-4:]])
