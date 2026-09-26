"""R263 residue-adoption verify: real FAM_PREV audit-face lengths vs h4 fix
(days 3333 -> expects n-1 = 3332 per producer NaN-head-drop convention)."""
import json
import re

src = open("scripts/cn_core_ddctl_p1.py", encoding="utf-8").read()
path = "results/cn_core_satellite/p1_results.json"
print("FAM_PREV_JSON =", path)
d = json.load(open(path, encoding="utf-8"))
a = d.get("judged_x2_returns_6dp_audit")
assert isinstance(a, dict) and a, "audit face missing"
lens = {k: len(v) for k, v in a.items()}
print("cells:", sorted(lens))
print("unique lens:", sorted(set(lens.values())))
expect = 3332
bad = {k: n for k, n in lens.items() if n != expect}
print("VERDICT:", "ALL n-1=3332, h4 fix aligned" if not bad else f"MISMATCH {bad}")
