"""r752 three-constant-equivalence gate for W167 burn products (pre-commit absorb gate).

Gate 1: n1 selftest (registration face) -- run separately by caller.
Gate 2: shard totals famA==2000 / famB==200 across 12 shards (prereg N slots exact).
Gate 3: cross-shard seed continuity: full-band no-gap sweep
        A entry seeds: unique==2000, min==382204, max==384203, contiguous
        B entry seeds: unique==200, == first 200 of A band (382204..382403)
        B exit seeds : unique==200, min==384204, max==384403, contiguous
Writes receipt results/_r806bma_w167_three_gate.json (PASS/FAIL verdict).
"""
import json, glob, os, sys

SHARD_DIR = "results/p2cal_ext/n1_w167"
A_LO, A_HI = 382204, 384203
B_EXIT_LO, B_EXIT_HI = 384204, 384403
N_A, N_B = 2000, 200
receipt = {"gate": "r752 three-constant-equivalence", "wave": 167, "shards": {}, "verdict": None}

shard_files = sorted(glob.glob(os.path.join(SHARD_DIR, "shard-*.json")),
                     key=lambda p: int(p.split("shard-")[1].split("-")[0]))
assert len(shard_files) == 12, f"expected 12 shards, found {len(shard_files)}"

tot_a = tot_b = 0
a_entry, b_entry, b_exit = set(), set(), set()
per_shard = []
for p in shard_files:
    d = json.load(open(p, encoding="utf-8"))
    fam = d["families"]
    fa, fb = fam["A_random_engine_exit"], fam["B_random_entry_random_exit"]
    tot_a += fa["n"]; tot_b += fb["n"]
    for r in fa["runs"]:
        a_entry.add(r["seed_rng"])
    for r in fb["runs"]:
        b_entry.add(r["seed_rng_entry"]); b_exit.add(r["seed_rng_exit"])
    per_shard.append({"shard": d["shard"], "a": fa["n"], "b": fb["n"],
                       "machine": d["audit"].get("machine")})
    assert d["audit"].get("machine") == "bm-a", f"shard {d['shard']} not bm-a"

gate2 = (tot_a == N_A and tot_b == N_B)
exp_a = set(range(A_LO, A_HI + 1))
exp_b_entry = set(range(A_LO, A_LO + N_B))
exp_b_exit = set(range(B_EXIT_LO, B_EXIT_HI + 1))
gate3 = (a_entry == exp_a and b_entry == exp_b_entry and b_exit == exp_b_exit)

receipt["shard_totals"] = {"A": tot_a, "B": tot_b}
receipt["gate2_totals"] = "PASS" if gate2 else "FAIL"
receipt["gate3_continuity"] = {
    "a_entry_unique": len(a_entry), "a_min": min(a_entry), "a_max": max(a_entry),
    "b_entry_unique": len(b_entry), "b_exit_unique": len(b_exit),
    "b_exit_min": min(b_exit), "b_exit_max": max(b_exit),
    "verdict": "PASS" if gate3 else "FAIL",
}
receipt["per_shard"] = per_shard
receipt["verdict"] = "PASS" if (gate2 and gate3) else "FAIL"
json.dump(receipt, open("results/_r806bma_w167_three_gate.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("gate2 (totals A/B):", tot_a, "/", tot_b, "->", receipt["gate2_totals"])
print("gate3 (continuity):", receipt["gate3_continuity"])
print("VERDICT:", receipt["verdict"])
sys.exit(0 if receipt["verdict"] == "PASS" else 1)
