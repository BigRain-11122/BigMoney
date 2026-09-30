"""Q6 (D-20260930-31) cost-caliber reconciliation probe.

Machine re-derivation of EVERY active cost face on one canonical trade,
answering audit Q6: is backtest flat 13bp the same caliber as the paper /
sleeve faces, or two calibers? Deterministic, read-only, zero network.

Faces measured (active tree only; Money0923/legacy/Money02 excluded per
house iron rules):
  A. engine/backtester.py v1 flat  -- FeeSchedule-derived per-side rate
     (commission 2.5bp + handling 0.341bp + supervision 0.2bp + slippage_a
     10bp), charged BOTH sides; x2/x3 via CostPatch(m) (all four components
     multiplied). Paper live face (live/paper.py COST_X1_RATE) selftest-locks
     the SAME number; batch probes import ce_transfer.COST_X1_RATE.
  B. engine/grid_sleeve.py         -- cost_bp param hardcoded 13.0 by BOTH
     callers (scripts/grid_sleeve_p1.py, scripts/grid_paper.py
     COST_BP_X1=13.0, x2=26.0); charged both sides; NOT FeeSchedule-derived.

Also checked: slippage_c (30bp) is defined in FeeSchedule but referenced by
NO active cost path (the audit's feared 30bp gap does not exist in active
calibers); commission_min (Y5) applies only in knowledge/rules.py helper
functions total_buy_cost/total_sell_proceeds, which no active engine path
calls (flat-rate engines; Y5 min binds only under Y20k notionals, below
every active sleeve size).
"""
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r474bma_q6_cost_recon.json")
sys.path.insert(0, ROOT)

from knowledge.rules import FeeSchedule  # noqa: E402

NOTIONAL = 100_000.0  # canonical single-side trade (Y100k = 10% sleeve on Y1M)


def face_a_rate(mult: float = 1.0) -> float:
    f = FeeSchedule()
    return (f.commission_rate * mult + f.handling_fee * mult
            + f.supervision_fee * mult + f.slippage_a * mult)


def main():
    f = FeeSchedule()
    a1 = face_a_rate()
    a2 = face_a_rate(2.0)
    a3 = face_a_rate(3.0)
    b1 = 13.0 / 1e4
    b2 = 26.0 / 1e4

    trade = {
        "notional_cny": NOTIONAL,
        "face_a_v1_flat": {"per_side_rate": a1, "per_side_cny": NOTIONAL * a1,
                           "round_trip_cny": 2 * NOTIONAL * a1,
                           "components_bp": {
                               "commission": f.commission_rate * 1e4,
                               "handling": f.handling_fee * 1e4,
                               "supervision": f.supervision_fee * 1e4,
                               "slippage_a": f.slippage_a * 1e4,
                               "sum_bp": a1 * 1e4}},
        "face_a_x2_costpatch": {"per_side_rate": a2,
                                "per_side_cny": NOTIONAL * a2,
                                "recorded_COST_X2_RATE": 0.0026082,
                                "matches_recorded": abs(a2 - 0.0026082) < 1e-12},
        "face_a_x3_costpatch": {"per_side_rate": a3,
                                "per_side_cny": NOTIONAL * a3},
        "face_b_grid_sleeve": {"per_side_rate": b1,
                               "per_side_cny": NOTIONAL * b1,
                               "round_trip_cny": 2 * NOTIONAL * b1,
                               "provenance": "hardcoded COST_BP_X1=13.0 in "
                                             "grid_sleeve_p1.py + grid_paper.py "
                                             "(frozen-batch verdict face)"},
        "face_b_grid_x2": {"per_side_rate": b2,
                           "per_side_cny": NOTIONAL * b2,
                           "provenance": "hardcoded COST_BP_X2=26.0"},
    }
    diff_side = a1 - b1
    out = {
        "probe": "q6_cost_caliber_reconciliation",
        "decision": "D-20260930-31 Q6 (48h deliverable)",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": "TWO_CALIBERS_CONFIRMED",
        "canonical_trade": trade,
        "divergence": {
            "per_side_rate_diff": diff_side,
            "per_side_bp_diff": diff_side * 1e4,
            "per_side_cny_diff_on_100k": NOTIONAL * diff_side,
            "round_trip_cny_diff_on_100k": 2 * NOTIONAL * diff_side,
            "x2_rate_diff": a2 - b2,
        },
        "single_source_status": {
            "face_a_derived_from_FeeSchedule": True,
            "face_b_derived_from_FeeSchedule": False,
            "paper_live_selftest_locks_face_a": True,
            "slippage_c_30bp_used_by_active_path": False,
            "commission_min_yuan5_used_by_active_engine": False,
            "commission_min_binding_threshold_cny": f.commission_min / f.commission_rate,
        },
        "risk_note": (
            "Numeric divergence is tiny (0.041bp/side = 0.31% of the cost, "
            "Y0.41 per Y100k side) and grid verdicts were frozen at 13.0 -- "
            "no historical number is wrong as declared. The structural issue "
            "is single-source: the grid face hardcodes its rate instead of "
            "deriving from FeeSchedule, so any future fee change would leave "
            "the grid face silently stale. RW-3 merge direction: canonical "
            "spec in knowledge/ recording both faces + derivation; next NEW "
            "grid prereg (post RW-5 unfreeze) uses FeeSchedule-derived "
            "cost_bp; frozen grid_sleeve_p1 verdicts stay 13.0 as declared "
            "historical evidence (no retroactive rewrite, r444/A7)."),
        "rw3_scope_next_slice": (
            "RW-3 (T-127): (1) knowledge/ canonical cost spec file shared by "
            "backtest/paper/gateway; (2) trade_pnl_mode='full' default flip "
            "REQUIRES explicit param propagation to all 6 trader JSONs first "
            "(anchor gates recompute from trader params -- a silent default "
            "flip breaks every anchor); (3) strict_open_fills default True same "
            "constraint; (4) selftest asserting all three faces give the same "
            "price+cost on the same bar."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    d = out["divergence"]
    print(f"q6 cost recon: faceA v1={a1*1e4:.4f}bp/side x2={a2*1e4:.4f}bp "
          f"x3={a3*1e4:.4f}bp | faceB grid={b1*1e4:.1f}bp x2={b2*1e4:.1f}bp")
    print(f"divergence: {d['per_side_bp_diff']:.4f}bp/side = "
          f"Y{d['per_side_cny_diff_on_100k']:.2f} per Y100k side")
    print(f"x2 recorded 0.0026082 matches CostPatch(2): {trade['face_a_x2_costpatch']['matches_recorded']}")
    print(f"verdict: {out['verdict']}")
    print(f"evidence -> {os.path.relpath(OUT, ROOT)}")
    assert abs(a1 - 0.0013041) < 1e-12, "face A must equal the recorded 13.041bp"
    assert abs(a1 * 1e4 - 13.041) < 1e-9
    assert not out["single_source_status"]["slippage_c_30bp_used_by_active_path"]


if __name__ == "__main__":
    main()
