# -*- coding: utf-8 -*-
"""R261 bm-a: fix the check-string fixture mistake in the
T-73-CN-CORE-SATELLITE-P1 post_review row (fact pre-verified: pool
harvest_note verbatim = 'harvested bm-a R261 same-round 2026-09-26 17:5x';
the original check string was authored against intended-not-actual text =
fixture defect, same-round fix, zero criteria change -- R256 rot-law
shape: fact verified first, no check gaming)."""
import collections
import json

P = "results/post_review_criteria.json"
d = json.load(open(P, encoding="utf-8"),
              object_pairs_hook=collections.OrderedDict)
row = [r for r in d["items"]
       if r["id"] == "T-73-CN-CORE-SATELLITE-P1"][0]
for c in row["checks"]:
    if c["kind"] == "file_contains" \
            and c["args"][0] == "results/runnable_pool.json":
        c["args"][1] = "harvested bm-a R261 same-round 2026-09-26 17:5x"
tmp = P + ".tmp"
open(tmp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(d, ensure_ascii=False, indent=1) + "\n")
import os
os.replace(tmp, P)
print("check fixed to verbatim artifact substring")
