#!/usr/bin/env python
"""book_pair_worst_windows -- how bad do the books actually get, and does the split hold there?

`book_pair_years` left one sentence open on purpose: the blend cushioned every bad year the
convertible book had (3 of 3), but the ETF book never had a bad year in the seven-year
overlap -- so "the split holds in a bad ETF year" was untested, not proven.

This face goes after that gap with observed data only.  It refuses to invent a bad ETF year
by scaling returns; instead it asks where the ETF book *was* at its worst and what the blend
did on exactly those bars:

  A. rolling 12-month windows (252 bars, stepped one bar).  The worst ETF window in the
     sample and the blend's return in that same window.  If the ETF's worst 12 months are
     still positive, the face says so in those words -- then "a bad ETF year" has no
     observation at all and the claim stays open rather than getting a green verdict.

  B. the ETF book's negative MONTHS.  Months do exist where it loses.  Every month the ETF
     book ends down, with the blend's return over the same month: how many of them the blend
     cushioned, and the average of each column on that same set.  This is the honest partial
     test -- a bad month is not a bad year, and the face prints that limit beside the number.

It builds no strategy and re-chooses no weight: it imports each parent book's own backtest and
the blend face's own chosen sleeve weight (best.w_cb), and it re-derives the blend's published
full-window CAGR/Sharpe as a known-truth cross-check before printing anything.

Usage:
  python scripts/book_pair_worst_windows.py run        # re-derive and publish json + md
  python scripts/book_pair_worst_windows.py check      # cheap drift check (stamps + numbers)
  python scripts/book_pair_worst_windows.py selftest   # offline arithmetic legs
"""

import argparse
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FACE = os.path.join(RESULTS, "book_pair_worst_windows.json")
MD = os.path.join(RESULTS, "book_pair_worst_windows.md")
BLEND_FACE = os.path.join(RESULTS, "book_pair_blend.json")

WINDOW_BARS = 252          # one trading year of bars
TOL_CAGR = 1e-6
TOL_SHARPE = 1e-6


def _rp(rel):
    return os.path.join(ROOT, rel)


def _iso(ts):
    import datetime as _dt

    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _now_iso():
    import datetime as _dt

    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _stamp(path):
    if not os.path.exists(path):
        return {"path": path, "missing": True}
    st = os.stat(path)
    return {"path": path, "size": int(st.st_size), "mtime": _iso(st.st_mtime)}


# ---------------------------------------------------------------- arithmetic
def rolling_windows(series, bars=WINDOW_BARS):
    """[(start_date, end_date, cumulative_return)] over every full `bars`-bar window."""
    vals = list(series.values)
    out = []
    if len(vals) <= bars:
        return out
    for i in range(0, len(vals) - bars):
        a, b = vals[i], vals[i + bars]
        if a <= 0:
            continue
        out.append((series.index[i], series.index[i + bars], b / a - 1.0))
    return out


def _dstr(x):
    return str(x.date()) if hasattr(x, "date") else str(x)


def worst_window(windows):
    if not windows:
        return None
    s, e, r = min(windows, key=lambda t: t[2])
    return {"start": _dstr(s), "end": _dstr(e), "ret": r}


def window_ret_at(series, start, end):
    """Return of `series` between the two dates (inclusive), or None if either is absent."""
    try:
        m = {_dstr(k): float(v) for k, v in zip(series.index, series.values)}
    except Exception:
        return None
    a = m.get(str(start))
    b = m.get(str(end))
    if a is None or b is None or a <= 0:
        return None
    return b / a - 1.0


def monthly_last(level):
    return level.groupby([level.index.year, level.index.month]).last()


def _lvl(level, key):
    # pandas allows level.loc[key]; the selftest stand-in only offers level.loc(key)
    try:
        return float(level.loc[key])
    except TypeError:
        return float(level.loc(key))


def negative_months(etf_level, cb_level, blend_level):
    """Every month the ETF book ends down, with each column's return over the same month."""
    return negative_months_from_monthly(monthly_last(etf_level), monthly_last(cb_level),
                                        monthly_last(blend_level))


def negative_months_from_monthly(e, c, b):
    rows = []
    for key in e.index:
        if key not in c.index or key not in b.index:
            continue
        prev = [k for k in e.index if k < key]
        if not prev:
            continue
        p = prev[-1]
        if not all(k in c.index and k in b.index for k in (p,)):
            continue
        e0, c0, b0 = _lvl(e, p), _lvl(c, p), _lvl(b, p)
        if min(e0, c0, b0) <= 0:
            continue
        re_ = _lvl(e, key) / e0 - 1.0
        rc = _lvl(c, key) / c0 - 1.0
        rb = _lvl(b, key) / b0 - 1.0
        if re_ < 0:
            rows.append({"month": "%04d-%02d" % key, "etf": re_, "cb": rc, "blend": rb})
    return rows


def cushion_stats(rows):
    if not rows:
        return {"n": 0, "cushioned": 0, "mean_etf": None, "mean_blend": None,
                "mean_cb": None, "worst": None}
    cushioned = sum(1 for r in rows if r["blend"] > r["etf"])
    worst = min(rows, key=lambda r: r["blend"])
    n = float(len(rows))
    return {
        "n": len(rows),
        "cushioned": cushioned,
        "mean_etf": sum(r["etf"] for r in rows) / n,
        "mean_blend": sum(r["blend"] for r in rows) / n,
        "mean_cb": sum(r["cb"] for r in rows) / n,
        "worst": worst,
    }


def verdict_of(rolling_worst, cush):
    """CUSHION_HOLDS / CUSHION_PARTIAL / NO_BAD_ETF_PERIOD_TO_TEST."""
    if not rolling_worst or rolling_worst.get("blend") is None:
        return "NO_BAD_ETF_PERIOD_TO_TEST"
    if rolling_worst["etf"] >= 0:
        return "NO_BAD_ETF_PERIOD_TO_TEST"
    if cush["n"] == 0:
        return "NO_BAD_ETF_PERIOD_TO_TEST"
    if cush["cushioned"] == cush["n"] and rolling_worst["blend"] > rolling_worst["etf"]:
        return "CUSHION_HOLDS"
    if rolling_worst["blend"] > rolling_worst["etf"]:
        return "CUSHION_PARTIAL"
    return "CUSHION_FAILS"


# ---------------------------------------------------------------- build
def build(write=True, quiet=False):
    import book_pair_blend as B

    cb, cb_meta = B.load_cb()
    etf, etf_meta = B.load_etf()
    cb_w, etf_w, idx = B.align(cb, etf)
    if cb_w is None:
        raise SystemExit("the two books share no days -- refusing to measure worst windows")

    with open(BLEND_FACE, encoding="utf-8") as fh:
        blend_face = json.load(fh)
    w_cb = float(blend_face["best"]["w_cb"])

    ra = cb_w.pct_change().dropna()
    re_ = etf_w.pct_change().dropna()
    common = ra.index.intersection(re_.index)
    bl = B.blend_daily(ra.reindex(common), re_.reindex(common), w_cb)

    # ---- A. rolling 12-month windows
    win_etf = rolling_windows(etf_w)
    win_cb = rolling_windows(cb_w)
    win_bl = rolling_windows(bl)
    worst_etf = worst_window(win_etf)
    worst_cb = worst_window(win_cb)
    worst_bl = worst_window(win_bl)
    etf_worst_window = None
    if worst_etf:
        etf_worst_window = {
            "start": worst_etf["start"], "end": worst_etf["end"],
            "etf": worst_etf["ret"],
            "blend": window_ret_at(bl, worst_etf["start"], worst_etf["end"]),
            "cb": window_ret_at(cb_w, worst_etf["start"], worst_etf["end"]),
        }
    blend_worst_window = None
    if worst_bl:
        blend_worst_window = {
            "start": worst_bl["start"], "end": worst_bl["end"],
            "blend": worst_bl["ret"],
            "etf": window_ret_at(etf_w, worst_bl["start"], worst_bl["end"]),
            "cb": window_ret_at(cb_w, worst_bl["start"], worst_bl["end"]),
        }
    n_neg_etf_windows = sum(1 for t in win_etf if t[2] < 0)

    # ---- B. ETF's negative months
    neg = negative_months(etf_w, cb_w, bl)
    cush = cushion_stats(neg)

    # ---- known-truth cross-check against the published blend numbers
    # read with the parent's own ruler (local_stats, base=1.0 for a cumprod that starts at 1)
    my = B.local_stats(bl, base=1.0)
    my_cagr = my.get("cagr")
    my_sharpe = my.get("sharpe")
    pub_cagr = float(blend_face["best"]["cagr"])
    pub_sharpe = float(blend_face["best"]["sharpe"])
    recon = {
        "cagr": {"published": pub_cagr, "mine": my_cagr,
                 "diff": None if my_cagr is None else my_cagr - pub_cagr,
                 "matched": my_cagr is not None and abs(my_cagr - pub_cagr) <= TOL_CAGR},
        "sharpe": {"published": pub_sharpe, "mine": my_sharpe,
                   "diff": None if my_sharpe is None else my_sharpe - pub_sharpe,
                   "matched": my_sharpe is not None and abs(my_sharpe - pub_sharpe) <= TOL_SHARPE},
    }

    verdict = verdict_of(etf_worst_window, cush)

    face = {
        "face": "book_pair_worst_windows",
        "generated_at": _now_iso(),
        "evidence_cutoff": str(max(cb_w.index[-1], etf_w.index[-1]).date()),
        "question": ("where does the ETF book actually get hurt, and does the 30/70 split "
                     "hold on exactly those bars?"),
        "opens": ("results/book_pair_years.json unverified[?]: 'etf has no negative year' -- "
                  "this face is the observed-data attempt to close it"),
        "sleeve": {"w_cb": w_cb, "w_etf": round(1.0 - w_cb, 4),
                   "chosen_by": "results/book_pair_blend.json best.w_cb (not re-chosen here)"},
        "window": {"first": str(bl.index[0].date()), "last": str(bl.index[-1].date()),
                   "bars": int(len(bl)), "window_bars": WINDOW_BARS,
                   "note": "rolling windows are 252 bars wide, stepped one bar; they overlap "
                           "heavily, so their spread is not a sample of independent years"},
        "method": {
            "a_rolling": "worst 252-bar window per column; the other two columns are read at "
                         "the same start/end dates so the comparison is on identical bars",
            "b_months": "every calendar month the ETF book ends down; each column's return over "
                        "the same month (from month-end to month-end levels)",
            "no_synthesis": "no return is scaled, shuffled or invented -- if the ETF book never "
                            "lost 12 months in a row, the face says so instead of manufacturing one",
        },
        "inputs": {
            "cb_panel": cb_meta.get("panel"),
            "blend_face": _stamp(BLEND_FACE),
            "blend_dep": {"w_cb": w_cb,
                          "window_last": (blend_face.get("window") or {}).get("last")},
        },
        "rolling": {
            "worst_etf_window": etf_worst_window,
            "worst_blend_window": blend_worst_window,
            "worst_cb_window": worst_cb,
            "n_windows": len(win_etf),
            "n_negative_etf_windows": n_neg_etf_windows,
            "worst_etf_window_beats": "the ETF's worst 252 bars in the sample",
        },
        "negative_months": {
            "n": cush["n"],
            "cushioned": cush["cushioned"],
            "mean_etf": cush["mean_etf"],
            "mean_blend": cush["mean_blend"],
            "mean_cb": cush["mean_cb"],
            "worst_blend_month": cush["worst"],
            "rows": neg if len(neg) <= 40 else neg[:20] + neg[-20:],
            "rows_truncated": len(neg) > 40,
        },
        "reconciliation": recon,
        "verdict": verdict,
        "unverified": [
            "a bad month is not a bad year: the month test says how the split behaves on the "
            "ETF's losing months, not on a sustained year-long drawdown it has never had",
            "rolling 252-bar windows overlap (1670 windows over 7 years), so the worst-window "
            "quantile is a description of this path, not an estimate of a distribution",
            "the 30/70 weight is the parent's in-sample optimum, inherited here without re-testing",
        ],
    }

    if write:
        with open(FACE, "w", encoding="utf-8") as fh:
            json.dump(_plain(face), fh, ensure_ascii=False, indent=1)
        with open(MD, "w", encoding="utf-8") as fh:
            fh.write(_md(face))
        if not quiet:
            print("BOOK-PAIR-WORST-WINDOWS verdict=%s" % verdict)
            if etf_worst_window:
                print("  worst etf 252 bars %s..%s: etf %+.2f%% blend %+.2f%% cb %+.2f%%" % (
                    etf_worst_window["start"], etf_worst_window["end"],
                    100 * etf_worst_window["etf"],
                    100 * (etf_worst_window["blend"] or 0.0),
                    100 * (etf_worst_window["cb"] or 0.0)))
            print("  etf negative months %d, cushioned %d, mean etf %+.2f%% blend %+.2f%%" % (
                cush["n"], cush["cushioned"],
                100 * (cush["mean_etf"] or 0.0), 100 * (cush["mean_blend"] or 0.0)))
            print("  recon cagr %s sharpe %s" % (recon["cagr"]["matched"], recon["sharpe"]["matched"]))
    return face


# ---------------------------------------------------------------- drift check
def check():
    """STALE if the parents moved (bytes or the numbers we lean on); CHECK FAILED if they did
    not move and our own published arithmetic no longer reproduces."""
    problems = []
    stale = False
    if not os.path.exists(FACE):
        return 3, {"ok": False, "problems": ["face missing: results/book_pair_worst_windows.json"]}
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    if not os.path.exists(BLEND_FACE):
        return 3, {"ok": False, "problems": ["STALE parent missing: results/book_pair_blend.json"]}
    with open(BLEND_FACE, encoding="utf-8") as fh:
        blend_face = json.load(fh)

    dep = (face.get("inputs") or {}).get("blend_dep") or {}
    now_w = float(blend_face["best"]["w_cb"])
    now_last = (blend_face.get("window") or {}).get("last")
    if abs(float(dep.get("w_cb", -1)) - now_w) > 1e-12:
        problems.append("STALE sleeve weight moved: %s -> %s" % (dep.get("w_cb"), now_w))
        stale = True
    if dep.get("window_last") != now_last:
        problems.append("STALE blend window moved: %s -> %s" % (dep.get("window_last"), now_last))
        stale = True

    cb_stamp_now = _stamp(_rp("data/cb_panel.csv.gz"))
    cb_stamp_old = ((face.get("inputs") or {}).get("cb_panel") or {})
    if cb_stamp_now.get("missing") or cb_stamp_old.get("missing"):
        problems.append("STALE cb panel stamp missing")
        stale = True
    elif (cb_stamp_now.get("size"), cb_stamp_now.get("mtime")) != (
            cb_stamp_old.get("size"), cb_stamp_old.get("mtime")):
        problems.append("STALE cb panel bytes moved: %s@%s -> %s@%s" % (
            cb_stamp_old.get("size"), cb_stamp_old.get("mtime"),
            cb_stamp_now.get("size"), cb_stamp_now.get("mtime")))
        stale = True

    if not stale:
        rec = face.get("reconciliation") or {}
        for key in ("cagr", "sharpe"):
            if not (rec.get(key) or {}).get("matched"):
                problems.append("CHECK FAILED %s does not reproduce the parent's published value" % key)
        stats = face.get("negative_months") or {}
        if stats.get("cushioned", 0) > stats.get("n", 0):
            problems.append("CHECK FAILED cushioned %s > n %s" % (stats.get("cushioned"), stats.get("n")))
        if face.get("verdict") == "CUSHION_HOLDS" and (
                (face.get("rolling") or {}).get("worst_etf_window") or {}).get("etf", 0) >= 0:
            problems.append("CHECK FAILED verdict holds while the etf's worst window is positive")

    return (3 if problems else 0), {"ok": not problems, "problems": problems}


# ---------------------------------------------------------------- selftest
def selftest():
    import datetime as _dt

    legs = []

    def leg(name, cond):
        legs.append({"leg": name, "ok": bool(cond)})

    class S(dict):
        pass

    # fake index series
    import types

    def mk(vals, start=_dt.date(2020, 1, 1)):
        idx = []
        d = start
        n = 0
        while len(idx) < len(vals):
            if d.weekday() < 5:
                idx.append(d)
                n += 1
            d += _dt.timedelta(days=1)
        class Ser:
            def __init__(self, values, index):
                self.values = values
                self.index = index

            def loc(self, key):
                if not hasattr(key, "weekday"):
                    key = _dt.date.fromisoformat(str(key))
                return self.values[self.index.index(key)]
        return Ser(list(vals), idx)

    # L1 window math on a known path
    s = mk([1.0, 1.1, 1.21])
    w = rolling_windows(s, bars=2)
    leg("L1 window return = end/start-1", abs(w[0][2] - 0.21) < 1e-12)

    # L2 worst picks the smallest
    w2 = [(1, 2, -0.05), (2, 3, -0.30), (3, 4, 0.10)]
    leg("L2 worst window is the min", worst_window(w2)["ret"] == -0.30)

    # L3 window_ret_at reads the level ratio at the given bars
    leg("L3 level ratio at window edges", abs(window_ret_at(s, s.index[0], s.index[2]) - 0.21) < 1e-12)

    # L4 cushion_stats counts only strictly better blend months
    rows = [{"etf": -0.05, "blend": -0.02, "cb": 0.01},
            {"etf": -0.03, "blend": -0.03, "cb": 0.0},
            {"etf": -0.04, "blend": -0.06, "cb": -0.01}]
    cs = cushion_stats(rows)
    leg("L4 cushioned counts strict improvements", cs["cushioned"] == 1 and cs["n"] == 3)
    leg("L5 mean etf is the plain mean", abs(cs["mean_etf"] + 0.04) < 1e-12)

    # L6 a positive ETF worst window must NOT read as cushioned
    leg("L6 positive etf window -> not testable",
        verdict_of({"etf": 0.02, "blend": 0.03}, cs) == "NO_BAD_ETF_PERIOD_TO_TEST")

    # L7 negative etf window + all months cushioned -> holds
    cush_all = cushion_stats([{"etf": -0.05, "blend": -0.01, "cb": 0.02}])
    leg("L7 holds when every month is cushioned and the window is better",
        verdict_of({"etf": -0.10, "blend": -0.02}, cush_all) == "CUSHION_HOLDS")

    # L8 window better but months not all cushioned -> partial
    leg("L8 partial when some months are not cushioned",
        verdict_of({"etf": -0.10, "blend": -0.02}, cs) == "CUSHION_PARTIAL")

    # L9 blend worse than etf in the window -> fails
    leg("L9 fails when the blend does worse on the window",
        verdict_of({"etf": -0.10, "blend": -0.12}, cush_all) == "CUSHION_FAILS")

    # L10 no window at all -> not testable
    leg("L10 no window -> not testable", verdict_of(None, cs) == "NO_BAD_ETF_PERIOD_TO_TEST")

    # L13 negative-month selector skips the very first month (no prior level)
    class Lv2:
        def __init__(self, idx, vals):
            self.index = idx
            self.values = vals

        def groupby(self, keys):
            outer = self
            class G:
                def last(self_inner):
                    acc = {}
                    for i, k in enumerate(outer.index):
                        acc[k] = outer.values[i]
                    return Lv(  # simple dict-like level series
                        None)
            return _MonthLevel(outer.index, outer.values)

    class _MonthLevel:
        def __init__(self, idx, vals):
            d = {}
            for i, k in enumerate(idx):
                d[(k.year, k.month)] = vals[i]
            self.d = d
            self.index = list(d.keys())

        def loc(self, key):
            return self.d[key]

    idx = [_dt.date(2020, 1, 31), _dt.date(2020, 2, 28), _dt.date(2020, 3, 31)]
    e = _MonthLevel(idx, [1.0, 0.95, 0.90])
    c = _MonthLevel(idx, [1.0, 1.02, 1.05])
    b = _MonthLevel(idx, [1.0, 0.99, 0.97])
    rows = negative_months_from_monthly(e, c, b)
    leg("L13 first month is skipped (no prior level)", len(rows) == 2)
    leg("L14 month returns use the prior month-end", abs(rows[0]["etf"] + 0.05) < 1e-12)

    ok = all(x["ok"] for x in legs)
    for x in legs:
        print(("  PASS " if x["ok"] else "  FAIL ") + x["leg"])
    print("SELFTEST %d/%d %s" % (sum(1 for x in legs if x["ok"]), len(legs), "ALL PASS" if ok else "FAILED"))
    return 0 if ok else 1


# ---------------------------------------------------------------- render
def _pct(x, nd=2):
    return "n/a" if x is None else ("%+." + str(nd) + "f%%") % (100.0 * x)


def _pp(x, nd=2):
    return "n/a" if x is None else ("%+." + str(nd) + "fpp") % (100.0 * x)


def _md(face):
    r = face["rolling"]
    m = face["negative_months"]
    ew = r.get("worst_etf_window") or {}
    bw = r.get("worst_blend_window") or {}
    L = []
    L.append("# The books at their worst: does the split hold where the ETF book actually hurts?")
    L.append("")
    L.append("- generated: %s · evidence cutoff: **%s** · window %s..%s (%d bars)" % (
        face["generated_at"], face["evidence_cutoff"],
        face["window"]["first"], face["window"]["last"], face["window"]["bars"]))
    L.append("- sleeve: %.0f%% convertible / %.0f%% ETF (parent's own choice, not re-chosen)" % (
        100 * face["sleeve"]["w_cb"], 100 * face["sleeve"]["w_etf"]))
    L.append("- verdict: **%s**" % face["verdict"])
    L.append("")
    L.append("## A. The ETF book's worst 252 bars")
    L.append("")
    L.append("| column | worst window | return |")
    L.append("|---|---|---|")
    L.append("| ETF | %s .. %s | **%s** |" % (ew.get("start"), ew.get("end"), _pct(ew.get("etf"))))
    L.append("| blend 30/70, same bars | %s .. %s | **%s** |" % (ew.get("start"), ew.get("end"), _pct(ew.get("blend"))))
    L.append("| convertible, same bars | %s .. %s | %s |" % (ew.get("start"), ew.get("end"), _pct(ew.get("cb"))))
    L.append("")
    L.append("The ETF book had **%d** negative 252-bar windows out of %d." % (
        r["n_negative_etf_windows"], r["n_windows"]))
    if ew and ew.get("etf") is not None and ew["etf"] >= 0:
        L.append("")
        L.append("> **It never had a losing one.** The worst 12 months of the ETF book in this sample "
                 "are still %s. So \"the split holds in a bad ETF year\" has no observation here — "
                 "this face does not get to call it proven." % _pct(ew["etf"]))
    L.append("")
    if bw:
        L.append("For reference the blend's own worst 252 bars: %s .. %s = **%s** (ETF %s, cb %s)." % (
            bw.get("start"), bw.get("end"), _pct(bw.get("blend")),
            _pct(bw.get("etf")), _pct(bw.get("cb"))))
        L.append("")
    L.append("## B. The ETF book's losing months — the bars that do exist")
    L.append("")
    L.append("Months the ETF book ended down: **%d**. The blend was better in **%d** of them." % (
        m["n"], m["cushioned"]))
    L.append("")
    L.append("| on those same months | mean |")
    L.append("|---|---|")
    L.append("| ETF | %s |" % _pct(m["mean_etf"]))
    L.append("| blend 30/70 | **%s** |" % _pct(m["mean_blend"]))
    L.append("| convertible | %s |" % _pct(m["mean_cb"]))
    L.append("")
    wm = m.get("worst_blend_month") or {}
    if wm:
        L.append("Worst of those months for the blend: **%s** — ETF %s, blend %s, cb %s." % (
            wm.get("month"), _pct(wm.get("etf")), _pct(wm.get("blend")), _pct(wm.get("cb"))))
        L.append("")
    L.append("## What this does and does not settle")
    L.append("")
    for u in face["unverified"]:
        L.append("- %s" % u)
    L.append("")
    L.append("Cross-check against the published blend face: CAGR %s / Sharpe %s (tolerance 1e-6)." % (
        "matches" if face["reconciliation"]["cagr"]["matched"] else "MISMATCH",
        "matches" if face["reconciliation"]["sharpe"]["matched"] else "MISMATCH"))
    L.append("")
    return "\n".join(L)


def _plain(o):
    if isinstance(o, dict):
        return {k: _plain(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_plain(v) for v in o]
    return o


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        build(write=True)
        return 0
    if args.cmd == "check":
        rc, info = check()
        print(json.dumps(info, ensure_ascii=False))
        return rc
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
