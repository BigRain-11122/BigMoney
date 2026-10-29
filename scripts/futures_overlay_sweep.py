"""Futures-overlay weight sweep on the shipped ETF book (descriptive shadow face).

Why this exists
---------------
`results/futures_tsmom_signal.json` publishes ONE point: sleeve 50/50 with the ETF book
(Sharpe 1.059 vs 0.98 alone). A single weight is a single decision sequence -- the r1262 /
r1131 lesson. This face measures the whole overlay axis (0/10/20/25/33/50 %) on the same
panels, at the same cost, with the same execution lag, and reports where the improvement
stops. It selects nothing: no weight is "the answer", the optimum below is in-sample.

Method
------
* futures leg  = futures_tsmom_probe.tsmom_weights/run_weights (imported, not re-implemented):
  sign(60d momentum) * risk parity, |w|<=2, gross<=3, weights decided at close t held t->t+1,
  1bp per side.
* ETF leg      = futures_tsmom_probe.etf_book_series() = the shipped book's own equity curve
  (open-to-open, 10bp per side, 8% vol target) -- the exact series the card prices.
* blend        = daily returns  (1-f) * book + f * sleeve, compounded.
  Both legs carry an 8% vol target, so a capital split is close to a risk split; the
  realised vol of every blend is published anyway rather than assumed.

Cost ladder (why it is the same face, not a second one)
-------------------------------------------------------
The sweep above charges the sleeve 1bp per side. That is a placeholder, not a measurement, and
an overlay that only pays at 1bp is not a tradeable overlay. So the same weights are re-priced
at 1/3/5/10 bp per side and the equal-risk reading is republished for each level, together with
the per-weight breakeven: the highest per-side cost at which the sleeve still helps. Nothing is
re-selected -- the weights, the panels, the execution lag and the vol target are identical, only
the friction number moves.

Honest scope: roll cost, margin and financing/carry are not modelled (main-continuous splice
hides them), the ETF leg's universe is survivors, and the best weight here is chosen on the
same data it is measured on. This is a measurement face, NOT an order, NOT a book change.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import futures_tsmom_probe as P                      # noqa: E402
from config import PATHS                             # noqa: E402

WEIGHTS = [0.0, 0.10, 0.20, 0.25, 1.0 / 3.0, 0.50]
LOOKBACKS = {"tsmom60": 60, "tsmom120": 120}
COST_GRID_BP = [1.0, 3.0, 5.0, 10.0]   # per side, on the futures sleeve
BREAKEVEN_WEIGHT = 1.0 / 3.0            # the weight the shipped card publishes
BAND_GRID = [0.0, 0.05, 0.10, 0.20, 0.30]   # no-trade band on the sleeve's own weights


def blend_returns(etf_r, sleeve_r, f):
    """Compounded blend: f of the risk budget in the sleeve, (1-f) in the book."""
    idx = etf_r.index.intersection(sleeve_r.index)
    a = etf_r.reindex(idx).fillna(0.0)
    b = sleeve_r.reindex(idx).fillna(0.0)
    return (1.0 - f) * a + f * b


def eq_from_returns(r, start=1.0):
    return (start * (1.0 + r).cumprod())


def stats_for(etf_r, sleeve_r, f, label):
    r = blend_returns(etf_r, sleeve_r, f)
    if len(r) < 60:
        return {"label": label, "note": "short"}
    eq = eq_from_returns(r)
    st = P.stats(eq, label)
    st["realised_vol"] = round(float(r.std() * np.sqrt(252)), 4)
    st["weight_in_sleeve"] = round(float(f), 4)
    st["worst_day"] = round(float(r.min()), 4)
    st["worst_month"] = round(float(r.resample("ME").apply(lambda x: (1 + x).prod() - 1).min()), 4)
    st["positive_month_share"] = round(
        float((r.resample("ME").apply(lambda x: (1 + x).prod() - 1) > 0).mean()), 3)
    return st


def window_stats(etf_r, sleeve_r, f, mask, label):
    return stats_for(etf_r[mask], sleeve_r[mask], f, label)


def row_for_weight(rows, f):
    """Rows store weight_in_sleeve rounded to 4dp (1/3 -> 0.3333); match on that grid,
    otherwise the exact float 1/3 silently matches nothing."""
    key = round(float(f), 4)
    return next((r for r in rows if round(float(r["weight_in_sleeve"]), 4) == key), None)


def breakeven_cost(ladder, f):
    """Highest per-side cost (bp) at which weight f still helps at equal risk.

    The ladder is climbed in ascending cost order and the scan stops at the first
    non-positive reading: a positive number that reappears at a HIGHER cost than a
    non-positive one is noise, not a breakeven."""
    best = None
    for blk in sorted(ladder, key=lambda b: b["cost_per_side_bp"]):
        row = row_for_weight(blk["rows"], f)
        if row is None:
            continue
        d = row.get("at_equal_vol_delta_cagr_pp")
        if d is None or d <= 0:
            break
        best = blk["cost_per_side_bp"]
    return best


def cost_ladder(close, w, book_r, book_vol, book_ref, tag):
    """Re-price the SAME sleeve weights at rising per-side cost; nothing is re-selected.

    book_vol = the book's own realised vol (the equal-risk anchor), book_ref = the f=0 row
    of the 1bp sweep, so every cost level is measured against ONE anchor rather than
    against itself."""
    ladder = []
    for bp in COST_GRID_BP:
        eq, turn, _ = P.run_weights(close, w, cost=bp / 10000.0)
        sleeve_r = P.daily_returns(eq)
        idx = book_r.index.intersection(sleeve_r.index)
        e = book_r.reindex(idx).fillna(0.0)
        s = sleeve_r.reindex(idx).fillna(0.0)
        rows = []
        for f in WEIGHTS:
            row = stats_for(e, s, f, "%s_c%gbp_f%02d" % (tag, bp, round(f * 100)))
            eq_b = eq_from_returns(blend_returns(e, s, f))
            at = P.stats(P.vol_normalize(eq_b, book_vol), "%s_c%gbp_scaled_f%02d"
                         % (tag, bp, round(f * 100)))
            row["at_equal_vol"] = at
            row["at_equal_vol_delta_cagr_pp"] = round(
                (at.get("cagr", 0) - book_ref["at_equal_vol"].get("cagr", 0)) * 100, 2)
            row["at_equal_vol_delta_maxdd_pp"] = round(
                (at.get("maxdd", 0) - book_ref["at_equal_vol"].get("maxdd", 0)) * 100, 2)
            rows.append(row)
        ladder.append({"cost_per_side_bp": bp,
                       "sleeve_turnover_total": round(turn, 1),
                       "rows": rows})
    return ladder


def banded_weights(w, band):
    """No-trade band (hysteresis) on the sleeve's own target weights.

    The cost ladder said the overlay only clears at 1-3bp per side, i.e. its problem is
    decision FREQUENCY, not signal quality. This damps the frequency without changing what
    the sleeve is allowed to hold:

      * entry from flat, exit to flat and a sign flip ALWAYS execute -- participation is
        not traded away, only the re-sizing of an already-open position is damped;
      * inside an open position a target that moves less than `band` (absolute weight) is
        ignored and the held weight stays;
      * a missing target (NaN row) goes flat, exactly like the baseline runner, so the
        band is the only difference between the two paths -- a data gap is not a trading
        decision.

    Causal by construction: out[t] reads w[<=t] and out[t-1] only.
    """
    if band <= 0:
        return w
    arr = np.asarray(w.to_numpy(), dtype=float)
    out = np.zeros_like(arr)
    held = np.zeros(arr.shape[1])
    for i in range(arr.shape[0]):
        tgt = arr[i]
        live = np.isfinite(tgt)
        t = np.where(live, tgt, 0.0)
        structural = (held == 0.0) | (t == 0.0) | (np.sign(t) != np.sign(held))
        small = np.abs(t - held) <= band
        held = np.where(live, np.where(structural | ~small, t, held), 0.0)
        out[i] = held
    return pd.DataFrame(out, index=w.index, columns=w.columns)


def band_face(close, w, book_r, book_vol, book_ref, tag):
    """Re-price the SAME decisions under rising no-trade bands (nothing re-selected).

    Two readings per band, because a band is not free: the turnover it removes and the
    gross return it gives up. A band that halves turnover by halving the position is not a
    fix. Every band is charged the whole cost ladder, so "does cutting the rebalance
    frequency move the breakeven" is answered against one anchor throughout."""
    rows = []
    for band in BAND_GRID:
        wb = banded_weights(w, band)
        eq0, turn, _ = P.run_weights(close, wb, cost=0.0)
        gross_cagr = P.stats(eq0, "%s_b%03d_gross" % (tag, int(round(band * 1000)))).get("cagr")
        cost_rows = []
        for bp in COST_GRID_BP:
            eq, turn_bp, _ = P.run_weights(close, wb, cost=bp / 10000.0)
            sleeve_r = P.daily_returns(eq)
            idx = book_r.index.intersection(sleeve_r.index)
            e = book_r.reindex(idx).fillna(0.0)
            s = sleeve_r.reindex(idx).fillna(0.0)
            eq_b = eq_from_returns(blend_returns(e, s, BREAKEVEN_WEIGHT))
            at = P.stats(P.vol_normalize(eq_b, book_vol),
                         "%s_b%03d_c%gbp" % (tag, int(round(band * 1000)), bp))
            cost_rows.append({
                "cost_per_side_bp": bp,
                "turnover_total": round(turn_bp, 1),
                "equal_risk_delta_cagr_pp": round(
                    (at.get("cagr", 0) - book_ref["at_equal_vol"].get("cagr", 0)) * 100, 2),
                "equal_risk_delta_maxdd_pp": round(
                    (at.get("maxdd", 0) - book_ref["at_equal_vol"].get("maxdd", 0)) * 100, 2),
            })
        breakeven = None
        for cr in sorted(cost_rows, key=lambda c: c["cost_per_side_bp"]):
            d = cr["equal_risk_delta_cagr_pp"]
            if d is None or d <= 0:
                break
            breakeven = cr["cost_per_side_bp"]
        rows.append({
            "band": band,
            "sleeve_turnover_total": round(turn, 1),
            "gross_cagr_0bp": round(gross_cagr, 4) if gross_cagr is not None else None,
            "breakeven_bp": breakeven,
            "cost_rows": cost_rows,
        })

    base_turn = rows[0]["sleeve_turnover_total"]
    base_gross = rows[0]["gross_cagr_0bp"]
    for r in rows:
        r["turnover_cut_pct"] = (round((1.0 - r["sleeve_turnover_total"] / base_turn) * 100, 1)
                                 if base_turn else None)
        r["gross_give_up_pp"] = (round((r["gross_cagr_0bp"] - base_gross) * 100, 2)
                                 if (r["gross_cagr_0bp"] is not None
                                     and base_gross is not None) else None)
    return rows


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

    idx = pd.bdate_range("2020-01-01", periods=300)
    rng = np.random.default_rng(7)
    a = pd.Series(rng.normal(0.0003, 0.005, len(idx)), index=idx)
    b = pd.Series(rng.normal(0.0001, 0.004, len(idx)), index=idx)

    chk("L1 f=0 reproduces the book leg exactly",
        np.allclose(blend_returns(a, b, 0.0).values, a.values))
    chk("L2 f=1 reproduces the sleeve leg exactly",
        np.allclose(blend_returns(a, b, 1.0).values, b.values))
    chk("L3 f=0.5 is the arithmetic mean of the two daily legs",
        np.allclose(blend_returns(a, b, 0.5).values, ((a + b) / 2).values))
    # the mechanism must actually fire before any equivalence is believed (r1261 law)
    r0, r50 = blend_returns(a, b, 0.0), blend_returns(a, b, 0.5)
    chk("L4 the blend really moves away from the book",
        abs(float(r50.std()) - float(r0.std())) > 0.0 or not r50.equals(r0))
    chk("L5 alignment keeps the shorter leg's index",
        len(blend_returns(a[:200], b, 0.5)) == 200)
    st = stats_for(a, b, 0.0, "book")
    chk("L6 weight 0 reports the book's own vol", st["weight_in_sleeve"] == 0.0,
        "vol %.4f" % st["realised_vol"])
    chk("L7 stats carry the money-shape fields",
        all(k in st for k in ("cagr", "sharpe", "maxdd", "worst_month", "positive_month_share")))
    chk("L8 blend of identical legs is the leg itself",
        np.allclose(blend_returns(a, a, 0.3).values, a.values))
    chk("L9 a weight outside [0,1] is reported, not silently clamped",
        abs(float(blend_returns(a, b, 1.5).mean()) - float((1.5 * b - 0.5 * a).mean())) < 1e-12)

    # --- cost ladder legs -------------------------------------------------------
    px = pd.DataFrame({"v1": 100 * (1 + pd.Series(rng.normal(0.0004, 0.012, 400), index=pd.bdate_range("2020-01-01", periods=400))).cumprod(),
                       "v2": 100 * (1 + pd.Series(rng.normal(-0.0002, 0.011, 400), index=pd.bdate_range("2020-01-01", periods=400))).cumprod()})
    wts = P.tsmom_weights(px, lookback=20)
    eq_c0, turn0, _ = P.run_weights(px, wts, cost=0.0)
    eq_c10, _, _ = P.run_weights(px, wts, cost=0.0010)
    chk("L10 the cost mechanism actually fires (rebalance happened)", turn0 > 0,
        "turnover %.2f" % turn0)
    chk("L11 a heavier per-side cost leaves the same weights worse off",
        float(eq_c10.iloc[-1]) < float(eq_c0.iloc[-1]),
        "eq0 %.4f vs eq10bp %.4f" % (float(eq_c0.iloc[-1]), float(eq_c10.iloc[-1])))

    def _row(f, d):
        return {"weight_in_sleeve": f, "at_equal_vol_delta_cagr_pp": d}
    ladder_fx = [{"cost_per_side_bp": 1.0, "rows": [_row(round(1 / 3.0, 4), 2.0)]},
                 {"cost_per_side_bp": 3.0, "rows": [_row(round(1 / 3.0, 4), 1.1)]},
                 {"cost_per_side_bp": 5.0, "rows": [_row(round(1 / 3.0, 4), -0.2)]},
                 {"cost_per_side_bp": 10.0, "rows": [_row(round(1 / 3.0, 4), -1.4)]}]
    chk("L12 breakeven is the last positive step of the ladder",
        breakeven_cost(ladder_fx, 1 / 3.0) == 3.0,
        "rows store 0.3333 while the caller asks for 1/3 -> must still match")
    chk("L13 a sleeve that never clears the book has no breakeven",
        breakeven_cost([{"cost_per_side_bp": 1.0, "rows": [_row(round(1 / 3.0, 4), -0.1)]}], 1 / 3.0) is None)
    noncontig = [{"cost_per_side_bp": 1.0, "rows": [_row(round(1 / 3.0, 4), 2.0)]},
                 {"cost_per_side_bp": 3.0, "rows": [_row(round(1 / 3.0, 4), -1.0)]},
                 {"cost_per_side_bp": 5.0, "rows": [_row(round(1 / 3.0, 4), 0.5)]}]
    chk("L14 a positive reading after a negative one does not extend the breakeven",
        breakeven_cost(noncontig, 1 / 3.0) == 1.0)
    chk("L15 a weight absent from the ladder reports None rather than borrowing a neighbour's",
        breakeven_cost(ladder_fx, 0.5) is None)

    # --- no-trade band legs ------------------------------------------------------
    wf = pd.DataFrame({"A": [0.10, 0.12, 0.50, 0.50]},
                      index=pd.bdate_range("2020-01-01", periods=4))
    chk("L16 a zero band is the identity (the baseline path is untouched)",
        banded_weights(wf, 0.0).equals(wf))
    got = banded_weights(wf, 0.05)["A"].tolist()
    chk("L17 a move inside the band is ignored, a move outside it is taken",
        all(abs(g - e) < 1e-12 for g, e in zip(got, [0.10, 0.10, 0.50, 0.50])),
        "band 0.05 -> %s" % [round(x, 4) for x in got])
    wn = pd.DataFrame({"A": [0.30, float("nan"), 0.30]},
                      index=pd.bdate_range("2020-01-01", periods=3))
    gotn = banded_weights(wn, 0.05)["A"].tolist()
    chk("L18 a missing target goes flat instead of holding a stale position",
        all(abs(g - e) < 1e-12 for g, e in zip(gotn, [0.30, 0.0, 0.30])),
        "NaN row -> %s" % [round(x, 4) for x in gotn])
    ws = pd.DataFrame({"A": [0.10, -0.30, 0.0]},
                      index=pd.bdate_range("2020-01-01", periods=3))
    gots = banded_weights(ws, 0.50)["A"].tolist()
    chk("L19 a sign flip and an exit are structural -- a wide band cannot block them",
        all(abs(g - e) < 1e-12 for g, e in zip(gots, [0.10, -0.30, 0.0])),
        "band 0.50 -> %s" % [round(x, 4) for x in gots])
    # the mechanism must actually fire before any turnover claim is believed (r1261 law)
    t_no, t_lo, t_hi = (P.run_weights(px, banded_weights(wts, b), cost=0.0)[1]
                        for b in (0.0, 0.05, 0.30))
    chk("L20 the band really cuts turnover and a wider band never adds it",
        t_no > t_hi > 0.0 and t_lo >= t_hi,
        "turnover %.1f -> %.1f -> %.1f (the remainder is structural: entries, exits, "
        "sign flips, which a band must not damper)" % (t_no, t_lo, t_hi))
    chk("L21 cost does not change the decisions the band leaves (one sequence per band)",
        abs(P.run_weights(px, banded_weights(wts, 0.05), cost=0.0)[1]
            - P.run_weights(px, banded_weights(wts, 0.05), cost=0.0010)[1]) < 1e-9,
        "turnover at 0bp == turnover at 10bp")
    print("\nselftest %d/%d" % (ok, total), flush=True)
    return 0 if ok == total else 1


def run():
    close = P.load_panel()
    ser_etf, etf_meta = P.etf_book_series()
    etf_r = P.daily_returns(ser_etf)

    out = {
        "evidence_cutoff": str(close.index[-1].date()),
        "face": "descriptive shadow sweep; selects no weight, changes no book, places no order",
        "legs": {
            "etf_book": dict(etf_meta, source="futures_tsmom_probe.etf_book_series (shipped card pricing)",
                             vol_target=P.TARGET_VOL),
            "futures_sleeve": dict(source="data/futures_daily main-continuous, risk parity, sign(60d)",
                                   varieties=int(close.shape[1]), bars=int(close.shape[0]),
                                   cost_per_side=P.COST_PER_SIDE, vol_target=P.TARGET_VOL),
        },
        "not_modelled": "roll cost, margin, financing/carry, contract multipliers; ETF universe is survivors",
        "sweeps": {},
    }

    for tag, lookback in LOOKBACKS.items():
        w = P.tsmom_weights(close, lookback=lookback)
        eq, turn, _ = P.run_weights(close, w)
        sleeve_r = P.daily_returns(eq)
        idx = etf_r.index.intersection(sleeve_r.index)
        e = etf_r.reindex(idx).fillna(0.0)
        s = sleeve_r.reindex(idx).fillna(0.0)
        corr = P.pair_corr(eq_from_returns(e), eq_from_returns(s))

        rows = []
        for f in WEIGHTS:
            row = stats_for(e, s, f, "%s_f%02d" % (tag, round(f * 100)))
            rows.append(row)

        # A heavier sleeve weight also LOWERS total risk, so the raw CAGR drop is a leverage
        # artifact and not a quality statement (r1291 law). Re-scale every blend to the book's
        # own realised vol and publish that reading next to the raw one.
        book_vol = rows[0]["realised_vol"]
        for f, row in zip(WEIGHTS, rows):
            eq_b = eq_from_returns(blend_returns(e, s, f))
            scaled = P.vol_normalize(eq_b, book_vol)
            at = P.stats(scaled, "%s_scaled_f%02d" % (tag, round(f * 100)))
            at["weight_in_sleeve"] = round(float(f), 4)
            at["target_vol"] = round(float(book_vol), 4)
            row["at_equal_vol"] = at

        base = rows[0]
        for row in rows:
            row["delta_cagr_pp"] = round((row.get("cagr", 0) - base.get("cagr", 0)) * 100, 2)
            row["delta_sharpe"] = round(row.get("sharpe", 0) - base.get("sharpe", 0), 3)
            row["delta_maxdd_pp"] = round((row.get("maxdd", 0) - base.get("maxdd", 0)) * 100, 2)
            eq_at = row["at_equal_vol"]
            row["at_equal_vol_delta_cagr_pp"] = round(
                (eq_at.get("cagr", 0) - base["at_equal_vol"].get("cagr", 0)) * 100, 2)
            row["at_equal_vol_delta_maxdd_pp"] = round(
                (eq_at.get("maxdd", 0) - base["at_equal_vol"].get("maxdd", 0)) * 100, 2)

        is_mask = e.index <= pd.Timestamp(P.IS_END)
        oos_mask = ~is_mask
        out["sweeps"][tag] = {
            "lookback": lookback,
            "common_window": [str(idx[0].date()), str(idx[-1].date())],
            "bars": int(len(idx)),
            "corr_to_book": round(float(corr), 3) if corr is not None else None,
            "sleeve_turnover_total": round(turn, 1),
            "full": rows,
            "is": [window_stats(e, s, f, is_mask, "%s_is_f%02d" % (tag, round(f * 100)))
                   for f in WEIGHTS],
            "oos": [window_stats(e, s, f, oos_mask, "%s_oos_f%02d" % (tag, round(f * 100)))
                    for f in WEIGHTS],
        }

        best = max(rows[1:], key=lambda r: r.get("sharpe", -9))
        out["sweeps"][tag]["best_sharpe_weight"] = best["weight_in_sleeve"]
        out["sweeps"][tag]["best_sharpe"] = best.get("sharpe")
        out["sweeps"][tag]["note"] = (
            "best_sharpe_weight is IN-SAMPLE over the same window it is measured on; "
            "it is a description of the curve, not a recommended allocation")

        ladder = cost_ladder(close, w, etf_r, book_vol, base, tag)
        out["sweeps"][tag]["cost_ladder"] = ladder
        out["sweeps"][tag]["cost_breakeven_bp"] = {
            "weight": round(BREAKEVEN_WEIGHT, 4),
            "max_cost_per_side_bp": breakeven_cost(ladder, BREAKEVEN_WEIGHT),
            "costs_tested_bp": COST_GRID_BP,
            "note": ("None means the sleeve did not clear the book even at the lowest cost "
                     "tested; the ladder stops at the first non-positive level"),
        }
        out["sweeps"][tag]["cost_at_published_weight"] = [
            {"cost_per_side_bp": blk["cost_per_side_bp"],
             "turnover_total": blk["sleeve_turnover_total"],
             "equal_risk_delta_cagr_pp": (row_for_weight(blk["rows"], BREAKEVEN_WEIGHT) or {}).get(
                 "at_equal_vol_delta_cagr_pp"),
             "equal_risk_delta_maxdd_pp": (row_for_weight(blk["rows"], BREAKEVEN_WEIGHT) or {}).get(
                 "at_equal_vol_delta_maxdd_pp")}
            for blk in ladder]

        bands = band_face(close, w, etf_r, book_vol, base, tag)
        # How much of the friction is STRUCTURAL (entries, exits, sign flips -- which a
        # no-trade band must not damper) versus re-sizing? An effectively infinite band
        # damps every re-size and leaves only the structural floor, so the split is
        # measured, not asserted.
        _, struct_turn, _ = P.run_weights(close, banded_weights(w, 10.0), cost=0.0)
        base_turn = bands[0]["sleeve_turnover_total"]
        out["sweeps"][tag]["turnover_control"] = {
            "bands_tested": BAND_GRID,
            "weight": round(BREAKEVEN_WEIGHT, 4),
            "structural_turnover_total": round(struct_turn, 1),
            "structural_share_pct": (round(struct_turn / base_turn * 100, 1) if base_turn else None),
            "resizing_share_pct": (round((1 - struct_turn / base_turn) * 100, 1) if base_turn else None),
            "note": ("band = absolute weight change ignored inside an already-open position; "
                     "entries, exits and sign flips always execute, so this measures rebalance "
                     "frequency, not participation. gross_give_up_pp is what the band costs "
                     "BEFORE any cost saving, and it is the honest half of the trade. "
                     "structural_turnover_total is the floor no band can remove"),
            "rows": bands,
        }

    p = os.path.join(PATHS.results_dir, "futures_overlay_sweep.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    for tag, blk in out["sweeps"].items():
        print("\n%s  window %s..%s  bars %d  corr %.3f"
              % (tag, blk["common_window"][0], blk["common_window"][1], blk["bars"],
                 blk["corr_to_book"] if blk["corr_to_book"] is not None else float("nan")), flush=True)
        print("  f     cagr      sharpe   maxdd    vol     dSR     dCAGR(pp)  dMDD(pp)", flush=True)
        for r in blk["full"]:
            print("  %4.2f  %6.2f%%  %6.3f  %6.2f%%  %5.2f%%  %+6.3f  %+8.2f  %+8.2f"
                  % (r["weight_in_sleeve"], r["cagr"] * 100, r["sharpe"], r["maxdd"] * 100,
                     r["realised_vol"] * 100, r["delta_sharpe"], r["delta_cagr_pp"],
                     r["delta_maxdd_pp"]), flush=True)
        print("  at equal risk (rescaled to the book's own vol %.2f%%):"
              % (blk["full"][0]["realised_vol"] * 100), flush=True)
        print("  f     cagr      sharpe   maxdd    dCAGR(pp)  dMDD(pp)", flush=True)
        for r in blk["full"]:
            print("  %4.2f  %6.2f%%  %6.3f  %6.2f%%  %+8.2f  %+8.2f"
                  % (r["weight_in_sleeve"], r["at_equal_vol"]["cagr"] * 100,
                     r["at_equal_vol"]["sharpe"], r["at_equal_vol"]["maxdd"] * 100,
                     r["at_equal_vol_delta_cagr_pp"], r["at_equal_vol_delta_maxdd_pp"]),
                  flush=True)
        print("  cost ladder at the published weight f=%.2f (equal risk vs the book):"
              % BREAKEVEN_WEIGHT, flush=True)
        print("  cost/side  turnover   dCAGR(pp)  dMDD(pp)", flush=True)
        for row in blk["cost_at_published_weight"]:
            print("  %5.1fbp    %8.1f   %+8.2f  %+8.2f"
                  % (row["cost_per_side_bp"], row["turnover_total"] or 0.0,
                     row["equal_risk_delta_cagr_pp"] if row["equal_risk_delta_cagr_pp"] is not None else float("nan"),
                     row["equal_risk_delta_maxdd_pp"] if row["equal_risk_delta_maxdd_pp"] is not None else float("nan")),
                  flush=True)
        tc = blk.get("turnover_control") or {}
        if tc.get("rows"):
            print("  turnover control at f=%.2f (band = weight change ignored while open):"
                  % tc["weight"], flush=True)
            print("  structural floor %.1f of %.1f = %.1f%% of all turnover is entries/exits/"
                  "sign flips; only %.1f%% is re-sizing"
                  % (tc["structural_turnover_total"], tc["rows"][0]["sleeve_turnover_total"],
                     tc["structural_share_pct"] or 0.0, tc["resizing_share_pct"] or 0.0), flush=True)
            print("  band   turnover  cut     gross CAGR  give-up(pp)  breakeven", flush=True)
            for r in tc["rows"]:
                print("  %4.2f   %8.1f  %5.1f%%  %8.2f%%  %+9.2f     %s"
                      % (r["band"], r["sleeve_turnover_total"], r["turnover_cut_pct"] or 0.0,
                         (r["gross_cagr_0bp"] or 0.0) * 100, r["gross_give_up_pp"] or 0.0,
                         ("%gbp" % r["breakeven_bp"]) if r["breakeven_bp"] else "none"),
                      flush=True)
            print("  equal-risk dCAGR(pp) by cost, per band:", flush=True)
            print("  band   " + "".join("%9s" % ("%gbp" % bp) for bp in COST_GRID_BP), flush=True)
            for r in tc["rows"]:
                print("  %4.2f   " % r["band"] + "".join(
                    "%+9.2f" % (cr["equal_risk_delta_cagr_pp"]
                                if cr["equal_risk_delta_cagr_pp"] is not None else float("nan"))
                    for cr in sorted(r["cost_rows"], key=lambda c: c["cost_per_side_bp"])), flush=True)
        be = blk["cost_breakeven_bp"]["max_cost_per_side_bp"]
        print("  breakeven = %s per side" % ("%.0fbp" % be if be is not None else "none at any cost tested"),
              flush=True)
    print("\nsaved", p, flush=True)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(run())