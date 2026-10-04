"""r486 bm-c SHARD-2 origin-state probe (r483 补翻四连律① fetch+实核):
- origin/main runnable_pool.json W3-JUDGE family statuses
- origin/main runnable_pool.bm-a.json (lane view) SHARD-2 face detail
- origin ls-tree w3_judge_shard_2of4.jsonl presence
- local shard-2 product presence + row count
Raw bytes via subprocess (r660), zero console CJK, output to file."""
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
OUT = os.path.join(REPO, "results", "_r486bmc_shard2_origin_check.txt")
lines = []


def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, cwd=REPO,
                       creationflags=CNW)
    return r.returncode, r.stdout


rc, out = git("fetch", "origin")
lines.append("fetch rc=%d" % rc)

rc, blob = git("show", "origin/main:results/runnable_pool.json")
pool = json.loads(blob.decode("utf-8"))
fam = {e["id"]: e for e in pool["entries"]
       if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
lines.append("origin pool entries=%d" % len(pool["entries"]))
for eid in sorted(fam):
    e = fam[eid]
    s = e["shards"][0]
    lines.append("origin %s entry=%s shard=%s owner=%s done_at=%s harvest_by=%s"
                 % (eid, e.get("status"), s.get("status"), s.get("owner"),
                    s.get("done_at"), s.get("harvested_by")))

rc, lblob = git("show", "origin/main:results/runnable_pool.bm-a.json")
if rc == 0:
    lane = json.loads(lblob.decode("utf-8"))
    lfam = {e["id"]: e for e in lane.get("entries", [])
            if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
    e2 = lfam.get("MASS-TRIAL-W3-JUDGE-SHARD-2", {})
    s2 = (e2.get("shards") or [{}])[0]
    lines.append("bm-a lane SHARD-2: entry=%s shard=%s owner=%s owner_since=%s done_at=%s done_by=%s harvest=%s"
                 % (e2.get("status"), s2.get("status"), s2.get("owner"),
                    s2.get("owner_since"), s2.get("done_at"), e2.get("done_by"),
                    s2.get("harvest_claim")))
else:
    lines.append("bm-a lane view read fail rc=%d" % rc)

rc, tree = git("ls-tree", "origin/main", "results/mass_trial/")
names = [l.split("\t")[-1] for l in tree.decode("utf-8").splitlines()]
lines.append("origin has shard2 product: %s"
             % ("results/mass_trial/w3_judge_shard_2of4.jsonl" in
                ["results/mass_trial/" + n for n in names]))
for n in sorted(names):
    if "w3_judge" in n:
        lines.append("origin w3_judge file: %s" % n)

local2 = os.path.join(REPO, "results", "mass_trial", "w3_judge_shard_2of4.jsonl")
if os.path.exists(local2):
    n = sum(1 for l in open(local2, encoding="utf-8") if l.strip())
    lines.append("local shard2 product rows=%d" % n)
else:
    lines.append("local shard2 product: MISSING")

for i in range(4):
    p = os.path.join(REPO, "results", "mass_trial", "w3_judge_shard_%dof4.jsonl" % i)
    n = sum(1 for l in open(p, encoding="utf-8") if l.strip()) if os.path.exists(p) else -1
    lines.append("local shard%d rows=%d" % (i, n))

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))
print("WROTE", OUT)
