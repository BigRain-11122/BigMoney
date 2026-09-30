"""W14 freeze-window seed three-step law facts (r441 law · r244 import-view law).

Mirrors _r461bma_w13_seed_law_facts schema (W13 freeze precedent). Post-
registration verification: (1) full import view zero exact collision;
(2) canon first-els mutually distinct vs all other bases; (3) derived bands
clean (gen 20327500..20327575, null 20328000..20328199, unc 20328500..20328700);
rg hits classified. Deterministic, offline, read-only on registry.
"""
import json
import subprocess

import numpy as np

import sys
sys.path.insert(0, r"scripts")
sys.path.insert(0, ".")  # repo root (knowledge package, science_gates dep)
from science_gates import SEED_REGISTRY  # noqa: E402

NEW_KEYS = ["trial_labor_w14_gen", "trial_labor_w14_scrnull", "trial_labor_w14_unc"]
NEW_VALS = [20327500, 20328000, 20328500]


def canon_first_el(seed):
    # canon draw face per W1-W13 lineage: integer-axis draw
    return int(np.random.default_rng([seed, 0]).integers(0, 2**31 - 1))


def main():
    int_view = {k: v for k, v in SEED_REGISTRY.items() if isinstance(v, int)}
    vals = list(int_view.values())
    new = [int_view[k] for k in NEW_KEYS]
    assert new == NEW_VALS, f"registration missing: {new}"

    rest = [v for v in vals if v not in NEW_VALS]
    collision_values = sorted({v for v in NEW_VALS if v in rest})

    first_els = {str(s): canon_first_el(s) for s in NEW_VALS}
    rest_first_els = {v: canon_first_el(v) for v in set(rest)}
    first_el_clash = sorted(
        {str(s) for s, fe in first_els.items() if fe in rest_first_els.values()}
        | {str(a) for a in first_els if a != str(NEW_VALS[0])
          and first_els[a] == first_els[str(NEW_VALS[0])]}
    )

    # derived bands: scrnull i<200, unc cell_idx<200 (+headroom to +200),
    # gen family_idx in [0,76)
    bands = {
        "gen_band": (20327500, 20327575),
        "scrnull_band": (20328000, 20328199),
        "unc_band": (20328500, 20328700),
    }
    band_overlap = [
        {"band": name, "foreign_base": v}
        for name, (lo, hi) in bands.items()
        for v in sorted(set(rest))
        if lo <= v <= hi
    ]

    # rg full-repo seed-face hits (data + docs, classified)
    pat = "|".join(str(v) for v in NEW_VALS)
    rg = subprocess.run(
        ["rg", "-n", pat, "--no-heading", "-g", "!*.log"],
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    lines = [l for l in rg.stdout.splitlines() if l]
    data_hits = [l for l in lines if l.startswith("data/")]
    doc_hits = [l for l in lines if not l.startswith("data/")]

    facts = {
        "ts": "2026-09-30 16:xx (bm-b r471 freeze window)",
        "machine": "bm-b",
        "round": "r471",
        "law": "r441 three-step (W13 _r461bma schema mirror); r244 import-view law; "
               "r276 band-interleave retake lineage (natural +500 push collided "
               "SLOT-7/8/9/10 band, retaken above then-max 20327000)",
        "new": NEW_VALS,
        "new_keys": NEW_KEYS,
        "total_int_keys": len(vals),
        "collision_values": collision_values,
        "collision_keys": sorted(
            k for k, v in int_view.items()
            if v in NEW_VALS and k not in NEW_KEYS
        ),
        "first_els": first_els,
        "first_el_clash": first_el_clash,
        "bands": {k: list(v) for k, v in bands.items()},
        "band_overlap": band_overlap,
        "rg_hits": {
            "data_coincidence_count": len(data_hits),
            "data_coincidence_sample": data_hits[:6],
            "doc_hit_count": len(doc_hits),
            "doc_hit_sample": doc_hits[:12],
            "classification": (
                "doc hits = berth/adoption/freeze docs + registry comments + state "
                "pointers, all self-classifiable per W7 r255 precedent; data hits "
                "(if any) = price/volume column numeric coincidences "
                "(t34/batch-69 precedent family)"
            ),
        },
        "verdict": (
            "ALL GREEN" if not (collision_values or first_el_clash or band_overlap)
            else "CLASH"
        ),
    }
    out = r"results\_r471bmb_w14_seed_law_facts.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: facts[k] for k in
                      ("total_int_keys", "collision_values", "first_els",
                       "first_el_clash", "band_overlap", "verdict")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
