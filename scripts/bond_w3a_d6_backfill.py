"""r212 bm-b: post-hoc D6 in-register disclosure backfill for BOND_CARRY_WAVE3A.

The batch `run` (2026-09-26 00:07, r212) computed every judgment face correctly,
but the d6 in_register disclosure slot holds an error string: the face iterated
the whole firm/traders directory and KeyErrored on firm/traders/_template.json
(schema-foreign: level INTERN by example, no params.entry) -- broken from
delivery, first exercised in production by this batch (hermetic selftest never
mirrored the real directory form; r157/r204 family).

A full batch re-run is FORBIDDEN here: append_ledger/gate_attrition are
append-only (re-run would double-count 35 trials, audit law "re-run needs fresh
prereg"). This script therefore recomputes ONLY the C1 daily sleeve series
(deterministic: same frozen panel + same code path + zero randomness in C1),
asserts byte-level anchors against the stored result (sharpe/n_entries/max_dd),
computes the in-register correlation through the SAME fixed helper the runner
now uses, and patches the d6.in_register slot with a provenance-labeled block.
Judgment faces (verdicts_g1/g2, d6 verdict, cells, nulls, trials_ledger,
gate_attrition) are untouched.

Usage: python scripts\bond_w3a_d6_backfill.py [--dry-run]
"""
import json
import os
import sys
import time
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RESULTS_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "results", "bond_carry_w3a.json")

import pandas as pd  # noqa: E402

import bond_carry_w3a as B  # noqa: E402


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(RESULTS_JSON, encoding="utf-8") as fh:
        result = json.load(fh, object_pairs_hook=collections.OrderedDict)
    stored_c1 = result["cells"]["C1"]["full"]
    orig_d6_ir = result["d6"].get("in_register", {})
    if "max_abs_corr" in orig_d6_ir and "error" not in orig_d6_ir:
        print("[backfill] in_register already populated -- nothing to do")
        return 0

    print("[backfill] recomputing C1 daily sleeve (deterministic) ...")
    panel, _ = B.load_panel()
    win = B.determine_window(panel)
    scan = B.scan_breakpoints(panel, win["i0"], win["i1"])
    firsts = B.whitelist_firsts(scan)
    plans = B.build_eval_plans(panel, win, firsts)
    c1 = B.run_sleeve(panel, plans, lambda p: dict(p["c1_targets"]), B.COST_JUDGMENT_MULT,
                      i0=win["i0"], i1=win["i1"],
                      tp_convergence=True, hard_bounds=True, label="C1-backfill", firsts=firsts)
    # determinism anchors vs the stored judgment face (exact recompute check)
    anchors = [
        ("sharpe", c1["full"]["sharpe"], stored_c1["sharpe"]),
        ("n_entries", c1["full"]["n_entries"], stored_c1["n_entries"]),
        ("max_drawdown", c1["full"]["max_drawdown"], stored_c1["max_drawdown"]),
        ("n_resizes", c1["full"]["n_resizes"], stored_c1["n_resizes"]),
    ]
    for name, got, want in anchors:
        if abs(float(got) - float(want)) > 1e-9:
            print(f"[backfill] DETERMINISM ANCHOR FAIL: {name} {got} != stored {want} -- abort, no write")
            return 2
    print("[backfill] anchors exact:", ", ".join(f"{n}={w}" for n, _, w in anchors))

    c1s = pd.Series(c1["_rets"], index=pd.to_datetime(c1["_dates"]))
    print("[backfill] computing in-register corr via fixed production helper ...")
    ir = B._inregister_corr(c1s)   # real TRADERS_DIR + real ew6 member_run
    block = collections.OrderedDict()
    block.update(ir)
    block["posthoc"] = collections.OrderedDict([
        ("r212_wiring_fix", True),
        ("method", "post-hoc recomputation of the C1 daily sleeve (deterministic "
                   "anchors exact vs stored judgment face); in-register corr via the "
                   "same fixed _inregister_corr helper the runner now calls; judgment "
                   "faces / trials_ledger / gate_attrition untouched (re-run of the "
                   "batch is forbidden: append-only ledger would double-count)"),
        ("error_at_run", orig_d6_ir.get("error")),
        ("backfill_ts", time.strftime("%Y-%m-%d %H:%M:%S")),
    ])
    print("[backfill] in_register:", json.dumps(block, ensure_ascii=False)[:400])
    if dry:
        print("[backfill] dry-run -- no write")
        return 0
    result["d6"]["in_register"] = block
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1, default=str)
    # self-verify
    with open(RESULTS_JSON, encoding="utf-8") as fh:
        again = json.load(fh)
    ir2 = again["d6"]["in_register"]
    assert "max_abs_corr" in ir2 and "posthoc" in ir2 and ir2["posthoc"]["error_at_run"]
    assert again["trials_ledger"]["total"] == 183135, "ledger touched!"
    assert again["d6"]["verdict"] == "reject", "d6 verdict touched!"
    assert again["verdicts_g1"]["C1"]["pass_v2"] is False
    print("[backfill] written + self-verified (ledger 183135 intact, verdicts intact)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
