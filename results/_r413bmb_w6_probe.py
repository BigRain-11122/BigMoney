import json, glob, os, collections
d = json.load(open("results/runnable_pool.json", encoding="utf-8"))
for e in d.get("entries", []):
    if e.get("id") == "TRIAL-LABOR-W6-SCREEN":
        print(json.dumps(e, ensure_ascii=False, indent=1)[:2500])
print("== trial_labor_w6 dir ==")
for f in sorted(glob.glob("results/trial_labor_w6/**/*", recursive=True)):
    print(f, os.path.getsize(f))
print("== checkpoint distinct cell count ==")
seen = set()
fams = collections.Counter()
n = 0
with open("results/trial_labor_w6/checkpoint/screen_shard_0of1.jsonl", encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        n += 1
        seen.add(r.get("cell_id"))
        fams[r.get("family")] += 1
print("rows:", n, "distinct cell_id:", len(seen))
print("families:", dict(fams))
