"""r383 bm-c: extract exact W113-only mu/sigma + gate deltas for the prereg
SS7 mechanical backfill (values are read from the landed results file only)."""
import json

P = (r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces"
     r"\n1_w113_results.json")
with open(P, encoding="utf-8") as f:
    d = json.load(f)
npc = d["null_pool_cumulative"]
w = npc["w113_only"]
m = npc["merged"]
fa = d["families"]["A_random_engine_exit"]
print("w113_only mu:", repr(w["mu"]), "sigma:", repr(w["sigma"]),
      "n:", w["n_values"])
print("merged mu:", repr(m["mu"]), "sigma:", repr(m["sigma"]), "K:", m["n_values"])
print("A p95:", fa["full_sharpe_p95"], "p99:", fa["full_sharpe_p99"])
anchor_mu = -0.09276358334710065
anchor_sigma = 0.24489883563788295
anchor_p95 = 0.3191
print("gate1 |dmu| =", abs(w["mu"] - anchor_mu))
print("gate2 sigma pct =", (m["sigma"] - anchor_sigma) / anchor_sigma * 100)
print("gate3 A-p95 delta =", round(fa["full_sharpe_p95"] - anchor_p95, 4))
