import json
d = json.load(open("results/runnable_pool.json", encoding="utf-8"))
for e in d.get("entries", []):
    if e.get("id") == "DECISION-CHAIN-V3-TOURNAMENT":
        print(json.dumps(e, ensure_ascii=False, indent=1)[:2200])
print("=== verdict receipt key fields ===")
v = json.load(open("results/decision_chain_v3_tournament.json", encoding="utf-8"))
for k in ("verdict", "n_eff", "winners", "seed", "evidence_cutoff", "generated",
          "arms", "ledger", "trials_ledger"):
    if k in v:
        s = json.dumps(v[k], ensure_ascii=False)
        print(k, "=", s[:300])
print("top_keys=", sorted(v.keys()))
