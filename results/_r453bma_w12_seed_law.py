# r453 bm-a W12 freeze-step seed law three-step re-verifier (r441 bm-b precedent, verbatim pattern)
# Seeds berth (draft sec.5 clause): 20320500/20321000/20321500 (natural +500 lineage from W11 20317000/20317500/20318000)
# Drafting-time tail-read max=20320000; freeze-time live-read must re-verify (non-historical, live).
# Step 1: int-base exact collision (values + digit keys) == zero
# Step 2: first elements (numpy default_rng(s).integers(0,2**31)) mutual-distinct among new, and vs all existing bases
# Step 3: derivation-band overlap check (scrnull band +0..+199, unc band +0..+200, gen no derived face)
import json, os, re, sys, subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from science_gates import SEED_REGISTRY  # live-read, import truth (r244 law: never regex-count source)

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NEW = [20320500, 20321000, 20321500]
NEW_KEYS = ["trial_labor_w12_gen", "trial_labor_w12_scrnull", "trial_labor_w12_unc"]

def as_int(v):
    try:
        return int(str(v).strip())
    except Exception:
        return None

bases = {}
for k, v in SEED_REGISTRY.items():
    iv = as_int(v)
    if iv is not None:
        bases.setdefault(iv, []).append(str(k))

collision_values = [b for b in NEW if b in bases]
collision_keys = [k for k in SEED_REGISTRY if as_int(SEED_REGISTRY.get(k)) in NEW]

import numpy as np
def first_el(s):
    return int(np.random.default_rng(s).integers(0, 2**31))

new_first = {str(s): first_el(s) for s in NEW}
existing_first = {}
for b in bases:
    existing_first[b] = first_el(b)
new_set = set(new_first.values())
first_el_clash = sorted({b for b in existing_first if existing_first[b] in new_set})
new_first_els_mutual_distinct = len(new_set) == len(NEW)

# Step 3: bands
bands_new = {
    "trial_labor_w12_scrnull": [NEW[1] + i for i in range(200)],
    "trial_labor_w12_unc": [NEW[2] + i for i in range(201)],
}
band_overlap = []
for name, band in bands_new.items():
    for b in bases:
        if b in band:
            band_overlap.append({"band": name, "hits_base": b, "keys": bases[b]})
# also new-gen base itself must not sit inside any new derived band
if NEW[0] in bands_new["trial_labor_w12_scrnull"] or NEW[0] in bands_new["trial_labor_w12_unc"]:
    band_overlap.append({"band": "gen-base-inside-derived", "hits_base": NEW[0]})

# rg repo-wide text hits classification (context classification, not collision)
rg_hits = {}
for s in NEW:
    try:
        out = subprocess.run(
            ["rg", "-n", "--no-heading", str(s), ROOT, "-g", "!*.pyc", "-g", "!results/_r453bma_w12_seed_law*"],
            capture_output=True, text=True, timeout=60)
        lines = [l.replace(ROOT + os.sep, "").replace(ROOT + "/", "") for l in out.stdout.splitlines() if l.strip()]
        rg_hits[str(s)] = [l[:160] for l in lines[:6]]
    except Exception as e:
        rg_hits[str(s)] = ["rg-error: %s" % e]

facts = {
    "new": NEW,
    "new_keys": NEW_KEYS,
    "collision_values": collision_values,
    "collision_keys": collision_keys,
    "first_els": new_first,
    "first_el_clash": first_el_clash,
    "band_overlap": band_overlap,
    "rg_hits": rg_hits,
    "new_first_els_mutual_distinct": new_first_els_mutual_distinct,
    "verdict_step1_zero_collision": len(collision_values) == 0 and len(collision_keys) == 0,
    "verdict_step2_distinct": new_first_els_mutual_distinct and len(first_el_clash) == 0,
    "verdict_step3_bands_clean": len(band_overlap) == 0,
    "n_registry_keys": len(SEED_REGISTRY),
    "n_int_bases": len(bases),
    "max_registered_seed": max(bases) if bases else None,
    "drafting_time_tail_max_delta": {
        "draft_claim": 20320000,
        "freeze_live_max": max(bases) if bases else None,
        "delta_source": "20322000 = innovation_quota_w4_volregime (bm-c r245 W4 SLOT-4, post-draft arrival)",
        "collision_status": "non-colliding (three W12 seeds all < 20322000 and outside any band)",
    },
}
dst = os.path.join(ROOT, "results", "_r453bma_w12_seed_law_facts.json")
with open(dst, "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print(json.dumps({k: facts[k] for k in ["verdict_step1_zero_collision", "verdict_step2_distinct", "verdict_step3_bands_clean", "n_registry_keys", "max_registered_seed"]}, ensure_ascii=False))
print("ALL GREEN" if (facts["verdict_step1_zero_collision"] and facts["verdict_step2_distinct"] and facts["verdict_step3_bands_clean"]) else "FAIL -- DO NOT FREEZE")
