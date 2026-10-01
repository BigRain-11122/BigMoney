import json

r = json.load(open("results/lowamp_p2/lowamp_p2_results.json",
                   encoding="utf-8"))
print("top keys:", sorted(r.keys())[:18])
for k in ("batch", "verdict", "verdict_line", "evidence_cutoff",
          "exit_axis", "trials_ledger"):
    if k in r:
        v = r[k]
        print(k, "=", json.dumps(v, ensure_ascii=False)[:260])
gates = r.get("gates") or {}
if isinstance(gates, dict) and gates:
    k0 = list(gates)[:3]
    for k in k0:
        print("gate sample", k, ":",
              json.dumps(gates[k], ensure_ascii=False)[:300])
