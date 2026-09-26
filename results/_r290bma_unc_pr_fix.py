# -*- coding: utf-8 -*-
"""R290 bm-a fixup: the T-86-S3 criteria check for uncert_summary.n_ic_p_le_0.05
is unaddressable via dotted json_field paths (the key itself contains a dot ->
path parser splits it). Replace that one check with a file_contains anchor on
the same value; product stays byte-stable (no post-hoc criteria tailoring --
same value, same file, mechanical path-format fix only)."""
import io
import json

P = "results/post_review_criteria.json"
d = json.load(io.open(P, encoding="utf-8"))
items = d["items"]

row = None
for it in items:
    if it.get("id") == "T-86-S3-CENSUS-FUS-UNC":
        row = it
        break
assert row is not None, "criteria row missing"

fixed = 0
for c in row["checks"]:
    if c["kind"] == "json_field" and c["args"][1] == "uncert_summary.n_ic_p_le_0.05":
        c["kind"] = "file_contains"
        c["args"] = ["results/census_fusion_s2/w1_unc.json",
                     '"n_ic_p_le_0.05": 2203']
        fixed += 1
assert fixed == 1, f"expected exactly 1 broken check, fixed {fixed}"

with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("criteria check fixed (file_contains anchor); re-run reviewer to re-derive")
