# -*- coding: utf-8 -*-
"""etf_book_entry_window_yield.py -- 「今天上车，一年后大概赚多少」

WHY (r2195): every face that quotes this book quotes ONE number (a CAGR over the
whole window, or a sub-window CAGR). A person who starts today does not get the
average of all start days -- they get one draw from the distribution over start
days. r2128 already showed that a single calendar winter can dominate a
"per-cell median" and that per-cell horizontal spreads exceed the effect being
measured. Nobody had published the distribution itself.

This face answers three sentences a wallet-holder actually says:
  1. if I start today and hold one year, what is the range of outcomes?
  2. how bad does it get inside that year (max drawdown along the path)?
  3. is the answer the same for the 8% vol-target arm and for the fully invested
     arm (i.e. what did the risk dial buy)?

Law carried:
  - no re-implementation: panel build, score, execution and stats are imported
    from etf_composite_pf / etf_robust_pf / etf_equity_alpha, exactly as
    etf_nobond_vt does (anti-dup law).
  - execution caliber = entry_lag=1 (decide at close t, own from open t+1) --
    the caliber the r1796 correction says is the executable one.
  - overlapping windows are NOT independent samples. The distribution is printed
    as a description of start days, and independent evidence is printed beside
    it as non-overlapping blocks (one per full year). No p-value is claimed.
  - the check anchors on an OUTSIDE byte (the data panel's own last bar), never
    on this face's own arithmetic (r1935: a guard that only recomputes itself
    can never say "I am stale").

Usage:
  python scripts/etf_book_entry_window_yield.py            # build the face
  python scripts/etf_book_entry_window_yield.py check      # cheap drift probe
  python scripts/etf_book_entry_window_yield.py selftest   # offline arithmetic
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

HORIZON = 252          # one trading year
ARMS = (("nobond_vt08", 0.08), ("nobond_base", None))
PANEL_PROBE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "daily", "sh510300.csv")


def build_arms():
    """Re-run the two published arms on the executable caliber (entry_lag=1)."""
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    out = {}
    for label, vt in ARMS:
        ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                          20, 5, 0.0010, vol_target=vt, entry_lag=1)
        out[label] = (ser, float(turn))
        print("arm %s bars=%d last=%s turnover=%.2f" % (label, len(ser), ser.index[-1].date(), turn),
              flush=True)
    return out, len(cols), n_flip


def window_stats(ser, h=HORIZON):
    """Every start day's one-year return + the worst drawdown inside that year."""
    vals = ser.values.astype(float)
    idx = ser.index
    n = len(vals)
    rows = []
    for i in range(0, n - h):
        seg = vals[i:i + h + 1]
        g = seg[-1] / seg[0] - 1.0
        peak = np.maximum.accumulate(seg)
        dd = float((seg / peak - 1.0).min())
        rows.append((str(idx[i].date()), str(idx[i + h].date()), float(g), dd))
    return rows


def _q(arr, p):
    return float(np.percentile(np.asarray(arr), p))


def distribution(rows):
    g = [r[2] for r in rows]
    dd = [r[3] for r in rows]
    worst = sorted(rows, key=lambda r: r[2])[:8]
    best = sorted(rows, key=lambda r: -r[2])[:3]
    # overlapping windows share the same crash: count the distinct start months among the
    # worst decile so a reader cannot mistake one bad event for many independent bad days
    worst_decile = sorted(rows, key=lambda r: r[2])[:max(1, len(rows) // 10)]
    cluster = {}
    for a, _b, _g, _d in worst_decile:
        cluster[a[:7]] = cluster.get(a[:7], 0) + 1
    return {
        "n_start_days": len(rows),
        "horizon_bars": HORIZON,
        "return": {
            "median_pct": round(np.median(g) * 100.0, 2),
            "p10_pct": round(_q(g, 10) * 100.0, 2),
            "p25_pct": round(_q(g, 25) * 100.0, 2),
            "p75_pct": round(_q(g, 75) * 100.0, 2),
            "p90_pct": round(_q(g, 90) * 100.0, 2),
            "min_pct": round(min(g) * 100.0, 2),
            "max_pct": round(max(g) * 100.0, 2),
            "share_of_starts_negative_pct": round(100.0 * sum(1 for x in g if x < 0) / len(g), 1),
            "spread_p90_minus_p10_pp": round((_q(g, 90) - _q(g, 10)) * 100.0, 2),
            "spread_over_median_x": round((_q(g, 90) - _q(g, 10)) / max(1e-9, abs(np.median(g))), 2),
        },
        "path_drawdown": {
            "median_pct": round(np.median(dd) * 100.0, 2),
            "p10_pct": round(_q(dd, 10) * 100.0, 2),
            "worst_pct": round(min(dd) * 100.0, 2),
            "n_distinct_values": len(set(round(x, 6) for x in dd)),
        },
        "worst_decile_start_months": dict(sorted(cluster.items(), key=lambda kv: -kv[1])[:5]),
        "worst_starts": [{"from": a, "to": b, "return_pct": round(c * 100.0, 2),
                          "path_maxdd_pct": round(d * 100.0, 2)} for a, b, c, d in worst],
        "best_starts": [{"from": a, "to": b, "return_pct": round(c * 100.0, 2)}
                        for a, b, c, d in best],
    }


def entry_year_table(rows):
    """Median one-year return by the year you start -- reads like a calendar."""
    by = {}
    for a, b, g, dd in rows:
        by.setdefault(a[:4], []).append(g)
    return {y: {"n": len(v), "median_pct": round(float(np.median(v)) * 100.0, 2),
                "worst_pct": round(min(v) * 100.0, 2)}
            for y, v in sorted(by.items())}


def non_overlapping(ser, h=HORIZON):
    """One reading per full year -- the independent half of the evidence."""
    vals = ser.values.astype(float)
    idx = ser.index
    out = []
    i = 0
    while i + h < len(vals):
        out.append({"from": str(idx[i].date()), "to": str(idx[i + h].date()),
                    "return_pct": round((vals[i + h] / vals[i] - 1.0) * 100.0, 2)})
        i += h
    return out


def verdict_for(d):
    r = d["return"]
    # 0.0% is not a loss: a flat path must read as "no losing window", not as "a rare loss"
    if r["min_pct"] >= 0:
        return "NO_LOSING_ONE_YEAR_WINDOW"
    if r["p10_pct"] < 0:
        return "ONE_YEAR_IN_FIVE_STARTS_ENDS_IN_THE_RED"
    return "LOSING_YEARS_EXIST_BUT_RARE"


def panel_last_bar():
    """Cheap outside anchor: the data panel's own tail date."""
    if not os.path.exists(PANEL_PROBE):
        return None
    with open(PANEL_PROBE, "r", encoding="utf-8", errors="replace") as f:
        head = f.readline()
        last = None
        for line in f:
            line = line.strip()
            if line:
                last = line
    if last is None:
        return None
    return last.split(",")[0][:10]


def main():
    arms, n_cols, n_flip = build_arms()
    face = {
        "schema": "etf-book-entry-window-yield/v1",
        "face": "etf_book_entry_window_yield",
        "machine": "bm-c",
        "question": "和今天差不多的时间上车、拿满一年，历史上的人都拿到了什么？中途要扛多深？",
        "execution": "decide at close t, own from open t+1 (entry_lag=1) -- the executable caliber",
        "universe": n_cols,
        "flips_repaired": n_flip,
        "arms": {},
    }
    for label, (ser, turn) in arms.items():
        rows = window_stats(ser)
        d = distribution(rows)
        d["turnover"] = round(turn, 2)
        d["window"] = [str(ser.index[0].date()), str(ser.index[-1].date())]
        d["independent_full_years"] = non_overlapping(ser)
        d["entry_year_median"] = entry_year_table(rows)
        d["verdict"] = verdict_for(d)
        face["arms"][label] = d
        print("%s: median=%.2f%% p10=%.2f%% p90=%.2f%% min=%.2f%% neg=%.1f%% verdict=%s"
              % (label, d["return"]["median_pct"], d["return"]["p10_pct"],
                 d["return"]["p90_pct"], d["return"]["min_pct"],
                 d["return"]["share_of_starts_negative_pct"], d["verdict"]), flush=True)

    vt, base = face["arms"]["nobond_vt08"], face["arms"]["nobond_base"]
    face["vol_target_bought"] = {
        "median_pp": round(vt["return"]["median_pct"] - base["return"]["median_pct"], 2),
        "p10_pp": round(vt["return"]["p10_pct"] - base["return"]["p10_pct"], 2),
        "worst_pp": round(vt["return"]["min_pct"] - base["return"]["min_pct"], 2),
        "path_drawdown_median_pp": round(vt["path_drawdown"]["median_pct"]
                                        - base["path_drawdown"]["median_pct"], 2),
        "path_drawdown_worst_pp": round(vt["path_drawdown"]["worst_pct"]
                                        - base["path_drawdown"]["worst_pct"], 2),
        "verdict": ("THE_DIAL_BUYS_THE_PATH_NOT_THE_YIELD"
                    if (vt["path_drawdown"]["median_pct"] > base["path_drawdown"]["median_pct"]
                        and vt["return"]["median_pct"] < base["return"]["median_pct"])
                    else "THE_DIAL_IS_NOT_ONLY_A_PATH_TRADE"),
        "reading": "if you would sell at the drawdown, the dial buys the ability to stay; "
                   "if you would not, it costs you one-year median return",
    }
    # the headline: how much of the outcome is the strategy vs the day you start
    face["verdict"] = {
        "headline": ("THE_DAY_YOU_START_MOVES_THE_ANSWER_MORE_THAN_THE_STRATEGY_DOES"
                     if vt["return"]["spread_over_median_x"] >= 1.0
                     else "THE_STRATEGY_MOVES_THE_ANSWER_MORE_THAN_THE_START_DAY"),
        "spread_over_median_x": vt["return"]["spread_over_median_x"],
        "reading": "same book, same year, 10th vs 90th percentile start day: the gap is the "
                   "spread; the typical outcome is the median",
    }

    # today's own last-one-year fact, when a full year exists
    ser_vt = arms["nobond_vt08"][0]
    if len(ser_vt) > HORIZON:
        v = ser_vt.values.astype(float)
        face["last_full_year"] = {
            "from": str(ser_vt.index[-(HORIZON + 1)].date()),
            "to": str(ser_vt.index[-1].date()),
            "return_pct_vt08": round((v[-1] / v[-(HORIZON + 1)] - 1.0) * 100.0, 2),
        }
    face["evidence_cutoff"] = str(ser_vt.index[-1].date())
    face["inputs"] = {
        "panel_probe": "data/daily/sh510300.csv",
        "panel_last_bar": panel_last_bar(),
        "books": ["results/etf_nobond_vt.json"],
    }
    face["not_measured"] = [
        "overlapping start days are not independent samples -- no p-value is claimed",
        "the carries/cb books are not on this ruler yet",
        "costs are the book's own 10bp per side; entry slippage beyond that is not priced",
    ]
    p = os.path.join(E.PATHS.results_dir, "etf_book_entry_window_yield.json")
    with open(p, "w", encoding="utf-8") as f:
        import json
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("saved", p)


def check():
    """Cheap drift probe against an OUTSIDE byte (the data panel's own tail)."""
    import json
    p = os.path.join(E.PATHS.results_dir, "etf_book_entry_window_yield.json")
    if not os.path.exists(p):
        print("STALE: face missing at", p)
        return 1
    with open(p, encoding="utf-8") as f:
        face = json.load(f)
    probs = []
    panel = panel_last_bar()
    if not panel:
        print("STALE: panel probe missing (%s)" % PANEL_PROBE)
        return 1
    if panel != face["evidence_cutoff"]:
        probs.append("STALE: face cutoff %s != panel last bar %s"
                     % (face["evidence_cutoff"], panel))
    for label in ("nobond_vt08", "nobond_base"):
        a = (face.get("arms") or {}).get(label)
        if not a:
            probs.append("%s: arm missing from face" % label)
            continue
        r = a["return"]
        want = round((r["p90_pct"] - r["p10_pct"]), 2)
        if abs(want - r["spread_p90_minus_p10_pp"]) > 0.05:
            probs.append("%s: spread %.2f != p90-p10 %.2f" % (label, r["spread_p90_minus_p10_pp"], want))
        if a["verdict"] != verdict_for(a):
            probs.append("%s: verdict does not follow from its own distribution" % label)
        if r["min_pct"] > r["median_pct"] or r["max_pct"] < r["median_pct"]:
            probs.append("%s: median outside [min,max]" % label)
    if probs:
        print("check FAIL:")
        for x in probs:
            print("  -", x)
        return 1
    print("check ok: cutoff=%s arms=%d" % (face["evidence_cutoff"], len(face.get("arms") or {})))
    return 0


# ---------------------------------------------------------------- selftest
def _synth(n=800, seed=7, drift=0.0004, vol=0.01):
    rng = np.random.default_rng(seed)
    r = rng.normal(drift, vol, n)
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.Series(np.cumprod(1.0 + r), index=idx)


def selftest():
    fails = []

    def ok(cond, msg):
        if not cond:
            fails.append(msg)

    ser = _synth()
    rows = window_stats(ser, 100)
    ok(len(rows) == len(ser) - 100, "window count off: %d vs %d" % (len(rows), len(ser) - 100))
    # a flat line yields exactly 0% and 0% drawdown on every start day
    flat = pd.Series(np.ones(400), index=pd.date_range("2020-01-01", periods=400, freq="B"))
    fr = window_stats(flat, 100)
    ok(all(abs(x[2]) < 1e-12 for x in fr), "flat line produced a non-zero window return")
    ok(all(abs(x[3]) < 1e-12 for x in fr), "flat line produced a drawdown")
    ok(verdict_for(distribution(fr)) == "NO_LOSING_ONE_YEAR_WINDOW",
       "flat line should have no losing window")
    # a strictly rising line also has no losing window
    up = pd.Series(np.linspace(1.0, 2.0, 400), index=pd.date_range("2020-01-01", periods=400, freq="B"))
    d_up = distribution(window_stats(up, 100))
    ok(d_up["return"]["min_pct"] > 0, "monotone line produced a negative window")
    ok(verdict_for(d_up) == "NO_LOSING_ONE_YEAR_WINDOW", "monotone line verdict wrong")
    # a strictly falling line must be ONE_YEAR_IN_FIVE_STARTS_ENDS_IN_THE_RED or worse
    down = pd.Series(np.linspace(2.0, 1.0, 400), index=pd.date_range("2020-01-01", periods=400, freq="B"))
    d_dn = distribution(window_stats(down, 100))
    ok(d_dn["return"]["max_pct"] < 0, "monotone falling line produced a positive window")
    ok(verdict_for(d_dn) == "ONE_YEAR_IN_FIVE_STARTS_ENDS_IN_THE_RED",
       "falling line verdict should be the red one, got %s" % verdict_for(d_dn))
    # negative control: move one value and the worst start must sharpen
    vals = up.copy()
    vals.iloc[150] = vals.iloc[150] * 0.70
    d_bad = distribution(window_stats(vals, 100))
    ok(d_bad["path_drawdown"]["worst_pct"] < -25.0,
       "a -30%% crash inside the path did not show up in worst drawdown")
    ok(d_up["path_drawdown"]["worst_pct"] > d_bad["path_drawdown"]["worst_pct"],
       "drawdown comparison did not separate the two series")
    # spread arithmetic
    r = d_up["return"]
    ok(abs(round(r["p90_pct"] - r["p10_pct"], 2) - r["spread_p90_minus_p10_pp"]) <= 0.05,
       "spread field is not p90-p10")
    # entry-year table covers every start year present
    et = entry_year_table(window_stats(ser, 100))
    ok(sum(v["n"] for v in et.values()) == len(window_stats(ser, 100)),
       "entry-year table lost start days")
    # non-overlapping blocks are strictly ordered and at most n/h
    nb = non_overlapping(ser, 100)
    ok(all(nb[i]["from"] < nb[i + 1]["from"] for i in range(len(nb) - 1)),
       "non-overlapping blocks are not in time order")
    ok(len(nb) <= len(ser) // 100, "too many non-overlapping blocks")
    # spread_over_median_x must be the spread divided by |median| (reading aid, not a new fact)
    r = d_up["return"]
    want_x = round(r["spread_p90_minus_p10_pp"] / max(1e-9, abs(r["median_pct"])), 2)
    ok(abs(want_x - r["spread_over_median_x"]) <= 0.02,
       "spread_over_median_x is not spread/|median|")
    # the worst decile must be counted in start months, never as independent days
    wd = d_bad["worst_decile_start_months"]
    ok(sum(wd.values()) == len(window_stats(vals, 100)) // 10,
       "worst-decile month cluster lost start days")

    if fails:
        print("selftest FAIL (%d)" % len(fails))
        for x in fails:
            print("  -", x)
        return 1
    print("selftest ok (13 legs)")
    return 0


if __name__ == "__main__":
    arg = sys.argv[1].lstrip("-").lower() if len(sys.argv) > 1 else ""
    if arg == "check":
        raise SystemExit(check())
    if arg == "selftest":
        raise SystemExit(selftest())
    main()
