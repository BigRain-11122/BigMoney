# -*- coding: utf-8 -*-
import json
d = json.load(open("results/shortline/p1e_zoo_behavior.json", encoding="utf-8"))
print("pool_h10:", d["pool_h10"])
print("counts:", d["counts"])
print("null p95 thresholds:")
for cls, t in d["thresholds"].items():
    print(" ", cls, {h: round(t[h]["p95_abs_ic"], 4) for h in ("h5", "h10", "h20")})
print()
for r in d["rows"]:
    g = r.get("gates", {})
    detail = {k: g.get(k) for k in ("v1", "v2", "v3", "a3") if k in g}
    print("%-16s mask=%-10s h10: ic=%+.4f ir=%+.3f n=%d thr=%.4f oos=%+.4f pass=%s h5=%s h20=%s in_pool=%s"
          % (r["factor"], r["mask_class"], r["h10_is_ic"], r["h10_is_ir"],
             r["h10_is_n"], r["h10_v1_thr"], r["h10_oos_ic"],
             r["h10_pass"], r["h5_pass"], r["h20_pass"], r["in_pool"]))
    print("    gates:", json.dumps(detail))
    print("    coverage: is_valid_cells=%s share=%s" %
          (r.get("is_valid_cells"), r.get("is_valid_cell_share")))
print()
print("ledger:", json.dumps(d["trials_ledger"]))
print("equiv:", json.dumps(d.get("equivalence"))[:200])
print("meta.seed_band:", d["meta"]["seed_band"])
print("mask_classes note keys:", list(d["nulls_meta"].keys()))
for cls, m in d["nulls_meta"].items():
    print(" ", cls, "mask_cells=", m["mask_cells"], "seed_band=", m["seed_band"])
