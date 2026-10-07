"""r860 bm-a: fix TRIAL-LABOR-W16-JUDGE runner_args (single comma string ->
proper 5-element list) in BOTH pool faces (shared + bm-a lane mirror).

Root cause: submit --runner-args passed a comma-joined string; submit
stored it as a 1-element list; the launcher passed one argv element ->
argparse instant-exit (honest zero-burn, checkpoint untouched).
Raw-text surgical edit per pool-edit law + json.loads round-trip gate.
"""
import json

OLD = '"runner_args": [\r\n    "judge,--shard,0,--shards,1"\r\n   ]'
NEW = ('"runner_args": [\r\n    "judge",\r\n    "--shard",\r\n'
       '    "0",\r\n    "--shards",\r\n    "1"\r\n   ]')

for path in (r"results/runnable_pool.json",
             r"results/runnable_pool.bm-a.json"):
    raw = open(path, encoding="utf-8", newline="").read()
    n = raw.count(OLD)
    assert n == 1, f"{path}: expected 1 occurrence, found {n}"
    fixed = raw.replace(OLD, NEW)
    d = json.loads(fixed)                      # round-trip gate
    ents = d["entries"] if isinstance(d.get("entries"), list) else []
    e = next(x for x in ents if x.get("id") == "TRIAL-LABOR-W16-JUDGE")
    assert e["runner_args"] == ["judge", "--shard", "0", "--shards", "1"]
    assert e["shards"][0]["key"] == "w16-judge-0of1"
    assert e["shards"][0]["status"] == "ready"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(fixed)
    d2 = json.loads(open(path, encoding="utf-8").read())   # post-write gate
    e2 = next(x for x in d2["entries"] if x.get("id") == "TRIAL-LABOR-W16-JUDGE")
    assert e2["runner_args"] == ["judge", "--shard", "0", "--shards", "1"]
    print(f"FIXED {path} | entries={len(d2['entries'])} | args OK")
print("receipt: both faces fixed, round-trip + post-write gates PASS")
