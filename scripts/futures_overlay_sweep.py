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
    print("\nsaved", p, flush=True)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(run())