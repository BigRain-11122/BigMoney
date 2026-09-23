"""T-02 deliverable 3/7 -- D5 cost-basis v2 gates (BACKTEST_SCIENCE.md s5).

Runs AFTER knowledge/rules.py gained the frozen ADV(20d) tier constants and
engine/backtester.py gained the additive cost_v2 flag (default None = legacy
path byte-identical). All gates must PASS before any new batch may declare
the v2 basis. Gate-script adoption itself (screen families switching) is
T-02 deliverable 4/7 and is NOT done here.

Gates:
  G0 rules sanity: tier monotonicity, 10bp tier == FeeSchedule().slippage_a,
     cap rate, basis version strings
  G1 legacy byte-identity: 432-grid 5-point sampled determinism with the
     flag absent -> bit-exact vs recorded artifacts (same harness as
     p4_batch2_gates G1; proves this engine edit is invisible when off)
  G2 tier math: cost_v2_slippage boundaries + missing/invalid fallbacks
  G3 engine cap+tier (synthetic): tiny-ADV entry capped to 1% ADV at 10bp
     tier; large-ADV entry uncapped at 2bp tier
  G4 zero-ADV drop + missing-ADV fallback (10bp slippage, no cap, counter)
  G5 no-look-ahead: execution day's OWN adv value never used (prior-day
     cap + prior-day tier both proven)
  G6 live-fire: VOLATILITY-CE-01 anchor under the v2 basis on the
     evidence-cutoff-truncated panel; anchor reproduction on the default
     path re-checked; v2 result declares cost_basis, counters sane, and
     (when no entry was capped) trade-fee total strictly below the legacy
     basis -- liquid core48 majors sit in the 2bp tier

Ledger: zero new trials (tooling verification, not a strategy screen;
per COMPUTE_AUDIT.md the audit note is embedded in the payload).

Products: results/cost_v2_gates.json. Exit 0 iff all PASS.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS, all_combinations, combo_hash
from engine import run_backtest
from knowledge.rules import (
    FeeSchedule, ADV_FILL_CAP_RATE, COST_BASIS_V1, COST_BASIS_V2,
    ADV20_TIER_2BP_YUAN, ADV20_TIER_5BP_YUAN,
    SLIPPAGE_TIER_2BP, SLIPPAGE_TIER_5BP, SLIPPAGE_TIER_10BP,
    cost_v2_slippage, cost_v2_side_rate,
)
import p4_batch2_gates as pg           # reuse the 432 harness (anti-rewrite)
from live.paper import (
    build_panels, load_core, SIGNAL_BUILDERS, ExitPatch, anchor_gate,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(PATHS.results_dir, "cost_v2_gates.json")
TRADER_JSON = os.path.join(ROOT, "firm", "traders", "VOLATILITY-CE-01.json")

FIXED_SIDE = (FeeSchedule().commission_rate + FeeSchedule().handling_fee
              + FeeSchedule().supervision_fee)          # 0.0003041
RATE_2BP = FIXED_SIDE + SLIPPAGE_TIER_2BP               # 0.0005041
RATE_10BP = FIXED_SIDE + SLIPPAGE_TIER_10BP             # 0.0013041 == legacy
BASE_PARAMS = {"position_size_pct": 0.10, "max_positions": 5}


def adv_panel(idx, syms, values):
    """values: dict sym -> scalar OR per-day list (len == len(idx))."""
    data = {}
    for s in syms:
        v = values[s]
        data[s] = list(v) if isinstance(v, (list, tuple)) else [v] * len(idx)
    return pd.DataFrame(data, index=idx, columns=syms)


def gate_g0(results):
    f = FeeSchedule()
    checks = {
        "tier_monotone": SLIPPAGE_TIER_2BP < SLIPPAGE_TIER_5BP < SLIPPAGE_TIER_10BP,
        "tier10bp_is_legacy": SLIPPAGE_TIER_10BP == f.slippage_a,
        "cap_rate": ADV_FILL_CAP_RATE == 0.01,
        "tier_edges": (ADV20_TIER_2BP_YUAN == 5e8 and ADV20_TIER_5BP_YUAN == 1e8),
        "basis_strings": COST_BASIS_V1 != COST_BASIS_V2,
    }
    results.append({"gate": "G0", "name": "rules constants sanity",
                    "status": "PASS" if all(checks.values()) else "FAIL",
                    "checks": {k: bool(v) for k, v in checks.items()}})
    return all(checks.values())


def gate_g1(results, prices):
    """Legacy byte-identity: reuse the p4_batch2_gates G1 harness verbatim.

    The recorded artifacts were produced on the panel ending 2026-09-22;
    update_daily has since appended 2026-09-23 bars, so the panel is
    truncated at the artifacts' recording cutoff first (documented drift
    in p4_batch2_gates.py docstring; equity length 1631 == core48 union
    calendar through 09-22).
    """
    ps = pd.Timestamp("2026-09-22")
    prices_t = {s: df[df.index <= ps] for s, df in prices.items()}
    return pg.gate_g1(results, prices_t)


def gate_g2(results):
    cases = [
        (6e8, SLIPPAGE_TIER_2BP), (5e8, SLIPPAGE_TIER_2BP),
        (4.99e8, SLIPPAGE_TIER_5BP), (1e8, SLIPPAGE_TIER_5BP),
        (0.99e8, SLIPPAGE_TIER_10BP), (1.0, SLIPPAGE_TIER_10BP),
        (float("nan"), SLIPPAGE_TIER_10BP), (None, SLIPPAGE_TIER_10BP),
        ("bad", SLIPPAGE_TIER_10BP), (-1e9, SLIPPAGE_TIER_10BP),
    ]
    ok = all(cost_v2_slippage(x) == want for x, want in cases)
    side_ok = (cost_v2_side_rate(6e8) == RATE_2BP
               and cost_v2_side_rate(5e7) == RATE_10BP)
    results.append({"gate": "G2",
                    "name": "tier math + fallbacks",
                    "status": "PASS" if (ok and side_ok) else "FAIL",
                    "cases": [[repr(x), w] for x, w in cases],
                    "side_rate_2bp": cost_v2_side_rate(6e8)})
    return ok and side_ok


def _run_syms(prices, entry_on, exit_on, adv_values, days=12):
    """Synthetic 2-3 symbol run: returns (result, idx)."""
    syms = list(adv_values.keys())
    panel, idx = pg.synth_panel(syms, days=days)
    entry = pg.sig_df(idx, syms, entry_on)
    exit_ = pg.sig_df(idx, syms, exit_on)
    adv = adv_panel(idx, syms, adv_values)
    res = run_backtest(panel, BASE_PARAMS, entry_signal=entry,
                       exit_signal=exit_, cost_v2=adv)
    return res, idx


def _trade(res, sym):
    for tr in res["trades"]:
        if tr["symbol"] == sym:
            return tr
    return None


def gate_g3(results):
    """Tiny-ADV capped at 1% ADV + 10bp tier; large-ADV uncapped + 2bp."""
    res, _ = _run_syms(
        None,
        entry_on={"AAA": [0], "BBB": [0]},
        exit_on={"AAA": [5], "BBB": [5]},
        adv_values={"AAA": 5e6, "BBB": 6e8},   # caps: 5e4 (binds) / 6e6 (free)
    )
    st = res["cost_v2"]
    ta, tb = _trade(res, "AAA"), _trade(res, "BBB")
    checks = {
        "two_trades": ta is not None and tb is not None,
        "aaa_qty_capped_to_1pct_adv": ta is not None and abs(ta["qty"] - 500.0) < 1e-6,
        "bbb_qty_uncapped": tb is not None and abs(tb["qty"] - 1000.0) < 1e-6,
        "aaa_fee_10bp_tier": ta is not None and abs(ta["fee"] / (ta["qty"] * ta["price"]) - RATE_10BP) < 2e-5,
        "bbb_fee_2bp_tier": tb is not None and abs(tb["fee"] / (tb["qty"] * tb["price"]) - RATE_2BP) < 2e-5,
        "capped_entries": st["capped_entries"] == 1,
        "tier_counts": (st["tier_entries_10bp"] == 1 and st["tier_entries_2bp"] == 1
                        and st["tier_entries_5bp"] == 0),
        "no_drops": st["dropped_zero_adv"] == 0 and st["missing_adv_executions"] == 0,
    }
    results.append({"gate": "G3",
                    "name": "engine cap + tiered cost (synthetic)",
                    "status": "PASS" if all(checks.values()) else "FAIL",
                    "checks": {k: bool(v) for k, v in checks.items()},
                    "stats": st})
    return all(checks.values())


def gate_g4(results):
    """Zero-ADV -> order dropped; missing-ADV -> 10bp, no cap, counted."""
    res, _ = _run_syms(
        None,
        entry_on={"ZED": [0], "MIS": [0]},
        exit_on={"ZED": [5], "MIS": [5]},
        adv_values={"ZED": 0.0, "MIS": float("nan")},
    )
    st = res["cost_v2"]
    tm = _trade(res, "MIS")
    tz = _trade(res, "ZED")
    checks = {
        "zed_dropped_no_trade": tz is None,
        "mis_uncapped_qty": tm is not None and abs(tm["qty"] - 1000.0) < 1e-6,
        "mis_fee_10bp_fallback": tm is not None and abs(tm["fee"] / (tm["qty"] * tm["price"]) - RATE_10BP) < 2e-5,
        "dropped_zero_adv_counter": st["dropped_zero_adv"] == 1,
        "missing_adv_counter": st["missing_adv_executions"] >= 1,
        "capped_zero": st["capped_entries"] == 0,
    }
    results.append({"gate": "G4",
                    "name": "zero-ADV drop + missing-ADV fallback",
                    "status": "PASS" if all(checks.values()) else "FAIL",
                    "checks": {k: bool(v) for k, v in checks.items()},
                    "stats": st})
    return all(checks.values())


def gate_g5(results):
    """No-look-ahead: exec-day adv spike must NOT loosen the day-0 cap/tier.

    LAH adv: day0=5e6 (cap 5e4 -> qty 500, 10bp), day1+=6e8 (would be cap
    6e6, 2bp if the engine wrongly used the execution day's own value).
    """
    days = 12
    idx = pd.bdate_range("2026-01-01", periods=days)
    spike = [5e6] + [6e8] * (days - 1)
    res, _ = _run_syms(
        None,
        entry_on={"LAH": [0]},
        exit_on={"LAH": [5]},
        adv_values={"LAH": spike},
    )
    st = res["cost_v2"]
    tr = _trade(res, "LAH")
    checks = {
        "qty_uses_prior_day_cap": tr is not None and abs(tr["qty"] - 500.0) < 1e-6,
        "tier_uses_prior_day_adv": st["tier_entries_10bp"] == 1 and st["tier_entries_2bp"] == 0,
        "sell_side_uses_its_own_prior_day": (
            tr is not None and abs(tr["fee"] / (tr["qty"] * tr["price"]) - RATE_2BP) < 2e-5),
    }
    results.append({"gate": "G5",
                    "name": "no-look-ahead (engine shifts adv one day)",
                    "status": "PASS" if all(checks.values()) else "FAIL",
                    "checks": {k: bool(v) for k, v in checks.items()},
                    "stats": st})
    return all(checks.values())


def gate_g6(results):
    """Live-fire: registered anchor under the v2 basis, cutoff-truncated."""
    t = json.load(open(TRADER_JSON, encoding="utf-8"))
    prices_full = load_core()
    # (a) default path still reproduces the registered evidence
    ag = anchor_gate(t, prices_full)
    # (b) same truncated panel, v2 basis on
    cutoff = t["evidence_cutoff"]
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    adv20 = P["amount"].rolling(20).mean()
    with ExitPatch(t.get("exit_overrides")):
        res_v1 = run_backtest(prices, params, entry_signal=entry,
                              exit_signal=(entry <= 0))
    with ExitPatch(t.get("exit_overrides")):
        res_v2 = run_backtest(prices, params, entry_signal=entry,
                              exit_signal=(entry <= 0), cost_v2=adv20)
    st = res_v2["cost_v2"]
    fee_v1 = sum(tr["fee"] for tr in res_v1["trades"])
    fee_v2 = sum(tr["fee"] for tr in res_v2["trades"])
    checks = {
        "anchor_repro_default_path": bool(ag.get("ok")),
        "basis_declared": st.get("cost_basis") == COST_BASIS_V2,
        "v1_result_has_no_cost_key": "cost_v2" not in res_v1,
        "equity_lengths_equal": len(res_v1["equity_curve"]) == len(res_v2["equity_curve"]),
        "zero_adv_drops": st["dropped_zero_adv"] == 0,
        "tier_counters_populated": (st["tier_entries_2bp"] + st["tier_entries_5bp"]
                                    + st["tier_entries_10bp"]) >= 1,
        "fees_not_higher_than_legacy": fee_v2 <= fee_v1,
        "uncapped_implies_strictly_cheaper": (
            st["capped_entries"] > 0 or fee_v2 < fee_v1),
    }
    results.append({
        "gate": "G6",
        "name": "live-fire VOLATILITY-CE-01 anchor under v2 basis",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": {k: bool(v) for k, v in checks.items()},
        "evidence_cutoff": cutoff,
        "v1_full_sharpe": res_v1["metrics"].get("sharpe"),
        "v2_full_sharpe": res_v2["metrics"].get("sharpe"),
        "v1_max_dd": res_v1["metrics"].get("max_dd"),
        "v2_max_dd": res_v2["metrics"].get("max_dd"),
        "v1_num_trades": res_v1["metrics"].get("num_trades"),
        "v2_num_trades": res_v2["metrics"].get("num_trades"),
        "fee_total_v1": round(fee_v1, 2), "fee_total_v2": round(fee_v2, 2),
        "cost_v2_stats": st,
        "note": "demonstration only, zero selection -> not a ledger trial",
    })
    return all(checks.values())


def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (bool, int, float, str)) or o is None:
        return o
    return str(o)


def main():
    t0 = time.time()
    results = []
    print("loading core48 panel (432-replication shape)...", flush=True)
    prices = pg.load_core48_like_432()
    print(f"  {len(prices)} bare-code symbols", flush=True)

    all_ok = True
    all_ok &= gate_g0(results)
    all_ok &= gate_g1(results, prices)
    all_ok &= gate_g2(results)
    all_ok &= gate_g3(results)
    all_ok &= gate_g4(results)
    all_ok &= gate_g5(results)
    all_ok &= gate_g6(results)

    for r in results:
        print(f"[{r['status']}] {r['gate']} {r['name']}", flush=True)

    payload = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "task": "T-2026-09-23-02 deliverable 3/7 (D5 cost-basis v2)",
        "engine_change": "additive cost_v2 flag (default None = legacy "
                         "byte-identical); ADV(20d) tiers 2/5/10bp + 1% ADV "
                         "entry fill cap; missing-ADV -> 10bp conservative, "
                         "no cap, counted",
        "all_pass": bool(all_ok),
        "elapsed_sec": round(time.time() - t0, 1),
        "audit": {"workers": 1, "purpose": "tooling-gate (engine/rules "
                   "verification, zero strategy selection)",
                  "ledger_trials_added": 0},
        "gates": results,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(_jsonable(payload), fh, ensure_ascii=False, indent=2)
    print(f"\nSummary: {'ALL PASS' if all_ok else 'GATE FAIL'} "
          f"({round(time.time() - t0, 1)}s) -> {OUT_JSON}", flush=True)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
