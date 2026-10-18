# r1100 bm-c: dump W271 finalize full-precision five-key anchor faces (r587 law)
import json


def _find_ledger(obj):
    if isinstance(obj, dict):
        if 'ledger' in obj and isinstance(obj['ledger'], dict) \
                and 'total' in obj['ledger']:
            return obj['ledger']
        for v in obj.values():
            r = _find_ledger(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_ledger(v)
            if r:
                return r
    return None


w271 = json.load(open("results/perpetual_faces/n1_w271_results.json", encoding="utf-8"))
p1 = w271["null_pool_cumulative"]
s1 = w271["skill_line_v2_k_lift"]
f1 = w271["families"]["A_random_engine_exit"]
out = {
    "merged_mu": p1["merged"]["mu"],
    "merged_sigma": p1["merged"]["sigma"],
    "merged_n": p1["merged"]["n_values"],
    "w271_only_mu": p1["w271_only"]["mu"],
    "se_mu_at_k594120": p1["se_mu_at_k594120"],
    "line_merged_594120": s1["line_merged_594120"],
    "line_pre_w271": s1["line_pre_w271"],
    "line_delta_k_lift": s1["line_delta_k_lift"],
    "a_p95": f1["full_sharpe_p95"],
    "a_p99": f1["full_sharpe_p99"],
    "ledger_total": _find_ledger(w271)["total"],
}
print(json.dumps(out, indent=1))
