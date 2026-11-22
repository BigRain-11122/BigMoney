"""Does the answer depend on how far back you look for the cash rate?

Three faces in a row (r1963 / r1965 / r1966) printed a verdict of the form "this book is
worth about what the money earns doing nothing", and all three priced "doing nothing" with
one number: 1.777%/yr taken from `capital_placement.json`, a recent window.  r1966 also
measured the same GC001 daily roll over fifteen years at 2.495%/yr and warned in prose that
the difference must not be papered over.  Nobody has yet asked the question that matters for
a decision taken *today*: the lookback you use to read the cash rate is itself a free
parameter, and every "excess over cash" number this desk publishes inherits it.

This face measures that inheritance instead of arguing about it.  For each arm and for each
lookback in a frozen ladder it recomputes, on the same tail window:

    cash_cagr(L)   -- the GC001 overnight roll, net of exchange commission, resampled to
                      the panel's own trading days
    book_cagr(L)   -- the arm's own engine series, same tail, same calendar-day CAGR
    excess(L)      -- book_cagr(L) - cash_cagr(L)

and then asks whether the sign of `excess` survives the ladder.  A verdict that flips sign
somewhere in the ladder is not a finding about the book; it is a finding about the lookback.

Rules frozen before the first run:
  * one implementation per number: the roll comes from `bench_repo_ladder.run_bucket`
    (already the desk's published GC001 vehicle), the arms from the production engine via
    `etf_robust_pf.open_to_open_equity`, CAGR from `etf_equity_alpha.stats2` or the same
    calendar-day formula;
  * the ladder is fixed here, not searched: 21 / 63 / 126 / 252 / 504 / 1008 trading days
    plus the full sample.  No lookback may be added after seeing a result;
  * a lookback that cannot be filled on both series is printed as null, never silently
    dropped and never back-filled with the nearest one (r98: unknown is not zero);
  * the arms' published CAGRs (r1964) are re-derived, not re-typed, and a reproduction miss
    is a check failure rather than a footnote;
  * no judging line is moved: this face books nothing, changes no rule, and does not rank.

  python scripts/bench_cash_window_sensitivity.py run
  python scripts/bench_cash_window_sensitivity.py check
  python scripts/bench_cash_window_sensitivity.py --selftest

Outputs results/bench_cash_window_sensitivity.json and
research/BENCH-CASH-WINDOW-SENSITIVITY.md (numbers in the page are rendered from the face).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (HERE, ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

OUT_JSON = ROOT / "results" / "bench_cash_window_sensitivity.json"
OUT_MD = ROOT / "research" / "BENCH-CASH-WINDOW-SENSITIVITY.md"
FACE = "results/bench_cash_window_sensitivity.json"
SCRIPT = "scripts/bench_cash_window_sensitivity.py"

CASH_VEHICLE = "results/bench_repo_ladder.json::baseline.net_cagr"
CASH_VEHICLE_HINT = "results/bench_repo_ladder.json::baseline.net_cagr (GC001 overnight roll, 2011-2026)"
PARENT_ARMS = "results/etf_book_rent_horse_race.json"          # r1964: the arm CAGRs
SHORT_WINDOW_CASH = "results/capital_placement.json::config.cash_net_annual"  # 1.777%

REBAL = 20
N_HOLD = 5
COST = 0.0010
VOL_TARGET = 0.08
CAPITAL = 1_000_000.0
RANDOM_DRAWS = 8                       # must match r1964 or the coin arm cannot be reproduced

ARMS = ("tuned_composite_6", "single_mom_12_1", "single_vol_60_low", "random_pick_5")
ARM_TRIALS = {"tuned_composite_6": 58, "single_mom_12_1": 6,
              "single_vol_60_low": 6, "random_pick_5": 1}

# The ladder is the question.  Frozen before the first run; never extended after a result.
LOOKBACKS = (21, 63, 126, 252, 504, 1008)
FULL = "full"

REPRO_TOL_PP = 0.20                    # arms must reproduce r1964's CAGR, in percentage points
REPRO_TOL_SR = 0.02
CASH_ANCHOR_TOL_PP = 0.20              # full-sample roll must match the published vehicle
MIN_BARS_ALIGNED = 1000
MIN_HISTORY = 21                       # a 21-bar tail needs 22 points to make one year-ish CAGR

CRITERIA = {
    "capital_cny": CAPITAL,
    "rebal_bars": REBAL,
    "n_hold": N_HOLD,
    "cost_bp_per_side": COST * 1e4,
    "vol_target": VOL_TARGET,
    "random_draws": RANDOM_DRAWS,
    "lookbacks_bars": list(LOOKBACKS) + [FULL],
    "arm_trials": ARM_TRIALS,
    "repro_tol_pp": REPRO_TOL_PP,
    "repro_tol_sr": REPRO_TOL_SR,
    "cash_anchor_tol_pp": CASH_ANCHOR_TOL_PP,
    "min_bars_aligned": MIN_BARS_ALIGNED,
    "cash_vehicle": CASH_VEHICLE,
    "parent_arms": PARENT_ARMS,
    "cagr": "calendar-day CAGR (same formula as etf_equity_alpha.stats2)",
    "frozen": "constants above were written before the first run",
}


# ---------------------------------------------------------------------------- small utils
def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _dump(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")


def _load(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _pct(x):
    return None if x is None else round(100.0 * float(x), 4)


def tail_cagr(eq, bars):
    """Calendar-day CAGR of the last `bars` points; None when the tail cannot be filled."""
    s = pd.Series(eq, dtype="float64").dropna()
    if bars != FULL:
        if len(s) < int(bars) + 1:
            return None
        s = s.iloc[-(int(bars) + 1):]
    if len(s) < 3:
        return None
    days = int((s.index[-1] - s.index[0]).days)
    if days <= 0 or s.iloc[0] <= 0:
        return None
    return float(s.iloc[-1] / s.iloc[0]) ** (365.0 / days) - 1.0


def tail_window(eq, bars):
    """The date span a given lookback actually reads (so a flip can be attributed)."""
    s = pd.Series(eq, dtype="float64").dropna()
    if bars != FULL:
        if len(s) < int(bars) + 1:
            return None
        s = s.iloc[-(int(bars) + 1):]
    if len(s) < 2:
        return None
    return [str(s.index[0].date()), str(s.index[-1].date())]


def aligned_excess(book, cash):
    """Daily excess series on the intersection of the two calendars."""
    b = pd.Series(book, dtype="float64").dropna().pct_change()
    c = pd.Series(cash, dtype="float64").dropna().pct_change()
    both = pd.concat([b.rename("book"), c.rename("cash")], axis=1, join="inner").dropna()
    return both["book"] - both["cash"], len(both)


def excess_t(ex):
    """Annualised t of a daily excess series.  Overlapping holding periods are NOT
    corrected here -- the number is printed with that caveat, not polished."""
    ex = pd.Series(ex, dtype="float64").dropna()
    if len(ex) < 3 or float(ex.std(ddof=1)) == 0.0:
        return None, int(len(ex))
    return float(ex.mean() / ex.std(ddof=1) * math.sqrt(len(ex))), int(len(ex))


def sign_of(x):
    if x is None:
        return None
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


# ------------------------------------------------------------------------------ cash curve
def cash_curve():
    """The desk's own GC001 overnight vehicle, one point per repo trading day."""
    import bench_repo_ladder as L

    got = L._read("GC001")
    if got is None or len(got["close"]) < MIN_HISTORY:
        return None, {"reason": "GC001 panel missing or too short"}
    calendar = list(got["close"].index)
    eq, log = L.run_bucket(got["close"], 1, calendar)
    return eq, log


# ------------------------------------------------------------------------------- arm series
def _elig(close, amt):
    import etf_composite_pf as E

    hist = close.notna().cumsum()
    return (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)


def _scores(close, amt, feats):
    import etf_composite_pf as E

    cols, idx = close.columns, close.index
    elig = _elig(close, amt)
    out = {"tuned_composite_6": E.build_score(close, amt, feats)}

    def one(name, sign):
        f = feats.get(name)
        if f is None:
            raise RuntimeError("factor %s missing" % name)
        f = f.reindex(index=idx, columns=cols)
        z = (f.rank(axis=1, pct=True) - 0.5) * 2.0
        return (sign * z).where(elig)

    out["single_mom_12_1"] = one("mom_12_1", +1.0)
    out["single_vol_60_low"] = one("vol_60", -1.0)
    return out, elig


def _random_score(close, elig, draw):
    rng = np.random.default_rng(90210 + int(draw))
    mat = rng.random((len(close.index), len(close.columns)))
    return pd.DataFrame(mat, index=close.index, columns=close.columns).where(elig)


def _engine(close, openp, amt, score):
    import etf_robust_pf as R

    diag = []
    ser, _turn = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                       vol_target=VOL_TARGET, diag=diag)
    return ser


# ----------------------------------------------------------------------------------- verdict
def arm_verdict(cells):
    """Sign survival of the excess across the frozen ladder, for one arm."""
    signs = [sign_of(c["excess_pp"]) for c in cells if c["excess_pp"] is not None]
    if not signs:
        return "NOT_MEASURABLE", None
    uniq = sorted(set(signs))
    if len(uniq) > 1:
        return "FLIPS_WITH_LOOKBACK", uniq
    return ("BOOK_WINS_ON_EVERY_LOOKBACK" if uniq == [1]
            else "CASH_WINS_ON_EVERY_LOOKBACK" if uniq == [-1]
            else "TIE_ON_EVERY_LOOKBACK"), uniq


def flip_point(cells):
    """The first adjacent pair of lookbacks whose excess changes sign (or None)."""
    seq = [(c["lookback"], sign_of(c["excess_pp"])) for c in cells
           if c["excess_pp"] is not None]
    for (l0, s0), (l1, s1) in zip(seq, seq[1:]):
        if s0 != 0 and s1 != 0 and s0 != s1:
            return [l0, l1]
    return None


def face_verdict(arms_out):
    flipping = [a["arm"] for a in arms_out if a["verdict"] == "FLIPS_WITH_LOOKBACK"]
    measurable = [a for a in arms_out if a["verdict"] != "NOT_MEASURABLE"]
    if not measurable:
        return {"verdict": "NOT_MEASURABLE",
                "why": "no arm could be priced on the full ladder"}
    if flipping:
        return {"verdict": "LOOKBACK_DECIDES_THE_ANSWER",
                "why": "the sign of excess-over-cash flips inside the frozen ladder",
                "arms_that_flip": flipping}
    won = [a["arm"] for a in measurable if a["verdict"] == "BOOK_WINS_ON_EVERY_LOOKBACK"]
    lost = [a["arm"] for a in measurable if a["verdict"] == "CASH_WINS_ON_EVERY_LOOKBACK"]
    if won and not lost:
        return {"verdict": "BOOK_WINS_ON_EVERY_LOOKBACK",
                "why": "every measurable arm beats the cash roll on every lookback",
                "arms": won}
    if lost and not won:
        return {"verdict": "CASH_WINS_ON_EVERY_LOOKBACK",
                "why": "every measurable arm loses to the cash roll on every lookback",
                "arms": lost}
    return {"verdict": "MIXED_BUT_STABLE",
            "why": "each arm keeps one sign; the arms disagree with each other, not with the lookback",
            "book_wins": won, "cash_wins": lost}


# ------------------------------------------------------------------------------------- build
def build(write=True, verbose=True):
    import etf_composite_pf as E
    import etf_equity_alpha as A
    import etf_book_production as P

    t0 = time.time()

    # ---- the cash vehicle first: everything else is measured against it
    cash, cash_log = cash_curve()
    if cash is None:
        payload = {"kind": "bench_cash_window_sensitivity", "generated": _now(),
                   "script": SCRIPT, "criteria": CRITERIA,
                   "verdict": {"verdict": "DATA-BLOCKED", "why": cash_log.get("reason")}}
        if write:
            _dump(OUT_JSON, payload)
        return payload

    # ---- the arms, on the production universe (same order as etf_book_production)
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols_keep = [c for c in close.columns if cls[c] in P.USE_CLASSES]
    close, openp, amt = close[cols_keep], openp[cols_keep], amt[cols_keep]
    feats = {k: v.reindex(columns=cols_keep) for k, v in feats.items()}

    scores, elig = _scores(close, amt, feats)

    parent = _load(ROOT / PARENT_ARMS) if (ROOT / PARENT_ARMS).exists() else {}
    pub = {}
    for row in parent.get("arms") or []:
        if row.get("arm") in ARMS and row.get("cagr") is not None:
            pub[row["arm"]] = row

    series = {}
    for name in ARMS:
        score = _random_score(close, elig, 0) if name == "random_pick_5" else scores[name]
        if name == "random_pick_5":
            # the coin cell in r1964 averages RANDOM_DRAWS independent draws
            acc = None
            for draw in range(RANDOM_DRAWS):
                ser = _engine(close, openp, amt, _random_score(close, elig, draw))
                acc = ser if acc is None else acc + ser
            series[name] = acc / float(RANDOM_DRAWS)
        else:
            series[name] = _engine(close, openp, amt, score)
        if verbose:
            print("engine %-18s bars=%d" % (name, len(series[name])), flush=True)

    # ---- one table: lookback x arm
    cash_tail = {}
    cash_span = {}
    for L in list(LOOKBACKS) + [FULL]:
        cash_tail[str(L)] = tail_cagr(cash, L)
        cash_span[str(L)] = tail_window(cash, L)

    arms_out = []
    for name in ARMS:
        eq = series[name]
        ex_all, n_aligned = aligned_excess(eq, cash)
        t_stat, n_t = excess_t(ex_all)
        cells = []
        for L in list(LOOKBACKS) + [FULL]:
            bc = tail_cagr(eq, L)
            cc = cash_tail[str(L)]
            ex = None if (bc is None or cc is None) else round(100.0 * (float(bc) - float(cc)), 4)
            cells.append({
                "lookback": L,
                "lookback_bars": (None if L == FULL else int(L)),
                "book_window": tail_window(eq, L),
                "book_cagr": None if bc is None else round(float(bc), 6),
                "cash_cagr": None if cc is None else round(float(cc), 6),
                "excess_pp": ex,
                "excess_cny": None if ex is None else round(CAPITAL * ex / 100.0, 2),
            })
        v, signs = arm_verdict(cells)
        p = pub.get(name) or {}
        repro = None
        if p.get("cagr") is not None:
            repro = {
                "published_cagr": p.get("cagr"),
                "published_sharpe": p.get("sharpe"),
                "cagr_gap_pp": round(100.0 * (float(tail_cagr(eq, FULL)) - float(p["cagr"])), 4),
            }
            repro["cagr_within_tol"] = bool(abs(repro["cagr_gap_pp"]) <= REPRO_TOL_PP)
        arms_out.append({
            "arm": name,
            "n_trials": ARM_TRIALS[name],
            "bars": int(len(eq)),
            "window": [str(eq.index[0].date()), str(eq.index[-1].date())],
            "cells": cells,
            "signs_seen": signs,
            "verdict": v,
            "flip_between": flip_point(cells),
            "excess_full_t": None if t_stat is None else round(float(t_stat), 4),
            "excess_full_bars": n_t,
            "aligned_bars_with_cash": n_aligned,
            "reproduction": repro,
        })

    # ---- the cash vehicle's own lookback table, read by a treasurer with no book at all
    cash_table = [{"lookback": L,
                   "lookback_bars": (None if L == FULL else int(L)),
                   "window": cash_span[str(L)],
                   "cash_cagr": (None if cash_tail[str(L)] is None
                                 else round(float(cash_tail[str(L)]), 6)),
                   "cash_money_on_capital": (None if cash_tail[str(L)] is None
                                             else round(CAPITAL * float(cash_tail[str(L)]), 2))}
                  for L in list(LOOKBACKS) + [FULL]]

    # ---- anchors: the full-sample roll must be the published vehicle; the short-window
    #      constant must be findable in its own face (two numbers, two windows, both printed)
    ladder = _load(ROOT / "results" / "bench_repo_ladder.json") if \
        (ROOT / "results" / "bench_repo_ladder.json").exists() else {}
    published_full = ((ladder.get("baseline") or {}).get("net_cagr"))
    anchor_gap_pp = (None if (published_full is None or cash_tail[FULL] is None)
                     else round(100.0 * (float(cash_tail[FULL]) - float(published_full)), 4))
    short_window = None
    try:
        cp = _load(ROOT / "results" / "capital_placement.json")
        short_window = float((cp.get("config") or {}).get("cash_net_annual"))
    except Exception:                                                # noqa: BLE001
        short_window = None

    # ---- the question a treasurer actually asks: if I decide today, which arms clear cash
    #      on the two horizons that are close enough to be information about now?
    def at(L):
        out = []
        for a in arms_out:
            c = next((x for x in a["cells"] if x["lookback"] == L), None)
            if c and c["excess_pp"] is not None:
                out.append({"arm": a["arm"], "excess_pp": c["excess_pp"],
                            "excess_cny": c["excess_cny"]})
        return sorted(out, key=lambda r: -(r["excess_pp"] or 0))

    def winners(rows):
        return [r["arm"] for r in rows if (r["excess_pp"] or 0) > 0]

    recent = {"one_year": {"lookback": 252, "arms": at(252)},
              "two_year": {"lookback": 504, "arms": at(504)}}
    recent["one_year"]["arms_above_cash"] = winners(recent["one_year"]["arms"])
    recent["two_year"]["arms_above_cash"] = winners(recent["two_year"]["arms"])
    recent["verdict"] = (
        "NOTHING_CLEARS_CASH_TODAY"
        if not recent["one_year"]["arms_above_cash"] and not recent["two_year"]["arms_above_cash"]
        else "SOME_ARMS_CLEAR_CASH_ON_A_HORIZON_READER_CAN_DEFEND")
    recent["why"] = ("judged on the 1-year and 2-year rungs only: these are the horizons whose "
                     "cash rate is still the rate you can get today; the longer rungs answer a "
                     "different question, namely what this book did when cash paid 2.5%")

    face = {
        "kind": "bench_cash_window_sensitivity",
        "generated": _now(),
        "script": SCRIPT,
        "question": ("for a decision taken today, does 'this book is worth what cash earns' "
                     "survive the choice of how far back the cash rate is read?"),
        "criteria": CRITERIA,
        "cash_vehicle": {
            "source": CASH_VEHICLE_HINT,
            "window": [str(cash.index[0].date()), str(cash.index[-1].date())],
            "points": int(len(cash)),
            "lend_log": cash_log,
            "full_cagr": None if cash_tail[FULL] is None else round(float(cash_tail[FULL]), 6),
            "published_full": published_full,
            "anchor_gap_pp": anchor_gap_pp,
            "short_window_constant": short_window,
            "short_window_source": SHORT_WINDOW_CASH,
        },
        "cash_table": cash_table,
        "panel": {
            "universe_after_class_filter": int(close.shape[1]),
            "flips_repaired": int(n_flip),
            "bars": int(close.shape[0]),
            "window": [str(close.index[0].date()), str(close.index[-1].date())],
        },
        "arms": arms_out,
        "recent_horizons": recent,
        "verdict": face_verdict(arms_out),
        "evidence_cutoff": str(close.index[-1].date()),
        "evidence_cutoff_source": "panel last bar (the arms' own series end here)",
        "honest": [
            "the daily excess t does not correct for overlapping 20-bar holding periods; "
            "it is a scale reference, not a significance claim",
            "a short lookback's CAGR is that many days' return annualised, so the 21- and "
            "63-bar rungs are noisier by construction than the 1008-bar and full rungs; "
            "they are printed so the flip is visible, not as comparable long-run returns",
            "arms are priced on a surviving-ETF universe; the lookback ladder cannot "
            "remove that bias",
            "cash is one vehicle (SSE GC001 net of commission); other liquid legs may "
            "carry a different window profile",
            "no lookback was added after seeing a result; the ladder is the frozen question",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    if write:
        _dump(OUT_JSON, face)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text(render_md(face), encoding="utf-8", newline="\n")
    if verbose:
        print("verdict=%s" % face["verdict"].get("verdict"), flush=True)
        print("cash full=%.4f%% published=%.4f%% gap=%spp" %
              (100 * (face["cash_vehicle"]["full_cagr"] or 0.0),
               100 * (published_full or 0.0), anchor_gap_pp), flush=True)
    return face


# ---------------------------------------------------------------------------------- render
def _pp(x, nd=2):
    return "n/a" if x is None else ("%.*fpp" % (nd, x))


def _pc(x, nd=2):
    return "n/a" if x is None else ("%.*f%%" % (nd, 100.0 * x))


def render_md(face):
    cv = face["cash_vehicle"]
    out = []
    out.append("# Does the cash benchmark answer depend on how far back you look?\n")
    out.append("Window of the arms: %s -> %s (%d bars). Cash vehicle: %s, %d points, %s -> %s.\n"
               % (face["panel"]["window"][0], face["panel"]["window"][1], face["panel"]["bars"],
                  cv["source"].split("::")[0], cv["points"], cv["window"][0], cv["window"][1]))
    out.append("## The cash vehicle's own ladder (nothing to do with any book)\n")
    out.append("| lookback | GC001 roll, net | on 1,000,000 CNY |")
    out.append("|---|---|---|")
    for r in face["cash_table"]:
        lb = "full" if r["lookback"] == FULL else "%d bars" % r["lookback"]
        out.append("| %s | %s | %s |" % (lb, _pc(r["cash_cagr"], 4),
                                         "n/a" if r["cash_money_on_capital"] is None
                                         else "{:,.0f} CNY".format(r["cash_money_on_capital"])))
    out.append("")
    out.append("Full-sample roll %s against the published vehicle %s (gap %s); the constant the "
               "older faces used is %s from `%s`.\n"
               % (_pc(cv["full_cagr"], 4), _pc(cv["published_full"], 4),
                  _pp(cv["anchor_gap_pp"], 3),
                  _pc(cv["short_window_constant"], 4), cv["short_window_source"].split("::")[0]))
    out.append("## Excess over cash, per arm and per lookback\n")
    cols = list(LOOKBACKS) + [FULL]
    out.append("| arm | %s | verdict | flip between |" % " | ".join(
        [("full" if L == FULL else "%d" % L) for L in cols]))
    out.append("|---|%s---|" % ("---|" * len(cols)))
    for a in face["arms"]:
        cells = {(c["lookback"]): c for c in a["cells"]}
        row = [a["arm"]]
        for L in cols:
            row.append(_pp(cells[L]["excess_pp"]))
        row.append(a["verdict"])
        fp = a.get("flip_between")
        row.append("n/a" if not fp else "%s -> %s" % tuple(
            "full" if x == FULL else x for x in fp))
        out.append("| %s |" % " | ".join(str(x) for x in row))
    out.append("")
    out.append("Full-sample daily excess t (no overlap correction): %s\n"
               % ", ".join("%s %s" % (a["arm"], "n/a" if a["excess_full_t"] is None
                                      else "%.2f" % a["excess_full_t"])
                           for a in face["arms"]))
    out.append("## What each rung actually reads\n")
    out.append("| lookback | cash window | cash | " +
               " | ".join(a["arm"] for a in face["arms"]) + " |")
    out.append("|---|---|---|%s" % ("---|" * len(face["arms"])))
    for r in face["cash_table"]:
        L = r["lookback"]
        w = r["window"]
        row = ["full" if L == FULL else "%d" % L,
               "n/a" if not w else "%s -> %s" % (w[0], w[1]),
               _pc(r["cash_cagr"], 4)]
        for a in face["arms"]:
            c = next(x for x in a["cells"] if x["lookback"] == L)
            row.append(_pp(c["excess_pp"]))
        out.append("| %s |" % " | ".join(row))
    out.append("")
    out.append("## If the decision is taken today (1-year and 2-year rungs only)\n")
    rh = face.get("recent_horizons") or {}
    for key in ("one_year", "two_year"):
        blk = rh.get(key) or {}
        out.append("**%s (lookback %s bars)** -- arms above cash: %s\n"
                   % (key.replace("_", "-"), blk.get("lookback"),
                      ", ".join(blk.get("arms_above_cash") or []) or "none"))
        out.append("| arm | excess | on 1,000,000 CNY |")
        out.append("|---|---|---|")
        for r in blk.get("arms") or []:
            out.append("| %s | %s | %s |" % (r["arm"], _pp(r["excess_pp"]),
                                             "n/a" if r["excess_cny"] is None
                                             else "{:,.0f} CNY".format(r["excess_cny"])))
        out.append("")
    out.append("**Today's reading: %s.** %s\n" % (rh.get("verdict"), rh.get("why")))
    v = face["verdict"]
    out.append("**Headline: %s.**\n" % v.get("verdict"))
    out.append("Why: %s\n" % v.get("why"))
    if v.get("arms_that_flip"):
        out.append("Arms whose sign flips inside the ladder: %s\n" % ", ".join(v["arms_that_flip"]))
    out.append("What this face does not claim: " + "; ".join(face["honest"]) + "\n")
    out.append("Generated %s by `%s`.\n" % (face["generated"], face["script"]))
    return "\n".join(out)


# ------------------------------------------------------------------------------------ check
def check(path=None):
    p = Path(path) if path else OUT_JSON
    if not p.exists():
        print("CHECK FAILED: face missing at %s" % p)
        return 1
    face = _load(p)
    problems = []

    # 1. every cell's excess must be book - cash on the printed numbers.  The tolerance is
    #    the face's own storage precision (two legs at 6dp feed a 4dp difference): anything
    #    tighter reddens a correct face, which is r1935's lesson about rulers.
    tol = 1e-4 + 1e-9
    for a in face.get("arms") or []:
        for c in a.get("cells") or []:
            if c["book_cagr"] is None or c["cash_cagr"] is None:
                if c["excess_pp"] is not None:
                    problems.append("%s/%s prints excess without both legs" % (a["arm"], c["lookback"]))
                continue
            want = round(100.0 * (c["book_cagr"] - c["cash_cagr"]), 4)
            if abs(want - c["excess_pp"]) > tol:
                problems.append("%s/%s excess %s != %s" % (a["arm"], c["lookback"],
                                                           c["excess_pp"], want))

    # 2. the verdict and the flip point must re-derive from the printed cells
    for a in face.get("arms") or []:
        v, signs = arm_verdict(a["cells"])
        if v != a["verdict"]:
            problems.append("%s verdict %s != re-derived %s" % (a["arm"], a["verdict"], v))
        if flip_point(a["cells"]) != a.get("flip_between"):
            problems.append("%s flip point %s != re-derived %s"
                            % (a["arm"], a.get("flip_between"), flip_point(a["cells"])))
    want_face = face_verdict(face.get("arms") or [])
    if want_face.get("verdict") != (face.get("verdict") or {}).get("verdict"):
        problems.append("face verdict %s != re-derived %s"
                        % ((face.get("verdict") or {}).get("verdict"), want_face.get("verdict")))

    # 3. the cash table must agree with the arms' cash leg on every lookback, and each
    #    printed money column must be the printed pp applied to the printed capital
    table = {r["lookback"]: r["cash_cagr"] for r in face.get("cash_table") or []}
    for a in face.get("arms") or []:
        for c in a.get("cells") or []:
            t = table.get(c["lookback"])
            if t is None or c["cash_cagr"] is None:
                continue
            if abs(t - c["cash_cagr"]) > 1e-6:
                problems.append("%s/%s cash %s != table %s"
                                % (a["arm"], c["lookback"], c["cash_cagr"], t))
            if c.get("excess_cny") is not None and c.get("excess_pp") is not None:
                want = round(CAPITAL * c["excess_pp"] / 100.0, 2)
                if abs(want - c["excess_cny"]) > 0.02:
                    problems.append("%s/%s excess_cny %s != %s"
                                    % (a["arm"], c["lookback"], c["excess_cny"], want))

    # 4. the "today" block must re-derive from the cells it names
    rh = face.get("recent_horizons") or {}
    for key in ("one_year", "two_year"):
        blk = rh.get(key) or {}
        L = blk.get("lookback")
        want = []
        for a in face.get("arms") or []:
            c = next((x for x in a["cells"] if x["lookback"] == L), None)
            if c and c["excess_pp"] is not None:
                want.append((a["arm"], c["excess_pp"], c["excess_cny"]))
        want.sort(key=lambda r: -r[1])
        got = [(r["arm"], r["excess_pp"], r["excess_cny"]) for r in blk.get("arms") or []]
        if len(got) != len(want) or any(abs(g[1] - w[1]) > 1e-6 for g, w in zip(got, want)):
            problems.append("recent_horizons/%s does not re-derive from the cells" % key)
        if [r["arm"] for r in blk.get("arms") or [] if (r["excess_pp"] or 0) > 0] != \
                (blk.get("arms_above_cash") or []):
            problems.append("recent_horizons/%s arms_above_cash does not follow the signs" % key)
    nothing = not (rh.get("one_year") or {}).get("arms_above_cash") and \
        not (rh.get("two_year") or {}).get("arms_above_cash")
    if rh.get("verdict") != ("NOTHING_CLEARS_CASH_TODAY" if nothing
                             else "SOME_ARMS_CLEAR_CASH_ON_A_HORIZON_READER_CAN_DEFEND"):
        problems.append("recent_horizons verdict %s does not follow the winners"
                        % rh.get("verdict"))

    # 4. the cash vehicle must still be the published one
    cv = face.get("cash_vehicle") or {}
    gap = cv.get("anchor_gap_pp")
    if gap is None or abs(gap) > CASH_ANCHOR_TOL_PP:
        problems.append("cash full-sample roll drifts %.3fpp from the published vehicle" % (gap or 0.0))

    # 5. arms must still reproduce r1964 (a moved engine or a moved parent is a failure)
    for a in face.get("arms") or []:
        r = a.get("reproduction")
        if r and not r.get("cagr_within_tol"):
            problems.append("%s no longer reproduces its published CAGR (%spp)"
                            % (a["arm"], r.get("cagr_gap_pp")))

    # 6. freshness: the face must still be priced on the panel's last bar.  A newer bar
    #    means this face is stale -- say STALE so the chain writer will pay to rebuild it
    try:
        import etf_composite_pf as E
        close, _o, _a, _f = E.build_panel()
        last = str(close.index[-1].date())
    except Exception as exc:                                        # noqa: BLE001
        last = None
        problems.append("cannot read the panel to judge freshness (%r)" % (exc,))
    if last is not None and face.get("evidence_cutoff") != last:
        problems.append("STALE: face is priced on %s, panel now ends %s"
                        % (face.get("evidence_cutoff"), last))

    # 7. the cutoff may never be blank, and it must name where it came from
    if not face.get("evidence_cutoff"):
        problems.append("evidence_cutoff is blank")
    if not face.get("evidence_cutoff_source"):
        problems.append("evidence_cutoff_source is missing")

    if problems:
        stale_only = all(p.startswith("STALE") for p in problems)
        print("%s" % ("STALE" if stale_only else "CHECK FAILED"))
        for x in problems:
            print(" - %s" % x)
        return 3 if stale_only else 1
    print("CHECK OK: %d arms x %d lookbacks re-derived; cash anchor within %.2fpp"
          % (len(face["arms"]), len(LOOKBACKS) + 1, CASH_ANCHOR_TOL_PP))
    return 0


# --------------------------------------------------------------------------------- selftest
def selftest():
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("  FAIL %s" % name)

    # L1 tail_cagr on a flat curve is exactly zero
    idx = pd.date_range("2024-01-01", periods=300, freq="D")
    flat = pd.Series(1.0, index=idx)
    leg("L1 flat curve CAGR is zero", abs(tail_cagr(flat, 252) or 0.0) < 1e-12)

    # L2 tail_cagr reproduces a known geometric growth exactly
    g = (1.0005) ** np.arange(400)
    geo = pd.Series(g, index=pd.date_range("2023-01-01", periods=400, freq="D"))
    want = (float(geo.iloc[-1] / geo.iloc[-253])) ** (365.0 / 252) - 1.0
    leg("L2 geometric CAGR matches the closed form", abs(tail_cagr(geo, 252) - want) < 1e-12)

    # L3 a tail that cannot be filled is None, not a shorter tail
    leg("L3 unfillable tail returns None", tail_cagr(flat, 1008) is None)

    # L4 sign_of is total on the three states
    leg("L4 sign_of covers +/0/-", (sign_of(0.1), sign_of(0.0), sign_of(-0.1)) == (1, 0, -1)
        and sign_of(None) is None)

    # L5 arm_verdict: a ladder with one positive cell flips
    flip = [{"excess_pp": 0.5}, {"excess_pp": -0.2}, {"excess_pp": None}]
    leg("L5 mixed signs -> FLIPS", arm_verdict(flip)[0] == "FLIPS_WITH_LOOKBACK")

    # L6 arm_verdict: all cash-wins cells
    cash_w = [{"excess_pp": -0.1}, {"excess_pp": -2.0}, {"excess_pp": None}]
    leg("L6 all negative -> CASH_WINS", arm_verdict(cash_w)[0] == "CASH_WINS_ON_EVERY_LOOKBACK")

    # L7 arm_verdict: nothing measurable
    leg("L7 no measurable cell -> NOT_MEASURABLE",
        arm_verdict([{"excess_pp": None}])[0] == "NOT_MEASURABLE")

    # L8 face_verdict: one flipping arm dominates a stable one
    face = face_verdict([{"arm": "a", "verdict": "FLIPS_WITH_LOOKBACK", "cells": []},
                         {"arm": "b", "verdict": "CASH_WINS_ON_EVERY_LOOKBACK", "cells": []}])
    leg("L8 any flip -> LOOKBACK_DECIDES", face["verdict"] == "LOOKBACK_DECIDES_THE_ANSWER"
        and face["arms_that_flip"] == ["a"])

    # L9 face_verdict: mixed but stable is not a flip
    face = face_verdict([{"arm": "a", "verdict": "BOOK_WINS_ON_EVERY_LOOKBACK", "cells": []},
                         {"arm": "b", "verdict": "CASH_WINS_ON_EVERY_LOOKBACK", "cells": []}])
    leg("L9 mixed-but-stable", face["verdict"] == "MIXED_BUT_STABLE")

    # L10 aligned_excess only counts days both series exist
    b = pd.Series([1.0, 1.01, 1.02, 1.03], index=pd.date_range("2024-01-01", periods=4))
    c = pd.Series([1.0, 1.001, 1.002], index=pd.date_range("2024-01-01", periods=3))
    ex, n = aligned_excess(b, c)
    leg("L10 alignment drops the unmatched day", n == 2 and len(ex) == 2)

    # L11 excess_t on a constant positive excess is finite and positive; zero variance is None
    ex_pos = pd.Series([0.001, 0.001, 0.001, 0.001])
    t, _n = excess_t(ex_pos)
    leg("L11 zero-variance excess has no t", t is None)
    ex_var = pd.Series([0.001, -0.0005, 0.002, 0.0005, 0.0015])
    t2, _n2 = excess_t(ex_var)
    leg("L11b varying excess has a t", t2 is not None and math.isfinite(t2))

    # L12 the ladder is frozen and never contains duplicates
    leg("L12 ladder frozen and unique", list(LOOKBACKS) == sorted(set(LOOKBACKS))
        and FULL not in [str(x) for x in LOOKBACKS])

    # L12b flip_point names the first sign change and nothing when the sign is stable
    cells_flip = [{"lookback": 21, "excess_pp": 0.5}, {"lookback": 63, "excess_pp": 0.1},
                  {"lookback": 126, "excess_pp": -0.2}]
    leg("L12b flip point is the first crossing", flip_point(cells_flip) == [63, 126])
    leg("L12c stable ladder has no flip point",
        flip_point([{"lookback": 21, "excess_pp": -0.5},
                    {"lookback": 63, "excess_pp": -0.1}]) is None)

    # L13 check() rejects a face whose cell arithmetic was moved by hand (behaviour, not shape)
    import tempfile
    base = {
        "kind": "bench_cash_window_sensitivity",
        "cash_vehicle": {"anchor_gap_pp": 0.0},
        "cash_table": [{"lookback": 21, "cash_cagr": 0.01},
                       {"lookback": FULL, "cash_cagr": 0.02}],
        "arms": [{"arm": "x", "verdict": "CASH_WINS_ON_EVERY_LOOKBACK",
                  "reproduction": None, "excess_full_t": None,
                  "cells": [{"lookback": 21, "book_cagr": 0.005, "cash_cagr": 0.01,
                             "excess_pp": -0.5},
                            {"lookback": FULL, "book_cagr": 0.01, "cash_cagr": 0.02,
                             "excess_pp": -1.0}]}],
        "verdict": {"verdict": "CASH_WINS_ON_EVERY_LOOKBACK"},
        "evidence_cutoff": "2026-11-20",
        "evidence_cutoff_source": "test",
    }
    with tempfile.TemporaryDirectory() as td:
        tp = Path(td) / "face.json"
        _dump(tp, base)
        poisoned = json.loads(json.dumps(base))
        poisoned["arms"][0]["cells"][0]["excess_pp"] = 9.99
        _dump(tp, poisoned)
        import io as _io
        from contextlib import redirect_stdout
        buf = _io.StringIO()
        with redirect_stdout(buf):
            rc = check(tp)
        txt = buf.getvalue()
        leg("L13 moved cell is named", rc == 1 and "21" in txt and "excess" in txt)
        leg("L13b a moved cell is not called STALE", "STALE" not in txt)

    print("selftest %d/%d PASS" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    build(write=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
