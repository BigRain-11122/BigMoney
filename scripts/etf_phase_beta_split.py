"""Is the 20-phase package excess just beta timing?

r1252 left the question open: the package beats its own equal weight by ~+6.8pp/yr full
window, but every published number so far is a raw return spread. If the package simply
carries a different market beta than the control, a chunk of that spread is factor
exposure, not selection.

Three rulers on the same curves (N=5, R=20, 8bp/side, next-open fill):

  (a) beta decomposition -- OLS beta of package and of control on 510300 daily returns,
      the beta-hedged excess (rp - beta*rm) annualised, and up/down capture ratios;
  (b) market-state split -- split every day by the sign of the trailing 20-bar market
      return and by market up/down *that day*, then report package and control inside
      each cell so the excess is visible in both states rather than netted away;
  (c) rolling-beta terciles -- 252-bar trailing package beta, tercile the days, and read
      the excess in the low/mid/high beta cells: an excess that lives only in one cell is
      a factor story, one that survives all three is selection.

Engine reused, not rewritten: `CR.phase_book_cost` (-> `PK.fast_next_open_vt`, pinned to
`V.fast_next_open` at 1e-12 by its own selftest). --selftest pins the estimators on
synthetic data where the true beta and alpha are known by construction.

Exploratory: no preregistration, no verdict, no ledger booking.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F  # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts import etf_phase_cost_rolling as CR  # noqa: E402
from scripts.etf_asset_class import classify  # noqa: E402

ANCHOR = "2020-01-01"
OOS = pd.Timestamp("2024-01-01")
REBAL = 20
N_HOLD = F.N_HOLD
COST_BP = 8.0
MKT = ("510300", "sh510300")
ROLL_BETA = 252
STATE_BARS = 20
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "results", "etf_phase_beta_split.json")


# ----------------------------------------------------------------------------------------
# estimators
# ----------------------------------------------------------------------------------------
def align(pkg, ew, mkt):
    """Daily returns of package, control and market on their common dates."""
    idx = pkg.index.intersection(ew.index).intersection(mkt.index)
    rp = pkg.reindex(idx).pct_change()
    re = ew.reindex(idx).pct_change()
    rm = mkt.reindex(idx).pct_change()
    df = pd.DataFrame({"pkg": rp, "ew": re, "mkt": rm}).dropna()
    return df


def beta_of(y, x):
    """OLS slope of y on x (no intercept drift term reported)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    vx = float(np.var(x))
    if vx <= 0 or len(x) < 3:
        return None
    return float(np.cov(y, x, bias=True)[0, 1] / vx)


def _ann(x):
    return float(np.mean(x) * 252.0 * 100.0)


def _sharpe(x):
    sd = float(np.std(x, ddof=1))
    return float(np.mean(x) / sd * np.sqrt(252.0)) if sd > 0 else None


def beta_block(df, market_label="510300"):
    """Beta, beta-hedged excess, and up/down capture for package and control."""
    out = {"market": market_label, "n_days": int(len(df))}
    mb = beta_of(df["mkt"], df["mkt"])
    for col in ("pkg", "ew"):
        b = beta_of(df[col], df["mkt"])
        hedge = df[col].to_numpy() - b * df["mkt"].to_numpy()
        up = df["mkt"] > 0
        dn = df["mkt"] < 0
        out[col] = {
            "beta_vs_market": round(b, 4),
            "ann_ret_pct": round(_ann(df[col]), 2),
            "ann_vol_pct": round(float(np.std(df[col], ddof=1) * np.sqrt(252.0) * 100), 2),
            "sharpe": round(_sharpe(df[col]), 3),
            "beta_hedged_excess_pp": round(_ann(hedge), 2),
            "beta_hedged_sharpe": round(_sharpe(hedge), 3),
            "beta_hedged_vol_pct": round(float(np.std(hedge, ddof=1) * np.sqrt(252.0) * 100), 2),
            "capture_up": (round(float(df.loc[up, col].mean() / df.loc[up, "mkt"].mean()), 3)
                           if up.any() and df.loc[up, "mkt"].mean() > 0 else None),
            "capture_down": (round(float(df.loc[dn, col].mean() / df.loc[dn, "mkt"].mean()), 3)
                             if dn.any() else None),
            "n_up_days": int(up.sum()), "n_down_days": int(dn.sum()),
        }
    out["beta_gap_pkg_minus_ew"] = round(out["pkg"]["beta_vs_market"]
                                         - out["ew"]["beta_vs_market"], 4)
    out["market_beta_is_1"] = round(mb, 4)
    ann_mkt = _ann(df["mkt"])
    out["market_ann_ret_pct"] = round(ann_mkt, 2)
    # what the same market exposure would have paid for free: beta * market, rest in cash at 0%
    for col in ("pkg", "ew"):
        synth = out[col]["beta_vs_market"] * ann_mkt
        out[col]["beta_synthetic_pp"] = round(synth, 2)
        out[col]["excess_over_beta_synthetic_pp"] = round(out[col]["ann_ret_pct"] - synth, 2)
    # beta-matched control: scale the package to the CONTROL's market beta (rest in cash at
    # 0% -- disclosed, rf is not modelled) so the two books carry the same factor exposure
    bp, be = out["pkg"]["beta_vs_market"], out["ew"]["beta_vs_market"]
    if bp and abs(bp) > 1e-9:
        scale = be / bp
        matched = df["pkg"].to_numpy() * scale
        out["pkg_beta_matched_to_ew"] = {
            "scale": round(scale, 4),
            "cash_share_pct": round((1.0 - scale) * 100, 2),
            "ann_ret_pct": round(float(np.mean(matched) * 252.0 * 100), 2),
            "ann_vol_pct": round(float(np.std(matched, ddof=1) * np.sqrt(252.0) * 100), 2),
            "sharpe": round(_sharpe(matched), 3),
            "excess_vs_ew_pp": round(float(np.mean(matched) * 252.0 * 100) - _ann(df["ew"]), 2),
        }
    return out


def _cell(frame, label):
    p, e, m = frame["pkg"], frame["ew"], frame["mkt"]
    return {
        "label": label, "n_days": int(len(frame)),
        "pkg_pct": round(_ann(p), 2), "ew_pct": round(_ann(e), 2),
        "excess_pp": round(_ann(p) - _ann(e), 2),
        "mkt_pct": round(_ann(m), 2),
        "pkg_beta": (round(beta_of(p, m), 4) if len(frame) >= 3 else None),
        "ew_beta": (round(beta_of(e, m), 4) if len(frame) >= 3 else None),
    }


def state_split(df, bars=STATE_BARS):
    """Excess inside market-state cells: trailing-N-bar sign and same-day sign."""
    mkt = df["mkt"]
    trail = (1.0 + mkt).cumprod().pct_change(bars)
    rows = {}
    for label, cond in (
        ("trail%d_up" % bars, trail > 0),
        ("trail%d_down" % bars, trail <= 0),
        ("mkt_day_up", mkt > 0),
        ("mkt_day_down", mkt <= 0),
    ):
        cond = cond.reindex(df.index).fillna(False).astype(bool)
        if int(cond.sum()) >= 10:
            rows[label] = _cell(df[cond.to_numpy()], label)
    return rows


def rolling_beta_terciles(df, window=ROLL_BETA):
    """Trailing package beta, terciled by RANK (ties never collapse a band); excess per third.

    Rank-based assignment (not value cut-offs) so a book with a near-constant beta still
    yields three populated cells instead of one -- a value cut there would silently report
    a single cell as if it were the whole picture.
    """
    mkt = df["mkt"]
    cov = df["pkg"].rolling(window).cov(mkt)
    var = mkt.rolling(window).var()
    rb = (cov / var).dropna()
    if len(rb) < 60:
        return {"available": False, "n": int(len(rb))}
    sub = df.loc[rb.index]
    order = np.argsort(rb.to_numpy(), kind="mergesort")
    labels = np.array(["beta_mid"] * len(order), dtype=object)
    third = len(order) // 3
    labels[order[:third]] = "beta_low"
    labels[order[len(order) - third:]] = "beta_high"
    q1, q2 = np.percentile(rb, [33.333, 66.667])
    rows = {}
    for label in ("beta_low", "beta_mid", "beta_high"):
        mask = labels == label
        part = sub[mask]
        if len(part) < 10:
            continue
        rows[label] = _cell(part, label)
        rows[label]["beta_median"] = round(float(np.median(rb.to_numpy()[mask])), 4)
    return {
        "available": True, "window_bars": window, "n_scored_days": int(len(rb)),
        "assignment": "rank thirds (mergesort on trailing beta)",
        "beta_tercile_bounds": [round(float(q1), 4), round(float(q2), 4)],
        "beta_min": round(float(rb.min()), 4), "beta_max": round(float(rb.max()), 4),
        "cells": rows,
    }


# ----------------------------------------------------------------------------------------
# selftest
# ----------------------------------------------------------------------------------------
def selftest():
    ok = total = 0

    def chk(name, cond, extra=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("SELFTEST FAIL:", name, extra)

    rng = np.random.default_rng(11)
    n = 1200
    idx = pd.bdate_range("2020-01-02", periods=n)
    rm = pd.Series(rng.normal(0.0004, 0.011, n), index=idx)
    # known construction: pkg = 2.0 * mkt (beta 2, zero alpha), ew = 1.0 * mkt + alpha
    rp = 2.0 * rm
    re = 1.0 * rm + 0.0005
    df = pd.DataFrame({"pkg": rp, "ew": re, "mkt": rm}).dropna()

    blk = beta_block(df)
    chk("pkg beta recovered", abs(blk["pkg"]["beta_vs_market"] - 2.0) < 1e-6,
        blk["pkg"]["beta_vs_market"])
    chk("ew beta recovered", abs(blk["ew"]["beta_vs_market"] - 1.0) < 1e-6,
        blk["ew"]["beta_vs_market"])
    chk("beta gap = 1.0", abs(blk["beta_gap_pkg_minus_ew"] - 1.0) < 1e-6,
        blk["beta_gap_pkg_minus_ew"])
    chk("pure-beta book has zero hedged excess",
        abs(blk["pkg"]["beta_hedged_excess_pp"]) < 0.5, blk["pkg"]["beta_hedged_excess_pp"])
    chk("ew hedged excess returns its alpha",
        abs(blk["ew"]["beta_hedged_excess_pp"] - 12.6) < 2.0,
        blk["ew"]["beta_hedged_excess_pp"])
    chk("pure-beta capture ratios equal beta",
        abs(blk["pkg"]["capture_up"] - 2.0) < 1e-6 and
        abs(blk["pkg"]["capture_down"] - 2.0) < 1e-6,
        (blk["pkg"]["capture_up"], blk["pkg"]["capture_down"]))

    # beta-matched leg: scaling a 2x book down to the 1x control must leave half in cash and
    # give back exactly the control's alpha (no selection left once exposure is equalised)
    bm = blk["pkg_beta_matched_to_ew"]
    chk("beta-matched scale = beta ratio", abs(bm["scale"] - 0.5) < 1e-6, bm["scale"])
    chk("beta-matched cash share", abs(bm["cash_share_pct"] - 50.0) < 1e-6, bm["cash_share_pct"])
    chk("beta-matched book loses to the control's alpha",
        abs(bm["excess_vs_ew_pp"] + 12.6) < 2.5, bm["excess_vs_ew_pp"])
    # beta-synthetic leg: a pure 2x market book must be FULLY explained by beta*mkt
    chk("pure-beta book is fully explained by beta*mkt",
        abs(blk["pkg"]["excess_over_beta_synthetic_pp"]) < 1e-6,
        blk["pkg"]["excess_over_beta_synthetic_pp"])
    chk("synthetic identity holds exactly",
        abs(blk["pkg"]["beta_synthetic_pp"]
            - blk["pkg"]["beta_vs_market"] * blk["market_ann_ret_pct"]) < 0.02,
        (blk["pkg"]["beta_synthetic_pp"],
         blk["pkg"]["beta_vs_market"] * blk["market_ann_ret_pct"]))

    # market-state split must partition the days and keep the raw spread inside each cell
    st = state_split(df)
    chk("four state cells present", set(st) == {"trail20_up", "trail20_down",
                                                "mkt_day_up", "mkt_day_down"}, list(st))
    chk("state cells partition days",
        st["mkt_day_up"]["n_days"] + st["mkt_day_down"]["n_days"] == len(df),
        (st["mkt_day_up"]["n_days"], st["mkt_day_down"]["n_days"]))
    chk("same-day cells keep a visible spread",
        st["mkt_day_up"]["excess_pp"] > 0 and st["mkt_day_down"]["excess_pp"] < 0,
        (st["mkt_day_up"]["excess_pp"], st["mkt_day_down"]["excess_pp"]))

    # terciles: rank assignment must populate all three bands and partition the scored days
    tc = rolling_beta_terciles(df, window=252)
    chk("terciles available", tc["available"] is True, tc)
    if tc["available"]:
        bands = list(tc["cells"])
        chk("tercile cells populated", len(bands) == 3, bands)
        chk("tercile bands partition the scored days",
            sum(tc["cells"][k]["n_days"] for k in bands) == tc["n_scored_days"],
            (sum(tc["cells"][k]["n_days"] for k in bands), tc["n_scored_days"]))
        chk("bands ordered by beta",
            tc["cells"]["beta_low"]["beta_median"] <= tc["cells"]["beta_mid"]["beta_median"]
            <= tc["cells"]["beta_high"]["beta_median"],
            [tc["cells"][k]["beta_median"] for k in bands])
    # identical book == identical control: every tercile must read zero excess
    same = rolling_beta_terciles(pd.DataFrame({"pkg": rm, "ew": rm, "mkt": rm}).dropna(),
                                 window=252)
    chk("identical book reads zero excess in every band",
        same["available"] and all(abs(same["cells"][k]["excess_pp"]) < 1e-9
                                  for k in same["cells"]),
        {k: same["cells"][k]["excess_pp"] for k in same["cells"]} if same["available"] else same)

    # degenerate inputs degrade instead of raising
    chk("beta of constant x is None", beta_of([1.0, 2.0, 3.0], [1.0, 1.0, 1.0]) is None)
    chk("rolling beta degrades on short input",
        rolling_beta_terciles(df.iloc[:40])["available"] is False)
    chk("state split degrades on short input", state_split(df.iloc[:8]) == {})

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


# ----------------------------------------------------------------------------------------
# burn
# ----------------------------------------------------------------------------------------
def _disp(vals):
    vals = sorted(vals)
    m = len(vals) // 2
    return {"n": len(vals), "median": round(vals[m], 2) if vals else None,
            "min": round(vals[0], 2) if vals else None,
            "max": round(vals[-1], 2) if vals else None}


def main():
    if "--selftest" in sys.argv:
        return selftest()
    t_all = time.time()
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    ew = F.run_ew(close[cols], amt[cols], REBAL, start=ANCHOR)
    base = F.metrics(ew, "ew")
    mkt_col = next((c for c in MKT if c in close.columns), None)
    if mkt_col is None:
        print("FATAL: no 510300 column on the panel")
        return 2
    mkt = close[mkt_col]
    print("panel %s bars=%d cols=%d | ew full %.2f%% | market col %s"
          % (close.index[0].date(), close.shape[0], len(cols), base["cagr"] * 100, mkt_col),
          flush=True)

    t0 = time.time()
    pkg, cells = CR.phase_book_cost(score, close[cols], openp[cols], N_HOLD, COST_BP)
    m_pkg = F.metrics(pkg, "package")
    print("package ready %.0fs | full %.2f%% oos %.2f%%"
          % (time.time() - t0, m_pkg["cagr"] * 100,
             F.metrics(pkg[pkg.index >= OOS], "pkg:oos")["cagr"] * 100), flush=True)

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "anchor": ANCHOR, "rebal": REBAL, "n_hold": N_HOLD, "cost_bp_per_side": COST_BP,
        "universe": "bond_removed (equity/commodity/crossborder), %d instruments" % len(cols),
        "market_proxy": mkt_col,
        "basis": "package = buy-and-hold mean of the R=20 phase NAVs (next-open fill, 8bp "
                 "per side); control = equal weight on the same subset; daily returns on the "
                 "common date grid for every beta/capture/state read",
        "question": "is the package excess a beta story (factor exposure) or selection "
                    "(positive inside every market state and every rolling-beta tercile)?",
        "headline": {"package": m_pkg, "control_ew": base,
                     "excess_pp": round((m_pkg["cagr"] - base["cagr"]) * 100, 2)},
        "windows": {}, "caveats": [
            "survivorship: on-disk panel holds ETFs that still exist",
            "single market proxy (510300) -- a beta read against CSI300 only, no multi-factor "
            "regression (size/value/momentum not modelled)",
            "rolling-beta terciles are overlapping windows, so the cells are a descriptive "
            "split, not an independent-sample test",
            "capture ratios are mean-return ratios, not downside/upside semivariance capture",
            "exploratory: no preregistration, no verdict, no ledger booking",
        ],
    }

    for label, sl in (("full", slice(None)), ("oos_2024plus", None)):
        if sl is None:
            part = pkg[pkg.index >= OOS]
        else:
            part = pkg
        df = align(part, ew, mkt)
        blk = beta_block(df, market_label=mkt_col)
        st = state_split(df)
        tc = rolling_beta_terciles(df)
        out["windows"][label] = {
            "start": str(df.index[0].date()), "end": str(df.index[-1].date()),
            "beta": blk, "market_state": st, "rolling_beta_terciles": tc,
        }
        print("[%s] %s..%s n=%d | pkg beta %.3f ew beta %.3f | hedged pkg %+.2fpp ew %+.2fpp"
              % (label, df.index[0].date(), df.index[-1].date(), len(df),
                 blk["pkg"]["beta_vs_market"], blk["ew"]["beta_vs_market"],
                 blk["pkg"]["beta_hedged_excess_pp"], blk["ew"]["beta_hedged_excess_pp"]),
              flush=True)
        for k, v in st.items():
            print("   %-14s n=%4d pkg %6.2f%% ew %6.2f%% excess %+6.2fpp mkt %6.2f%%"
                  % (k, v["n_days"], v["pkg_pct"], v["ew_pct"], v["excess_pp"], v["mkt_pct"]),
                  flush=True)
        if tc["available"]:
            for k, v in tc["cells"].items():
                print("   %-10s n=%4d excess %+6.2fpp (pkg beta %.2f)"
                      % (k, v["n_days"], v["excess_pp"], v["pkg_beta"] or float("nan")),
                      flush=True)

    # headline span checks: the excess must survive every state cell and every beta third
    for label in out["windows"]:
        w = out["windows"][label]
        st_ex = [v["excess_pp"] for v in w["market_state"].values()]
        tc = w["rolling_beta_terciles"]
        tc_ex = [v["excess_pp"] for v in tc["cells"].values()] if tc["available"] else []
        w["span"] = {
            "state_cells": len(st_ex),
            "state_min_excess_pp": round(min(st_ex), 2) if st_ex else None,
            "state_max_excess_pp": round(max(st_ex), 2) if st_ex else None,
            "state_cells_positive": sum(1 for v in st_ex if v > 0),
            "beta_cells": len(tc_ex),
            "beta_cells_positive": sum(1 for v in tc_ex if v > 0),
            "beta_min_excess_pp": round(min(tc_ex), 2) if tc_ex else None,
            "beta_max_excess_pp": round(max(tc_ex), 2) if tc_ex else None,
        }

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", OUT_PATH, "(%.0fs total)" % (time.time() - t_all), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())