# -*- coding: utf-8 -*-
# W228 prereg derive prep: dump machine values from n1_w227_results.json
# (r587 law: bands/facts machine-read, never eyeballed).
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
r = json.load(open(r"results\perpetual_faces\n1_w227_results.json", encoding="utf-8"))
led = r["science_gates"]["ledger"]
print("LEDGER total=%s prev=%s batch=%s" % (led["total"], led["prev_total"], led["batch_trials"]))
m = r["null_pool_cumulative"]["merged"]
print("MERGED n=%s mu=%r sigma=%r" % (m["n_values"], m["mu"], m["sigma"]))
o = r["null_pool_cumulative"]["w227_only"]
print("W227only mu=%r" % (o["mu"],))
print("DIFF=%s" % f"{abs(o['mu'] - m['mu']):.4f}")
print("A_p95=%r" % (r["families"]["A_random_engine_exit"]["full_sharpe_p95"],))
kl = r["skill_line_v2_k_lift"]
print("KL keys:", sorted(kl.keys()))
for k in sorted(kl.keys()):
    print("  KL[%s]=%r" % (k, kl[k]))
print("se_mu_at_k497320=%r" % (r["null_pool_cumulative"]["se_mu_at_k497320"],))
print("cutoff_meta=", r["science_gates"].get("cutoff_meta"))
print("evidence_cutoff=", r.get("evidence_cutoff"))
# formatted-string faces exactly as the derive script asserts them
def fmt8(x):
    return ("\u2212" if x < 0 else "") + f"{abs(x):.8f}"
print("fmt8 merged.mu =", fmt8(m["mu"]))
print("fmt8 w227only.mu =", fmt8(o["mu"]))
print("sigma .8 =", f"{m['sigma']:.8f}")
print("A_p95 .4 =", f"{r['families']['A_random_engine_exit']['full_sharpe_p95']:.4f}")
