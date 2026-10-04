# -*- coding: utf-8 -*-
# r705 bm-b merge resolver: single UU results/crash_fuse.json
# (churn-absorbed local daemon face vs origin bm-a autofill 12-judge
# keepalive commit 5e9da3930). Policy = r701 lineage resolve_token
# (per-key union, ts newer-wins, tie->theirs r440, CRLF producer format).
# Sides read by rev (HEAD/MERGE_HEAD), not by stage index (merge-mode
# swapped-stage pit avoided per r701-pit3 law).
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r701bmb_merge_resolve as R

PATH = "results/crash_fuse.json"
ours = R.show("HEAD", PATH)
theirs = R.show("MERGE_HEAD", PATH)
assert ours is not None and theirs is not None, "missing side"
data, side = R.resolve_token(ours, theirs)
assert data.count(b"<<<<<<<") == 0 and data.count(b">>>>>>>") == 0
merged = json.loads(data)          # reparse gate (fail-closed)

# face-level evidence: which top keys came in new from theirs
o_keys = set(json.loads(ours))
t_keys = set(json.loads(theirs))
print("side_pick=%s" % (side,))
print("ours-only keys: %s" % sorted(o_keys - t_keys))
print("theirs-new keys: %s" % sorted(t_keys - o_keys))
with open(PATH, "wb") as f:
    f.write(data)
json.dump({"face": PATH, "method": "r701-lineage resolve_token per-key union",
           "side_pick": side, "ours_sha": None, "theirs_rev": "MERGE_HEAD",
           "ours_new_keys": sorted(o_keys - t_keys),
           "theirs_new_keys": sorted(t_keys - o_keys)},
          open("results/_r705bmb_merge_resolve.json", "w"), indent=1)
print("RESOLVED %s" % PATH)
