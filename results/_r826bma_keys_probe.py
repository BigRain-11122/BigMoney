import json

res = json.load(open(r"results/perpetual_faces/n1_w174_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
for k in ("pre_w174_cumulative", "w174_only", "merged"):
    d = npc[k]
    print(k, "n=", d["n_values"], "mu=%.6f" % d["mu"], "sigma=%.6f" % d["sigma"])
for k, v in npc.items():
    if "se_mu" in str(k):
        print("se key:", k, "=", v)
kl = res["skill_line_v2_k_lift"]
print("kl:", json.dumps(kl))
fam = res["families"]["A_random_engine_exit"]
print("fam: n=", fam["n"], "p95=", fam["full_sharpe_p95"], "p99=", fam["full_sharpe_p99"],
      "mu=%.6f" % fam["full_sharpe_mu"])
print("sec5:", {k: v for k, v in res["science_gates"].items() if k != "ledger"})
print("ledger:", res["science_gates"]["ledger"])
print("audit:", res["audit"], "shards:", len(res["shards_consumed"]), "cutoff:", res["evidence_cutoff"])
print("cutoff_meta:", res.get("cutoff_meta"))
