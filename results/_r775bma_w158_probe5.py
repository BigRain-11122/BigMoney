# -*- coding: utf-8 -*-
import json
d = json.load(open(r"results\perpetual_faces\n1_w157_results.json", encoding="utf-8"))
np_ = d.get("null_pool_cumulative", {})
print("null_pool keys:", sorted(np_.keys()))
for k in sorted(np_.keys()):
    v = np_[k]
    if isinstance(v, (int, float, str)):
        print(k, "=", v)
print("skill_line_v2_k_lift:", d.get("skill_line_v2_k_lift"))
sg = d.get("science_gates", {})
print("science_gates keys:", sorted(sg.keys()) if isinstance(sg, dict) else sg)
audit = d.get("audit", {})
print("audit keys:", sorted(audit.keys()) if isinstance(audit, dict) else audit)
