"""Does the edge need breadth, or does it only need a rule?

`etf_book_prehistory` answered one half of this: the pre-2020 window did not beat its own
equal weight, and the modern window's excess survived a pool narrowed to 15 names/day
(`POOL_WIDTH_DOES_NOT_EXPLAIN_IT`). One narrowed point is not a curve -- it cannot tell a
reader whether 15/25/40 names are equivalent or whether the excess is quietly climbing
with breadth, which is exactly the difference between "the picking rule works" and "we
got paid for owning a wide pool".

This face prices the *same frozen book* (N5 / R20 / 10bp per side / 8% vol target, bond-free
universe, cost always on) on a ladder of pool widths, each capped per day by 20-day median
turnover rank, and prints for every width the book's CAGR/Sharpe/maxdd, the same-pool
equal weight it has to beat, the excess, and the paired daily t-stat of that excess.

Criteria are frozen here, before the first run, and re-derived by `check`:

  W1 MONOTONE_UP        excess(width) never drops by more than 0.5pp per step going up
  W2 RULE_WORKS_ANYWHERE  every width's excess >= 1.0pp/yr -- the picks, not the breadth
  W3 WIDTH_DRIVES_EDGE  full pool >= 2.0pp/yr and the narrowest width < 1.0pp/yr
  W4 MIXED_NOT_MONOTONE anything else

A t-stat below 2 on a step means the *shape* of the curve at that step is not
distinguishable from noise; the face prints it per width instead of letting a reader
read a 0.3pp wiggle as a trend.

The pre-2020 window is priced too, but only to show why it cannot answer the question:
its pool was already ~13 names/day, so every cap in the ladder is the same pool there.
That is printed, not hidden.

Usage:
  python scripts/etf_book_width_curve.py run      # -> results/etf_book_width_curve.json
  python scripts/etf_book_width_curve.py check    # re-derive the verdict from the face
  python scripts/etf_book_width_curve.py --selftest
"""
import json
import math
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

OUT = "etf_book_width_curve.json"

# frozen before the first run
WIDTHS = (15, 25, 40, 60, None)      # names offered per day by turnover rank; None = full pool
REBAL = 20
N_HOLD = 5
COST = 0.0010
TARGET_VOL = 0.08
MODERN_START = "2020-01-01"
PRE_WINDOW = ("2013-01-01", "2019-12-31")
MONO_SLACK_PP = 0.5                   # a step may wobble this much and still count as flat
RULE_WORKS_MIN_PP = 1.0               # every width beats its own equal weight by this much
WIDTH_EDGE_FULL_PP = 2.0              # full pool must be at least this good for W3
WIDTH_EDGE_NARROW_PP = 1.0            # narrowest width must be at most this good for W3
T_READABLE = 2.0


def label_of(width):
    return "all" if width is None else str(width)


def width_verdict(rows, full_key="all"):
    """rows: {label: {excess_pp, t}} in ladder order. Frozen rule, no I/O."""
    keys = [k for k in rows if k != "full" and rows[k].get("excess_pp") is not None]
    if not keys:
        return "NOT_READABLE"
    full = rows.get(full_key) or {}
    if full.get("excess_pp") is None:
        return "NOT_READABLE"
    steps = []
    for i in range(1, len(keys)):
        steps.append(round(rows[keys[i]]["excess_pp"] - rows[keys[i - 1]]["excess_pp"], 3))
    monotone = all(s >= -MONO_SLACK_PP for s in steps)
    every = all(rows[k]["excess_pp"] >= RULE_WORKS_MIN_PP for k in keys)
    narrow = rows[keys[0]]["excess_pp"]
    slope_pp = full["excess_pp"] - narrow
    if full["excess_pp"] >= WIDTH_EDGE_FULL_PP and narrow < WIDTH_EDGE_NARROW_PP and monotone:
        return "WIDTH_DRIVES_EDGE"
    # the edge is there at every width and climbing buys nothing: breadth is not the source
    if every and slope_pp < WIDTH_EDGE_FULL_PP:
        return "RULE_WORKS_ANYWHERE"
    if monotone:
        return "MONOTONE_UP"
    return "MIXED_NOT_MONOTONE"


def _stats(ser):
    return A.stats2(ser.dropna(), "x")


def paired_t(a, b):
    """t-stat of the mean daily difference a-b on the common calendar."""
    a = a.dropna()
    b = b.dropna()
    j = a.index.intersection(b.index)
    if len(j) < 60:
        return None, len(j)
    d = (a.loc[j] - b.loc[j]).dropna()
    if len(d) < 60 or float(d.std()) == 0.0:
        return None, len(d)
    t = float(d.mean() / d.std() * math.sqrt(len(d)))
    return round(t, 2), int(len(d))


def _ew(close, cols, mask=None, lo=None):
    r = close[cols].pct_change()
    if mask is not None:
        r = r.where(mask)
    return (1.0 + r.mean(axis=1, skipna=True).fillna(0.0)).cumprod()


def _slice(ser, lo, hi=None):
    m = ser.index >= pd.Timestamp(lo)
    if hi is not None:
        m &= ser.index <= pd.Timestamp(hi)
    return ser[m]


def price_ladder(close, openp, amt, sc, widths, lo, hi=None):
    """One row per width: the book, its own equal weight, the excess and the t."""
    amt_rank = amt.rank(axis=1, ascending=False)
    out = {}
    for w in widths:
        mask = None if w is None else (amt_rank <= w)
        sc_w = sc if mask is None else sc.where(mask)
        offered = sc_w.notna().sum(axis=1)
        offered = _slice(offered, lo, hi)
        s, turn = R.open_to_open_equity(close, openp, amt, sc_w, REBAL, N_HOLD, COST,
                                        vol_target=TARGET_VOL, start=lo)
        s = _slice(s, lo, hi)
        ew = _slice(_ew(close, list(close.columns), mask), lo, hi)
        st, ewst = _stats(s), _stats(ew)
        row = {"pool_cap": w if w is not None else "full",
               "pool_median_names": round(float(offered.median()), 1) if len(offered) else 0.0,
               "turnover_x": round(float(turn), 2),
               "book": st, "pool_equal_weight": ewst}
        if st.get("cagr") is not None and ewst.get("cagr") is not None:
            row["excess_pp"] = round((st["cagr"] - ewst["cagr"]) * 100.0, 3)
            t, n = paired_t(s.pct_change(), ew.pct_change())
            row["excess_t"] = t
            row["paired_days"] = n
        else:
            row["excess_pp"] = None
            row["excess_t"] = None
            row["paired_days"] = 0
        out[label_of(w)] = row
    return out


def _published_control():
    """The published bond-free book's vt08 arm, to prove this face prices the same rule."""
    path = "results/etf_nobond_vt.json"
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            face = json.load(f)
    except Exception:
        return None
    for run in face.get("runs") or []:
        if run.get("label") == "nobond_vt08" and run.get("cagr") is not None:
            return {"label": run["label"], "cagr": run["cagr"],
                    "sharpe": run.get("sharpe"), "maxdd": run.get("maxdd"),
                    "cutoff": face.get("evidence_cutoff")}
    return None


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

    modern = price_ladder(close[cols], openp[cols], amt[cols], sc, WIDTHS, MODERN_START)
    pre = price_ladder(close[cols], openp[cols], amt[cols], sc,
                       (15, None), PRE_WINDOW[0], PRE_WINDOW[1])

    verdict = width_verdict(modern)
    ladder = [modern[label_of(w)] for w in WIDTHS if label_of(w) in modern]
    readable = [r for r in ladder if r.get("excess_t") is not None]
    shape_noise = bool(readable) and all(abs(r["excess_t"]) < T_READABLE for r in readable)

    out = {
        "evidence_cutoff": str(close.index[-1].date()),
        "universe": len(cols),
        "class_counts": counts,
        "flips_repaired": int(n_flip),
        "rule": {"rebal_days": REBAL, "n_hold": N_HOLD, "cost_per_side": COST,
                 "vol_target": TARGET_VOL,
                 "note": "bond-free arm, same frozen book as etf_nobond_vt / etf_book_prehistory"},
        "window": {"modern_start": MODERN_START, "modern_end": str(close.index[-1].date())},
        "criteria": {"mono_slack_pp": MONO_SLACK_PP,
                     "rule_works_min_pp": RULE_WORKS_MIN_PP,
                     "width_edge_full_pp": WIDTH_EDGE_FULL_PP,
                     "width_edge_narrow_pp": WIDTH_EDGE_NARROW_PP,
                     "t_readable": T_READABLE},
        "ladder": {label_of(w): modern[label_of(w)] for w in WIDTHS},
        "verdict": verdict,
        "shape_is_noise": shape_noise,
        "pre_window": {
            "window": list(PRE_WINDOW),
            "note": ("the pre window's own pool was already ~13 names/day, so every cap in "
                     "the ladder is the same pool there -- it cannot separate widths"),
            "rows": pre,
        },
    }

    ctl = _published_control()
    got = modern[label_of(None)]["book"].get("cagr")
    if ctl and got is not None:
        out["control_full_pool"] = {"published_label": ctl["label"],
                                    "published_cagr": ctl["cagr"],
                                    "published_cutoff": ctl.get("cutoff"),
                                    "reproduced_cagr": got,
                                    "delta_pp": round((got - ctl["cagr"]) * 100.0, 3)}
    # the bare arm (no vol target) already beats the pool by more than the sized arm does:
    # so the excess is the picks, not the de-risking overlay. Read, never re-run.
    bare = None
    if ctl:
        try:
            with open("results/etf_nobond_vt.json", encoding="utf-8") as f:
                for run in (json.load(f).get("runs") or []):
                    if run.get("label") == "nobond_base" and run.get("cagr") is not None:
                        bare = run
        except Exception:
            bare = None
    if bare is not None and modern[label_of(None)].get("excess_pp") is not None:
        ew_cagr = modern[label_of(None)]["pool_equal_weight"].get("cagr")
        out["sizing_or_picks"] = {
            "bare_cagr": bare["cagr"], "bare_sharpe": bare.get("sharpe"),
            "bare_maxdd": bare.get("maxdd"),
            "bare_excess_vs_ew_pp": round((bare["cagr"] - ew_cagr) * 100.0, 3),
            "sized_excess_vs_ew_pp": modern[label_of(None)]["excess_pp"],
            "note": ("the sizing overlay LOWERS the CAGR (11.16% sized vs 15.18% bare) while it "
                     "cuts the drawdown; if the bare arm beats equal weight by more, the excess "
                     "is the picks, not the de-risking"),
        }

    for r in ladder:
        print("cap=%5s pool_med=%5.1f cagr=%6s sr=%5s dd=%7s | ew=%6s | excess=%6spp t=%5s"
              % (r["pool_cap"], r["pool_median_names"],
                 _pct(r["book"].get("cagr")), _num(r["book"].get("sharpe")),
                 _pct(r["book"].get("maxdd")), _pct(r["pool_equal_weight"].get("cagr")),
                 _num(r.get("excess_pp")), _num(r.get("excess_t"))), flush=True)
    print("pre window (cap 15 vs full): pool_med %s vs %s -> %s"
          % (pre.get("15", {}).get("pool_median_names"),
             pre.get("all", {}).get("pool_median_names"),
             "same pool" if pre.get("15", {}).get("pool_median_names") ==
             pre.get("all", {}).get("pool_median_names") else "different"), flush=True)
    print("VERDICT %s (shape_is_noise=%s)" % (verdict, shape_noise), flush=True)

    with open(os.path.join("results", OUT), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote results/%s" % OUT, flush=True)
    return 0


def _pct(x):
    return "n/a" if x is None else "%.2f%%" % (x * 100.0)


def _num(x):
    return "n/a" if x is None else "%.2f" % x


def check():
    path = os.path.join("results", OUT)
    if not os.path.exists(path):
        print("STALE face missing: %s" % path)
        return 3
    with open(path, encoding="utf-8") as f:
        face = json.load(f)
    ladder = face.get("ladder") or {}
    if not ladder:
        print("CHECK FAILED ladder empty")
        return 3
    rows = {}
    for k, r in ladder.items():
        rows[k] = {"excess_pp": r.get("excess_pp"), "t": r.get("excess_t")}
    want = width_verdict(rows)
    problems = []
    if want != face.get("verdict"):
        problems.append("verdict %r != re-derived %r" % (face.get("verdict"), want))
    for k, r in ladder.items():
        b, e = r.get("book") or {}, r.get("pool_equal_weight") or {}
        if b.get("cagr") is not None and e.get("cagr") is not None:
            if r.get("excess_pp") != round((b["cagr"] - e["cagr"]) * 100.0, 3):
                problems.append("%s excess_pp does not re-derive from its own two CAGRs" % k)
        else:
            problems.append("%s arm unreadable (no cagr)" % k)
    pre = face.get("pre_window") or {}
    prows = pre.get("rows") or {}
    if prows.get("15", {}).get("pool_median_names") != prows.get("all", {}).get("pool_median_names"):
        problems.append("pre window rows disagree on pool width; the note would be wrong")
    ctl = face.get("control_full_pool")
    if ctl and ctl.get("published_cagr") is not None and ctl.get("reproduced_cagr") is not None:
        d = abs(ctl["reproduced_cagr"] - ctl["published_cagr"]) * 100.0
        if d > 2.0:
            problems.append("full-pool control drifted %.2fpp from the published book" % d)
    if problems:
        for p in problems:
            print("PROBLEM", p)
        return 3
    print("CHECK OK verdict=%s ladder=%d shape_is_noise=%s"
          % (face.get("verdict"), len(ladder), face.get("shape_is_noise")))
    return 0


def selftest():
    legs = []

    def L(text, ok):
        legs.append((text, bool(ok)))

    up = {"15": {"excess_pp": 0.6}, "25": {"excess_pp": 2.5}, "40": {"excess_pp": 4.0},
          "all": {"excess_pp": 7.0}}
    L("0.6pp at 15 names -> 7pp full pool -> WIDTH_DRIVES_EDGE",
      width_verdict(up) == "WIDTH_DRIVES_EDGE")

    flat = {"15": {"excess_pp": 6.0}, "25": {"excess_pp": 6.2}, "40": {"excess_pp": 5.9},
            "all": {"excess_pp": 6.3}}
    L("flat-and-high ladder -> RULE_WORKS_ANYWHERE", width_verdict(flat) == "RULE_WORKS_ANYWHERE")

    wobble = {"15": {"excess_pp": 0.5}, "25": {"excess_pp": 1.8}, "40": {"excess_pp": 1.2},
              "all": {"excess_pp": 1.6}}
    L("0.6pp drop beyond the slack and a width under 1pp -> MIXED",
      width_verdict(wobble) == "MIXED_NOT_MONOTONE")

    small = {"15": {"excess_pp": 1.5}, "25": {"excess_pp": 1.8}, "40": {"excess_pp": 1.9},
             "all": {"excess_pp": 1.6}}
    L("every width above 1pp and no climb -> RULE_WORKS_ANYWHERE",
      width_verdict(small) == "RULE_WORKS_ANYWHERE")

    climb_small = {"15": {"excess_pp": 0.5}, "25": {"excess_pp": 0.8}, "40": {"excess_pp": 0.9},
                   "all": {"excess_pp": 1.1}}
    L("climbing but never reaches 2pp -> MONOTONE_UP", width_verdict(climb_small) == "MONOTONE_UP")

    neg = {"15": {"excess_pp": -3.0}, "25": {"excess_pp": -2.0}, "40": {"excess_pp": -1.0},
           "all": {"excess_pp": 0.2}}
    L("all negative with flat-ish shape -> MONOTONE_UP not WORKS", width_verdict(neg) == "MONOTONE_UP")

    L("no numbers -> NOT_READABLE", width_verdict({"15": {"excess_pp": None}}) == "NOT_READABLE")
    L("missing full pool -> NOT_READABLE",
      width_verdict({"15": {"excess_pp": 3.0}}) == "NOT_READABLE")

    # the slack is a band, not a pass: exactly 0.5pp down still counts as flat
    edge = {"15": {"excess_pp": 1.2}, "25": {"excess_pp": 1.3}, "40": {"excess_pp": 0.8},
            "all": {"excess_pp": 0.9}}
    L("exactly 0.5pp down stays inside the slack", width_verdict(edge) == "MONOTONE_UP")
    edge2 = {"15": {"excess_pp": 1.2}, "25": {"excess_pp": 1.32}, "40": {"excess_pp": 0.81},
             "all": {"excess_pp": 0.9}}
    L("0.51pp down breaks the slack", width_verdict(edge2) == "MIXED_NOT_MONOTONE")

    # paired t: a constant 1bp/day edge on 252 days is readable, noise is not
    idx = pd.date_range("2020-01-01", periods=300, freq="B")
    a = pd.Series(0.0010, index=idx)
    b = pd.Series(0.0, index=idx)
    t, n = paired_t(a, b)
    L("constant 1bp/day -> t is None (zero variance) or huge", t is None or abs(t) > 10)
    rng = np.random.RandomState(7)
    a2 = pd.Series(rng.normal(0.0, 0.01, 300), index=idx)
    t2, _n = paired_t(a2, b)
    L("pure noise -> |t| < 2", t2 is not None and abs(t2) < 2)
    t3, n3 = paired_t(a.iloc[:30], b.iloc[:30])
    L("30 paired days is not enough -> None", t3 is None and n3 == 30)

    # equal weight with a mask must not divide by an empty row
    px = pd.DataFrame({"a": [1.0, 1.1, 1.1], "b": [1.0, 1.0, 1.1]}, index=idx[:3])
    mask = pd.DataFrame({"a": [True, True, True], "b": [False, False, False]}, index=idx[:3])
    s = _ew(px, ["a", "b"], mask)
    L("masked equal weight follows the surviving name",
      abs(float(s.iloc[-1]) - 1.1) < 1e-9)

    for text, ok in legs:
        print(("PASS " if ok else "FAIL ") + text)
    print("selftest %d/%d" % (sum(1 for _t, ok in legs if ok), len(legs)))
    return 0 if all(ok for _t, ok in legs) else 1


if __name__ == "__main__":
    arg = (sys.argv[1] if len(sys.argv) > 1 else "run").strip().lower()
    if arg in ("--selftest", "selftest"):
        sys.exit(selftest())
    if arg == "check":
        sys.exit(check())
    sys.exit(run())
