# -*- coding: utf-8 -*-
"""_r259bmc_slot9_berth_registry.py -- INNOVATION-QUOTA-SLOT-9 berth registration
(bm-c r259): fill_ladder_catalog named entry + pool entries-list entry.

Idempotent: skips faces already present. r459 pit-law three-check enforced
in-script (enqueue_gates canonical syntax / workers_plan dict / runner_args
non-empty) -- registry not written unless all three pass.

Exit 0 normal / 2 mechanism fault.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "Tools", "fill_ladder_catalog.json")
PREREG = "research/INNOVATION_QUOTA_W9_PREREG.md"
RUNNER = "scripts/innovation_quota_w9.py"

NAMED = {
    "INNOVATION-QUOTA-SLOT-9": {
        "state": "berth-declared",
        "evidence": (
            "berth prereg research/INNOVATION_QUOTA_W9_PREREG.md (BERTH status, "
            "bm-c r259) + zoo #84 row berth-declare (four-vote composite "
            "author-verbatim thresholds zero-calibration, CROWD-VOTE-P1 4 cells "
            "ASYM/SYM x cost x1/x2); park condition from bm-b r448 W8-draft "
            "census (width-leg structural overlap + wait-W7-verdict) resolved by "
            "W7 verdict 07:26 0/4 judged-negative family closure -> re-yi; probe "
            "facts results/_r259bmc_w9_crowding_probe_facts.json (occupancy "
            "verdict: V1 94.4%/V2 98.9% near-saturated -> composite effective "
            "face = V3&V4 joint gate + asymmetric confirm state machine; D6 "
            "width-leg vs REGIME_GUARD below-MA20 pearson +0.7728 disclosed, "
            "composite +0.5965; crowd occupancy 53.2%, ~5.5 exits/yr); freeze "
            "steps next round by drafting machine per W5/W6/W7 mirror"),
        "verified": "direct, bm-c r259 (prereg + probe facts + scan artifact in-tree)",
    }
}

POOL_ENTRY = {
    "id": "INNOVATION-QUOTA-SLOT-9",
    "ticket_ref": "T-2026-09-28-107 sec.4(d) fill-ladder innovation quota",
    "prereg_ref": (
        "research/INNOVATION_QUOTA_W9_PREREG.md BERTH (bm-c r259 berth declare; "
        "freeze window next round per W5/W6/W7 mirror: status-flip FROZEN + seed "
        "innovation_quota_w9_crowd=20326000 three-step law + D6 cells probe + "
        "theta-constant zero-drift assertion; probe facts "
        "results/_r259bmc_w9_crowding_probe_facts.json core48 48/1,616d; 4 cells "
        "ASYM author-verbatim / SYM ablation x cost x1/x2; n_entries berth read "
        "~36 vs F6 gate 30 marginal honest-carry)"),
    "runner": RUNNER,
    "runner_note": (
        "NOT BUILT yet (berth window); build = freeze window per W7 mirror "
        "(W1-W7 single-target exposure-gate skeleton parameterization reuse + "
        "selftest + read-only verify subcommand G-ANCHOR bit-exact vs berth "
        "probe facts n_decidable 1616 / crowd_days 860 / votes 1525/1599/715/824)"),
    "consumer_plan": (
        "CROWD-VOTE-P1 judged verdict -> G2 pass = T-34 fastline candidate pool "
        "eligibility (STYLE_CORPS routing candidate per zoo #84 row, harness A/B "
        "adoption face) + crowding-family material shelf; fail = judged-negative "
        "family closure (five negative-prior burden upheld as predicted "
        "mainline, legal output saving future crowding-family burns) + attrition "
        "row + 48h CEO report (O-1116 return/drawdown dual-column)"),
    "lane_owner": None,
    "priority": 1,
    "enqueue_gates": [f"prereg_frozen:{PREREG}", "runner_exists"],
    "runner_args": ["run"],
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal",
        "priority": "BelowNormal",
        "note": (
            "4-cell judged batch x1000 vstarts + 100 splits + 2000 null draws, "
            "single-process minutes-scale per prereg sec.0 (core48 in-repo "
            "panel, vectorized four-vote composite); CEO 10% CPU headroom law = "
            "BelowNormal"),
    },
    "note": (
        "ladder (d) slot-9 (bm-c r259 berth): zoo #84 crowding_vote family "
        "(CROWD-VOTE-P1, berth prereg research/INNOVATION_QUOTA_W9_PREREG.md; "
        "probe facts results/_r259bmc_w9_crowding_probe_facts.json -- core48 "
        "face 48/1,616d, D6 signal face width-leg vs REGIME_GUARD below-MA20 "
        "pearson +0.7728 disclosed, composite +0.5965; park condition from bm-b "
        "r448 W8-draft census resolved by W7 verdict 07:26 0/4 family closure); "
        "enqueue_gates = prereg_frozen + runner_exists (both must pass before "
        "pool); supply_floor response: ready=0<3 breach standing, W12-JUDGE "
        "bm-b in flight + W13 bm-a runner + SLOT-8 bm-b freeze window = next "
        "supply line after A-layer inventory exhausted (r258 scan verdict "
        "PRIMARY)"),
    "parked": "2026-09-30 bm-c r259",
}


def main() -> int:
    try:
        with open(CAT, encoding="utf-8") as f:
            cat = json.load(f)

        changed = []
        named = cat.get("berths") or cat
        # named consumption_state dict lives at top level (keys are ids)
        for key, val in NAMED.items():
            if key in cat and isinstance(cat[key], dict):
                print(f"NAMED already present: {key} (skip)")
            else:
                cat[key] = val
                changed.append(f"named:{key}")

        entries = cat["entries"]
        if any(e.get("id") == POOL_ENTRY["id"] for e in entries):
            print(f"POOL entry already present: {POOL_ENTRY['id']} (skip)")
        else:
            # r459 three-check before write
            gates = POOL_ENTRY["enqueue_gates"]
            assert any(g.startswith("prereg_frozen:") for g in gates), \
                "r459: enqueue_gates must use canonical prereg_frozen:<path>"
            assert isinstance(POOL_ENTRY["workers_plan"], dict) and \
                POOL_ENTRY["workers_plan"], "r459: workers_plan dict required"
            assert isinstance(POOL_ENTRY["runner_args"], list) and \
                POOL_ENTRY["runner_args"], "r459: runner_args required"
            assert isinstance(POOL_ENTRY["runner"], str) and \
                "/" in POOL_ENTRY["runner"], "r459: runner bare path in field"
            entries.append(POOL_ENTRY)
            changed.append("pool:INNOVATION-QUOTA-SLOT-9")

        if changed:
            with open(CAT, "w", encoding="utf-8", newline="\n") as f:
                json.dump(cat, f, ensure_ascii=False, indent=1)
            print("CHANGED:", "; ".join(changed))
        else:
            print("NO-OP (idempotent)")
        # post-write verification
        with open(CAT, encoding="utf-8") as f:
            re = json.load(f)
        assert "INNOVATION-QUOTA-SLOT-9" in re
        assert any(e.get("id") == "INNOVATION-QUOTA-SLOT-9" for e in re["entries"])
        print("VERIFY: named + pool entries present, JSON valid")
        return 0
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"REGISTRY FAULT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
