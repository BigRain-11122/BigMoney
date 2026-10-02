# -*- coding: utf-8 -*-
"""_r372bmc_w92_readout.py -- W92 finalize precise readout for prereg sec.7
backfill (W91 r579 receipt pattern). Read-only; prints selected fields from
results/perpetual_faces/n1_w92_results.json without loading run arrays into
stdout."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fp = os.path.join(ROOT, "results", "perpetual_faces", "n1_w92_results.json")
d = json.load(open(fp, encoding="utf-8"))
np_ = d["null_pool_cumulative"]
sk = d["skill_line_v2_k_lift"]
fam_a = d["families"]["A_random_engine_exit"]
out = {
    "w92_only": np_["w92_only"],
    "pre_w92_cumulative": np_["pre_w92_cumulative"],
    "merged": np_["merged"],
    "mu_delta_w92_vs_w91ext": np_.get("mu_delta_w92_vs_w91ext"),
    "se_mu_at_k200320": np_.get("se_mu_at_k200320"),
    "skill_line": {k: v for k, v in sk.items() if k != "formula"},
    "A_full_sharpe_p95": fam_a["full_sharpe_p95"],
    "A_full_sharpe_p99": fam_a["full_sharpe_p99"],
    "A_full_sharpe_mu": fam_a["full_sharpe_mu"],
    "ledger": d["science_gates"]["ledger"],
    "evidence_cutoff": d["evidence_cutoff"],
    "cutoff_meta": d["science_gates"]["cutoff_meta"]["evidence_cutoff"],
    "audit": d["audit"],
    "shards_consumed_n": len(d["shards_consumed"]),
}
print(json.dumps(out, ensure_ascii=False, indent=1))
