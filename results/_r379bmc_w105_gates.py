# r379 W105 finalize gate check + value extraction (for SS7/SS8 backfill)
import json
d = json.load(open("results/perpetual_faces/n1_w105_results.json", encoding="utf-8"))
npc = d["null_pool_cumulative"]
w105 = npc["w105_only"]
merged = npc["merged"]
pre = npc["pre_w105_cumulative"]
famA = d["families"]["A_random_engine_exit"]
p95 = famA["full_sharpe_p95"]
kl = d["skill_line_v2_k_lift"]
led = d["science_gates"]["ledger"]
# frozen anchors (W99 keys per prereg S5)
A_MU, A_SIG, A_P95 = -0.09282891108844799, 0.24492323649678793, 0.3262
g1 = abs(w105["mu"] - merged["mu"])
g2 = (merged["sigma"] - A_SIG) / A_SIG * 100.0
g3 = p95 - A_P95
g4 = kl["line_delta_k_lift"]
print("w105_only  mu=%.17g sigma=%.17g n=%d" % (w105["mu"], w105["sigma"], w105["n_values"]))
print("merged     mu=%.17g sigma=%.17g K=%d" % (merged["mu"], merged["sigma"], merged["n_values"]))
print("pre        mu=%.17g sigma=%.17g K=%d" % (pre["mu"], pre["sigma"], pre["n_values"]))
print("A_p95=%.4f p99=%.4f se_mu=%s" % (p95, famA["full_sharpe_p99"], npc.get("se_mu_at_k228920")))
print("kl:", json.dumps(kl, ensure_ascii=False)[:400])
print("ledger:", json.dumps(led, ensure_ascii=False)[:400])
print("mu_delta_w105_vs_w104ext=", npc.get("mu_delta_w105_vs_w104ext"))
print("audit:", json.dumps(d.get("audit"), ensure_ascii=False))
print("evidence_cutoff=", d.get("evidence_cutoff"), "cutoff_meta=", d.get("science_gates", {}).get("cutoff_meta", {}).get("evidence_cutoff"))
print("shards_consumed=", len(d.get("shards_consumed") or []))
print("GATE1 |dmu|=%.6f <0.02 -> %s" % (g1, "PASS" if g1 < 0.02 else "FAIL"))
print("GATE2 sigma_rel=%.4f%% within +-10 -> %s" % (g2, "PASS" if abs(g2) < 10 else "FAIL"))
print("GATE3 A_p95 diff=%+.4f abs<0.05 -> %s" % (g3, "PASS" if abs(g3) < 0.05 else "FAIL"))
print("GATE4 K-lift=%+.4f >=-0.02 -> %s" % (g4, "PASS" if g4 >= -0.02 else "FAIL"))
