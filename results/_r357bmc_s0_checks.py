# r357 bm-c S0 helper: D-19 decisions raw-blob SHA + W61 shard-9/10 ownership audit.
# Laws: r292 (raw-bytes SHA, no PS pipeline transcoding), r503 (upper() normalize),
# r525 (audit.machine ownership gate before any product action).
import hashlib
import json
import os
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"

# 1) D-19: group decisions.md content-addressed watermark (raw blob bytes).
out = subprocess.check_output(
    ["git", "-C", GROUP, "show", "origin/main:docs/decisions.md"])
sha = hashlib.sha256(out).hexdigest().upper()
print("DEC_SHA=" + sha)

# 2) shard 9/10 ownership + identity (r525 gate before rescue push).
for shard in (9, 10):
    p = os.path.join(ROOT, "results", "p2cal_ext", "n1_w61",
                     "shard-%d-of-12.json" % shard)
    with open(p, "rb") as f:
        d = json.load(f)
    keys = sorted(d.keys())
    audit = d.get("audit", {})
    # robust key probes across runner schema variants
    n_cells = None
    for k in ("cells", "trials", "results", "rows"):
        v = d.get(k)
        if isinstance(v, list):
            n_cells = len(v)
            break
    print("SHARD%d keys=%s" % (shard, keys))
    print("SHARD%d audit=%s" % (shard, json.dumps(audit, ensure_ascii=False)[:300]))
    print("SHARD%d n_cells=%s wave=%s shard=%s" % (
        shard, n_cells, d.get("wave"), d.get("shard")))
