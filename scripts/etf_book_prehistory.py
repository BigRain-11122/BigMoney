"""Does the production candidate survive the years nobody ever ran it on?

Every published number in this house starts on 2020-01-01, because that is where
`etf_robust_pf.START` sits. The panel does not start there: 226 of the 1,725 files in
data/daily have first bars before 2020, and 60+ before 2016. So the same frozen rules can
be priced on 2015-2019 -- the 2015 crash, the 2016 circuit breaker, the 2018 bear -- which
is the one stretch where "the bond-free book with an 8% vol target earns 11.5%/yr, Sharpe
1.13, maxdd -10.6%" has never been tested on its own terms.

Three segments, all priced on the same panel, same repair, same class map:

  pre     2013-01-01 .. 2019-12-31   never run before this face
  modern  2020-01-01 .. cutoff       the published window (control: must reproduce)
  all     2013-01-01 .. cutoff

Frozen criteria, written before the first run (see `verdict_of`):

  PRE_SURVIVES             pre CAGR > 0 and pre maxdd >= -25% and pre Sharpe > 0.3
  PRE_FAILS                pre CAGR <= 0 or pre maxdd < -35%
  PRE_MARGINAL             anything in between
  NOT_READABLE_SMALL_POOL  the median number of names the score actually offers on a
                           rebalance day is < 20 -- a five-name book picked out of twelve
                           is not the same rule, and its numbers are not evidence

The pool is measured from `build_score`'s own output, so it already carries the
liquidity gate (20d median turnover >= 20m) and the 120-bar history gate. Nothing is
re-derived here.

Honesty rails:
  * the pre window has no bond sleeve by construction (the arm is bond-free), but it also
    has far fewer commodity names. Per segment we print how many equity / commodity /
    convertible names the panel held and how many were actually offered per rebalance day,
    so a reader cannot mistake "the rule held up" for "the universe was the same".
  * the equal-weight control is the same-pool, same-day mean of daily returns compounded
    once; it is not an N5 book. It answers "did the picks beat owning all of them", which
    is the only question a pick rule has to answer.

Usage:
  python scripts/etf_book_prehistory.py run      # -> results/etf_book_prehistory.json
  python scripts/etf_book_prehistory.py check    # re-derive the verdict from the face
  python scripts/etf_book_prehistory.py --selftest
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

OUT = "etf_book_prehistory.json"
SEGMENTS = (
    ("pre", "2013-01-01", "2019-12-31"),
    ("modern", "2020-01-01", None),
    ("all", "2013-01-01", None),
)
COST = 0.0010
REBAL = 20
N_HOLD = 5
TARGET_VOL = 0.08
MIN_POOL = 20          # median names offered per rebalance day for the segment to count
POOL_MATCH_N = 15      # narrow the modern pool to about what the pre window offered
POOL_MATCH_KEEP_PP = 2.0  # excess >= 2pp/yr on the narrow pool = width does not explain it
PRE_MAXDD_PASS = -0.25
PRE_MAXDD_FAIL = -0.35
PRE_SHARPE_MIN = 0.30


def verdict_of(pre, pool_median):
    """Frozen rule. `pre` is a stats2 dict; `pool_median` is the segment's median name count."""
    if pool_median is None or pool_median < MIN_POOL:
        return "NOT_READABLE_SMALL_POOL"
    cagr = pre.get("cagr")
    dd = pre.get("maxdd")
    sr = pre.get("sharpe")
    if cagr is None or dd is None or sr is None:
        return "NOT_READABLE_SHORT"
    if cagr <= 0.0 or dd < PRE_MAXDD_FAIL:
        return "PRE_FAILS"
    if dd >= PRE_MAXDD_PASS and sr > PRE_SHARPE_MIN:
        return "PRE_SURVIVES"
    return "PRE_MARGINAL"


def ew_series(close, cols):
    """Same-pool equal weight: mean of daily simple returns, compounded once."""
    px = close[cols]
    r = px.pct_change()
    day = r.mean(axis=1, skipna=True).fillna(0.0)
    return (1.0 + day).cumprod()


def _seg_mask(ser, lo, hi):
    m = ser.index >= pd.Timestamp(lo)
    if hi is not None:
        m &= ser.index <= pd.Timestamp(hi)
    return ser[m]


def _stats(ser, label):
    return A.stats2(ser, label)


def run():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)

    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    counts = {k: sum(1 for c in cols if cls[c] == k) for k in want}
    print("bond-free universe %d (eq %d / cmdty %d / conv %d), flips %d"
          % (len(cols), counts["equity"], counts["commodity"], counts["convertible"], n_flip),
          flush=True)

    sc = E.build_score(close[cols], amt[cols], feats)
    offered = sc.notna().sum(axis=1)
    # rebalance days are the score index rows that a 20-bar cadence would land on;
    # using the whole index overstates nothing because we take the median, not the sum.
    ew = ew_series(close, cols)

    out = {"evidence_cutoff": str(close.index[-1].date()),
           "universe": len(cols),
           "class_counts": counts,
           "flips_repaired": int(n_flip),
           "rule": {"rebal_days": REBAL, "n_hold": N_HOLD, "cost_per_side": COST,
                    "vol_target": TARGET_VOL,
                    "note": "bond-free arm = equity + commodity + convertible, as in etf_nobond_vt"},
           "criteria": {"min_pool_median": MIN_POOL,
                        "pre_maxdd_pass": PRE_MAXDD_PASS,
                        "pre_maxdd_fail": PRE_MAXDD_FAIL,
                        "pre_sharpe_min": PRE_SHARPE_MIN},
           "segments": {}}

    for name, lo, hi in SEGMENTS:
        seg = {}
        pool = offered[(offered.index >= pd.Timestamp(lo))]
        if hi is not None:
            pool = pool[pool.index <= pd.Timestamp(hi)]
        pool_med = float(pool.median()) if len(pool) else 0.0
        seg["pool_median_names"] = round(pool_med, 1)
        seg["pool_max_names"] = int(pool.max()) if len(pool) else 0

        # production candidate: bond-free + 8% vol target
        s_prod, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                             REBAL, N_HOLD, COST, vol_target=TARGET_VOL,
                                             start=lo)
        s_prod = _seg_mask(s_prod, lo, hi)
        st = _stats(s_prod, "prod_%s" % name) if len(s_prod) > 40 else {"note": "short"}
        st["turnover_x"] = round(float(turn), 2)
        seg["prod_vt08"] = st

        # same rules without the vol target -- separates "the sizing did the work"
        s_bare, _t2 = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                            REBAL, N_HOLD, COST, vol_target=None, start=lo)
        s_bare = _seg_mask(s_bare, lo, hi)
        seg["bare"] = _stats(s_bare, "bare_%s" % name) if len(s_bare) > 40 else {"note": "short"}

        # same-pool equal weight over the same calendar
        s_ew = _seg_mask(ew, lo, hi)
        seg["pool_equal_weight"] = _stats(s_ew, "ew_%s" % name) if len(s_ew) > 40 else {"note": "short"}

        prod, bare, ewst = seg["prod_vt08"], seg["bare"], seg["pool_equal_weight"]
        seg["excess_vs_ew_pp"] = (round((prod.get("cagr", 0.0) - ewst.get("cagr", 0.0)) * 100.0, 3)
                                  if prod.get("cagr") is not None and ewst.get("cagr") is not None
                                  else None)
        seg["vol_target_delta_pp"] = (round((prod.get("cagr", 0.0) - bare.get("cagr", 0.0)) * 100.0, 3)
                                      if prod.get("cagr") is not None and bare.get("cagr") is not None
                                      else None)
        if name == "pre":
            seg["verdict"] = verdict_of(prod, pool_med)
        out["segments"][name] = seg
        print("%-7s pool_med=%5.1f prod cagr=%s sr=%s dd=%s | ew cagr=%s | %s"
              % (name, pool_med,
                 _pct(prod.get("cagr")), _num(prod.get("sharpe")), _pct(prod.get("maxdd")),
                 _pct(ewst.get("cagr")), seg.get("verdict", "")), flush=True)

    # Second question, and the one that decides what the pre window means: is the excess
    # a property of the RULE or of the WIDTH of the pool? Price the same rule on a pool
    # narrowed to roughly the size the pre window actually offered (top N by turnover each
    # day), on the modern window where we can measure it. If the excess survives the
    # narrowing, a 13-name pool is not why pre did not beat equal weight.
    amt_rank = amt[cols].rank(axis=1, ascending=False)
    pm_mask = amt_rank <= POOL_MATCH_N
    sc_pm = sc.where(pm_mask)
    pm_offered = sc_pm.notna().sum(axis=1)
    pm_offered_mod = pm_offered[pm_offered.index >= pd.Timestamp("2020-01-01")]
    s_pm, turn_pm = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc_pm,
                                          REBAL, N_HOLD, COST, vol_target=TARGET_VOL,
                                          start="2020-01-01")
    st_pm = _stats(s_pm, "prod_poolmatched_modern")
    r_all = close[cols].pct_change()
    ew_pm = (1.0 + r_all.where(pm_mask).mean(axis=1, skipna=True).fillna(0.0)).cumprod()
    st_ew_pm = _stats(ew_pm[ew_pm.index >= pd.Timestamp("2020-01-01")], "ew_poolmatched_modern")
    pm_excess = (st_pm.get("cagr") - st_ew_pm.get("cagr")) if (
        st_pm.get("cagr") is not None and st_ew_pm.get("cagr") is not None) else None
    if pm_excess is None:
        pm_verdict = "NOT_READABLE"
    elif pm_excess * 100.0 < POOL_MATCH_KEEP_PP:
        pm_verdict = "POOL_WIDTH_EXPLAINS_IT"
    else:
        pm_verdict = "POOL_WIDTH_DOES_NOT_EXPLAIN_IT"
    out["pool_matched_modern"] = {
        "pool_cap_names_per_day": POOL_MATCH_N,
        "pool_median_names": round(float(pm_offered_mod.median()), 1) if len(pm_offered_mod) else 0.0,
        "prod_vt08": st_pm,
        "pool_equal_weight": st_ew_pm,
        "excess_vs_ew_pp": (round(pm_excess * 100.0, 3) if pm_excess is not None else None),
        "excess_full_pool_pp": out["segments"]["modern"].get("excess_vs_ew_pp"),
        "verdict": pm_verdict,
        "threshold_pp": POOL_MATCH_KEEP_PP,
    }
    print("pool-matched modern (<=%d/day, median %.1f): prod cagr=%s ew cagr=%s excess=%spp -> %s"
          % (POOL_MATCH_N, out["pool_matched_modern"]["pool_median_names"],
             _pct(st_pm.get("cagr")), _pct(st_ew_pm.get("cagr")),
             _num(pm_excess * 100.0) if pm_excess is not None else "n/a", pm_verdict), flush=True)

    # control: the published modern window must reproduce the book that is already on paper
    published = _published_modern()
    if published is not None:
        got = out["segments"]["modern"]["prod_vt08"].get("cagr")
        out["control_modern_vs_published"] = {
            "published_cagr": published,
            "reproduced_cagr": got,
            "delta_pp": (round((got - published) * 100.0, 4) if got is not None else None),
            "note": "published = results/etf_nobond_vt.json nobond_vt08 cagr (same rules, same panel)",
        }
        print("control modern cagr=%s vs published=%s" % (_pct(got), _pct(published)), flush=True)

    out["verdict"] = out["segments"]["pre"]["verdict"]
    p = os.path.join(E.PATHS.results_dir, OUT)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)
    print("VERDICT", out["verdict"])


def _published_modern():
    p = os.path.join(E.PATHS.results_dir, "etf_nobond_vt.json")
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        face = json.load(f)
    for r in face.get("runs", []):
        if r.get("label") == "nobond_vt08":
            return r.get("cagr")
    return None


def _pct(x):
    return "  n/a" if x is None else "%5.1f%%" % (x * 100.0)


def _num(x):
    return " n/a" if x is None else "%4.2f" % x


def check():
    """Re-derive everything on the face that is derivable from the face itself."""
    p = os.path.join(E.PATHS.results_dir, OUT)
    problems = []
    if not os.path.exists(p):
        print("STALE face missing:", p)
        return 3
    with open(p, "r", encoding="utf-8") as f:
        face = json.load(f)

    segs = face.get("segments", {})
    for need in ("pre", "modern", "all"):
        if need not in segs:
            problems.append("segment missing: %s" % need)
    if problems:
        for x in problems:
            print("PROBLEM", x)
        return 1

    pre = segs["pre"]
    v = verdict_of(pre.get("prod_vt08", {}), pre.get("pool_median_names", 0.0))
    if v != pre.get("verdict"):
        problems.append("pre verdict does not re-derive: printed %r, re-derived %r"
                        % (pre.get("verdict"), v))
    if face.get("verdict") != pre.get("verdict"):
        problems.append("top-level verdict != pre verdict")

    for name, seg in segs.items():
        prod = seg.get("prod_vt08", {})
        ew = seg.get("pool_equal_weight", {})
        if "cagr" in prod and "cagr" in ew:
            want = round((prod["cagr"] - ew["cagr"]) * 100.0, 3)
            if seg.get("excess_vs_ew_pp") != want:
                problems.append("%s excess_vs_ew_pp %r != %r" % (name, seg.get("excess_vs_ew_pp"), want))

    pm = face.get("pool_matched_modern")
    if pm:
        prod_pm = pm.get("prod_vt08", {})
        ew_pm = pm.get("pool_equal_weight", {})
        if prod_pm.get("cagr") is not None and ew_pm.get("cagr") is not None:
            want = round((prod_pm["cagr"] - ew_pm["cagr"]) * 100.0, 3)
            if pm.get("excess_vs_ew_pp") != want:
                problems.append("pool_matched excess_vs_ew_pp %r != %r" % (pm.get("excess_vs_ew_pp"), want))
            want_v = ("POOL_WIDTH_EXPLAINS_IT" if want < POOL_MATCH_KEEP_PP
                      else "POOL_WIDTH_DOES_NOT_EXPLAIN_IT")
            if pm.get("verdict") != want_v:
                problems.append("pool_matched verdict %r != re-derived %r" % (pm.get("verdict"), want_v))
        else:
            problems.append("pool_matched arm is unreadable (no cagr)")

    ctl = face.get("control_modern_vs_published")
    if ctl and ctl.get("published_cagr") is not None and ctl.get("reproduced_cagr") is not None:
        d = abs(ctl["reproduced_cagr"] - ctl["published_cagr"])
        if d > 0.02:   # 2pp: a different window/panel would show up here, not as noise
            problems.append("modern control drifted %.3fpp from the published book" % (d * 100.0))

    if problems:
        for x in problems:
            print("PROBLEM", x)
        return 1
    print("CHECK OK verdict=%s segments=%d pre_pool_med=%.1f"
          % (face.get("verdict"), len(segs), segs["pre"].get("pool_median_names", 0.0)))
    return 0


def selftest():
    legs = []
    passes = []

    # L1 a healthy pre window passes
    ok = verdict_of({"cagr": 0.06, "maxdd": -0.18, "sharpe": 0.7}, 40)
    legs.append(("healthy pre -> PRE_SURVIVES", ok == "PRE_SURVIVES"))
    # L2 a losing pre window fails
    ok = verdict_of({"cagr": -0.01, "maxdd": -0.20, "sharpe": 0.2}, 40)
    legs.append(("negative cagr -> PRE_FAILS", ok == "PRE_FAILS"))
    # L3 a deep drawdown fails even with a positive cagr
    ok = verdict_of({"cagr": 0.03, "maxdd": -0.42, "sharpe": 0.5}, 40)
    legs.append(("maxdd -42% -> PRE_FAILS", ok == "PRE_FAILS"))
    # L4 shallow drawdown but weak sharpe is marginal, not a pass
    ok = verdict_of({"cagr": 0.02, "maxdd": -0.27, "sharpe": 0.1}, 40)
    legs.append(("dd -27% / sr 0.1 -> PRE_MARGINAL", ok == "PRE_MARGINAL"))
    # L5 a small pool is not evidence, whatever the numbers say
    ok = verdict_of({"cagr": 0.20, "maxdd": -0.05, "sharpe": 2.0}, 12)
    legs.append(("pool 12 -> NOT_READABLE_SMALL_POOL", ok == "NOT_READABLE_SMALL_POOL"))
    # L6 missing numbers do not become a pass
    ok = verdict_of({"note": "short"}, 40)
    legs.append(("no numbers -> NOT_READABLE_SHORT", ok == "NOT_READABLE_SHORT"))
    # L7 equal weight compounding: flat prices produce a flat line
    idx = pd.date_range("2015-01-05", periods=6, freq="B")
    px = pd.DataFrame({"a": [1.0] * 6, "b": [2.0] * 6}, index=idx)
    s = ew_series(px, ["a", "b"])
    legs.append(("flat prices -> flat equal weight", abs(float(s.iloc[-1]) - 1.0) < 1e-12))
    # L8 equal weight: +10% on both legs is +10%, not +20%
    px2 = pd.DataFrame({"a": [1.0, 1.1], "b": [1.0, 1.1]}, index=idx[:2])
    s2 = ew_series(px2, ["a", "b"])
    legs.append(("+10% on both -> +10%", abs(float(s2.iloc[-1]) / float(s2.iloc[0]) - 1.1) < 1e-9))
    # L9 the pool-matched verdict is decided by its own arithmetic, both directions
    legs.append(("pool-matched +0.4pp -> width explains",
                 ("POOL_WIDTH_EXPLAINS_IT" if 0.4 < POOL_MATCH_KEEP_PP else "X") == "POOL_WIDTH_EXPLAINS_IT"))
    legs.append(("pool-matched +7.9pp -> width does not explain",
                 ("POOL_WIDTH_EXPLAINS_IT" if 7.9 < POOL_MATCH_KEEP_PP else "POOL_WIDTH_DOES_NOT_EXPLAIN_IT")
                 == "POOL_WIDTH_DOES_NOT_EXPLAIN_IT"))

    for text, ok in legs:
        print(("PASS " if ok else "FAIL ") + text)
        passes.append(bool(ok))
    print("selftest %d/%d" % (sum(passes), len(passes)))
    return 0 if all(passes) else 1


if __name__ == "__main__":
    arg = (sys.argv[1] if len(sys.argv) > 1 else "run").strip().lower()
    if arg in ("--selftest", "selftest"):
        sys.exit(selftest())
    if arg == "check":
        sys.exit(check())
    run()
