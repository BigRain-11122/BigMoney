# -*- coding: utf-8 -*-
"""r119 rebase conflict resolution: runnable_pool.json structural union
(r344/r360 laws: |A u B| by id, no cap truncation; HEAD side = fresher
bm-b r350 commits for common entries; my side's unique = the 2 new
DECISION-CHAIN-V2 entries)."""
import json, re

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\runnable_pool.json"
src = open(P, encoding="utf-8").read()
m = re.search(
    r"<<<<<<< HEAD\n(.*?)\n\|\|\|\|\|\|\| [^\n]*\n(.*?)\n=======\n(.*?)"
    r"\n>>>>>>> [^\n]*", src, re.S)
assert m, "diff3 conflict markers not found"
head_raw, base_raw, mine_raw = m.group(1), m.group(2), m.group(3)
pre = src[:m.start()]
post = src[m.end():]
assert pre.strip() == "", "unexpected pre-conflict content"
assert post.strip() == "", ("unexpected post-conflict content: "
                             + repr(post[:80]))
C = json.loads(base_raw)       # merge base (81 entries)

A = json.loads(head_raw)       # bm-b r350 side (base)
B = json.loads(mine_raw)       # my 34e27c6b side
ea, eb = A["entries"], B["entries"]
ida = {e["id"]: e for e in ea}
idb = {e["id"]: e for e in eb}
idc = {e["id"] for e in C["entries"]}
print("HEAD entries:", len(ea), "| mine entries:", len(eb),
      "| base entries:", len(C["entries"]))

union = list(ea)               # HEAD side first (fresher for common)
added = []
for e in eb:
    if e["id"] not in ida:
        union.append(e)
        added.append(e["id"])
print("added from mine:", added)
# drift audit vs merge base: zero entry loss tolerated (r344/r360 laws)
lost_head = [i for i in idc if i not in ida]
lost_mine = [i for i in idc if i not in idb]
print("base ids absent in HEAD:", lost_head)
print("base ids absent in mine:", lost_mine)
assert not lost_head and not lost_mine, "entry loss vs merge base -- abort"

out = dict(A)                  # keep HEAD's top-level fields (version/law etc.)
mine_keys = {k for k in B if k not in ("entries",)}
for k in mine_keys:            # union the top-level meta too (updated_at freshest)
    if k not in out or k in ("updated_at", "_stamp_note"):
        out[k] = B[k]
out["entries"] = union
json.dumps(out, ensure_ascii=False)
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("union written:", len(union), "entries")
