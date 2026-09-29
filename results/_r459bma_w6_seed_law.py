# -*- coding: utf-8 -*-
"""_r459bma_w6_seed_law.py -- three-step seed law live re-verification for
INNOVATION-QUOTA-SLOT-6 RRG_ROTATION_P1 seed 20324500 (r459 bm-a freeze
window; FULL import-based registry view per r244 pitfall law -- source-text
regex counting is forbidden: it sees only 6+-digit int literals and misses
imported/aliased bases).

Step 1: zero exact collision vs ALL existing int bases + key uniqueness.
Step 2: NPCG first-element distinctness vs ALL existing bases.
Step 3: band clean (identical base = identical band; k-sub-streams derive
        from the base, so only an exact base re-use is a band collision)
        + repo-wide bare-number scan classifiable.

Mirror of results/_r248bmc_w5_seed_law.py (W5 freeze, bm-c r248).
"""
import io
import json
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, "scripts")
import numpy as np
import science_gates as sg

NEW = [20324500]
KEY = "innovation_quota_w6_rrg_rotation"

reg = dict(sg.SEED_REGISTRY)
assert KEY in reg and reg[KEY] == NEW[0], \
    "w6 key missing/mismatch in working tree (edit science_gates.py first)"

existing = {k: v for k, v in reg.items() if isinstance(v, int) and k != KEY}
all_bases = sorted(set(existing.values()))
facts = {
    "new": NEW, "new_keys": [KEY],
    "verification": "FULL import-based registry view (r244 pitfall law: no "
                    "source-text regex counting; import SEED_REGISTRY "
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
# berthed-but-unregistered W13 draft seeds 20323000/20323500/20324000 are
# checked too -- they are NOT in the registry yet but their bands must
# stay clear)
BERTHED_W13 = [20323000, 20323500, 20324000]
for n in NEW:
    if n in all_bases:
        facts["band_overlap"].append({"new": n, "vs_base": n})
    for w in BERTHED_W13:
        if n == w:
            facts["band_overlap"].append({"new": n, "vs_berthed_w13": w})

# Step 3b: repo-wide bare-number scan (classifiable hits only)
r = subprocess.run(["git", "grep", "-n", "--", str(NEW[0])],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace")
hits = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
facts["rg_hits"]["count"] = len(hits)
facts["rg_hits"]["lines"] = hits[:10]

def _classifiable(h: str) -> bool:
    """Classifiable hit families (W5/W12 freeze precedents): own
    registration lines in science_gates.py, own berth/prereg/catalog/
    pool/probe/facts text, and data/daily CSV volume-column numeric
    coincidences (t34/69 precedent family -- bare numbers in the volume
    column are price-data coincidences, never seed claims)."""
    if "scripts/science_gates.py:" in h:
        return True
    if any(t in h for t in ("INNOVATION_QUOTA_W6_PREREG", "_r459bma",
                            "fill_ladder", "runnable_pool")):
        return True
    if h.startswith("data/daily/") and ".csv:" in h:
        # volume-column coincidence face: date,o,h,l,c,VOLUME,amount -- the
        # bare number sits in a numeric data column, classifiable family
        return True
    return False

ok = (not facts["collision_values"] and not facts["collision_keys"]
      and not facts["first_el_clash"] and not facts["band_overlap"]
      and facts["new_first_els_mutual_distinct"]
      and all(_classifiable(h) for h in hits))
facts["rg_hits"]["unclassifiable"] = [h for h in hits if not _classifiable(h)]
facts["verdict"] = "ALL_GREEN" if ok else "RED"
out = "results/_r459bma_w6_seed_law_facts.json"
with open(out, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, ensure_ascii=False, indent=1)
print(json.dumps({k: facts[k] for k in
                  ("n_registry_keys_total", "n_existing_int_bases",
                   "collision_values", "first_el_clash", "band_overlap",
                   "rg_hits", "verdict")}, ensure_ascii=False, indent=1))
sys.exit(0 if ok else 2)
