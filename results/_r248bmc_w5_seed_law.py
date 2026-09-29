# r248 bm-c freeze window: three-step seed law live re-verification for
# W5 ICU_MA_TIMING_P1 seed 20322500 (FULL import-based registry view per
# r244 pitfall law -- source-text regex counting is forbidden: it sees
# only 6+-digit int literals and misses imported/aliased bases).
# Step 1: zero exact collision vs ALL existing int bases + key uniqueness.
# Step 2: NPCG first-element distinctness vs ALL existing bases.
# Step 3: band clean (identical base = identical band; k-sub-streams
#         derive from the base) + repo-wide bare-number scan classifiable.
import io, json, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts")
import science_gates as sg
import numpy as np

NEW = [20322500]
KEY = "innovation_quota_w5_icu_ma"

reg = dict(sg.SEED_REGISTRY)
assert KEY in reg and reg[KEY] == NEW[0], "w5 key missing/mismatch in working tree"

# existing bases = every int base EXCLUDING the new key itself
existing = {k: v for k, v in reg.items() if isinstance(v, int) and k != KEY}
all_bases = sorted(set(existing.values()))
facts = {
    "new": NEW, "new_keys": [KEY],
    "verification": "FULL import-based registry view (r244 pitfall law: "
                    "no source-text regex counting; import SEED_REGISTRY "
                    "whole-dict view)",
    "n_registry_keys_total": len(reg),
    "n_existing_int_bases": len(all_bases),
    "collision_values": [], "collision_keys": [],
    "first_els": {}, "first_el_clash": [],
    "band_overlap": [], "rg_hits": {},
}

# Step 1: exact zero-collision vs ALL existing bases + key uniqueness
for n in NEW:
    hits = [k for k, v in existing.items() if v == n]
    if hits:
        facts["collision_values"].append({"value": n, "keys": hits})
if KEY in existing:
    facts["collision_keys"].append(KEY)

# Step 2: NPCG first-element distinctness vs ALL existing bases
def first_el(s):
    return int(np.random.default_rng(s).integers(0, 2 ** 31))
existing_els = {b: first_el(b) for b in all_bases}
for n in NEW:
    facts["first_els"][str(n)] = first_el(n)
    fe = facts["first_els"][str(n)]
    for b, be in existing_els.items():
        if fe == be:
            facts["first_el_clash"].append({"new": n, "first_el": fe,
                                             "clashes_base": b})
facts["new_first_els_mutual_distinct"] = \
    len(set(facts["first_els"][str(n)] for n in NEW)) == len(NEW)

# Step 3a: band overlap (identical base = identical band; k-sub-streams
# derive from base, so only an exact base re-use is a band collision;
# adjacent ladders use disjoint bases by construction)
for n in NEW:
    ov = [k for k, v in existing.items() if v == n]
    if ov:
        facts["band_overlap"].append({"band": [n, n], "keys": ov})
facts["ladder_adjacency"] = {
    "w4_registered_base": 20322000,
    "w12_trio_registered": [20320500, 20321000, 20321500],
    "note": "20322500 = +500 above W4 20322000; W12 trio registered "
            "bm-b r444 before this window (present in imported view, "
            "zero-collision verified above); k-sub-stream ranges "
            "[20322500, 20322500+3100) derive from a base distinct "
            "from every other family's base (tuple-keyed streams)",
}

# Step 3b: repo-wide bare-number scan (hits must be classifiable)
for n in NEW:
    r = subprocess.run(["git", "grep", "-n", "-F", str(n), "--", "."],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    facts["rg_hits"][str(n)] = [l for l in r.stdout.splitlines() if l.strip()]

facts["verdict_step1_zero_collision"] = (not facts["collision_values"]) \
    and (not facts["collision_keys"])
facts["verdict_step2_distinct"] = (not facts["first_el_clash"]) \
    and facts["new_first_els_mutual_distinct"]
facts["verdict_step3_bands_clean"] = not facts["band_overlap"]

out = "results/_r248bmc_w5_seed_law_facts.json"
io.open(out, "w", encoding="utf-8").write(
    json.dumps(facts, ensure_ascii=False, indent=1))
print("FULL registry view: total keys", facts["n_registry_keys_total"],
      "| existing int bases", facts["n_existing_int_bases"])
print("step1 zero-collision:", facts["verdict_step1_zero_collision"])
print("step2 first-el distinct:", facts["verdict_step2_distinct"],
      "| new first_el", facts["first_els"])
print("step3 bands clean:", facts["verdict_step3_bands_clean"],
      "| rg hits", {k: len(v) for k, v in facts["rg_hits"].items()})
print("ALL GREEN" if (facts["verdict_step1_zero_collision"]
                      and facts["verdict_step2_distinct"]
                      and facts["verdict_step3_bands_clean"]) else "NOT GREEN")
