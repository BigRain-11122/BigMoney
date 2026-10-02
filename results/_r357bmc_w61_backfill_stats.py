# r357 bm-c: extract W61 finalize stats block for prereg s7 mechanical backfill
# (derive-not-copy, r307 same-window law). Reads n1_w61_results.json only.
import json

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w61_results.json"
d = json.load(open(P, encoding="utf-8"))
print("top_keys =", sorted(d.keys()))
for k in ("stats", "s5", "merge", "merged", "mu", "sigma", "a_p95",
          "k_lift", "skill_line", "ledger", "audit", "k", "n_trials",
          "evidence_cutoff", "cutoff_meta", "voids"):
    if k in d:
        print(k, "=", json.dumps(d[k], ensure_ascii=False)[:600])
# nested probe for stats-like dicts
for k, v in d.items():
    if isinstance(v, dict) and any(s in str(v)[:400] for s in
                                   ("mu", "sigma", "p95")):
        print("NESTED", k, "=", json.dumps(v, ensure_ascii=False)[:700])
