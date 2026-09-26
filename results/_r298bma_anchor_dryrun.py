import json

P = "results/fusion_grid_p1/p1_results.json"
d = json.load(open(P, encoding="utf-8"))
probes = [
    ("batch",), ("evidence_cutoff",),
    ("trials_ledger", "total"), ("trials_ledger", "batch_trials"), ("trials_ledger", "prev_total"),
    ("skill_line", "line"), ("skill_line", "n_eff"), ("skill_line", "mu_null"), ("skill_line", "sigma_null"),
    ("family_pbo", "pbo"),
    ("cells", "EW__DEDUP", "sharpe_full"), ("cells", "EW__DEDUP", "g1_pass_v2"),
    ("cells", "EW__DEDUP", "eligible_v2"), ("cells", "EW__DEDUP", "dsr"),
    ("cells", "EW__ALL32", "sharpe_full"), ("cells", "EW__ALL32", "g1_pass_v2"),
    ("cells", "REGIME_COND__TOP2", "sharpe_full"),
    ("cells", "INV_MDD__ALL32", "sharpe_full"),
    ("nulls", "K"), ("nulls", "coverage", "n_values"),
    ("audit", "elapsed_sec"), ("audit", "workers"),
    ("baselines_descriptive", "ew48_passive", "sharpe"),
]
for path in probes:
    v = d
    try:
        for k in path:
            v = v[k]
        print("#" + ".".join(path), "=", repr(v))
    except Exception as ex:
        print("#" + ".".join(path), "ERROR", ex)
