"""Second book, slice 2: can the futures TSMOM sleeve actually be traded, and with how
much money?

r1297 measured the sleeve as a continuous-weight, cost-only backtest and published
+1.37%/SR 0.27 (tsmom60) at 8% vol, correlation 0.078 to the shipped ETF book. That is a
signal measurement, not a tradeable claim. Three things stand between the two, and all
three are arithmetic on data already on disk:

  1. CONTRACT GRANULARITY. The backtest pretends any dollar weight is attainable. Futures
     trade in whole contracts whose notional is fixed by price times multiplier, so at
     small capital a variety cannot be held at its target weight at all. This script
     rounds every weight to whole contracts (never over-shooting: floor on the absolute
     notional) and measures the tracking cost of that rounding as a function of capital.
     The output includes the capital FLOOR: the smallest account in which every variety
     that wants a position can hold at least one lot.

  2. MARGIN. Gross notional at 8% vol with the 3.0 gross cap is a multiple of capital;
     margin is charged on notional, not on equity. Required margin = sum(|w_i| * rate_i)
     and the exchange/minimum rates here are APPROXIMATIONS disclosed as a parameter, not
     a broker fact.

  3. ROLL AND COMMISSION. Main-continuous series splice contracts, so the price gap at a
     roll sits inside the return series -- the size and even the sign of that gap is a
     data artefact. Rather than pretending to know it, this script charges an explicit
     per-roll haircut over a disclosed roll-frequency convention and publishes the net
     CAGR as a grid over (commission, roll cost, capital). If the sleeve only works at
     zero roll cost it does not work.

Exploratory measurement: no live face, no registry entry, no capital claim.
Outputs results/futures_sleeve_economics.json.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import numpy as np
import pandas as pd

from config import PATHS
import futures_tsmom_probe as P

# Contract multiplier: quoted price -> CNY notional per contract.
# Bond futures quote clean price per 100 face, so notional = price * (face/100).
MULTIPLIER = {
    "AU": 1000.0,        # CNY/gram x 1000 g
    "RB": 10.0,          # CNY/ton x 10 t
    "SC": 1000.0,        # CNY/barrel x 1000 bbl
    "IC": 200.0,         # index points x 200
    "IF": 300.0,         # index points x 300
    "IH": 300.0,         # index points x 300
    "IM": 200.0,         # index points x 200
    "T": 10000.0,        # clean price x (1,000,000 face / 100)
    "TF": 10000.0,       # clean price x (1,000,000 face / 100)
    "TS": 20000.0,       # clean price x (2,000,000 face / 100)
}

# Approximate exchange minimum margin rates. Disclosed as a parameter: brokers charge more.
MARGIN_RATE = {
    "AU": 0.09, "RB": 0.09, "SC": 0.12,
    "IC": 0.12, "IF": 0.12, "IH": 0.12, "IM": 0.12,
    "T": 0.02, "TF": 0.02, "TS": 0.02,
}

# Main-contract rolls per year (convention: index futures quarterly, the rest roughly
# bi-monthly). Used only to turn a per-roll haircut into an annual drag.
ROLLS_PER_YEAR = {
    "AU": 6.0, "RB": 6.0, "SC": 6.0,
    "IC": 4.0, "IF": 4.0, "IH": 4.0, "IM": 4.0,
    "T": 4.0, "TF": 4.0, "TS": 4.0,
}

# Minimum tick size, in the same units as the quoted price. A roll crosses the spread
# twice (sell the old contract, buy the new one), and main-contract spreads are normally
# one tick wide -- so a roll costs ~2 ticks of notional, which is the honest per-variety
# replacement for a uniform "N bp per roll" assumption. Bond futures are the expensive
# ones: 0.005 on a ~100 quote is 5bp per tick, ten times a gold tick.
TICK_SIZE = {
    "AU": 0.02, "RB": 1.0, "SC": 0.1,
    "IC": 0.2, "IF": 0.2, "IH": 0.2, "IM": 0.2,
    "T": 0.005, "TF": 0.005, "TS": 0.002,
}
TICKS_PER_ROLL = 2.0

REF_CAPITAL = 1_000_000.0
CAPITAL_SWEEP = [3e5, 5e5, 1e6, 2e6, 3e6, 5e6, 1e7, 2e7, 5e7]
COMMISSION_BP = [0.5, 1.0, 2.0, 5.0]
ROLL_BP = [0.0, 5.0, 10.0, 20.0]


def unit_notional(close):
    """CNY notional of one contract, from the latest price in the panel."""
    last = close.ffill().iloc[-1]
    return pd.Series({v: float(last[v]) * MULTIPLIER.get(v, 1.0) for v in close.columns})


def margin_rate(close):
    return pd.Series({v: MARGIN_RATE.get(v, 0.12) for v in close.columns})


def rolls_per_year(close):
    return pd.Series({v: ROLLS_PER_YEAR.get(v, 6.0) for v in close.columns})


def lot_weights(w, unit, capital, min_lot_fill=0.0):
    """Round target dollar weights to whole contracts, never over-shooting the target.

    floor on |notional| is deliberate: a rounded-up book would be a quietly levered book,
    and the point of this leg is to measure what granularity COSTS, not to hide it.
    """
    target = w.fillna(0.0).mul(capital)
    lots = np.sign(target) * np.floor(target.abs() / unit)
    exec_ntl = lots.mul(unit, axis=1)
    return exec_ntl.div(capital)


def fill_shortfall(w, w_exec, capital):
    """Fraction of |target notional| that lot rounding could not place."""
    target = w.fillna(0.0).abs().mul(capital).sum(axis=1)
    placed = w_exec.abs().mul(capital).sum(axis=1)
    ok = target > 0
    if not bool(ok.any()):
        return 1.0
    return float((placed[ok] / target[ok]).mean())


def capital_floor(w, unit):
    """Smallest capital at which every variety that ever wants a position can hold 1 lot."""
    need = {}
    for v in w.columns:
        m = float(w[v].abs().max())
        if m <= 0:
            continue
        need[v] = float(unit[v]) / m
    if not need:
        return None, {}
    return max(need.values()), need


def margin_series(w, unit, rate):
    """Required margin as a fraction of capital (w is already a fraction of capital)."""
    return w.abs().mul(rate, axis=1).sum(axis=1)


def annual_roll_drag(w, rolls, roll_bp):
    """Annual return drag from rolling the main contract, per variety, in return terms."""
    mean_abs_w = w.abs().mean()
    per_var = mean_abs_w.mul(rolls) * (roll_bp / 10000.0)
    return float(per_var.sum()), {k: round(float(v), 5) for k, v in per_var.items()}


def roll_cost_bp_from_ticks(close):
    """Per-roll cost per variety, in bp of notional, from tick size x ticks per roll."""
    last = close.ffill().iloc[-1]
    out = {}
    for v in close.columns:
        tick = TICK_SIZE.get(v)
        px = float(last[v])
        if not tick or px <= 0:
            continue
        out[v] = TICKS_PER_ROLL * tick / px * 10000.0
    return pd.Series(out)


def annual_roll_drag_ticks(w, rolls, cost_bp):
    """Same drag, but each variety paid at its own tick-derived cost."""
    mean_abs_w = w.abs().mean()
    per_var = mean_abs_w.mul(rolls).mul(cost_bp.reindex(mean_abs_w.index)) / 10000.0
    return float(per_var.fillna(0.0).sum()), {k: round(float(v), 5) for k, v in per_var.items()}


def split_stats(eq, label):
    """Full / in-sample / out-of-sample stats. stats() has no 'oos' key -- asking it for
    one silently returns None, which is how a grid column can promise a number it never
    computes (r1292 unit-坑 class)."""
    full = P.stats(eq, label)
    full["is"] = P.stats(eq[eq.index <= P.IS_END], label + "_is")
    full["oos"] = P.stats(eq[eq.index > P.IS_END], label + "_oos")
    return full


def equity_with_drag(close, w, cost, annual_drag=0.0, index=None):
    eq, turn, gross = P.run_weights(close, w, cost=cost)
    if annual_drag:
        eq = eq * (1.0 - annual_drag) ** (np.arange(len(eq)) / 252.0)
    if index is not None:
        eq = eq.reindex(index)
    return eq, turn, gross


def tracking(close, w_cont, w_exec, capital, cost=0.0001, annual_drag=0.0):
    """How closely the lot-rounded book follows the continuous one."""
    base, _, _ = P.run_weights(close, w_cont, cost=cost)
    lot, turn, _ = equity_with_drag(close, w_exec, cost, annual_drag)
    idx = base.index.intersection(lot.index)
    a, b = base.reindex(idx), lot.reindex(idx)
    corr = P.pair_corr(a, b)
    s_cont, s_lot = P.stats(a, "continuous"), P.stats(b, "lot")
    return {
        "capital": capital,
        "corr_to_continuous": round(corr, 4) if corr is not None else None,
        "continuous_cagr": s_cont.get("cagr"),
        "lot_cagr": s_lot.get("cagr"),
        "cagr_gap_pp": round(((s_lot.get("cagr") or 0) - (s_cont.get("cagr") or 0)) * 100, 3),
        "lot_sharpe": s_lot.get("sharpe"),
        "lot_maxdd": s_lot.get("maxdd"),
        "notional_placed_frac": round(fill_shortfall(w_cont, w_exec, capital), 4),
        "turnover_total": round(turn, 2),
    }


def contract_count(w_exec, unit, capital, index):
    ntl = w_exec.abs().mul(capital)
    lots = ntl.div(unit, axis=1).sum(axis=1)
    return {"mean_total_lots": round(float(lots[index].mean()), 2),
            "max_total_lots": round(float(lots[index].max()), 1)}


def selftest():
    ok = total = 0

    def chk(label, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[PASS]", label, "|", detail, flush=True)
        else:
            print("[FAIL]", label, "|", detail, flush=True)

    idx = pd.bdate_range("2021-01-01", periods=260)
    close = pd.DataFrame({"T": 100.0 + 0.01 * np.arange(len(idx)),
                          "AU": 400.0 + 0.5 * np.arange(len(idx))}, index=idx)
    unit = unit_notional(close)
    chk("L1 bond notional uses face value, gold uses grams",
        abs(float(unit["T"]) - (100.0 + 0.01 * (len(idx) - 1)) * 10000.0) < 1e-6
        and abs(float(unit["AU"]) - (400.0 + 0.5 * (len(idx) - 1)) * 1000.0) < 1e-6,
        "T=%.0f AU=%.0f" % (unit["T"], unit["AU"]))

    # L2 lot rounding never over-shoots and preserves sign
    w = pd.DataFrame({"T": 0.30, "AU": -0.20}, index=idx)
    cap = 1_000_000.0
    we = lot_weights(w, unit, cap)
    over = (we.abs() > w.abs() + 1e-12).any().any()
    sign_ok = bool(((np.sign(we) == np.sign(w)) | (we == 0)).all().all())
    chk("L2 rounding never over-shoots the target and keeps sign", (not over) and sign_ok,
        "placed frac %.3f" % fill_shortfall(w, we, cap))

    # L3 causality: a lot weight at row t does not change when later rows are appended
    wf = pd.DataFrame({"T": 0.3 * np.sin(np.arange(len(idx)) / 9.0),
                       "AU": 0.2 * np.cos(np.arange(len(idx)) / 7.0)}, index=idx)
    a = lot_weights(wf, unit, cap)
    b = lot_weights(wf.iloc[:150], unit, cap)
    chk("L3 lot weights are causal",
        np.allclose(a.iloc[149].values, b.iloc[149].values), "row 149 identical when truncated")

    # L4 margin is charged on notional: 2 varieties, known weighted rate
    mrate = margin_rate(close)
    m = float(margin_series(w, unit, mrate).iloc[0])
    expect = 0.30 * 0.02 + 0.20 * 0.09
    chk("L4 margin = sum(|w| * rate)", abs(m - expect) < 1e-12, "got %.4f want %.4f" % (m, expect))

    # L5 roll drag: zero haircut is a no-op, and drag reduces CAGR
    rolls = rolls_per_year(close)
    d0, _ = annual_roll_drag(w, rolls, 0.0)
    d10, per_var = annual_roll_drag(w, rolls, 10.0)
    r = close.pct_change().fillna(0.0)
    eq0 = (1.0 + (w.shift(1).fillna(0.0) * r).sum(axis=1)).cumprod()
    s0, s10 = P.stats(eq0, "c0"), P.stats(eq0 * (1 - d10) ** (np.arange(len(eq0)) / 252.0), "c10")
    chk("L5 roll drag is zero at zero haircut and costs CAGR",
        d0 == 0.0 and d10 > 0 and s10["cagr"] < s0["cagr"],
        "drag %.4f/yr, cagr %.4f -> %.4f" % (d10, s0["cagr"], s10["cagr"]))

    # L6 capital floor: it is the smallest account where the widest-need variety gets a lot
    w2 = pd.DataFrame({"T": 0.30, "AU": 0.02}, index=idx)
    floor_c, need = capital_floor(w2, unit)
    per_T = float(unit["T"]) / 0.30
    per_AU = float(unit["AU"]) / 0.02
    chk("L6 capital floor is the binding variety, not the average",
        abs(floor_c - max(per_T, per_AU)) < 1e-6 and need["AU"] > need["T"],
        "floor %.0f (T needs %.0f, AU needs %.0f)" % (floor_c, per_T, per_AU))

    # L7 finer capital tracks better: more money -> smaller relative lot error
    big = tracking(close, w, lot_weights(w, unit, 5e7), 5e7)
    small = tracking(close, w, lot_weights(w, unit, 1e5), 1e5)
    chk("L7 bigger capital tracks the continuous book at least as well",
        (big["notional_placed_frac"] or 0) >= (small["notional_placed_frac"] or 0),
        "5e7 places %.3f vs 1e5 places %.3f"
        % (big["notional_placed_frac"], small["notional_placed_frac"]))

    # L8 an all-NaN weight row is flat, not a crash
    wn = pd.DataFrame(np.nan, index=idx, columns=["T", "AU"])
    we_n = lot_weights(wn, unit, cap)
    chk("L8 missing weights round to flat", float(we_n.abs().sum().sum()) == 0.0,
        "total |w| after rounding = %.6f" % float(we_n.abs().sum().sum()))

    # L9 the tick-based roll cost is per variety, and the bond tick is the dear one.
    # T: 2 ticks x 0.005 on a ~100 quote = 1.0bp; AU: 2 x 0.02 on ~529 = 0.76bp -- the
    # POINT is that they are different numbers, so no single "bp per roll" is honest.
    close_fx = pd.DataFrame({"T": 100.0, "AU": 500.0, "RB": 3500.0}, index=idx[:5])
    bp = roll_cost_bp_from_ticks(close_fx)
    want_t = TICKS_PER_ROLL * 0.005 / 100.0 * 10000.0
    want_au = TICKS_PER_ROLL * 0.02 / 500.0 * 10000.0
    chk("L9 tick-based roll cost is per variety",
        abs(float(bp["T"]) - want_t) < 1e-9 and abs(float(bp["AU"]) - want_au) < 1e-9
        and abs(float(bp["RB"]) - bp["AU"]) > 1e-6,
        "T %.2fbp AU %.2fbp RB %.2fbp" % (bp["T"], bp["AU"], bp["RB"]))

    # L10 split_stats really splits: an 'oos' column that reads None is the r1292 class
    # of defect (a field promising a quantity nobody computes).
    eq = pd.Series(np.linspace(1.0, 1.5, 2000),
                   index=pd.bdate_range("2020-01-01", periods=2000))
    ss = split_stats(eq, "fixture")
    chk("L10 split_stats publishes a real out-of-sample number",
        ss["oos"].get("cagr") is not None and ss["is"].get("cagr") is not None
        and ss["is"]["years"] > 1 and ss["oos"]["years"] > 1,
        "is %.2fy oos %.2fy" % (ss["is"]["years"], ss["oos"]["years"]))

    print("\nselftest %d/%d" % (ok, total), flush=True)
    return 0 if ok == total else 1


def main():
    close = P.load_panel()
    out = {
        "evidence_cutoff": str(close.index[-1].date()),
        "universe": {"varieties": list(close.columns), "bars": int(close.shape[0])},
        "model": {
            "sizing": "risk parity at %.0f%% vol, |w|<=%.1f, gross<=%.1f (r1297 model)"
                      % (P.TARGET_VOL * 100, P.W_CAP, P.GROSS_CAP),
            "lot_rounding": "contracts = sign(w)*floor(|w*capital| / unit_notional)",
            "multiplier": MULTIPLIER,
            "margin_rate_approx": MARGIN_RATE,
            "rolls_per_year_convention": ROLLS_PER_YEAR,
            "not_modelled": "intraday slippage, market impact (futures are deep), tax, "
                            "broker-specific margin, actual roll spread sign",
        },
        "note": "exploratory slice 2; feasibility arithmetic, not a tradeable claim",
    }

    w = P.tsmom_weights(close, lookback=60)
    unit = unit_notional(close)
    mrate = margin_rate(close)
    rolls = rolls_per_year(close)
    w_valid = w.dropna(how="all")

    out["contract_notional_cny"] = {k: round(float(v)) for k, v in unit.items()}
    floor_c, need = capital_floor(w, unit)
    out["capital_floor"] = {
        "cny": round(floor_c) if floor_c else None,
        "per_variety_cny": {k: round(v) for k, v in sorted(need.items(), key=lambda kv: -kv[1])},
        "why": "max over varieties of unit_notional / max|w| -- the variety needing the most "
               "capital to hold one lot sets the floor",
    }

    # gross notional and margin at the continuous weights
    gross = w_valid.abs().sum(axis=1)
    marg = margin_series(w_valid, unit, mrate)
    out["gross_and_margin"] = {
        "gross_notional_leverage_mean": round(float(gross.mean()), 3),
        "gross_notional_leverage_max": round(float(gross.max()), 3),
        "margin_required_frac_mean": round(float(marg.mean()), 4),
        "margin_required_frac_max": round(float(marg.max()), 4),
        "note": "margin fraction of capital is pointwise independent of capital size "
                "(weights are already fractions of capital); capital only moves lot granularity",
    }

    # capital sweep with lot rounding
    rings = []
    for cap in CAPITAL_SWEEP:
        we = lot_weights(w, unit, cap)
        t = tracking(close, w, we, cap)
        t.update(contract_count(we, unit, cap, w.index))
        t["margin_peak_frac"] = round(float(margin_series(we, unit, mrate).max()), 4)
        rings.append(t)
    out["capital_sweep"] = rings

    # cost grid at the reference capital, lot-rounded (what you would actually own)
    we_ref = lot_weights(w, unit, REF_CAPITAL)
    grid = {}
    for comm in COMMISSION_BP:
        for rb in ROLL_BP:
            drag, per_var = annual_roll_drag(w_valid, rolls, rb)
            eq_lot, turn, _ = equity_with_drag(close, we_ref, comm / 10000.0, drag)
            s_lot = split_stats(eq_lot, "lot_%.1fbp_roll%.0fbp" % (comm, rb))
            eq_cont, _, _ = equity_with_drag(close, w, comm / 10000.0, drag)
            s_cont = split_stats(eq_cont, "cont_%.1fbp_roll%.0fbp" % (comm, rb))
            grid["comm%.1fbp_roll%.0fbp" % (comm, rb)] = {
                "annual_roll_drag": round(drag, 4),
                "lot": {k: s_lot.get(k) for k in ("cagr", "sharpe", "maxdd")},
                "lot_oos": s_lot.get("oos", {}).get("cagr"),
                "continuous": {k: s_cont.get(k) for k in ("cagr", "sharpe", "maxdd")},
                "continuous_oos": s_cont.get("oos", {}).get("cagr"),
            }
    out["cost_grid_at_ref_capital"] = {"capital": REF_CAPITAL, "rows": grid}

    drag0 = annual_roll_drag(w_valid, rolls, 0.0)[0]
    out["roll_drag_per_variety_at_10bp"] = annual_roll_drag(w_valid, rolls, 10.0)[1]
    out["roll_drag_zero_check"] = drag0

    # Roll cost from tick sizes: each variety pays its own spread, not a uniform band.
    tick_bp = roll_cost_bp_from_ticks(close)
    out["roll_cost_bp_per_roll_tick_based"] = {k: round(float(v), 3) for k, v in tick_bp.items()}
    tick_grid = {}
    for comm in COMMISSION_BP:
        drag, per_var = annual_roll_drag_ticks(w_valid, rolls, tick_bp)
        eq_lot, _, _ = equity_with_drag(close, we_ref, comm / 10000.0, drag)
        eq_cont, _, _ = equity_with_drag(close, w, comm / 10000.0, drag)
        s_lot, s_cont = split_stats(eq_lot, "lot_tick_%.1fbp" % comm), split_stats(
            eq_cont, "cont_tick_%.1fbp" % comm)
        tick_grid["comm%.1fbp" % comm] = {
            "annual_roll_drag": round(drag, 4),
            "roll_drag_per_variety": per_var,
            "lot": {k: s_lot.get(k) for k in ("cagr", "sharpe", "maxdd")},
            "lot_oos": s_lot.get("oos", {}).get("cagr"),
            "continuous": {k: s_cont.get(k) for k in ("cagr", "sharpe", "maxdd")},
            "continuous_oos": s_cont.get("oos", {}).get("cagr"),
        }
    out["cost_grid_tick_based_roll"] = tick_grid

    # Which friction actually eats the sleeve? Turnover x commission vs roll drag.
    turn_per_year = float(w_valid.diff().abs().sum(axis=1).sum()) / max(
        1e-9, (close.index[-1] - close.index[0]).days / 365.25)
    out["friction_attribution"] = {
        "turnover_per_year": round(turn_per_year, 2),
        "commission_drag_at_1bp": round(turn_per_year * 0.0001, 4),
        "roll_drag_tick_based": round(annual_roll_drag_ticks(w_valid, rolls, tick_bp)[0], 4),
        "roll_drag_at_10bp_uniform": round(annual_roll_drag(w_valid, rolls, 10.0)[0], 4),
        "reads": "compare with the sleeve's gross return before costs; whichever drag is "
                 "larger is the one a cost-cutting redesign has to attack",
    }

    # the honest headline: worst-case within the disclosed band
    worst = min(((k, v["lot"]["cagr"] or -9) for k, v in grid.items()), key=lambda kv: kv[1])
    best = max(((k, v["lot"]["cagr"] or -9) for k, v in grid.items()), key=lambda kv: kv[1])
    out["verdict"] = {
        "best_lot_cagr": {"cell": best[0], "cagr": best[1]},
        "worst_lot_cagr": {"cell": worst[0], "cagr": worst[1]},
        "capital_floor_cny": round(floor_c) if floor_c else None,
        "reads": "a sleeve whose CAGR is the difference between the best and worst cell of "
                 "this grid is a cost artefact, not a return stream",
    }

    p = os.path.join(PATHS.results_dir, "futures_sleeve_economics.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("capital floor CNY %.0f" % (floor_c or 0), flush=True)
    print("gross lev mean %.2f max %.2f | margin mean %.2f max %.2f"
          % (gross.mean(), gross.max(), marg.mean(), marg.max()), flush=True)
    for r in rings:
        print("cap %10.0f corr %.3f cagr %6.2f%% gap %6.2fpp placed %.3f margin %.2f lots %.1f"
              % (r["capital"], r["corr_to_continuous"] or 0, (r["lot_cagr"] or 0) * 100,
                 r["cagr_gap_pp"], r["notional_placed_frac"], r["margin_peak_frac"],
                 r["mean_total_lots"] or 0), flush=True)
    for k, v in out["cost_grid_at_ref_capital"]["rows"].items():
        print("%-22s lot cagr %6.2f%% SR %5.3f dd %6.2f%% | cont %6.2f%%"
              % (k, (v["lot"]["cagr"] or 0) * 100, v["lot"]["sharpe"] or 0,
                 (v["lot"]["maxdd"] or 0) * 100, (v["continuous"]["cagr"] or 0) * 100), flush=True)
    print("saved", p, flush=True)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main())