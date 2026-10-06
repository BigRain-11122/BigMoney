# -*- coding: utf-8 -*-
# r653 bm-c push-claw surgery probe: compare shared pool faces HEAD vs origin
import subprocess, json, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args):
    p = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True)
    return p.stdout.decode("utf-8", "replace")

head = git("rev-parse", "HEAD").strip()
origin = git("rev-parse", "origin/main").strip()
ahead = git("rev-list", "--count", "origin/main..HEAD").strip()
behind = git("rev-list", "--count", "HEAD..origin/main").strip()
print("HEAD=%s origin=%s ahead=%s behind=%s" % (head[:12], origin[:12], ahead, behind))

def pool(blob_ref):
    s = git("show", "%s:results/runnable_pool.json" % blob_ref)
    return json.loads(s)

for ref in ("origin/main", "HEAD"):
    d = pool(ref)
    ents = d.get("entries", [])
    hits = [(e.get("id"), e.get("status"), str(e.get("owner_since"))[:19], e.get("owner"))
            for e in ents if e.get("id") in ("FUND-QUALITY-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS")
            or "TRIAL-LABOR" in str(e.get("id"))]
    print(ref, "n_entries=%d" % len(ents), hits)

# deletions my unpushed range would carry vs origin tip
d = git("diff", "--diff-filter=D", "--name-only", "origin/main...HEAD")
print("deletions(merge-base range):", [x for x in d.split() if x])
d2 = git("diff", "--diff-filter=D", "--name-only", "origin/main..HEAD")
print("deletions(two-dot range):", [x for x in d2.split() if x])
