"""Canonical single-source cost spec (RW-3, T-127 / D-20260930-05).

Every face that charges trading cost -- backtest engine, live paper
anchor/paper/x2 paths, transfer screens, the (future) order gateway --
derives its rate from THIS module, never from a local literal. Root of
the derivation = knowledge.rules.FeeSchedule (the only fee table).

Two calibers exist and are FROZEN here with owners (recon memo
results/COST_CALIBER_RECON_20260930.md, D-20260930-31 Q6):

Face A (active canonical) -- FeeSchedule-derived, x1 = 13.041 bp/side
    = commission 2.5bp + handling 0.341bp + supervision 0.2bp
      + slippage_a 10bp (flat v1 basis).
    Consumers: engine backtester, live.paper (COST_X1_RATE),
    ce_transfer, combined_exit_screen, science_gates CostPatch faces,
    AGGR/ALLOC/SYSTEM-V1 paper accounts. x2/x3 stress = integer
    multiples of this rate (CostPatch), never an independent number.

Face B (grid legacy, FROZEN) -- 13.0 bp/side, hardcoded by the frozen
    T-78 grid batch at prereg time. Historical grid verdicts and the
    grid_paper daily replay stay on the declared 13.0 caliber (no
    retroactive rewrite, archive-valuation law). NEW grid batches after
    the RW-5 freeze MUST declare Face A (cost_spec.X1_RATE) instead;
    the 0.041bp divergence is documented, not silently inherited.

Deltas (per ¥100,000 notional, one side): Face A ¥130.41 vs Face B
¥130.00 -> ¥0.41/side, ¥0.82 round-trip (~0.3% of cost, ~0.0008% of
notional). slippage_c (30bp) exists in FeeSchedule but NO active path
uses it (recon memo: verified zero consumers).
"""

try:
    from knowledge.rules import FeeSchedule
except ImportError:  # direct `python knowledge/cost_spec.py` execution
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    from knowledge.rules import FeeSchedule

_X1_RECORDED = 0.0013041   # G2-recorded baseline single-side cost
_X2_RECORDED = 0.0026082   # G2-recorded 2x stressed single-side cost


def x1_side_rate(fee: FeeSchedule = FeeSchedule()) -> float:
    """Active canonical per-side cost rate (Face A), derived -- never
    hardcoded. Any fee-table change propagates to every face at once;
    the assert below then FAILS, forcing a conscious re-record instead
    of silent drift. D-39: transfer_fee is a BOTH-sides fee and is part
    of every side rate (0 for the ETF default -> recorded face intact)."""
    return (fee.commission_rate + fee.handling_fee
            + fee.supervision_fee + fee.transfer_fee + fee.slippage_a)


X1_RATE = x1_side_rate()
X2_RATE = 2.0 * X1_RATE

# D-20260930-39 CN-C2: sell-side rate for a given schedule = buy side +
# stamp tax (sell-only). ETF default (stamp_tax=0) -> X1_SELL == X1_RATE
# bit-for-bit; stock schedules (rules.fee_schedule_for) add the 5bp
# sell-only stamp tax so stock backtests can never silently reuse the
# symmetric ETF rate.
def x1_sell_side_rate(fee: FeeSchedule = FeeSchedule()) -> float:
    return x1_side_rate(fee) + fee.stamp_tax


X1_SELL_RATE = x1_sell_side_rate()

# Face B: frozen historical grid caliber (see module docstring).
GRID_LEGACY_COST_BP_X1 = 13.0


def verify() -> bool:
    """Self-check: derived rates must equal the G2-recorded constants
    bit-for-bit (within float equality tolerance of the recorded
    decimal). A failure means the fee table drifted from the recorded
    cost basis -- refuse to run and re-record consciously."""
    ok = abs(X1_RATE - _X1_RECORDED) < 1e-12
    ok &= abs(X2_RATE - _X2_RECORDED) < 1e-12
    ok &= abs(GRID_LEGACY_COST_BP_X1 * 1e-4 - 0.0013) < 1e-12
    return bool(ok)


if __name__ == "__main__":
    print(f"X1_RATE={X1_RATE} ({X1_RATE*1e4:.4f} bp/side)")
    print(f"X2_RATE={X2_RATE} ({X2_RATE*1e4:.4f} bp/side)")
    print(f"GRID_LEGACY_COST_BP_X1={GRID_LEGACY_COST_BP_X1}")
    print("verify:", "PASS" if verify() else "FAIL")
