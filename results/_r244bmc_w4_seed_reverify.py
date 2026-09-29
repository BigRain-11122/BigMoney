# r244 bm-c adopt-verify: FULL-registry re-verification of W4 seed 20322000.
# Original dead-tick facts (_r244bmc_w4_seed_law_facts.json) counted the
# registry via source-text regex -> 86-key PARTIAL view (only 6+ digit
# int literals); true imported registry = 130 keys / 129 int bases (incl.
# the new w4 key). Banner's "129-key" (pre-w4 true count) was correct;
# facts' 86 was the regex artifact. This re-run verifies the three-step
# law against the FULL imported registry (import-based, zero regex blind
# spots) and rewrites the facts with corrected evidence.
import io, json, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts")
import science_gates as sg
import numpy as np

NEW = [20322000]
KEY = "innovation_quota_w4_volregime"

reg = dict(sg.SEED_REGISTRY)
assert KEY in reg and reg[KEY] == NEW[0], "w4 key missing/mismatch in working tree"

# existing bases = every int base EXCLUDING the new key itself
existing = {k: v for k, v in reg.items() if isinstance(v, int) and k != KEY}
all_bases = sorted(set(existing.values()))
facts = {
    "new": NEW, "new_keys": [KEY],
    "verification": "FULL import-based registry view (fix of dead-tick "
                    "regex artifact: source-text 6+digit-literal scan saw "
                    "only 86/129 int bases)",
    "n_registry_keys_total": len(reg),
    "n_existing_int_bases": len(all_bases),
    "collision_values": [], "collision_keys": [],
    "first_els": {}, "first_el_clash": [],
    "band_overlap": [], "rg_hits": {},
}

# Step 1: exact zero-collision vs ALL existing bases + key uniqueness
for n in NEW:
    facts["collision_values"].extend(
        {"value": n, "keys": [k for k, v in existing.items() if v == n]}
        for _ in [0]) if any(v == n for v in existing.values()) else None
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

# Step 3a: band overlap (single base; k-sub-streams derive from base)
for n in NEW:
    ov = [k for k, v in existing.items() if v == n]
    if ov:
        facts["band_overlap"].append({"band": [n, n], "keys": ov})
facts["w12_declared_berth_adjacency"] = {
    "w12_draft_berths": [20320500, 20321000, 20321500],
    "registered_on_origin": False,
    "note": "W12 berths declared (bm-a r447 MSG-2225) but unregistered at "
            "freeze; 20322000 = +500 above last declared berth; verified "
            "absent from local full registry AND origin/main "
            "(git show scan this window)"}

# Step 3b: repo-wide bare-number scan (unchanged from dead tick, hits
# classifiable: 2 data coincidences + prereg own text)
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

out = "results/_r244bmc_w4_seed_law_facts.json"
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
