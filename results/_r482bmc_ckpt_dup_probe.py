"""r482 bm-c: checkpoint duplicate-id hazard probe (double-burn union face).
Reads LOCAL checkpoint id multiset + ORIGIN blob via git show (subprocess raw
bytes, r660 law), reports per-id dupes and per-shard-range coverage."""
import json
import subprocess


def rows_from_blob(path):
    r = subprocess.run(["git", "show", "origin/main:" + path],
                       capture_output=True)
    if r.returncode != 0:
        return None
    ids = []
    for line in r.stdout.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                ids.append(json.loads(line)["id"])
            except Exception:
                pass
    return ids


local_ids = []
with open("results/mass_trial/w3_screen_checkpoint.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            local_ids.append(json.loads(line)["id"])

origin_ids = rows_from_blob("results/mass_trial/w3_screen_checkpoint.jsonl")

out = []
out.append("LOCAL rows %d unique %d" % (len(local_ids), len(set(local_ids))))
ldup = sorted({i for i in local_ids if local_ids.count(i) > 1})
out.append("LOCAL dup ids %d %s" % (len(ldup), ldup[:6]))
if origin_ids is None:
    out.append("ORIGIN blob: (not present)")
else:
    out.append("ORIGIN rows %d unique %d" % (len(origin_ids), len(set(origin_ids))))
    odup = sorted({i for i in origin_ids if origin_ids.count(i) > 1})
    out.append("ORIGIN dup ids %d %s" % (len(odup), odup[:6]))
    only_origin = sorted(set(origin_ids) - set(local_ids))
    only_local = sorted(set(local_ids) - set(origin_ids))
    out.append("ONLY_ORIGIN %d %s" % (len(only_origin), only_origin[:6]))
    out.append("ONLY_LOCAL %d %s" % (len(only_local), only_local[:6]))

# shard-range coverage from id position map (combined rows: cand ids order)
cand = json.load(open("results/mass_trial/w3_candidates.json", encoding="utf-8"))
cids = [r["id"] for r in cand["candidates"]]
pos = {cid: i for i, cid in enumerate(cids)}
cov = {"s0[0,1227)": 0, "s1[1227,2454)": 0, "s2[2454,3681)": 0, "s3[3681,4909)": 0,
       "other": 0}
for i in local_ids:
    if i in pos:
        p = pos[i]
        if p < 1227:
            cov["s0[0,1227)"] += 1
        elif p < 2454:
            cov["s1[1227,2454)"] += 1
        elif p < 3681:
            cov["s2[2454,3681)"] += 1
        else:
            cov["s3[3681,4909)"] += 1
    else:
        cov["other"] += 1
out.append("LOCAL coverage by id-position: %s" % json.dumps(cov))
# non-candidate rows (DEF-*/NULL-*) live in 'other' + are expected at the
# control/null burn phase (their positions are appended after candidates)
n_ctrl_null = cov["other"]
out.append("CTRL+NULL rows so far: %d (expect 95 when all 4 shards done)" % n_ctrl_null)

open("results/_r482bmc_ckpt_dup_probe_out.txt", "w",
     encoding="utf-8").write("\n".join(out) + "\n")
print("PROBE_DONE")
