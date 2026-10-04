# -*- coding: utf-8 -*-
# r663 bm-b push-race resolve step 1: full both-side face intersection since
# merge-base, classified per r437 ② law (regen snapshots -> checkout origin;
# pool faces -> checkout origin + sync_face settle after merge; append-only
# jsonl/round-reports -> union surgery if hit; lane single-writer -> ours).
import json, subprocess, io, os

def lines(cmd):
    p = subprocess.run(cmd, capture_output=True)
    return [l.strip() for l in p.stdout.decode("utf-8", "replace").splitlines() if l.strip()]

mb = lines(["git", "merge-base", "HEAD", "origin/main"])[0]
mine = set(lines(["git", "diff", "--name-only", mb, "HEAD"]))
theirs = set(lines(["git", "diff", "--name-only", mb, "origin/main"]))
inter = sorted(mine & theirs)

REGEN = []
POOL = []
APPEND_ONLY = []
OTHER = []
for f in inter:
    base = os.path.basename(f)
    if f.endswith("nulls.jsonl") or base.startswith("gate_attrition") or "round_reports" in f or f.endswith("CODELY.md"):
        APPEND_ONLY.append(f)
    elif base in ("runnable_pool.json", "crash_fuse.json"):
        POOL.append(f)
    elif f.endswith(".json") or f.endswith(".js") or f.endswith(".md"):
        REGEN.append(f)
    else:
        OTHER.append(f)

out = {"base": mb, "mine_n": len(mine), "theirs_n": len(theirs),
       "intersection": inter, "regen": REGEN, "pool": POOL,
       "append_only": APPEND_ONLY, "other": OTHER}
with io.open("results/_r663bmb_race_faces.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("intersection:", len(inter))
print("APPEND_ONLY (needs union, DO NOT checkout):", APPEND_ONLY)
print("POOL (checkout + settle):", POOL)
print("OTHER (review):", OTHER)
print("REGEN n:", len(REGEN))
