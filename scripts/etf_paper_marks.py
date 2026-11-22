"""Mark the bond-free ETF paper book to market -- the ledger records picks, not money.

Why this face exists
--------------------
``scripts/etf_paper_signal.py`` appends one row per signal date to
``results/etf_paper/ledger.jsonl``.  As of the 2026-10-23..2026-11-20 run of that ledger,
**17 of 18 rows carry ``period_return=None`` and ``nav=1.0``** (one row, 1.00027).  In other
words the forward book records *what it would hold* but never records *what that was worth*,
so no reader can answer the only question that matters: did the book make money?

This face answers it from the ledger's own weights and nothing else:

  * entry  = open of the first trading bar **after** the previous row's ``as_of``
    (the book's frozen rule is "signal at close, fill next open");
  * exit   = close of the current row's ``as_of``;
  * weight w of the previous row earns ``w * (exit_close / entry_open - 1)``;
  * the un-weighted remainder (``1 - sum(w)``) is cash and earns **0** -- no interest is
    credited, which is conservative;
  * periods compound into a NAV series starting at 1.0.

It writes a NEW face (``results/etf_paper_marks.json``); it never rewrites the ledger and
never touches any face another writer owns.  The upstream defect (empty nav/period_return)
is disclosed inside the face rather than silently repaired.

Verdict is frozen before the numbers are read: a forward record shorter than 60 trading
bars cannot support an inference, so the verdict says so instead of dressing up a month.

Usage:
    python scripts/etf_paper_marks.py run
    python scripts/etf_paper_marks.py --selftest
    python scripts/etf_paper_marks.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

LEDGER = os.path.join(ROOT, "results", "etf_paper", "ledger.jsonl")
OUT_JSON = os.path.join(ROOT, "results", "etf_paper_marks.json")

# ---- frozen verdict rule (read before the numbers were) -------------------------------
MIN_BARS_FOR_INFERENCE = 60          # one trading quarter of forward record
SHARPE_CONSISTENT = 1.0              # backtest candidate printed 1.13 on this config
# --------------------------------------------------------------------------------------


def ledger_sha(path=None):
    h = hashlib.sha256()
    with open(path or LEDGER, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def load_ledger(path=None):
    rows = []
    with io.open(path or LEDGER, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    rows.sort(key=lambda r: r["as_of"])
    return rows


def _entry_bar(idx, prev_as_of):
    """First bar strictly after prev_as_of, or None."""
    j = int(idx.searchsorted(pd.Timestamp(prev_as_of), side="right"))
    return j if j < len(idx) else None


def mark_period(prev, cur, close, openp, idx, fallbacks=None):
    """Return (period_return, engaged_weight, missing_syms) for one holding period."""
    t_end = pd.Timestamp(cur["as_of"])
    j = _entry_bar(idx, prev["as_of"])
    if j is None:
        return None, 0.0, ["<no entry bar>"]
    t_entry = idx[j]
    if t_entry > t_end:
        return None, 0.0, ["<entry after exit>"]
    r = 0.0
    engaged = 0.0
    missing = []
    for sym, w in prev.get("weights", {}).items():
        if w == 0 or sym not in close.columns or sym not in openp.columns:
            missing.append(sym)
            continue
        ci = close.columns.get_loc(sym)
        p0 = openp.at[t_entry, sym]
        p1 = close.at[t_end, sym]
        if not (np.isfinite(p0) and p0 > 0):
            k = j - 1                       # same-bar fallback: previous close as entry
            if k >= 0:
                p0 = close.iat[k, ci]
            if np.isfinite(p0) and p0 > 0 and fallbacks is not None:
                fallbacks.append(sym)
        if not (np.isfinite(p0) and p0 > 0 and np.isfinite(p1)):
            missing.append(sym)
            continue
        r += float(w) * (float(p1) / float(p0) - 1.0)
        engaged += float(w)
    return r, engaged, missing


def marks_from_frames(rows, close, openp):
    """Pure function: ledger rows + price frames -> period table. No I/O."""
    idx = close.index
    periods = []
    nav = 1.0
    bnav = 1.0
    for i in range(1, len(rows)):
        prev, cur = rows[i - 1], rows[i]
        fb = []
        r, engaged, missing = mark_period(prev, cur, close, openp, idx, fb)
        if r is None:
            periods.append({"from": prev["as_of"], "to": cur["as_of"],
                            "skipped": True, "missing": missing})
            continue
        nav = nav * (1.0 + r)
        # baseline: same names, same entry/exit, weights flattened (what "no scoring" earns)
        syms = [s for s, w in prev.get("weights", {}).items()
                if w and s in close.columns and s in openp.columns]
        br = 0.0
        cnt = 0
        j = _entry_bar(idx, prev["as_of"])
        t_end = pd.Timestamp(cur["as_of"])
        if j is not None and syms:
            t_entry = idx[j]
            if t_entry <= t_end:
                for s in syms:
                    p0 = openp.at[t_entry, s]
                    p1 = close.at[t_end, s]
                    if not (np.isfinite(p0) and p0 > 0):
                        k = j - 1
                        p0 = close.iat[k, close.columns.get_loc(s)] if k >= 0 else np.nan
                    if np.isfinite(p0) and p0 > 0 and np.isfinite(p1):
                        br += float(p1) / float(p0) - 1.0
                        cnt += 1
        br = br / cnt if cnt else None
        if br is not None:
            bnav = bnav * (1.0 + br)
        periods.append({
            "from": prev["as_of"], "to": cur["as_of"],
            "entry_bar": str(idx[j].date()), "exit_bar": str(t_end.date()),
            "period_return": round(r, 6),
            "engaged_weight": round(engaged, 6),
            "cash_weight_prev": round(1.0 - engaged, 6),
            "nav": round(nav, 6),
            "equal_weight_return": round(br, 6) if br is not None else None,
            "equal_weight_nav": round(bnav, 6),
            "entry_fallback": fb,
            "missing": missing,
        })
    return periods


def _stats(navs, rets, bars_days):
    if not rets:
        return {}
    arr = np.asarray(rets, dtype=float)
    cum = float(np.prod(1.0 + arr) - 1.0)
    peak = 1.0
    mdd = 0.0
    for v in navs:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1.0)
    sd = float(np.std(arr, ddof=1)) if len(arr) > 1 else float("nan")
    mean = float(np.mean(arr))
    return {
        "periods": len(arr),
        "calendar_days": int(bars_days),
        "cumulative_return": round(cum, 6),
        "mean_period": round(mean, 6),
        "worst_period": round(float(np.min(arr)), 6),
        "best_period": round(float(np.max(arr)), 6),
        "win_rate": round(float(np.mean(arr > 0)), 4),
        "period_vol": round(sd, 6) if np.isfinite(sd) else None,
        "annualised_arith": round(mean * 252.0 / max(1.0, bars_days / max(1, len(arr))), 6)
        if bars_days else None,
        "sharpe_arith": round(mean / sd * math.sqrt(252.0 / max(1.0, bars_days / max(1, len(arr)))), 4)
        if np.isfinite(sd) and sd > 0 else None,
        "max_drawdown": round(mdd, 6),
    }


def summary_of(periods, key="period_return", nav_key="nav"):
    rets = [p[key] for p in periods if not p.get("skipped") and p.get(key) is not None]
    navs = [p[nav_key] for p in periods if not p.get("skipped") and p.get(nav_key) is not None]
    bars = 0
    for p in periods:
        if p.get("skipped"):
            continue
        bars += int(np.busday_count(p["from"], p["to"])) or 1
    return _stats(navs, rets, bars)


def verdict_of(summary, baseline):
    n = summary.get("periods", 0)
    if n < MIN_BARS_FOR_INFERENCE:
        return ("NOT_INFORMATIVE_YET",
                "only %d forward holding periods (frozen floor %d bars): no forward claim is "
                "made either way; the point of this face is that the book now records money "
                "at all" % (n, MIN_BARS_FOR_INFERENCE))
    s = summary.get("sharpe_arith")
    c = summary.get("cumulative_return")
    bc = (baseline or {}).get("cumulative_return")
    if s is not None and s >= SHARPE_CONSISTENT and c is not None and c > 0:
        if bc is not None and c <= bc:
            return ("POSITIVE_BUT_BELOW_EQUAL_WEIGHT",
                    "forward Sharpe %.2f clears %.2f but the same names held flat did better "
                    "(%.2f%% vs %.2f%%)" % (s, SHARPE_CONSISTENT, bc * 100, c * 100))
        return ("FORWARD_CONSISTENT_WITH_BACKTEST",
                "forward Sharpe %.2f >= %.2f over %d bars" % (s, SHARPE_CONSISTENT, n))
    if c is not None and c < 0:
        return ("FORWARD_NEGATIVE", "cumulative %.2f%% over %d bars" % (c * 100, n))
    return ("FORWARD_BELOW_BACKTEST",
            "forward Sharpe %s vs backtest 1.13" % (s,))


def _gate_readable(blk):
    """A 17-period annualisation is an extrapolation, not a measurement.  Print it under a
    name that says so instead of letting it read as an annual return (r1880/r1980 family:
    the headline must not carry a number the sample cannot support)."""
    if blk.get("periods", 0) >= MIN_BARS_FOR_INFERENCE:
        return blk
    ext = {"annualised_arith": blk.pop("annualised_arith", None),
           "sharpe_arith": blk.pop("sharpe_arith", None)}
    blk["annualised_arith"] = None
    blk["sharpe_arith"] = None
    blk["arithmetic_extrapolation_NOT_READABLE"] = ext
    blk["suppressed_because"] = (
        "%d holding periods < frozen floor %d: annualised return and Sharpe are an "
        "extrapolation of a month, not a measurement" % (blk.get("periods", 0),
                                                         MIN_BARS_FOR_INFERENCE))
    return blk


def build_face(rows, close, openp, nflip=None, elapsed=None):
    periods = marks_from_frames(rows, close, openp)
    live = [p for p in periods if not p.get("skipped")]
    summary = _gate_readable(summary_of(periods))
    baseline = _gate_readable(summary_of(periods, key="equal_weight_return",
                                         nav_key="equal_weight_nav"))
    same_weights = sum(1 for p in live
                       if p.get("equal_weight_return") is not None
                       and p.get("period_return") == p.get("equal_weight_return"))
    verdict, why = verdict_of(summary, baseline)
    nav_ledger_filled = sum(1 for r in rows if r.get("period_return") is not None)
    return {
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "machine": os.environ.get("BIGMONEY_MACHINE", "bm-c"),
        "face": "etf_paper_marks",
        "evidence_cutoff": rows[-1]["as_of"] if rows else None,
        "ledger": {
            "path": "results/etf_paper/ledger.jsonl",
            "sha256": ledger_sha(),
            "rows": len(rows),
            "span": [rows[0]["as_of"], rows[-1]["as_of"]] if rows else [],
            "rows_with_period_return": nav_ledger_filled,
            "upstream_defect": (
                "etf_paper_signal writes period_return/nav, but only %d of %d rows carry a "
                "non-null period_return; this face recomputes money from the weights instead "
                "of trusting those fields" % (nav_ledger_filled, len(rows))
            ),
        },
        "method": {
            "entry": "open of first bar strictly after previous as_of",
            "exit": "close of this as_of",
            "cash": "un-weighted remainder earns 0 (no interest credited)",
            "equal_weight_baseline": "same names, same entry/exit, weights flattened",
        },
        "periods": periods,
        "summary": summary,
        "baseline_equal_weight": baseline,
        "weighting_observation": {
            "periods_where_scored_weights_equal_flat": same_weights,
            "of_periods": len(live),
            "why_it_matters": (
                "when the scored book holds every name at the same weight it cannot beat or "
                "lose to the flat baseline -- the only live decision in those periods is WHICH "
                "ten names, so the selection, not the sizing, is what is being tested"
            ),
        },
        "verdict": verdict,
        "verdict_because": why,
        "caveats": [
            "forward length is tiny (%d holding periods); nothing here overrides the "
            "backtest, it only shows what happened after the book started recording"
            % len(live),
            "weights are treated as constant inside a period; the live book re-scales daily "
            "on the 8%% vol target, so a long gap between ledger rows is approximated",
            "no dividends beyond the ETF's own price series; no commission modelled here "
            "(the ticket face already prices friction)",
        ],
        "n_flips_repaired": nflip,
        "panel": {
            "cutoff": str(close.index[-1].date()),
            "rows": int(close.shape[0]),
            "cols": int(close.shape[1]),
        },
        "elapsed_sec": round(elapsed, 1) if elapsed is not None else None,
    }


def run():
    t0 = time.time()
    import etf_composite_pf as E
    import etf_equity_alpha as A
    close, openp, amt, feats = E.build_panel()
    close, openp, nflip = A.repair_flips(close, openp)
    rows = load_ledger()
    face = build_face(rows, close, openp, nflip, time.time() - t0)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    s, b = face["summary"], face["baseline_equal_weight"]
    print("as_of", face["evidence_cutoff"], "periods", s.get("periods"),
          "cum", s.get("cumulative_return"), "mdd", s.get("max_drawdown"))
    print("baseline cum", b.get("cumulative_return"), "| verdict", face["verdict"])
    print("ledger nav filled", face["ledger"]["rows_with_period_return"], "/", face["ledger"]["rows"])
    return face


def check():
    """Recompute from the ledger + panel; classify drift (r1934: STALE vs CHECK FAILED).

    A checker that only recomputes from its own printed rows can never say "I am stale"
    (r1850/r1935).  So this one rebuilds the panel and re-derives the numbers, then asks
    three separate questions: did the ledger move, did the panel move, and do the numbers
    still match.  Only the third is a defect.
    """
    if not os.path.exists(OUT_JSON):
        print("STALE face missing:", OUT_JSON)
        return 3
    old = json.load(io.open(OUT_JSON, encoding="utf-8"))
    if old["ledger"]["sha256"] != ledger_sha():
        print("STALE ledger bytes moved since this face was written (%s -> %s)"
              % (old["ledger"]["sha256"][:12], ledger_sha()[:12]))
        return 3

    import etf_composite_pf as E
    import etf_equity_alpha as A
    close, openp, amt, feats = E.build_panel()
    close, openp, nflip = A.repair_flips(close, openp)
    fresh = build_face(load_ledger(), close, openp, nflip)
    panel_moved = (old.get("panel") or {}) != fresh.get("panel")

    diffs = []
    for k in ("periods", "cumulative_return", "max_drawdown", "win_rate", "periods"):
        if old["summary"].get(k) != fresh["summary"].get(k):
            diffs.append("summary.%s %s != %s" % (k, old["summary"].get(k), fresh["summary"].get(k)))
    if len(old["periods"]) != len(fresh["periods"]):
        diffs.append("period count %d != %d" % (len(old["periods"]), len(fresh["periods"])))
    else:
        for a, b in zip(old["periods"], fresh["periods"]):
            if a.get("to") != b.get("to") or a.get("period_return") != b.get("period_return"):
                diffs.append("period %s: %s != %s" % (a.get("to"), a.get("period_return"),
                                                      b.get("period_return")))
                break
    if diffs:
        if panel_moved:
            print("STALE panel re-stated under a fixed ledger:", "; ".join(diffs))
        else:
            print("CHECK FAILED (same inputs, different answer):", "; ".join(diffs))
        return 3
    print("OK periods", fresh["summary"]["periods"], "cum", fresh["summary"]["cumulative_return"],
          "verdict", fresh["verdict"])
    return 0


def selftest():
    """Synthetic-frame legs. No panel build, no network."""
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    # 4 bars, one symbol doubling between bar1-open and bar2-close
    idx = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"])
    close = pd.DataFrame({"AAA": [10.0, 12.0, 11.0, 13.0]}, index=idx)
    openp = pd.DataFrame({"AAA": [10.0, 10.0, 11.5, 12.5]}, index=idx)
    rows = [{"as_of": "2026-01-05", "weights": {"AAA": 1.0}, "nav": 1.0, "period_return": None},
            {"as_of": "2026-01-07", "weights": {"AAA": 1.0}, "nav": 1.0, "period_return": None}]
    per = marks_from_frames(rows, close, openp)
    p = per[0]
    leg("entry is the open of the first bar after prev as_of (10.0, not 12.0)",
        p["entry_bar"] == "2026-01-06" and abs(p["period_return"] - (11.0 / 10.0 - 1.0)) < 1e-9,
        str(p.get("period_return")))
    leg("exit is the close of the current as_of", p["exit_bar"] == "2026-01-07")
    leg("nav compounds the period return", abs(p["nav"] - 1.1) < 1e-9, str(p.get("nav")))

    # cash is not credited
    rows2 = [{"as_of": "2026-01-05", "weights": {"AAA": 0.5}, "nav": 1.0},
             {"as_of": "2026-01-07", "weights": {"AAA": 0.5}, "nav": 1.0}]
    p2 = marks_from_frames(rows2, close, openp)[0]
    leg("half the book in cash earns half the move and no interest",
        abs(p2["period_return"] - 0.5 * (11.0 / 10.0 - 1.0)) < 1e-9 and p2["cash_weight_prev"] == 0.5,
        str(p2.get("period_return")))

    # equal-weight baseline flattens the same names
    close3 = pd.DataFrame({"AAA": [10.0, 11.0, 12.0, 13.0], "BBB": [10.0, 13.0, 14.0, 20.0]}, index=idx)
    open3 = pd.DataFrame({"AAA": [10.0, 10.0, 11.0, 12.0], "BBB": [10.0, 10.0, 13.0, 14.0]}, index=idx)
    rows3 = [{"as_of": "2026-01-05", "weights": {"AAA": 0.9, "BBB": 0.1}, "nav": 1.0},
             {"as_of": "2026-01-07", "weights": {"AAA": 0.5, "BBB": 0.5}, "nav": 1.0}]
    p3 = marks_from_frames(rows3, close3, open3)[0]
    want_eq = ((12.0 / 10.0 - 1.0) + (14.0 / 10.0 - 1.0)) / 2.0
    leg("baseline equal-weights the same names over the same bars",
        abs(p3["equal_weight_return"] - want_eq) < 1e-9, str(p3.get("equal_weight_return")))
    leg("scored weights differ from the flat baseline when weights are not flat",
        abs(p3["period_return"] - (0.9 * 0.2 + 0.1 * 0.4)) < 1e-9, str(p3.get("period_return")))

    # skipped period when there is no bar after prev as_of
    rows4 = [{"as_of": "2026-01-08", "weights": {"AAA": 1.0}, "nav": 1.0},
             {"as_of": "2026-01-08", "weights": {"AAA": 1.0}, "nav": 1.0}]
    p4 = marks_from_frames(rows4, close, openp)[0]
    leg("no bar after the previous as_of -> period skipped, not zero-filled", p4.get("skipped") is True)

    # verdict floor
    v, why = verdict_of({"periods": 17, "cumulative_return": 0.5, "sharpe_arith": 3.0}, {})
    leg("17 periods never earns an inference", v == "NOT_INFORMATIVE_YET", v)
    v2, _ = verdict_of({"periods": 80, "cumulative_return": 0.1, "sharpe_arith": 1.5},
                       {"cumulative_return": 0.12})
    leg("beat the floor but lose to flat weights -> names it", v2 == "POSITIVE_BUT_BELOW_EQUAL_WEIGHT", v2)
    v3, _ = verdict_of({"periods": 80, "cumulative_return": 0.1, "sharpe_arith": 0.2}, {})
    leg("weak forward Sharpe -> FORWARD_BELOW_BACKTEST", v3 == "FORWARD_BELOW_BACKTEST", v3)

    bad = [n for n, ok, _ in legs if not ok]
    for n, ok, extra in legs:
        print(("PASS " if ok else "FAIL ") + n + (("  [" + extra + "]") if extra else ""))
    print("%d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
