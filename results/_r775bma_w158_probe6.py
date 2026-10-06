# -*- coding: utf-8 -*-
import json
d = json.load(open(r"results\perpetual_faces\n1_w157_results.json", encoding="utf-8"))
np_ = d["null_pool_cumulative"]
for face in ("canon", "merged", "pre_w157_cumulative", "w157_only"):
    v = np_.get(face)
    print(face, "=>", json.dumps(v, ensure_ascii=False)[:600])
    print()
