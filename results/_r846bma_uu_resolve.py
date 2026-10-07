# r846 bm-a: resolve rebase UU on results/compute_audit.json
# Law: rolling-ledger ts-key union (r819/r825/r829 bloodline). Rebase stage labels:
#   :2: = base side (origin/new base), :3: = replayed side (my churn absorb). r840 errata applied.
# Top-level scalars: side with fresher last-history ts wins; history: ts-key union zero-loss, sorted.
import json, subprocess, sys

PATH = "results/compute_audit.json"

def stage_blob(spec):
    b = subprocess.run(["git", "show", spec], capture_output=True).stdout
    return json.loads(b.decode("utf-8", errors="strict"))

base = stage_blob(":2:" + PATH)   # origin side
mine = stage_blob(":3:" + PATH)    # my churn side

bh = base.get("history", [])
mh = mine.get("history", [])
def last_ts(h):
    return h[-1].get("ts", "") if h else ""

# ts-key union: row identity = ts (rolling ledger), conflict same-ts -> deeper dict max-merge not needed (rows immutable snapshots)
seen = {}
for row in bh + mh:
    ts = row.get("ts", "")
    if ts not in seen:
        seen[ts] = row
union = [seen[k] for k in sorted(seen.keys())]

winner = base if last_ts(bh) >= last_ts(mh) else mine
out = dict(winner)
out["history"] = union
out["_r846_union_note"] = "rebase UU resolved ts-key union L2=%d L3=%d -> %d zero-loss" % (len(bh), len(mh), len(union))

with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("RESOLVED history %d+%d -> %d, winner=%s" % (len(bh), len(mh), len(union), "base(:2:)" if last_ts(bh) >= last_ts(mh) else "mine(:3:)"))
