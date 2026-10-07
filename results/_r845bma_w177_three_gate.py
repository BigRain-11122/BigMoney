# -*- coding: utf-8 -*-
"""r845 bm-a W177 three-gate receipt (r752 law, backfill window):
the r844 dead-tail adoption ran the three identity gates inline (round
report + state) but no receipt file landed -- this script re-runs the
gates machine-read from the on-disk shard files + finalize product and
writes results/_r845bma_w177_three_gate.json for the W177 prereg sec7
citation.  Zero-writes except the receipt; read-only on all inputs.
"""
import glob
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

shards = []
for p in sorted(glob.glob(r"results\p2cal_ext\n1_w177\shard-*-of-12.json"),
                key=lambda s: int(s.split("shard-")[1].split("-")[0])):
    shards.append(json.load(io.open(p, encoding="utf-8")))
assert len(shards) == 12, len(shards)

# gate 1: totals + per-shard audit==families parity
A_n = sum(s["families"]["A_random_engine_exit"]["n"] for s in shards)
B_n = sum(s["families"]["B_random_entry_random_exit"]["n"] for s in shards)
nb = sum(s["audit"]["n_backtests"] for s in shards)
per_shard_ok = all(
    s["audit"]["n_backtests"] ==
    s["families"]["A_random_engine_exit"]["n"] +
    s["families"]["B_random_entry_random_exit"]["n"] for s in shards)
assert A_n == 2000 and B_n == 200 and nb == 2200, (A_n, B_n, nb)
assert per_shard_ok, "per-shard audit != families"

# gate 2: seed continuity (unique + min/max machine-read)
A_seeds = [r["seed_rng"] for s in shards
           for r in s["families"]["A_random_engine_exit"]["runs"]]
B_exit = [r["seed_rng_exit"] for s in shards
          for r in s["families"]["B_random_entry_random_exit"]["runs"]]
B_entry = [r["seed_rng_entry"] for s in shards
           for r in s["families"]["B_random_entry_random_exit"]["runs"]]
assert len(A_seeds) == len(set(A_seeds)) == 2000, "A seeds not unique-2000"
assert min(A_seeds) == 404204 and max(A_seeds) == 406203, (min(A_seeds), max(A_seeds))
assert len(B_exit) == len(set(B_exit)) == 200, "B exit seeds not unique-200"
assert min(B_exit) == 406204 and max(B_exit) == 406403, (min(B_exit), max(B_exit))
assert len(B_entry) == len(set(B_entry)) == 200, "B entry seeds not unique-200"
assert min(B_entry) == 404204 and max(B_entry) == 404403, (min(B_entry), max(B_entry))

# gate 3: half-open contiguous tiling A[0,2000) B[0,200)
ar = sorted((s["a_range"][0], s["a_range"][1]) for s in shards)
br = sorted((s["b_range"][0], s["b_range"][1]) for s in shards)
assert ar[0][0] == 0 and ar[-1][1] == 2000, ar
for (a, b), (c, d) in zip(ar, ar[1:]):
    assert b == c, ("A tiling gap", a, b, c, d)
assert br[0][0] == 0 and br[-1][1] == 200, br
for (a, b), (c, d) in zip(br, br[1:]):
    assert b == c, ("B tiling gap", a, b, c, d)
assert sum(b - a for a, b in ar) == 2000 and sum(b - a for a, b in br) == 200

# finalize numbers (machine-read, r587)
res = json.load(io.open(r"results\perpetual_faces\n1_w177_results.json",
                        encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
fam = res["families"]["A_random_engine_exit"]
pre_mu = npc["pre_w177_cumulative"]["mu"]
mu4 = round(npc["merged"]["mu"], 6)

receipt = {
    "wave": 177,
    "machine": "bm-a",
    "round": "r845 (backfill window; gates first run inline at r844 "
             "dead-tail adoption -- this receipt = machine re-derive, "
             "values identical, honest provenance)",
    "law_ref": "pit r752 three-identity gates; r844 inline gates + this "
               "re-derive",
    "gate1_totals": {
        "A": A_n,
        "B": B_n,
        "n_backtests_sum": nb,
        "per_shard_audit_eq_families": per_shard_ok,
    },
    "gate2_seeds": {
        "A": "unique=2000 min=404204 max=406203",
        "B_exit": "unique=200 min=406204 max=406403",
        "B_entry": "unique=200 min=404204 max=404403",
    },
    "gate3_tiling": {
        "A": "[" + "),[".join("%d,%d" % r for r in ar) + ") half-open contiguous PASS",
        "B": "[" + "),[".join("%d,%d" % r for r in br) + ") half-open contiguous PASS",
    },
    "finalize": {
        "prev_total": 793105,
        "batch_trials": 2200,
        "total": 795305,
        "voids_applied": res.get("voids_applied"),
        "evidence_cutoff": res["evidence_cutoff"],
        "merged_k": npc["merged"]["n_values"],
        "merged_mu": npc["merged"]["mu"],
        "merged_sigma": npc["merged"]["sigma"],
        "w_only_mu": npc["w177_only"]["mu"],
        "w_only_sigma": npc["w177_only"]["sigma"],
        "pre_mu": pre_mu,
        "pre_sigma": npc["pre_w177_cumulative"]["sigma"],
        "mu_delta_w177_vs_w176ext": npc["mu_delta_w177_vs_w176ext"],
        "se_mu_at_k387320": npc["se_mu_at_k387320"],
        "skill_line_v2": {
            "n_eff_held_equal": kl["n_eff_held_equal"],
            "line_pre": kl["line_pre_w177"],
            "line_merged": kl["line_merged_387320"],
            "delta": kl["line_delta_k_lift"],
        },
        "A_p95": fam["full_sharpe_p95"],
        "A_p99": fam["full_sharpe_p99"],
        "canon_flip": kl["canon_flip"],
        "pred_keys": {
            "1_mu_gap": abs(npc["w177_only"]["mu"] - npc["merged"]["mu"]),
            "2_sigma_rel_pct": (npc["merged"]["sigma"] -
                                npc["pre_w177_cumulative"]["sigma"]) /
                               npc["pre_w177_cumulative"]["sigma"] * 100,
            "3_Ap95_delta_vs_w176": fam["full_sharpe_p95"] - 0.3118,
            "4_k_lift_delta": kl["line_delta_k_lift"],
        },
        "audit_finalize_only": res["audit"]["finalize_only"],
    },
    "generated_at": "2026-10-07T21:5x+08:00 (r845 backfill window)",
}
pk = receipt["finalize"]["pred_keys"]
assert pk["1_mu_gap"] < 0.02 and abs(pk["2_sigma_rel_pct"]) < 10 \
    and abs(pk["3_Ap95_delta_vs_w176"]) < 0.05 and abs(pk["4_k_lift_delta"]) <= 0.02, pk
out = json.dumps(receipt, ensure_ascii=False, indent=1)
io.open(r"results\_r845bma_w177_three_gate.json", "w", encoding="utf-8",
        newline="\n").write(out + "\n")
print("three-gate receipt written: results/_r845bma_w177_three_gate.json")
print("gate1", receipt["gate1_totals"])
print("gate2", receipt["gate2_seeds"])
print("pred_keys", {k: round(v, 6) for k, v in pk.items()})
print("ALL GATES PASS")
