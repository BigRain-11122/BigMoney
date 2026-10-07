# -*- coding: utf-8 -*-
"""r826 bm-a W174 three-constant-equivalence receipt (r752 law bloodline,
W173 r823 precedent): shard_totals gate (A 2000 / B 200) + continuity gate
(entry/exit rng uniqueness + machine-read band ranges from the 12/12
shards). Receipt -> results/_r826bma_w174_three_gate.json."""
import json

A, B = [], []
per = []
for k in range(12):
    s = json.load(open(rf"results/p2cal_ext/n1_w174/shard-{k}-of-12.json",
                       encoding="utf-8"))
    af = s["families"]["A_random_engine_exit"]["runs"]
    bf = s["families"]["B_random_entry_random_exit"]["runs"]
    A.extend(r["seed_rng"] for r in af)
    B.extend((r["seed_rng_entry"], r["seed_rng_exit"]) for r in bf)
    per.append({"shard": k, "a": len(af), "b": len(bf),
                "machine": s["audit"]["machine"]})
b_entry = [t[0] for t in B]
b_exit = [t[1] for t in B]
g2 = (len(A) == 2000 and len(B) == 200)
g3 = (len(set(A)) == 2000 and min(A) == 397604 and max(A) == 399603
      and len(set(b_entry)) == 200 and len(set(b_exit)) == 200
      and min(b_exit) == 399604 and max(b_exit) == 399803)
receipt = {
    "gate": "r752 three-constant-equivalence",
    "wave": 174,
    "shard_totals": {"A": len(A), "B": len(B)},
    "gate2_totals": "PASS" if g2 else "FAIL",
    "gate3_continuity": {
        "a_entry_unique": len(set(A)), "a_min": min(A), "a_max": max(A),
        "b_entry_unique": len(set(b_entry)),
        "b_exit_unique": len(set(b_exit)),
        "b_exit_min": min(b_exit), "b_exit_max": max(b_exit),
        "verdict": "PASS" if g3 else "FAIL",
    },
    "per_shard": per,
    "bands_src": ("results/_r823bma_w174_probe_receipt.json ADMIT "
                   "(A 397604..399603 / B-exit 399604..399803)"),
    "verdict": "PASS" if (g2 and g3) else "FAIL",
}
json.dump(receipt, open(r"results/_r826bma_w174_three_gate.json", "w",
                        encoding="utf-8"), indent=1, ensure_ascii=False)
print("three-gate verdict:", receipt["verdict"],
      "A:", len(A), "B:", len(B),
      "a_range", min(A), "..", max(A),
      "b_exit_range", min(b_exit), "..", max(b_exit))
assert receipt["verdict"] == "PASS"
