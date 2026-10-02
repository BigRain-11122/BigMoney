# r357 bm-c: extract W62 finalize stats for prereg s7 mechanical backfill.
import json

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w62_results.json"
d = json.load(open(P, encoding="utf-8"))
npc = d["null_pool_cumulative"]
print("pre_w62 mu=%.6f sigma=%.8f n=%d" % (
    npc["pre_w62_cumulative"]["mu"], npc["pre_w62_cumulative"]["sigma"],
    npc["pre_w62_cumulative"]["n_values"]))
print("w62_only mu=%.6f sigma=%.8f n=%d" % (
    npc["w62_only"]["mu"], npc["w62_only"]["sigma"], npc["w62_only"]["n_values"]))
print("merged mu=%.6f sigma=%.8f n=%d" % (
    npc["merged"]["mu"], npc["merged"]["sigma"], npc["merged"]["n_values"]))
print("mu_delta_w62_vs_w61ext=%s" % npc.get("mu_delta_w62_vs_w61ext"))
print("se_mu_at_k134320=%s" % npc.get("se_mu_at_k134320"))
fam = d["families"]["A_random_engine_exit"]
print("A_p95=%.4f A_p99=%.4f A_mu=%.5f" % (
    fam["full_sharpe_p95"], fam["full_sharpe_p99"], fam["full_sharpe_mu"]))
print("k_lift=", json.dumps(d["skill_line_v2_k_lift"], ensure_ascii=False)[:300])
print("audit=", json.dumps(d["audit"], ensure_ascii=False))
print("se_mu_pre=%s" % npc.get("se_mu_at_k132120"))
