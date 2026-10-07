# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
res = json.load(open(r"results/perpetual_faces/n1_w172_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
for k in ("pre_w172_cumulative", "w172_only", "merged"):
    v = npc[k]
    print(k, "n_values=", v["n_values"], "mu=", f"{v['mu']:.6f}", "sigma=", f"{v['sigma']:.6f}")
print("se_mu key:", [k for k in npc if "se_mu" in k], "value:", npc.get("se_mu_at_k376320"))
print("LEDGER:", res["science_gates"]["ledger"])
print("KL:", res["skill_line_v2_k_lift"])
fam = res["families"]["A_random_engine_exit"]
print("FAM A:", {k: fam[k] for k in ("n", "full_sharpe_p95", "full_sharpe_p99", "full_sharpe_mu") if k in fam})
print("AUDIT:", res.get("audit"), "shards:", len(res.get("shards_consumed", [])), "cutoff:", res["evidence_cutoff"])
w171 = json.load(open(r"results/perpetual_faces/n1_w171_results.json", encoding="utf-8"))
fam171 = w171["families"]["A_random_engine_exit"]
print("W171 fam p95 (prior key):", fam171["full_sharpe_p95"])
wonly = npc["w172_only"]
mu171 = w171["null_pool_cumulative"]["w171_only"]["mu"]
print("mu_delta_w172_vs_w171ext:", f"{wonly['mu'] - mu171:+.6f}")
# sec5 four keys machine-judged
pre, merged = npc["pre_w172_cumulative"], npc["merged"]
d1 = abs(wonly["mu"] - merged["mu"])
d2 = (merged["sigma"] - pre["sigma"]) / pre["sigma"] * 100
d3 = fam["full_sharpe_p95"] - fam171["full_sharpe_p95"]
d4 = res["skill_line_v2_k_lift"]["line_delta_k_lift"]
print("sec5 keys: d1=%.4f d2=%+.4f%% d3=%+.4f d4=%+.4f" % (d1, d2, d3, d4))
print("KL keys:", {k: res["skill_line_v2_k_lift"][k] for k in res["skill_line_v2_k_lift"]})
