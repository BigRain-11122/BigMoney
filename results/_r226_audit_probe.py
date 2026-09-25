# -*- coding: utf-8 -*-
import json
d = json.load(open("results/shortline/p1e_zoo_behavior.json", encoding="utf-8"))
print("meta.universe:", d["meta"]["universe"])
print("meta.mask_disclosure:", d["meta"]["mask_disclosure"][:150])
print("multiplicity:", d["meta"]["multiplicity"][:120])
print("audit.elapsed_s:", d["audit"]["elapsed_s"])
print("audit.coverage:")
for k, v in d["audit"]["coverage"].items():
    print("  ", k, v)
print("h20 crossers (pass at h20):",
      [r["factor"] for r in d["rows"] if r.get("h20_pass")])
print("h5 pass:", [r["factor"] for r in d["rows"] if r.get("h5_pass")])
print("v1 thr per member h10:",
      {r["factor"]: round(r["h10_v1_thr"], 4) for r in d["rows"]})
print("oos retention stv/coin_team:",
      [(r["factor"], round(abs(r["h10_oos_ic"] / r["h10_is_ic"]), 3))
       for r in d["rows"] if r["in_pool"]])
