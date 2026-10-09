# -*- coding: utf-8 -*-
"""Check prediction (f): start-dist right-skew + rule-vs-dist-median."""
import json

import numpy as np

d = json.load(open("results/theme_deepen_p1/theme_deepen_p1.json", encoding="utf-8"))
rows = d["face2"]["by_wave"]
med_below_midrange = 0
rule_beats_dist_med = 0
n = 0
for r in rows:
    dist = r["start_dist"]
    if dist["n"] == 0 or dist["median"] is None:
        continue
    midrange = (dist["best"] + dist["worst"]) / 2.0
    if dist["median"] < midrange:
        med_below_midrange += 1
    n += 1
    if r["rule_net"] is not None and dist["median"] is not None \
            and r["rule_net"] > dist["median"]:
        rule_beats_dist_med += 1
print(f"waves with start-dist: {n}")
print(f"median < midrange (right-skew): {med_below_midrange} "
      f"({med_below_midrange / n:.1%})")
print(f"rule_net > dist median: {rule_beats_dist_med} "
      f"({rule_beats_dist_med / n:.1%})")
# W1 subset
w1 = [r for r in rows if r["pos"] == "W1"]
w1_beat = sum(1 for r in w1 if r["rule_net"] is not None
              and r["start_dist"]["median"] is not None
              and r["rule_net"] > r["start_dist"]["median"])
w1_n = sum(1 for r in w1 if r["rule_net"] is not None
           and r["start_dist"]["n"] > 0)
print(f"W1 rule beats dist median: {w1_beat}/{w1_n}")
