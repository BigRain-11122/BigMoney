"""Does the admission ruler see the next year, or only the last one?

r1426 certified which rulers can adjudicate themselves; r1429/r1435/r1438/r1440 then
spent five rounds reading the *same* book through them and kept landing on
``CONDITIONAL``.  Every one of those readings is retrospective: the concentration
caliber (Y4, top-2-year share <= 0.70) is computed on a record that has already
happened.  Nobody has asked the forward question, and it is the only one that
decides whether a red supply floor is protecting money or just refusing a shape.

The test here needs no new data and no new pricing rule:

  1. price one frozen grid of arms on the same panel with the published engine
     (imported, never re-implemented) -- the same family the desk already runs,
     varying only width and rebalance;
  2. cut each arm into rolling fixed-length calendar windows and read the
     concentration caliber on each window **only from its own years**;
  3. compare that reading with the return of the year that comes *after* the window.

Fixed-length windows are the whole methodological point: r1433 showed the caliber's
value is a function of record length, so a 3-year window and a 7-year record are not
comparable and must never be pooled.  Every cell below carries a window of exactly
``WINDOW_YEARS``.

Two reads are published:

  * ``forward_relation`` -- pooled rank correlation between the window's concentration
    and the following year's return, with a permutation p-value.  Direction is frozen
    before any reading: a *useful* strictness ruler must mean higher concentration ->
    worse forward year (negative).  A positive-and-significant result is not "the ruler
    is great", it is INVERTED and is published as such.
  * ``selector`` -- the gate used as an actual selector: at each year-end hold the arms
    that pass, else the published book, and price the following year.  Compared against
    equal-weighting every arm (the null: the gate adds nothing) and the published book.

Honest limits, printed not hidden: the arms are one family, so most cells share one
bet; the forward sample is at most three decision points, which cannot settle a
strategy question (r1316 power floor).  What it *can* settle is whether the ruler
carries forward information at all -- and that is what the supply floor has been
assuming for forty rounds.

Usage:
    python scripts/etf_book_ruler_forward.py run [--arms=fast]
    python scripts/etf_book_ruler_forward.py --check
    python scripts/etf_book_ruler_forward.py --selftest
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_book_year_caliber as C  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "etf_book_ruler_forward")
OUT = os.path.join(OUT_DIR, "RULER-FORWARD.json")
COST = 0.0010
BARS_PER_COHORT = 60
MIN_COHORTS_FULL_YEAR = 4

# ---- frozen before any reading ------------------------------------------------
CRITERIA = {
    "assay": "leading fixed-length window concentration vs the NEXT calendar year's return",
    "window_years": 3,
    "window_years_secondary": 4,
    "forward_years": 1,
    "caliber_primary": "net_top2_share",
    "caliber_secondary": "effective_years",
    "partial_year_rule": "a year with fewer than %d complete cohorts is partial; "
                         "a cell whose leading window OR forward year touches a partial "
                         "year is published but excluded from the pooled reading"
                         % MIN_COHORTS_FULL_YEAR,
    "min_cells": 12,
    "decision": {
        "RULER_SEES_FORWARD": "rho <= -0.35 and perm_p < 0.10",
        "RULER_INVERTED": "rho >= +0.35 and perm_p < 0.10",
        "RULER_BLIND": "otherwise",
    },
    "direction_frozen": "a useful STRICTNESS ruler must show higher concentration -> "
                        "worse forward year, i.e. a negative correlation",
    "selector_rule": "at each year-end, equal-weight the arms whose leading-window "
                     "top2 share <= the gate line; if none pass, hold the published "
                     "book (n5/r20/vol_target 0.08)",
    "permutations": 2000,
    "seed": 20261108,
    "severity_worst_first": ["RULER_INVERTED", "RULER_BLIND", "NOT_ASSESSED",
                             "RULER_SEES_FORWARD"],
    "severity_why": "a backwards ruler is worse than a decorative one: it does not merely "
                    "fail to protect, it refuses the right book and admits the wrong one",
}

GRID_FAST = [{"n_hold": 5, "rebal": 20, "vol_target": 0.08},
             {"n_hold": 5, "rebal": 20, "vol_target": None},
             {"n_hold": 3, "rebal": 20, "vol_target": 0.08},
             {"n_hold": 8, "rebal": 20, "vol_target": 0.08}]
GRID_FULL = [{"n_hold": n, "rebal": r, "vol_target": vt}
             for vt in (0.08, None) for n in (3, 5, 8) for r in (10, 20, 40)]
PUBLISHED_ARM = {"n_hold": 5, "rebal": 20, "vol_target": 0.08}


def arm_name(a: dict) -> str:
    vt = "vt08" if a["vol_target"] else "plain"
    return "n%d_r%d_%s" % (a["n_hold"], a["rebal"], vt)


# ---- pure helpers (the selftest legs pin every one of them) --------------------
def ranks(vals: list[float]) -> list[float]:
    """Average ranks, ties shared -- Spearman on a grid of books is tie-heavy."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def pearson(x: list[float], y: list[float]) -> float | None:
    n = len(x)
    if n < 3 or n != len(y):
        return None
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0.0 or sy == 0.0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3:
        return None
    return pearson(ranks(x), ranks(y))


def perm_p(x: list[float], y: list[float], rho: float | None, iters: int, seed: int) -> float | None:
    """Two-sided permutation p for |rho|: the ruler is only credited for beating chance."""
    if rho is None:
        return None
    rng = np.random.default_rng(seed)
    ys = np.array(y, dtype=float)
    hits = 0
    total = 0
    for _ in range(iters):
        rng.shuffle(ys)
        r2 = spearman(x, list(ys))
        if r2 is None:
            continue
        total += 1
        if abs(r2) >= abs(rho) - 1e-12:
            hits += 1
    return (hits + 1) / (total + 1) if total else None


def year_table(ser: pd.Series) -> dict:
    """Calendar-year returns on the book's own published definition (last/first)."""
    ser = ser.dropna()
    out = {}
    for year, blk in ser.groupby(ser.index.year):
        if len(blk) < 2:
            continue
        ret = float(blk.iloc[-1]) / float(blk.iloc[0]) - 1.0
        cohorts = int(len(blk) // BARS_PER_COHORT)
        out[int(year)] = {"net_pct": ret * 100.0, "bars": int(len(blk)),
                          "cohorts": cohorts,
                          "partial": cohorts < MIN_COHORTS_FULL_YEAR}
    return out


def window_rows(table: dict, start: int, length: int) -> list[dict] | None:
    years = list(range(start, start + length))
    if any(y not in table for y in years):
        return None
    return [{"year": str(y), "net_pct": table[y]["net_pct"]} for y in years]


def window_partial(table: dict, start: int, length: int) -> bool:
    return any(table[y]["partial"] for y in range(start, start + length) if y in table)


def forward_return(table: dict, start: int, length: int, fwd: int) -> tuple[float | None, bool]:
    yrs = list(range(start + length, start + length + fwd))
    if any(y not in table for y in yrs):
        return None, False
    growth = 1.0
    partial = False
    for y in yrs:
        growth *= 1.0 + table[y]["net_pct"] / 100.0
        partial = partial or table[y]["partial"]
    return (growth - 1.0) * 100.0, partial


def cells_for_arm(name: str, table: dict, window_years: int) -> list[dict]:
    """Every leading window that has a real forward year behind it."""
    out = []
    years = sorted(table)
    if not years:
        return out
    for start in range(years[0], years[-1] - window_years + 1):
        rows = window_rows(table, start, window_years)
        if rows is None:
            continue
        fwd, fwd_partial = forward_return(table, start, window_years, CRITERIA["forward_years"])
        if fwd is None:
            continue
        lead = C.calibers(rows)
        out.append({
            "arm": name,
            "window": "%d-%d" % (start, start + window_years - 1),
            "forward_year": start + window_years,
            "leading": {k: lead[k] for k in ("net_sum_pct", "net_top2_share",
                                             "gross_top2_share", "effective_years",
                                             "years_for_half")},
            "forward_pct": round(fwd, 4),
            "leading_partial": window_partial(table, start, window_years),
            "forward_partial": fwd_partial,
        })
    return out


def pooled(cells: list[dict], caliber: str) -> dict:
    use = [c for c in cells
           if not c["leading_partial"] and not c["forward_partial"]
           and c["leading"].get(caliber) is not None]
    xs = [float(c["leading"][caliber]) for c in use]
    ys = [float(c["forward_pct"]) for c in use]
    rho = spearman(xs, ys)
    p = perm_p(xs, ys, rho, CRITERIA["permutations"], CRITERIA["seed"])
    return {"caliber": caliber, "cells": len(use), "cells_published": len(cells),
            "excluded_partial": len(cells) - len(use), "rho": None if rho is None else round(rho, 4),
            "perm_p": None if p is None else round(p, 4),
            "min_cells_met": len(use) >= CRITERIA["min_cells"]}


def verdict_of(read: dict) -> str:
    if not read.get("min_cells_met") or read.get("rho") is None:
        return "NOT_ASSESSED"
    rho, p = read["rho"], read["perm_p"]
    if p is None:
        return "NOT_ASSESSED"
    if rho <= -0.35 and p < 0.10:
        return "RULER_SEES_FORWARD"
    if rho >= 0.35 and p < 0.10:
        return "RULER_INVERTED"
    return "RULER_BLIND"


def combine(primary: str, secondary: str) -> dict:
    """Composite word = the worst of the two windows, never an average of them (E433).

    Severity order is frozen in CRITERIA["severity_worst_first"]: a backwards ruler is
    worse than a decorative one, because it does not merely fail to protect, it
    actively refuses the right book and admits the wrong one.
    """
    words = [primary, secondary]
    worst = None
    for word in CRITERIA["severity_worst_first"]:
        if word in words:
            worst = word
            break
    if worst is None:
        # every window read the same non-worst word -- keep it only if all agree
        worst = words[0] if words.count(words[0]) == len(words) else "NOT_ASSESSED"
    return {"windows": words, "composite": worst,
            "agree": primary == secondary}


def pooled_disjoint(cells: list[dict], caliber: str, window_years: int) -> dict:
    """The same test with overlapping windows removed (one cell per non-overlapping blow).

    ADDED AFTER the first full reading, and only in the strict direction: dropping
    overlapping cells throws away information, so it can weaken a claim and never
    strengthen one.  A ruler that only works on overlapping windows is reading the same
    year twice, which is why this number is published next to the headline.
    """
    by_arm: dict[str, list[dict]] = {}
    for c in cells:
        by_arm.setdefault(c["arm"], []).append(c)
    keep = []
    for name, rows in by_arm.items():
        rows.sort(key=lambda c: int(c["window"].split("-")[0]))
        last_start = None
        for c in rows:
            start = int(c["window"].split("-")[0])
            if last_start is not None and start - last_start < window_years:
                continue
            last_start = start
            keep.append(c)
    out = pooled(keep, caliber)
    out["arms"] = len(by_arm)
    out["verdict"] = verdict_of(out)
    return out


def selector(tables: dict, window_years: int) -> dict:
    """The gate as a selector: hold next year the passing arms, else the published book.

    STRUCTURAL CAVEAT, printed with the numbers: ``net_top2_share`` on a record of n
    years cannot fall below 2/n while every year is positive (the two best years are at
    least an even share of the sum).  So the 0.70 line leaves exactly
    ``0.70 - 2/n`` of room -- 3.3pp at n=3, 20pp at n=4.  A run in which nothing passes
    must therefore be read together with that floor: at n=3 it may say more about the
    line than about the books.
    """
    line = C.CALIBERS["net_top2_share"]["line"]
    floor = 2.0 / window_years
    years = sorted(next(iter(tables.values())))
    rows = []
    cum_gate = 1.0
    cum_all = 1.0
    cum_pub = 1.0
    for year in years:
        rows_w = window_rows(tables[list(tables)[0]], year - window_years + 1, window_years)
        if rows_w is None:
            continue
        nxt = year + 1
        if nxt not in next(iter(tables.values())):
            continue
        picked, passing = [], []
        for name, table in tables.items():
            r = window_rows(table, year - window_years + 1, window_years)
            if r is None:
                continue
            cal = C.calibers(r)["net_top2_share"]
            if cal is not None and cal <= line:
                passing.append(name)
        if passing:
            picked = passing
            basis = "gate_pass"
        else:
            picked = [arm_name(PUBLISHED_ARM)]
            basis = "published_fallback"
        if not picked:
            continue
        gate_ret = float(np.mean([tables[a][nxt]["net_pct"] for a in picked if a in tables]))
        all_ret = float(np.mean([t[nxt]["net_pct"] for t in tables.values()]))
        pub_name = arm_name(PUBLISHED_ARM)
        pub_ret = float(tables[pub_name][nxt]["net_pct"]) if pub_name in tables else None
        partial = any(tables[a][nxt]["partial"] for a in picked if a in tables)
        rows.append({"decided_at": year, "forward_year": nxt, "basis": basis,
                     "picked": picked, "n_passing": len(passing),
                     "best_leading_share": _best_share(tables, year, window_years),
                     "gate_pct": round(gate_ret, 4), "all_arms_pct": round(all_ret, 4),
                     "published_pct": None if pub_ret is None else round(pub_ret, 4),
                     "forward_partial": partial})
        cum_gate *= 1.0 + gate_ret / 100.0
        cum_all *= 1.0 + all_ret / 100.0
        if pub_ret is not None:
            cum_pub *= 1.0 + pub_ret / 100.0
    return {"rule": CRITERIA["selector_rule"], "window_years": window_years,
            "gate_line": line, "arithmetic_floor_2_over_n": round(floor, 4),
            "room_above_floor_pp": round((line - floor) * 100.0, 2),
            "decisions": rows,
            "cum_gate": round((cum_gate - 1.0) * 100.0, 4),
            "cum_all_arms": round((cum_all - 1.0) * 100.0, 4),
            "cum_published": round((cum_pub - 1.0) * 100.0, 4),
            "gate_minus_null_pp": round(((cum_gate - 1.0) - (cum_all - 1.0)) * 100.0, 4),
            "decisions_count": len(rows),
            "never_passed": all(d["n_passing"] == 0 for d in rows) if rows else None,
            "power_note": "%d decision points cannot settle a strategy question (r1316); "
                          "this read prices the gate, it does not certify it"
                          % len(rows)}


def _best_share(tables: dict, year: int, window_years: int) -> float | None:
    """The closest any arm came to the line -- 'nothing passed' needs its margin."""
    best = None
    for table in tables.values():
        r = window_rows(table, year - window_years + 1, window_years)
        if r is None:
            continue
        cal = C.calibers(r)["net_top2_share"]
        if cal is None:
            continue
        best = cal if best is None else min(best, cal)
    return None if best is None else round(best, 4)


# ---- build -------------------------------------------------------------------
def build(grid: list[dict], window_years: int) -> dict:
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    score = E.build_score(close[cols], amt[cols], feats)

    tables, arm_stats = {}, {}
    for a in grid:
        name = arm_name(a)
        ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], score,
                                          a["rebal"], a["n_hold"], COST,
                                          vol_target=a["vol_target"])
        ser = ser.dropna()
        if len(ser) < 400:
            continue
        tables[name] = year_table(ser)
        arm_stats[name] = {"from": str(ser.index[0].date()), "to": str(ser.index[-1].date()),
                           "full": A.stats2(ser, name)}
    if len(tables) < 3:
        raise SystemExit("FATAL: fewer than three arms survived pricing")

    all_cells = []
    per_arm = {}
    for name, table in tables.items():
        cells = cells_for_arm(name, table, window_years)
        all_cells.extend(cells)
        per_arm[name] = {
            "years": {str(y): round(v["net_pct"], 4) for y, v in sorted(table.items())},
            "partial_years": [str(y) for y, v in sorted(table.items()) if v["partial"]],
            "cells": len(cells),
            "leading_top2": [{"window": c["window"], "share": c["leading"]["net_top2_share"],
                              "fwd_pct": c["forward_pct"]} for c in cells],
        }

    primary = pooled(all_cells, CRITERIA["caliber_primary"])
    secondary = pooled(all_cells, CRITERIA["caliber_secondary"])
    primary["verdict"] = verdict_of(primary)
    secondary["verdict"] = verdict_of(secondary)

    payload = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": max(A.stats2(pd.Series([1.0]), "x").get("y", 0) or 0,
                              0) or None,
        "criteria": CRITERIA,
        "panel": {"arms": sorted(tables), "flips_repaired": int(n_flip),
                  "bars": int(len(close)), "from": str(close.index[0].date()),
                  "to": str(close.index[-1].date())},
        "arms": arm_stats,
        "per_arm": per_arm,
        "cells": all_cells,
        "forward_relation": {"primary": primary, "secondary": secondary,
                             "disjoint_primary": pooled_disjoint(
                                 all_cells, CRITERIA["caliber_primary"], window_years),
                             "disjoint_secondary": pooled_disjoint(
                                 all_cells, CRITERIA["caliber_secondary"], window_years)},
        "verdict": combine(primary["verdict"], secondary["verdict"]),
        "selector": selector(tables, window_years),
        "selector_secondary_window": selector(tables, CRITERIA["window_years_secondary"]),
        "limits": [
            "every arm belongs to one family, so pooled cells share one bet",
            "forward sample is at most three decision points (r1316 power floor)",
            "the caliber is read on fixed-length windows precisely because r1433 showed "
            "its value depends on record length -- a 3-year cell and a 7-year receipt are "
            "not comparable and are never pooled here",
        ],
        "runtime_sec": round(time.time() - t0, 1),
    }
    # evidence_cutoff must be the panel's own last bar (science_gates C2 legal key)
    payload["evidence_cutoff"] = str(close.index[-1].date())
    return payload


# ---- commands ----------------------------------------------------------------
def run(mode: str) -> int:
    grid = GRID_FAST if mode == "fast" else GRID_FULL
    payload = build(grid, CRITERIA["window_years"])
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    p = payload["forward_relation"]["primary"]
    s = payload["forward_relation"]["secondary"]
    sel = payload["selector"]
    print("arms=%d cells=%d (usable primary %d) runtime=%.1fs"
          % (len(payload["arms"]), len(payload["cells"]), p["cells"], payload["runtime_sec"]))
    print("primary  %s  rho=%s p=%s -> %s"
          % (p["caliber"], p["rho"], p["perm_p"], p["verdict"]))
    print("secondary %s  rho=%s p=%s -> %s"
          % (s["caliber"], s["rho"], s["perm_p"], s["verdict"]))
    print("composite: %s (agree=%s)"
          % (payload["verdict"]["composite"], payload["verdict"]["agree"]))
    for key in ("disjoint_primary", "disjoint_secondary"):
        d = payload["forward_relation"][key]
        print("%s %s cells=%d rho=%s p=%s -> %s"
              % (key, d["caliber"], d["cells"], d["rho"], d["perm_p"], d["verdict"]))
    print("selector: gate %+.2f%% vs all-arms %+.2f%% vs published %+.2f%% over %d decisions"
          % (sel["cum_gate"], sel["cum_all_arms"], sel["cum_published"], sel["decisions_count"]))
    print("  window=%dy line=%.2f arithmetic floor 2/n=%.3f (room %.1fpp) never_passed=%s"
          % (sel["window_years"], sel["gate_line"], sel["arithmetic_floor_2_over_n"],
             sel["room_above_floor_pp"], sel["never_passed"]))
    selw = payload["selector_secondary_window"]
    print("  window=%dy line=%.2f floor 2/n=%.3f (room %.1fpp) gate %+.2f all %+.2f never_passed=%s"
          % (selw["window_years"], selw["gate_line"], selw["arithmetic_floor_2_over_n"],
             selw["room_above_floor_pp"], selw["cum_gate"], selw["cum_all_arms"],
             selw["never_passed"]))
    for d in sel["decisions"]:
        print("   %d -> %d %-18s n=%d best_share=%s gate %+.2f all %+.2f"
              % (d["decided_at"], d["forward_year"], d["basis"], d["n_passing"],
                 d["best_leading_share"], d["gate_pct"], d["all_arms_pct"]))
    print("wrote", OUT)
    return 0


def check() -> int:
    """Re-derive every verdict from the receipt's own cells.  Nothing is re-priced."""
    if not os.path.exists(OUT):
        print("check: no receipt")
        return 2
    with open(OUT, encoding="utf-8") as fh:
        rec = json.load(fh)
    errs = []
    fr = rec["forward_relation"]
    for key, want in (("primary", fr["primary"]), ("secondary", fr["secondary"])):
        got = pooled(rec["cells"], want["caliber"])
        for f in ("cells", "rho", "perm_p"):
            if got[f] != want[f]:
                errs.append("%s.%s %r != %r" % (key, f, got[f], want[f]))
        if verdict_of(got) != want["verdict"]:
            errs.append("%s verdict %s != %s" % (key, verdict_of(got), want["verdict"]))
    comp = combine(fr["primary"]["verdict"], fr["secondary"]["verdict"])
    if comp != rec["verdict"]:
        errs.append("composite %r != %r" % (comp, rec["verdict"]))
    for key in ("disjoint_primary", "disjoint_secondary"):
        want = fr[key]
        got = pooled_disjoint(rec["cells"], want["caliber"], rec["criteria"]["window_years"])
        for f in ("cells", "rho", "verdict"):
            if got[f] != want[f]:
                errs.append("%s.%s %r != %r" % (key, f, got[f], want[f]))
    # the arithmetic floor claimed on the page must be the line's own arithmetic
    for sel in (rec["selector"], rec["selector_secondary_window"]):
        floor = 2.0 / sel["window_years"]
        if abs(sel["arithmetic_floor_2_over_n"] - round(floor, 4)) > 1e-9:
            errs.append("floor 2/n wrong at %dy window" % sel["window_years"])
        if not all("best_leading_share" in d for d in sel["decisions"]):
            errs.append("selector decision without its margin at %dy" % sel["window_years"])
    # every published cell must carry a fixed-length window of the frozen length
    wy = rec["criteria"]["window_years"]
    for c in rec["cells"]:
        a, b = c["window"].split("-")
        if int(b) - int(a) + 1 != wy:
            errs.append("cell %s/%s window length %d != %d" % (c["arm"], c["window"],
                                                               int(b) - int(a) + 1, wy))
    if not rec["cells"]:
        errs.append("receipt carries no cells")
    if errs:
        for e in errs[:10]:
            print("FAIL", e)
        return 1
    print("check OK: %d cells, primary %s, secondary %s, composite %s"
          % (len(rec["cells"]), fr["primary"]["verdict"], fr["secondary"]["verdict"],
             rec["verdict"]["composite"]))
    return 0


def selftest() -> int:
    ok, fail = 0, 0

    def leg(cond, name):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print("  FAIL", name)

    # L1 ranks with ties
    leg(ranks([10, 20, 20, 30]) == [1.0, 2.5, 2.5, 4.0], "average ranks share ties")
    # L2 spearman is antisymmetric and exact on a monotone pair
    leg(abs(spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) + 1.0) < 1e-12, "anti-monotone rho=-1")
    leg(abs(spearman([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) - 1.0) < 1e-12, "monotone rho=+1")
    # L3 a constant array has no rank information -> None, never 0.0
    leg(spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None, "no-variance is None not 0")
    # L4 the caliber identity is the upstream library's, not a copy
    rows = [{"year": "a", "net_pct": 10.0}, {"year": "b", "net_pct": 5.0},
            {"year": "c", "net_pct": 3.0}, {"year": "d", "net_pct": 2.0}]
    cal = C.calibers(rows)
    leg(abs(cal["net_top2_share"] - 0.75) < 1e-12, "top2 share 0.75 on the fixture")
    leg(C.passes("net_top2_share", cal["net_top2_share"]) is False, "0.75 fails the 0.70 line")
    leg(abs(cal["effective_years"] - C.calibers(rows)["effective_years"]) < 1e-12,
        "caliber read is deterministic")
    # L5 the year table marks a short calendar year partial (the 2026 trap)
    idx = pd.date_range("2026-10-01", periods=40, freq="B")
    ser = pd.Series(np.linspace(1.0, 1.1, len(idx)), index=idx)
    leg(year_table(ser)[2026]["partial"] is True, "40 bars read as a partial year")
    idx2 = pd.date_range("2023-01-03", periods=250, freq="B")
    ser2 = pd.Series(np.linspace(1.0, 1.2, len(idx2)), index=idx2)
    leg(year_table(ser2)[2023]["partial"] is False, "250 bars read as a full year")
    # L6 forward composition compounds, it does not average
    table = {2020: {"net_pct": 10.0, "partial": False}, 2021: {"net_pct": 10.0, "partial": False},
             2022: {"net_pct": 10.0, "partial": False}, 2023: {"net_pct": 0.0, "partial": False}}
    fwd, part = forward_return(table, 2020, 3, 1)
    leg(abs(fwd - 0.0) < 1e-12 and part is False, "forward year is the year after the window")
    fwd2, _ = forward_return(table, 2019, 2, 1) if 2019 in table else (None, False)
    leg(fwd2 is None, "window touching a missing year yields no cell")
    # L7 a cell whose forward year is partial is published but excluded from the reading
    tbl = {2020: {"net_pct": 5.0, "partial": False}, 2021: {"net_pct": 5.0, "partial": False},
           2022: {"net_pct": 5.0, "partial": False}, 2023: {"net_pct": 9.0, "partial": True}}
    cells = cells_for_arm("fx", tbl, 3)
    leg(len(cells) == 1 and cells[0]["forward_partial"] is True, "partial forward cell flagged")
    leg(pooled(cells, "net_top2_share")["cells"] == 0, "partial cell excluded from pooling")
    # L8 verdict words are reachable in BOTH directions (a leg that cannot fail is no evidence)
    leg(verdict_of({"min_cells_met": True, "rho": -0.62, "perm_p": 0.01}) == "RULER_SEES_FORWARD",
        "negative+significant reads SEES_FORWARD")
    leg(verdict_of({"min_cells_met": True, "rho": 0.62, "perm_p": 0.01}) == "RULER_INVERTED",
        "positive+significant reads INVERTED, not BLIND")
    leg(verdict_of({"min_cells_met": True, "rho": -0.62, "perm_p": 0.40}) == "RULER_BLIND",
        "significance is required, magnitude alone is not")
    leg(verdict_of({"min_cells_met": False, "rho": -0.62, "perm_p": 0.01}) == "NOT_ASSESSED",
        "too few cells is NOT_ASSESSED, never a pass")
    # L9 permutation p is small for a perfect relation and large for noise
    xs = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    ys = [-3, -2, -2, -1, 0, 1, 2, 3, 4]
    leg((perm_p(xs, ys, spearman(xs, ys), 500, 7) or 1.0) < 0.05, "perm p small on perfect order")
    noise = [0.5, 0.9, 0.2, 0.8, 0.1, 0.7, 0.3, 0.6, 0.4]
    leg((perm_p(noise, ys, spearman(noise, ys), 500, 7) or 0.0) > 0.10, "perm p large on noise")
    # L10 composite never averages, and disagreement cannot read SEES_FORWARD
    leg(combine("RULER_SEES_FORWARD", "RULER_BLIND")["composite"] == "RULER_BLIND",
        "composite takes the worse word")
    leg(combine("RULER_INVERTED", "RULER_BLIND")["composite"] == "RULER_INVERTED",
        "inverted is worse than blind")
    leg(combine("RULER_SEES_FORWARD", "RULER_SEES_FORWARD")["agree"] is True,
        "agreement is reported, not assumed")
    # L11 selector: fallback when nothing passes, and a single pick reproduces that arm
    tables = {
        "n5_r20_vt08": {2020: {"net_pct": 5.0, "partial": False},
                        2021: {"net_pct": 5.0, "partial": False},
                        2022: {"net_pct": 5.0, "partial": False},
                        2023: {"net_pct": 7.0, "partial": False}},
        "n3_r20_vt08": {2020: {"net_pct": 1.0, "partial": False},
                        2021: {"net_pct": 1.0, "partial": False},
                        2022: {"net_pct": 9.0, "partial": True},
                        2023: {"net_pct": 2.0, "partial": False}},
    }
    sel = selector(tables, 3)
    leg(sel["decisions_count"] == 1, "one decision point from four calendar years")
    d = sel["decisions"][0]
    leg(d["basis"] in ("gate_pass", "published_fallback"), "decision carries its basis")
    leg(abs(d["gate_pct"] - tables[arm_name(PUBLISHED_ARM)][d["forward_year"]]["net_pct"]) < 1e-9
        or d["basis"] == "gate_pass", "fallback prices the published book, not an average")
    # L12 a tampered cell must break --check's re-derivation
    rec_rows = [{"year": "a", "net_pct": 1.0}, {"year": "b", "net_pct": 9.0},
                {"year": "c", "net_pct": 1.0}]
    before = C.calibers(rec_rows)["net_top2_share"]
    rec_rows[0]["net_pct"] = 8.0
    leg(C.calibers(rec_rows)["net_top2_share"] != before, "tampering moves the caliber")
    # L13 disjoint pooling keeps one cell per non-overlapping block per arm
    fake = []
    for arm in ("a1", "a2"):
        for start in (2020, 2021, 2022, 2023):
            fake.append({"arm": arm, "window": "%d-%d" % (start, start + 2),
                         "leading": {"net_top2_share": 0.5 + start * 1e-4,
                                     "effective_years": 3.0},
                         "forward_pct": float(start), "leading_partial": False,
                         "forward_partial": False})
    dj = pooled_disjoint(fake, "net_top2_share", 3)
    leg(dj["cells"] == 4, "disjoint keeps 2 of 4 windows per arm")
    leg(pooled(fake, "net_top2_share")["cells"] == 8, "overlapping read keeps all 8")
    # L14 the selector's arithmetic floor is the line's, not a fitted number
    leg(abs(2.0 / 3 - 0.6667) < 1e-3, "2/n floor for a three-year window is 0.667")
    print("selftest: %d PASS, %d FAIL" % (ok, fail))
    return 0 if fail == 0 else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--arms", default="full", choices=("fast", "full"))
    ns = ap.parse_args(argv[1:] if len(argv) > 1 else [])
    if ns.selftest or ns.cmd == "selftest":
        return selftest()
    if ns.check or ns.cmd == "check":
        return check()
    return run(ns.arms)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))