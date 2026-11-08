"""Is "top two years carry 71% of the profit" a fact about the book, or about having seven years?

WHY THIS FILE EXISTS
--------------------
r1418 pointed the frozen calendar gate at the desk's adopted book and got CONDITIONAL on a
single failing row: Y4, top-2 years = 71.08% of the annual sum, 1.08pp over the 70% line.
r1420 then showed the same book reads 71.08/79.46/79.58/79.82/79.62 depending on which week
the decision grid starts, and that the line is decisive for three of the five books the desk
publishes (nobond_vt08 71.08, all_classes 77.19, breadth ALL 79.34).

Nobody ever asked the line what it measures. It is the only one of the four frozen lines with
no external referent: 70% of positive years, -15% worst year and 20M CNY capacity all mean
something on their own, while "top two of seven years" has a distribution that is entirely
determined by the book's annual Sharpe -- a book whose yearly returns are seven draws from a
process with mean m and sd s has a top-2 share that depends only on m/s, because the share is
scale-invariant. So Y4 may not be a concentration check at all; it may be an annual-Sharpe
check wearing a concentration word.

WHAT THIS FILE DOES
-------------------
1. builds the null that Y4 needs and never had: for a stationary process with annual Sharpe S,
   the distribution of the top-2 share over seven years (Monte Carlo, seeded, iid normal);
2. inverts it: what annual Sharpe makes the MEDIAN book read exactly 70%? That number is the
   Sharpe the line is actually demanding;
3. reads every book the desk publishes against the null at its own Sharpe (percentile) and
   against the second statistic C2 = top-2 share of the ABSOLUTE annual sum, which does not
   explode when the annual sum is near zero;
4. prices a Sharpe-conditional replacement line -- "not more concentrated than 95% of books
   with this Sharpe" -- so the pass/fail no longer depends on a constant chosen by hand.

Every number is re-derived from published receipts (results/etf_book_year_gate/YEAR-GATE.json,
results/admission/CANDIDATES.json); no book is re-priced here and no line is moved. The
proposal is printed as a proposal.

TWO AGGREGATORS (r1240 / E213): the parametric normal null is paired with an empirical
bootstrap of the book's own seven years. Where the two disagree the reading says so instead of
picking the friendlier one.

Usage:
    python scripts/year_concentration_calibration.py run
    python scripts/year_concentration_calibration.py selftest
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "admission", "YEAR-CONC-CALIBRATION.json")

N_YEARS = 7
MEAN_LEVEL = 10.0          # percent; the share is scale-invariant, this only sets the scale
REPS_GRID = 120_000
REPS_BOOK = 200_000
SEED = 20261108
SHARPE_GRID = [round(0.20 + 0.05 * i, 2) for i in range(57)]   # 0.20 .. 3.00
LINE_TOP2 = 0.70           # the line this file is asking about; imported below as a check
CONDITIONAL_TAIL = 0.95    # "not more concentrated than 95% of books with this Sharpe"

BOOK_SOURCES = [
    ("nobond_vt08_adopted", "results/etf_book_year_gate/YEAR-GATE.json"),
    ("nobond_base", "results/etf_book_year_gate/YEAR-GATE.json"),
    ("all_classes_published", "results/etf_book_year_gate/YEAR-GATE.json"),
    ("smallcap_n20", "results/admission/CANDIDATES.json"),
    ("breadth_ALL", "results/admission/CANDIDATES.json"),
]


# ----------------------------------------------------------------------------- statistics
def top2_share(vals) -> float | None:
    """The gate's own Y4 statistic: two best years over the sum of all years."""
    v = [float(x) for x in vals]
    s = sum(v)
    if s <= 0:
        return None          # a non-positive sum has no share; never silently 0 or 1
    return sum(sorted(v, reverse=True)[:2]) / s


def top2_abs_share(vals) -> float | None:
    """C2: two biggest magnitudes over the sum of all magnitudes.

    Why a second statistic: C1's denominator is the SIGNED sum, so a book whose years are
    noisy about zero gets a large share from arithmetic rather than from concentration --
    and a book with one catastrophic year can get a small share for the same reason.
    """
    a = [abs(float(x)) for x in vals]
    s = sum(a)
    if s <= 0:
        return None
    return sum(sorted(a, reverse=True)[:2]) / s


def sharpe_annual(vals) -> float | None:
    v = np.asarray([float(x) for x in vals], dtype=float)
    if v.size < 2:
        return None
    sd = float(v.std(ddof=1))
    if sd <= 0:
        return None
    return float(v.mean()) / sd


# ----------------------------------------------------------------------------- null
def null_draws(sharpe: float, reps: int, seed: int) -> np.ndarray:
    """(reps, N_YEARS) draws of a stationary book with the given annual Sharpe."""
    rng = np.random.default_rng(seed)
    sd = MEAN_LEVEL / float(sharpe)
    return rng.normal(MEAN_LEVEL, sd, size=(reps, N_YEARS))


def null_top2(arr: np.ndarray) -> np.ndarray:
    tot = arr.sum(axis=1)
    part = np.sort(arr, axis=1)[:, -2:].sum(axis=1)
    out = np.full(arr.shape[0], np.nan)
    ok = tot > 0
    out[ok] = part[ok] / tot[ok]
    return out


def null_top2_abs(arr: np.ndarray) -> np.ndarray:
    a = np.abs(arr)
    tot = a.sum(axis=1)
    part = np.sort(a, axis=1)[:, -2:].sum(axis=1)
    out = np.full(arr.shape[0], np.nan)
    ok = tot > 0
    out[ok] = part[ok] / tot[ok]
    return out


def sharpe_table(reps: int = REPS_GRID, seed: int = SEED) -> list[dict]:
    """median / 5-95 band of both statistics as a function of annual Sharpe."""
    rows = []
    for s in SHARPE_GRID:
        arr = null_draws(s, reps, seed)
        c1 = null_top2(arr)
        c2 = null_top2_abs(arr)
        c1 = c1[~np.isnan(c1)]
        c2 = c2[~np.isnan(c2)]
        rows.append({
            "annual_sharpe": s,
            "c1_median": round(float(np.median(c1)), 4),
            "c1_q05": round(float(np.quantile(c1, 0.05)), 4),
            "c1_q95": round(float(np.quantile(c1, 0.95)), 4),
            "c2_median": round(float(np.median(c2)), 4),
            "c2_q05": round(float(np.quantile(c2, 0.05)), 4),
            "c2_q95": round(float(np.quantile(c2, 0.95)), 4),
            "p_c1_above_line": round(float(np.mean(c1 > LINE_TOP2)), 4),
        })
    return rows


def invert(table: list[dict], key: str, target: float) -> dict:
    """Smallest Sharpe whose median statistic is still <= target (table is decreasing)."""
    prev = None
    for r in table:
        if r[key] <= target:
            if prev is None:
                return {"sharpe": r["annual_sharpe"], "at_grid_edge": True}
            # linear interpolation on the crossing
            x0, y0 = prev["annual_sharpe"], prev[key]
            x1, y1 = r["annual_sharpe"], r[key]
            if y0 == y1:
                return {"sharpe": round(x1, 3), "at_grid_edge": False}
            x = x0 + (y0 - target) * (x1 - x0) / (y0 - y1)
            return {"sharpe": round(float(x), 3), "at_grid_edge": False}
        prev = r
    return {"sharpe": None, "at_grid_edge": True,
            "note": "no Sharpe on the grid has a median at or below the target"}


# ----------------------------------------------------------------------------- books
def _load(rel: str) -> dict:
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def _sha16(rel: str) -> str:
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def published_books() -> tuple[list[dict], dict]:
    """Read the two published receipts; no repricing, no constants typed in."""
    books: list[dict] = []
    sources: dict = {}
    yg = _load("results/etf_book_year_gate/YEAR-GATE.json")
    sources["year_gate"] = {"path": "results/etf_book_year_gate/YEAR-GATE.json",
                            "sha16": _sha16("results/etf_book_year_gate/YEAR-GATE.json"),
                            "asof": yg.get("asof"), "cell": yg.get("cell")}
    for b in yg.get("books") or []:
        yrs = b.get("yearly_returns_pct") or {}
        books.append({"book": b.get("book"), "verdict_published": b.get("verdict"),
                      "years": {k: float(v) for k, v in sorted(yrs.items())},
                      "source": "results/etf_book_year_gate/YEAR-GATE.json"})
    cand = _load("results/admission/CANDIDATES.json")
    sources["candidates"] = {"path": "results/admission/CANDIDATES.json",
                             "sha16": _sha16("results/admission/CANDIDATES.json"),
                             "asof": cand.get("asof")}
    alias = {"smallcap_book": "smallcap_n20", "breadth_book": "breadth_ALL"}
    for c in cand.get("candidates") or []:
        label = alias.get(c.get("candidate"))
        if label is None:
            continue
        rows = c.get("years") or []
        books.append({"book": label, "verdict_published": c.get("verdict"),
                      "years": {str(r["year"]): float(r["net_pct"]) for r in rows},
                      "source": "results/admission/CANDIDATES.json"})
    return books, sources


def read_book(bk: dict, table: list[dict]) -> dict:
    vals = [bk["years"][k] for k in sorted(bk["years"])]
    n = len(vals)
    sh = sharpe_annual(vals)
    c1 = top2_share(vals)
    c2 = top2_abs_share(vals)
    out = {"book": bk["book"], "years": bk["years"], "n_years": n,
           "annual_mean_pct": round(float(np.mean(vals)), 4),
           "annual_sd_pct": round(float(np.std(vals, ddof=1)), 4) if n > 1 else None,
           "annual_sharpe": None if sh is None else round(sh, 4),
           "c1_top2_share": None if c1 is None else round(c1, 4),
           "c2_top2_abs_share": None if c2 is None else round(c2, 4),
           "verdict_published": bk.get("verdict_published"),
           "source": bk.get("source")}

    # A1: parametric normal null at the book's own Sharpe
    if sh is not None and sh > 0:
        arr = null_draws(sh, REPS_BOOK, SEED)
        n1 = null_top2(arr)
        n1 = n1[~np.isnan(n1)]
        n2 = null_top2_abs(arr)
        n2 = n2[~np.isnan(n2)]
        out["null_A1_normal"] = {
            "reps": int(n1.size),
            "c1_median": round(float(np.median(n1)), 4),
            "c1_q05": round(float(np.quantile(n1, 0.05)), 4),
            "c1_q95": round(float(np.quantile(n1, 0.95)), 4),
            "c1_percentile_of_observed": None if c1 is None
            else round(float(np.mean(n1 <= c1)), 4),
            "c2_median": round(float(np.median(n2)), 4),
            "c2_q95": round(float(np.quantile(n2, 0.95)), 4),
            "c2_percentile_of_observed": None if c2 is None
            else round(float(np.mean(n2 <= c2)), 4),
        }
        # the Sharpe this book's own share implies, read off the frozen grid
        impl = invert(table, "c1_median", c1) if c1 is not None else {"sharpe": None}
        out["implied_sharpe_from_c1"] = impl.get("sharpe")
        out["realized_minus_implied_sharpe"] = (
            None if impl.get("sharpe") is None
            else round(float(sh) - float(impl["sharpe"]), 4))
        # the conditional line: is this book beyond 95% of its own-Sharpe peers?
        out["passes_conditional_line_c1"] = (
            None if c1 is None else bool(c1 <= float(np.quantile(n1, 0.95))))
        out["passes_conditional_line_c2"] = (
            None if c2 is None else bool(c2 <= float(np.quantile(n2, 0.95))))
        out["passes_fixed_line_c1"] = None if c1 is None else bool(c1 <= LINE_TOP2)
        a1_state = None if c1 is None else (
            "beyond_95pct" if out["null_A1_normal"]["c1_percentile_of_observed"] > 0.95
            else "below_5pct" if out["null_A1_normal"]["c1_percentile_of_observed"] < 0.05
            else "typical")
        out["null_A1_state"] = a1_state
    else:
        out["null_A1_normal"] = {"error": "annual Sharpe unavailable or non-positive"}
        out["null_A1_state"] = None

    # A2: empirical bootstrap of the book's own seven years (skew/outliers included)
    rng = np.random.default_rng(SEED + 1)
    if n >= 2:
        idx = rng.integers(0, n, size=(REPS_BOOK, n))
        arr = np.asarray(vals, dtype=float)[idx]
        b1 = null_top2(arr)
        b1 = b1[~np.isnan(b1)]
        b2 = null_top2_abs(arr)
        b2 = b2[~np.isnan(b2)]
        out["null_A2_bootstrap"] = {
            "reps": int(b1.size),
            "c1_median": round(float(np.median(b1)), 4),
            "c1_q95": round(float(np.quantile(b1, 0.95)), 4),
            "c1_percentile_of_observed": None if c1 is None
            else round(float(np.mean(b1 <= c1)), 4),
            "c2_median": round(float(np.median(b2)), 4),
            "c2_q95": round(float(np.quantile(b2, 0.95)), 4),
            "c2_percentile_of_observed": None if c2 is None
            else round(float(np.mean(b2 <= c2)), 4),
            "degenerate_samples": int((arr.sum(axis=1) <= 0).sum()),
        }
        a2_state = None if c1 is None else (
            "beyond_95pct" if out["null_A2_bootstrap"]["c1_percentile_of_observed"] > 0.95
            else "below_5pct" if out["null_A2_bootstrap"]["c1_percentile_of_observed"] < 0.05
            else "typical")
        out["null_A2_state"] = a2_state
        out["aggregators_agree"] = (None if (a1_state is None or a2_state is None)
                                    else a1_state == a2_state)
    else:
        out["null_A2_bootstrap"] = {"error": "fewer than two years"}
        out["null_A2_state"] = None
        out["aggregators_agree"] = None
    return out


# ----------------------------------------------------------------------------- selftest
def selftest() -> int:
    errs: list = []
    tot = ok = 0

    def chk(cond, msg):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            errs.append(msg)

    # L1 the share is scale invariant: doubling a book's years changes nothing
    base = [5.0, 8.0, 2.0, 4.0, 12.0, 40.0, 1.0]
    chk(abs(top2_share(base) - top2_share([2 * x for x in base])) < 1e-12,
        "L1 top-2 share is scale invariant (so the null depends on Sharpe only)")

    # L2 the share is order invariant: the years can be sorted any way
    rev = list(reversed(base))
    chk(abs(top2_share(base) - top2_share(rev)) < 1e-12,
        "L2 top-2 share is order invariant (permuting years is not a null)")

    # L3 a non-positive sum is not a share, and is never silently 0 or 1
    chk(top2_share([-3.0, -4.0, 1.0]) is None,
        "L3 a negative annual sum publishes no share rather than a flattering one")
    chk(top2_share([0.0, 0.0, 0.0]) is None, "L3b all-zero book publishes no share")

    # L4 C2 differs from C1 exactly where it must: a big loss hurts C1's denominator
    lossy = [30.0, 25.0, -40.0, 5.0, 4.0, 3.0, 2.0]
    chk(top2_share(lossy) > 1.0, "L4 a loss year can push C1 above 1.0 (%.3f)"
        % top2_share(lossy))
    chk(0.0 < top2_abs_share(lossy) < 1.0, "L4b C2 stays inside [0,1] on the same book")

    # L5 the null is monotone: a higher Sharpe book is less concentrated
    t = sharpe_table(reps=20_000)
    meds = [r["c1_median"] for r in t]
    chk(all(meds[i] >= meds[i + 1] - 1e-9 for i in range(len(meds) - 1)),
        "L5 the null median top-2 share falls monotonically in annual Sharpe")
    chk(t[0]["p_c1_above_line"] > t[-1]["p_c1_above_line"],
        "L5b the 70%% line fires far more often on low-Sharpe books (%s -> %s)"
        % (int(t[0]["p_c1_above_line"] * 100), int(t[-1]["p_c1_above_line"] * 100)))

    # L6 the inversion lands inside the grid and brackets the target
    inv = invert(t, "c1_median", LINE_TOP2)
    chk(inv["sharpe"] is not None and not inv["at_grid_edge"],
        "L6 the line 0.70 inverts to a Sharpe inside the grid (%r)" % inv["sharpe"])
    near = min(t, key=lambda r: abs(r["annual_sharpe"] - inv["sharpe"]))
    chk(abs(near["c1_median"] - LINE_TOP2) < 0.03,
        "L6b the inverted Sharpe is within 3pp of the line (%.4f)" % near["c1_median"])

    # L7 the null is frozen: same seed, same numbers
    a = null_top2(null_draws(0.8, 5_000, SEED))
    b = null_top2(null_draws(0.8, 5_000, SEED))
    chk(float(np.nanmedian(a)) == float(np.nanmedian(b)), "L7 the null is seeded/reproducible")

    # L8 THE POWER TEST, pinned in the direction the numbers actually go: a book whose two
    # years carry 95% of its entire profit is still only ~70th percentile against peers of
    # its own Sharpe, because the peers are that concentrated too. This leg pins the
    # measured absence of power; if a future change makes the check able to catch this
    # fixture, the leg should be rewritten deliberately, not silently.
    carried = {"book": "fixture_genuine_carry",
               "years": {"2020": 90.0, "2021": 95.0, "2022": 2.0, "2023": 2.0,
                         "2024": 2.0, "2025": 2.0, "2026": 2.0},
               "verdict_published": None, "source": "fixture"}
    cb = read_book(carried, t)
    chk(cb["c1_top2_share"] > 0.90, "L8 the carried fixture reads %.3f" % cb["c1_top2_share"])
    pct = cb["null_A1_normal"]["c1_percentile_of_observed"]
    chk(0.60 < pct < 0.90,
        "L8b a 95%%-carried book reads only the %.2f percentile of its own-Sharpe peers -- "
        "the published check has almost no power over this statistic" % pct)

    # L8c why it has no power: C1's own 95% band exceeds 1.0 at the desk's Sharpe range,
    # because the denominator is a SIGNED sum. Nothing can read "beyond 95%" until the
    # book is far past anything a real book reaches.
    q95_080 = [r for r in t if abs(r["annual_sharpe"] - 0.80) < 1e-9][0]["c1_q95"]
    chk(q95_080 > 1.0,
        "L8c C1's null 95%% band at Sharpe 0.80 is %.3f -- the statistic is not bounded by "
        "1, so the upper tail is arithmetic, not concentration" % q95_080)

    # L8d C2 measures shape; C1 measures Sharpe. Over the desk's own Sharpe range the C1
    # median moves an order of magnitude more than the C2 median.
    lo = [r for r in t if abs(r["annual_sharpe"] - 0.60) < 1e-9][0]
    hi = [r for r in t if abs(r["annual_sharpe"] - 2.00) < 1e-9][0]
    chk(abs(lo["c2_median"] - hi["c2_median"]) < 0.20,
        "L8d C2's null median is nearly Sharpe-flat (%.3f -> %.3f)"
        % (lo["c2_median"], hi["c2_median"]))
    chk(abs(lo["c1_median"] - hi["c1_median"]) > 0.30,
        "L8e C1's null median tracks Sharpe (%.3f -> %.3f)"
        % (lo["c1_median"], hi["c1_median"]))

    # L9 an all-market-of-seven book must read typical, not flagged
    momo = {"book": "fixture_noise", "source": "fixture", "verdict_published": None,
            "years": {"y1": 8.0, "y2": -4.0, "y3": 20.0, "y4": 3.0,
                      "y5": 11.0, "y6": -2.0, "y7": 15.0}}
    mb = read_book(momo, t)
    chk(mb["null_A1_state"] == "typical",
        "L9 an ordinary seven-year book is typical against its own null (%s)"
        % mb["null_A1_state"])

    # L10 fewer than two years is unpriced, not passed
    one = {"book": "fixture_one_year", "years": {"2026": 40.0}, "source": "fixture",
           "verdict_published": None}
    ob = read_book(one, t)
    chk(ob["annual_sharpe"] is None and "error" in ob["null_A2_bootstrap"],
        "L10 a one-year book publishes no null and no Sharpe")

    print("selftest %d/%d PASS" % (ok, tot))
    for e in errs:
        print("  FAIL:", e)
    return 0 if ok == tot else 1


# ----------------------------------------------------------------------------- run
def run() -> dict:
    t0 = time.time()
    table = sharpe_table()
    inv_c1 = invert(table, "c1_median", LINE_TOP2)
    inv_c2 = invert(table, "c2_median", LINE_TOP2)

    books, sources = published_books()
    rows = [read_book(b, table) for b in books]

    # POWER: the question the line was never asked. Two parts -- (a) can any real book
    # read "beyond 95%"? the band itself is above 1.0 for the Sharpe range the desk lives
    # in, so the upper tail is arithmetic; (b) does the statistic catch a book whose two
    # years carry 95% of the profit? measured below on a fixture, priced the same way.
    carried = read_book({"book": "power_fixture_95pct_carried", "source": "fixture",
                         "verdict_published": None,
                         "years": {"2020": 90.0, "2021": 95.0, "2022": 2.0, "2023": 2.0,
                                   "2024": 2.0, "2025": 2.0, "2026": 2.0}}, table)
    power = {
        "fixture_95pct_carried": {
            "c1_top2_share": carried["c1_top2_share"],
            "annual_sharpe": carried["annual_sharpe"],
            "c1_percentile_under_own_sharpe_null":
                carried["null_A1_normal"].get("c1_percentile_of_observed"),
            "would_the_fixed_line_flag_it": carried.get("passes_fixed_line_c1"),
            "read": ("a book whose two years carry 95% of its whole profit is not beyond "
                     "95% of its own-Sharpe peers; the check cannot see the thing it names"),
        },
        "books_beyond_95pct_c1": [r["book"] for r in rows
                                  if r.get("null_A1_state") == "beyond_95pct"],
        "books_beyond_95pct_c2": [r["book"] for r in rows
                                  if r.get("passes_conditional_line_c2") is False],
        "c1_band_above_one_at_sharpe_le_1": [
            r["annual_sharpe"] for r in table
            if r["annual_sharpe"] <= 1.0 and r["c1_q95"] > 1.0],
        "note": ("C1's denominator is a signed sum, so the statistic is unbounded and its "
                 "95% band exceeds 1.0 wherever the annual Sharpe is at or below ~1.0"),
    }

    # DISCRIMINATION: which statistic actually moves with shape rather than with Sharpe
    lo = [r for r in table if abs(r["annual_sharpe"] - 0.60) < 1e-9][0]
    hi = [r for r in table if abs(r["annual_sharpe"] - 2.00) < 1e-9][0]
    discrimination = {
        "c1_median_moves_with_sharpe_pp": round((lo["c1_median"] - hi["c1_median"]) * 100, 2),
        "c2_median_moves_with_sharpe_pp": round((lo["c2_median"] - hi["c2_median"]) * 100, 2),
        "reading": ("C1's median falls with Sharpe by an order of magnitude more than C2's; "
                    "C1 is an annual-Sharpe test in a concentration costume"),
    }

    summary = {r["book"]: {
        "c1_top2_share": r["c1_top2_share"],
        "annual_sharpe": r["annual_sharpe"],
        "implied_sharpe_from_c1": r.get("implied_sharpe_from_c1"),
        "null_state": r.get("null_A1_state"),
        "A2_state": r.get("null_A2_state"),
        "passes_fixed_line": r.get("passes_fixed_line_c1"),
        "passes_conditional_line": r.get("passes_conditional_line_c1"),
        "verdict_published": r["verdict_published"],
    } for r in rows}

    flips = [b for b, s in summary.items()
             if s["passes_fixed_line"] is False and s["passes_conditional_line"] is True]
    at_risk = [b for b, s in summary.items()
               if s["passes_fixed_line"] is True and s["passes_conditional_line"] is False]

    out = {
        "face": "year_concentration_calibration",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": max((str(max(b["years"])) for b in books), default=None),
        "question": ("does the frozen Y4 line measure calendar concentration, or is it an "
                     "annual-Sharpe test wearing a concentration word?"),
        "rule": {
            "statistic_c1": "top-2 calendar years / sum of calendar years (the published gate)",
            "statistic_c2": "top-2 |calendar years| / sum |calendar years| (proposed reading)",
            "null": ("stationary iid normal annual returns with mean %.1f%% and the book's "
                     "own annual Sharpe; %d draws, seed %d" % (MEAN_LEVEL, REPS_BOOK, SEED)),
            "second_aggregator": "empirical bootstrap of the book's own seven years",
            "inversion": "the Sharpe at which the null MEDIAN equals the frozen line",
            "conditional_line": ("pass if the observed statistic is at or below the null's "
                                 "%d%% quantile at the book's own Sharpe"
                                 % int(CONDITIONAL_TAIL * 100)),
            "frozen_before_read": True,
        },
        "sharpe_table": table,
        "inversion": {
            "c1_sharpe_that_reads_70pct_on_the_median": inv_c1.get("sharpe"),
            "c2_sharpe_that_reads_70pct_on_the_median": inv_c2.get("sharpe"),
            "reading": ("a book with annual Sharpe below this number fails Y4 by arithmetic "
                        "even when its years are exactly independent draws"),
        },
        "sources": sources,
        "books": rows,
        "power": power,
        "discrimination": discrimination,
        "summary": summary,
        "flips_under_conditional_line": flips,
        "at_risk_under_conditional_line": at_risk,
        "honest": [
            "no book is re-priced here: every year row is read from a published receipt",
            "the null is iid normal; real books cluster (crisis years) and would be MORE "
            "concentrated, so a book inside the null band is not proof of independence",
            "the Sharpe in the null is plugged in from the same seven years, so the null band "
            "is narrower than a fully accounting-for-estimation null would be",
            "C2 is published as a READING; replacing Y4 is a law change and needs its own "
            "prereg, not a line chosen after seeing these numbers",
            "a non-positive annual sum publishes no share; it is never read as 0 or 1",
            "seven annual observations cannot separate a book's luck from its process; the "
            "percentile here says only whether the shape is unusual for its own Sharpe",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    r = run()
    print(json.dumps({
        "line_implies_annual_sharpe": r["inversion"][
            "c1_sharpe_that_reads_70pct_on_the_median"],
        "books": {k: {"c1": v["c1_top2_share"], "sharpe": v["annual_sharpe"],
                      "implied": v["implied_sharpe_from_c1"],
                      "null_state": v["null_state"], "A2": v["A2_state"],
                      "fixed_line": v["passes_fixed_line"],
                      "conditional_line": v["passes_conditional_line"]}
                  for k, v in r["summary"].items()},
        "flips_under_conditional_line": r["flips_under_conditional_line"],
        "power": {"fixture_95pct_carried_percentile":
                  r["power"]["fixture_95pct_carried"]["c1_percentile_under_own_sharpe_null"],
                  "books_beyond_95pct_c1": r["power"]["books_beyond_95pct_c1"],
                  "books_beyond_95pct_c2": r["power"]["books_beyond_95pct_c2"]},
        "discrimination": r["discrimination"],
        "elapsed_sec": r["elapsed_sec"],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())