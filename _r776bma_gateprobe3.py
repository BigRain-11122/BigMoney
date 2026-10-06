# -*- coding: utf-8 -*-
"""Max seed band check for new theme_deepen_p1 band allocation."""
import json
import sys

sys.path.insert(0, "scripts")
import science_gates  # noqa: E402

sr = science_gates.SEED_REGISTRY
pairs = []
for k, v in sr.items():
    if isinstance(v, int):
        pairs.append((v, k))
pairs.sort()
for v, k in pairs[-10:]:
    print(v, k)
print("MAX BAND:", pairs[-1][0])
# check candidate band 20595000 and 20600000 for overlap
vals = set(v for v, _ in pairs)
for cand in (20595000, 20600000, 20590000):
    overlaps = [x for x in vals if abs(x - cand) < 10000]
    print("cand", cand, "near(overlap<10k):", overlaps)
