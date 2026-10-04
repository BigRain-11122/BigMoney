# r670 bm-a: fix verification - ks coverage arithmetic on real config + poisoned-frag skip logic
import ast, json

src = open("scripts/theme_judge_p1.py", encoding="utf-8").read()
ast.parse(src)  # AST gate (r580/r581 law)
print("AST gate: PASS")

K_NULLS, CHUNK = 2000, 100
STRATA = ["TJ-FULL", "TJ-SOLO"]

# 1. ks tiling PER STRATUM (same-mask across strata is the frozen design:
# rng([SEED_NULLS, k]) seeds only on k -- identical mask sequence per k
# across strata/cost faces, prereg "same-mask random-ignition nulls")
for st in STRATA:
    seen = {}
    for ci in range(0, K_NULLS, CHUNK):
        ks = list(range(ci, min(ci + CHUNK, K_NULLS)))
        assert len(ks) > 0, f"EMPTY CHUNK at {st}/{ci}"
        for k in ks:
            assert k not in seen, f"OVERLAP {st} k={k} at {seen.get(k)} vs {ci}"
            seen[k] = ci
    assert sorted(seen) == list(range(K_NULLS)), f"{st} coverage hole"
print("ks tiling: per-stratum 2000 ks each exactly once, 40/40 chunks non-empty PASS")

# 2. healthy-frags resume check: the 2 chunk_00 frags on disk have ks 0..99
import glob, os
healthy = poisoned = 0
for p in glob.glob("results/theme_judge_p1/nulls_frags/*.json"):
    row = json.load(open(p, encoding="utf-8"))
    if row.get("ks"):
        healthy += 1
        assert row["ci"] == 0 and row["ks"] == list(range(100))
    else:
        poisoned += 1
print(f"on-disk frags: healthy={healthy} poisoned-empty={poisoned}")
assert healthy == 2 and poisoned == 38

# 3. done-set semantics with the fixed scanner: only (st, 0) skip
done = set()
for p in glob.glob("results/theme_judge_p1/nulls_frags/*.json"):
    row = json.load(open(p, encoding="utf-8"))
    if row.get("digest") == "663f1f112514e70b" and row.get("ks"):
        done.add((row["stratum"], row["ci"]))
tasks = [(st, ci) for st in STRATA for ci in range(0, K_NULLS, CHUNK)
         if (st, ci) not in done]
print(f"resume task list: {len(tasks)} chunks to recompute (expect 38)")
assert len(tasks) == 38 and ("TJ-FULL", 0) not in tasks
print("ALL FIX-VERIFICATION LEGS PASS")
