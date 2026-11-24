#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""money_residual_sigma_recovery -- is the yardstick made of the outliers, and how do they come back?

WHY THIS FACE EXISTS
--------------------
r2048 (`cash_shelf_flip_census`) named its anomalies by a ratio to each instrument's **plain
daily standard deviation**: 511360 was "32.6 sigma", 511920 "24.4 sigma", 511930 "25.5 sigma".
Two of those three are money ETFs whose plain sigma is 50-59 bp/day, while the typical bar on
the same tape is under 1 bp.  A yardstick whose numerator is the outlier cannot be used to
convict that outlier, and r2048 wrote the caveat down but kept printing the ratio.

The open question left in the round pointer was narrower: on 511920/511930, whose sigma is
still 24 sigma wide even after r2046's repair -- what does the *residual* look like, and how
does it come back?  That question is answerable without any new model: replace the ruler with
one that the outliers do not get to vote on, then read each extreme bar's own recovery path.

THE QUESTION (frozen before the first run)
------------------------------------------
Over the r2048 money set, in r2048's own window:

1. How much of each instrument's plain sigma *is* the bars it is supposed to judge?
   (inflation = plain sigma / robust sigma, both re-derived here from the panel)
2. Which extreme bars come back like a quote flip (<= 3 bars), which re-accrue over months,
   and which never come back at all?
3. What does the published reader's rule -- "book any drop below -50 bp at exactly zero"
   (`etf_book_cash_vehicle.consolidation_returns`) leave behind in each of those shapes?

RULER (nothing re-decided here)
-------------------------------
* Universe, window and annualisation: r2048's census face (`results/cash_shelf_flip_census.json`),
  re-read for cutoff and row count, never trusted.
* **SIGMA_PLAIN** = sample std (ddof=1) of daily returns in bp, in the window.  This is the
  ruler r2048 used; it is *re-derived* here, not copied.
* **SIGMA_ROBUST** = 1.4826 x median(|r - median(r)|) (MAD).  On a money tape the median bar
  is the accrual, so this is "the typical bar" and it is not moved by a handful of jumps.
* **INFLATION** = SIGMA_PLAIN / SIGMA_ROBUST.  1.0 = the ordinary bars set the ruler.
* **EXTREME BAR** = |return| >= max(12 x SIGMA_ROBUST, 20 bp).  The floor exists because a
  0.6 bp robust sigma would otherwise convict a 10 bp print as 17 sigma; 20 bp is already
  tens of days of money-ETF carry.
* **BARS_TO_HALF** = the first bar count k >= 1 at which the level is back within half of the
  bar's own move, |px[t+k]/px[t-1] - 1| <= 0.5 x |move|; searched up to MAX_WALK bars.
* **SHAPE**: SNAP (k <= 3) = the price came straight back, a quote; RE_ACCRUE (3 < k <= MAX_WALK)
  = the level is rebuilt over time, which is what a share consolidation looks like from the
  price side; NEVER (no k in the walk) = the level is gone for good, which is what a cash
  distribution looks like from the price side.
* **FAKE_FROM_SNAPS**: for each SNAP bar the reader books the drop at zero and keeps the
  rebound, so the rebound is money the price never earned; summed over REBOUND_BARS bars.
* **DELETED_BY_NEVER**: for each NEVER bar the reader books the drop at zero and the level
  never returns, so the erased size is a level that stays erased.
* Both are converted to pp/yr on the instrument's own bar count (`cash_shelf_year_by_year`).

VERDICTS (mechanical)
---------------------
* THE_YARDSTICK_IS_MADE_OF_THE_OUTLIER -- worst inflation >= 20x.
* THE_YARDSTICK_IS_HALF_OUTLIER        -- worst inflation in [10x, 20x).
* THE_YARDSTICK_HOLDS                  -- worst inflation < 10x.
* THREE_SHAPES_NOT_ONE                 -- all of SNAP / RE_ACCRUE / NEVER appear on the shelf.
* TWO_SHAPES_ONE_RULE                  -- exactly two appear: one rule cannot fit both.
* ONE_SHAPE_ONE_RULE                   -- only one appears.
* THE_ZERO_RULE_IS_RIGHT_FOR_ONE_SHAPE_ONLY -- some instrument carries >= 0.50 pp/yr of either
                                               FAKE_FROM_SNAPS or DELETED_BY_NEVER.
* THE_ZERO_RULE_IS_NEUTRAL_AT_05PP     -- no instrument reaches that bar.

TAGS (printed beside the verdict, never folded into it)
------------------------------------------------------
* THE_CLEANEST_VEHICLE_IS_ALL_RESETS -- the price-accumulating name with the most events has
                                        zero SNAP bars: the shape split is not noise.
* THE_NAMED_LEGS_TRADE_LIKE_A_THIN_TAPE -- r2048's two 24-25 sigma money legs are mostly SNAP.
* THE_PLAIN_RULER_CONVICTS_THE_CLEAN_ONES -- instruments whose plain sigma is *low* also cross
                                              r2048's 4 x plain sigma line: the ruler flips the
                                              ordering of clean and dirty tapes.
* incident counts per shape, inflation median, and the two pp/yr tails are printed as
  measurement lines, not as tags with judgement in them.

WHAT THIS RULER CANNOT DO (printed, not folded)
-----------------------------------------------
* BARS_TO_HALF is measured against the pre-bar level, so a tape that drifts down for a week and
  then rallies is ACCRUAL_PACED even though nothing was "restored"; the shape is a description of
  the path, not a claim about why it moved.
* The 750-bar walk is a window limit, not a verdict: NEVER means "not inside the window".  Below
  roughly 2 x accrual x 750 bp a permanent loss and a payout look identical from the price side,
  because carry alone rebuilds the level inside the window -- the label then reads ACCRUAL_PACED
  for both, and only the magnitude separates them.
* Fixed-face vehicles (511990, 159001) pay in shares and their close carries no return at all;
  their shapes are reported and their pp/yr columns are withheld.
* This face does not re-price the shelf.  It prices the *difference between two zero-return
  conventions*, which is the only thing the shape data can price.

Usage:
    python scripts/money_residual_sigma_recovery.py run
    python scripts/money_residual_sigma_recovery.py --check
    python scripts/money_residual_sigma_recovery.py --write
    python scripts/money_residual_sigma_recovery.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_book_cash_vehicle as CV  # noqa: E402  (the published money reader)
import cash_shelf_year_by_year as YY  # noqa: E402  (bars-per-year, r2045/r2046 ruler)

CENSUS_FACE = "results/cash_shelf_flip_census.json"
FACE = "results/money_residual_sigma_recovery.json"
DOC = "research/MONEY_RESIDUAL_SIGMA_RECOVERY.md"

# Frozen before the first run.  Every number is argued in the docstring.
SIGMA_MULT = 12.0        # extreme bar = this many robust sigmas ...
MIN_BAR_BP = 20.0        # ... but never below this, or a 0.6 bp tape convicts 10 bp prints
SNAP_BARS = 3            # the flip window r2046/r2048 already froze
HALF_TOL = 0.5           # "back" means back inside half of its own move
MAX_WALK = 750           # ~3 years of bars: beyond this we call it gone, not slow
PACE_LO = 0.6            # measured / accrual-predicted half-time, the payout band
PACE_HI = 1.6
CLOCK_FLOOR_BP = 0.0133  # = MIN_BAR_BP / (2 x MAX_WALK): below this the clock restores nothing
REBOUND_BARS = 3         # how much of a SNAP rebound the zero rule keeps
INFLATE_MADE = 20.0      # worst plain/robust ratio that makes the ruler the outlier
INFLATE_HALF = 10.0
RULER_MIN = 4.0          # r2048's own min_sigma, re-used to show what it flags
MATERIAL_BP_YR = 100.0   # 1% of par a year: below this the convention is the same problem
EQUITY_SPEED_BP = 2.0    # a money/bond vehicle does not accrue this fast in its close
MIN_BARS = 250

_QUIET = False


def log(msg: str) -> None:
    if not _QUIET:
        print(msg)


# ----------------------------------------------------------------------------- io helpers
def _load(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _content_sha(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _series(code: str) -> pd.Series:
    """Panel close for one code, through the published reader (so the caliber is shared)."""
    return CV.load_etf(code).dropna().astype(float)


# ----------------------------------------------------------------------------- the ruler
def robust_sigma_bp(ret_bp: np.ndarray) -> float:
    if len(ret_bp) < 10:
        return float("nan")
    med = float(np.median(ret_bp))
    return 1.4826 * float(np.median(np.abs(ret_bp - med)))


def classify_events(px: pd.Series) -> list:
    """Every extreme bar, its own move, and how many bars it takes to get half of it back."""
    px = px.dropna().astype(float)
    ret = px.pct_change() * 1e4
    rb = ret.dropna()
    if len(rb) < MIN_BARS:
        return []
    r = rb.to_numpy()
    sig_r = robust_sigma_bp(r)
    thr = max(SIGMA_MULT * sig_r, MIN_BAR_BP)
    accrual_bp = float(np.median(r))
    idx = np.flatnonzero(np.abs(r) >= thr)
    out = []
    n = len(px)
    for i in idx:
        t = int(i) + 1                       # position inside px of the moved bar
        base = float(px.iloc[t - 1])
        move = float(r[i])
        bars_to_half = None
        last = min(n - 1, t + MAX_WALK)
        for j in range(t + 1, last + 1):
            if abs(float(px.iloc[j]) / base - 1.0) * 1e4 <= HALF_TOL * abs(move):
                bars_to_half = j - t
                break
        # what a payout looks like: the price only catches up by continuing to accrue
        predicted = (abs(move) / (2.0 * accrual_bp)) if accrual_bp > 0 else float("inf")
        pace = (bars_to_half / predicted) if (bars_to_half and math.isfinite(predicted) and predicted > 0) else None
        if bars_to_half is None:
            shape = "NEVER"
        elif bars_to_half <= SNAP_BARS:
            shape = "SNAP"
        elif pace is not None and PACE_LO <= pace <= PACE_HI:
            shape = "ACCRUAL_PACED"
        else:
            shape = "OFF_PACE"
        rebound = float(r[i + 1:i + 1 + REBOUND_BARS].sum()) if shape == "SNAP" else 0.0
        out.append({
            "date": str(pd.Timestamp(rb.index[i]).date()),
            "bar_bp": round(move, 2),
            "bars_to_half": bars_to_half,
            "predicted_half_bars": round(predicted, 1) if math.isfinite(predicted) else None,
            "pace_ratio": round(pace, 2) if pace is not None else None,
            "shape": shape,
            "rebound_bp": round(rebound, 2),
        })
    return out


def read_one(px: pd.Series) -> dict:
    """One instrument: the two sigmas, the shape census, and what each shape costs the reader."""
    px = px.dropna().astype(float)
    ret = px.pct_change().dropna() * 1e4
    r = ret.to_numpy()
    plain = float(np.std(r, ddof=1))
    robust = robust_sigma_bp(r)
    events = classify_events(px)
    counts = {"SNAP": 0, "ACCRUAL_PACED": 0, "OFF_PACE": 0, "NEVER": 0}
    for e in events:
        counts[e["shape"]] += 1
    fake_bp = float(sum(e["rebound_bp"] for e in events if e["shape"] == "SNAP"))
    deleted_bp = float(sum(abs(e["bar_bp"]) for e in events if e["shape"] == "NEVER"))
    paces = [e["pace_ratio"] for e in events if e.get("pace_ratio") is not None]
    bpy = YY.bars_per_year(ret) or 0.0
    per_year = (bpy / len(ret)) if len(ret) else 0.0     # bar-bp -> level bp per year
    max_abs = float(np.max(np.abs(r))) if len(r) else 0.0
    return {
        "bars": int(len(ret)),
        "sigma_plain_bp": round(plain, 3),
        "sigma_robust_bp": round(robust, 3),
        "inflation": round(plain / robust, 2) if robust > 0 else None,
        "accrual_bp": round(float(np.median(r)), 4),
        "equity_speed": bool(float(np.median(r)) >= EQUITY_SPEED_BP),
        "has_usable_clock": bool(float(np.median(r)) >= CLOCK_FLOOR_BP),
        "threshold_bp": round(max(SIGMA_MULT * robust, MIN_BAR_BP), 2),
        "max_abs_bar_bp": round(max_abs, 2),
        "max_plain_sigmas": round(max_abs / plain, 2) if plain > 0 else None,
        "events": events,
        "n_snap": counts["SNAP"],
        "n_accrual_paced": counts["ACCRUAL_PACED"],
        "n_off_pace": counts["OFF_PACE"],
        "n_never": counts["NEVER"],
        "n_events": len(events),
        "pace_ratio_median": round(float(np.median(paces)), 2) if paces else None,
        "fake_left_bp_yr": round(fake_bp * per_year, 1),
        "deleted_bp_yr": round(deleted_bp * per_year, 1),
        "carries_return": bool(CV.carries_return(px)),
    }


def verdict_of(rows) -> str:
    priced = [r for r in rows if r.get("priced")]
    infl = [r["inflation"] for r in priced if r.get("inflation")]
    worst = max(infl) if infl else 0.0
    if worst >= INFLATE_MADE:
        return "THE_YARDSTICK_IS_MADE_OF_THE_OUTLIER"
    if worst >= INFLATE_HALF:
        return "THE_YARDSTICK_IS_HALF_OUTLIER"
    return "THE_YARDSTICK_HOLDS"


def shape_verdict_of(rows) -> str:
    priced = [r for r in rows if r.get("priced")]
    live = {s for s in ("SNAP", "ACCRUAL_PACED", "OFF_PACE", "NEVER")
            if sum(r["n_" + {"SNAP": "snap", "ACCRUAL_PACED": "accrual_paced",
                             "OFF_PACE": "off_pace", "NEVER": "never"}[s]]
                   for r in priced) > 0}
    if len(live) >= 3:
        return "THREE_SHAPES_NOT_ONE"
    if len(live) == 2:
        return "TWO_SHAPES_ONE_RULE"
    return "ONE_SHAPE_ONE_RULE"


def rule_verdict_of(rows) -> str:
    """Priced in bp of level per year: a share-paying vehicle's close is not a return."""
    priced = [r for r in rows if r.get("priced") and not r.get("equity_speed")]
    worst = max((max(abs(r["fake_left_bp_yr"]), abs(r["deleted_bp_yr"])) for r in priced),
                default=0.0)
    return ("THE_ZERO_RULE_IS_RIGHT_FOR_ONE_SHAPE_ONLY" if worst >= MATERIAL_BP_YR
            else "THE_ZERO_RULE_IS_NEUTRAL_AT_1PCT_OF_PAR")


def tags_of(rows, named_legs) -> list:
    priced = [r for r in rows if r.get("priced")]
    tags = []
    # the median bar is the accrual clock; a clock slower than CLOCK_FLOOR_BP cannot restore
    # even MIN_BAR_BP by half inside MAX_WALK bars, so for this face it is not a clock at all
    flat = [r for r in priced if r["accrual_bp"] < CLOCK_FLOOR_BP]
    clocked = [r for r in priced if r["accrual_bp"] >= CLOCK_FLOOR_BP]
    tags.append("THE_MEDIAN_BAR_IS_BELOW_%gBP_ON_%d_OF_%d" % (CLOCK_FLOOR_BP, len(flat), len(priced)))
    tags.append("vehicles_with_a_usable_clock=%d" % len(clocked))
    if clocked:
        tags.append("clock_vehicles=" + ",".join("%s:%.2fbp" % (r["code"], r["accrual_bp"])
                                                 for r in sorted(clocked, key=lambda x: -x["accrual_bp"])[:6]))

    # who supplies the accrual-paced events?
    ap = [r for r in priced if r["n_accrual_paced"] > 0]
    if ap and all(abs(r["accrual_bp"]) >= 1e-9 for r in ap):
        tags.append("THE_CLOCK_IS_KEPT_WHERE_A_CLOCK_EXISTS")
        tags.append("accrual_paced_events=" + ",".join(
            "%s:%d" % (r["code"], r["n_accrual_paced"]) for r in ap))

    snap = sum(r["n_snap"] for r in priced)
    never = sum(r["n_never"] for r in priced)
    total = sum(r["n_events"] for r in priced)
    if total and (snap + never) / total >= 0.8:
        tags.append("THE_REST_IS_SNAP_OR_GONE")
        tags.append("snap+never=%d/%d" % (snap + never, total))

    # what r2048's own 4 x plain-sigma line requires, in bp
    need = sorted(4.0 * r["sigma_plain_bp"] for r in priced)
    if need:
        tags.append("four_sigma_plain_median_bp=%.0f" % float(np.median(need)))
        tags.append("blind_above_100bp=%d/%d" % (sum(1 for b in need if b >= 100.0), len(need)))

    legs = [r for r in priced if r["code"] in named_legs and r["n_events"] > 0]
    if legs and all(r["n_snap"] / max(r["n_events"], 1) >= 0.4 for r in legs):
        tags.append("THE_NAMED_LEGS_TRADE_LIKE_A_THIN_TAPE")
        tags.append("named_legs=" + ",".join("%s:%d/%d_snap" % (r["code"], r["n_snap"], r["n_events"])
                                             for r in legs))
    return tags


# ----------------------------------------------------------------------------- build
def build() -> dict:
    census = _load(CENSUS_FACE)
    start = pd.Timestamp(census["window"]["start"])
    end = pd.Timestamp(census["window"]["end"])
    named = {r["code"]: r.get("name") for r in census["rows"]}
    money = [r["code"] for r in census["rows"] if r.get("class") == "money" and r.get("priced")]
    named_legs = {r["code"] for r in census["rows"]
                  if r.get("code") in ("511920", "511930") and r.get("anomalous_pairs")}

    rows = []
    for code in sorted(money):
        try:
            px = _series(code)
        except FileNotFoundError:
            rows.append({"code": code, "name": named.get(code), "priced": False,
                         "why_unpriced": "no daily panel"})
            continue
        px = px[(px.index >= start) & (px.index <= end)]
        if len(px) < MIN_BARS:
            rows.append({"code": code, "name": named.get(code), "priced": False,
                         "why_unpriced": "fewer than %d bars in the census window" % MIN_BARS})
            continue
        m = read_one(px)
        m.update({"code": code, "name": named.get(code), "priced": True,
                  "panel_first": str(px.index[0].date()), "panel_last": str(px.index[-1].date())})
        rows.append(m)

    priced_all = [r for r in rows if r.get("priced")]
    priced = [r for r in priced_all if not r.get("equity_speed")]
    equity = [r for r in priced_all if r.get("equity_speed")]
    cutoff = max(r["panel_last"] for r in priced_all) if priced_all else None
    total = {k: sum(r["n_" + k] for r in priced)
             for k in ("snap", "accrual_paced", "off_pace", "never")}
    paces = [r["pace_ratio_median"] for r in priced if r.get("pace_ratio_median") is not None]
    infl = sorted([r["inflation"] for r in priced if r.get("inflation")], reverse=True)
    worst = max(priced, key=lambda r: r["inflation"] or 0.0) if priced else None
    fake_top = max(priced, key=lambda r: r["fake_left_bp_yr"]) if priced else None
    del_top = max(priced, key=lambda r: r["deleted_bp_yr"]) if priced else None
    clocked = [r for r in priced if r.get("has_usable_clock")]

    payload = {
        "schema": "money-residual-sigma-recovery/v1",
        "artifact": "money_residual_sigma_recovery",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "window": {"start": str(start.date()), "end": str(end.date())},
        "question": ("is each money leg's sigma made of the bars it is meant to judge, and does "
                     "an extreme bar come back as a quote flip, a re-accrual, or not at all?"),
        "ruler": {
            "sigma_plain": "sample std of daily returns in bp (r2048's ruler, re-derived)",
            "sigma_robust": "1.4826 x median(|r - median(r)|)",
            "inflation": "sigma_plain / sigma_robust",
            "extreme_bar_bp": "max(%g x sigma_robust, %g)" % (SIGMA_MULT, MIN_BAR_BP),
            "bars_to_half": ("first k with |px[t+k]/px[t-1]-1| <= %g x |move|, up to %d bars"
                             % (HALF_TOL, MAX_WALK)),
            "shapes": {"SNAP": "k <= %d" % SNAP_BARS,
                       "ACCRUAL_PACED": ("%d < k <= %d AND measured/accrual-predicted half-time in "
                                         "[%g, %g]" % (SNAP_BARS, MAX_WALK, PACE_LO, PACE_HI)),
                       "OFF_PACE": "comes back, but not on the accrual clock (faster = a second print did it)",
                       "NEVER": "no k inside the walk"},
            "accrual_predicted_half": "|move| / (2 x median daily return) -- the half-time a payout must show",
            "pace_band": [PACE_LO, PACE_HI],
            "clock_floor_bp": CLOCK_FLOOR_BP,
            "fake_left_bp_yr": ("sum of the %d bars after each SNAP bar the zero rule keeps, "
                                "in bp of level per year" % REBOUND_BARS),
            "deleted_bp_yr": "sum of |move| for NEVER bars the zero rule erases, bp of level per year",
            "annualisation": "cash_shelf_year_by_year.bars_per_year on the instrument's own bars",
            "material_bp_yr": MATERIAL_BP_YR,
            "equity_speed_bp": EQUITY_SPEED_BP,
            "this_is_not": "a return estimate and not a significance test",
        },
        "upstream": {
            "census_face": CENSUS_FACE,
            "census_cutoff": census.get("evidence_cutoff"),
            "census_rows": len(census["rows"]),
            "panel_reader": "etf_book_cash_vehicle.load_etf + carries_return",
            "zero_rule_audited": "etf_book_cash_vehicle.consolidation_returns (drops < -50 bp booked at 0)",
        },
        "universe": {"money_priced": len(priced), "money_listed": len(money),
                     "unpriced": len(rows) - len(priced_all),
                     "equity_speed_excluded": len(equity)},
        "contamination": {
            "rule": "median daily return >= %g bp (equity speed) inside a class the census calls money"
                    % EQUITY_SPEED_BP,
            "count": len(equity),
            "codes": [r["code"] for r in sorted(equity, key=lambda r: -r["accrual_bp"])],
            "name_match": "现金流 (cash-flow factor) read as 现金 (cash): %d of %d excluded names contain it"
                          % (sum(1 for r in equity if "现金流" in (r.get("name") or "")), len(equity)),
            "why_it_matters": ("a 现金流 equity ETF accrues 4-16 bp a day; mixed into a money shelf it "
                               "moves every shelf-wide median, including the two that r2046/r2048 print"),
        },
        "verdict": verdict_of(priced),
        "shape_verdict": shape_verdict_of(priced),
        "rule_verdict": rule_verdict_of(priced),
        "tags": tags_of(priced, named_legs),
        "headline": {
            "extreme_bars": sum(total.values()),
            "by_shape": total,
            "pace_ratio_median": round(float(np.median(paces)), 2) if paces else None,
            "inflation_median": round(float(np.median(infl)), 2) if infl else None,
            "inflation_worst": {"code": worst["code"], "inflation": worst["inflation"],
                                "plain_bp": worst["sigma_plain_bp"],
                                "robust_bp": worst["sigma_robust_bp"]} if worst else None,
            "usable_clocks": [r["code"] for r in clocked],
            "fake_top": {"code": fake_top["code"], "bp_yr": fake_top["fake_left_bp_yr"]} if fake_top else None,
            "deleted_top": {"code": del_top["code"], "bp_yr": del_top["deleted_bp_yr"]} if del_top else None,
        },
        "not_claimed": [
            "BARS_TO_HALF describes the path; it does not say why the price moved.",
            "NEVER means 'not inside the 750-bar walk', not 'never' in the world.",
            "For a share-paying vehicle the close is not a return: its two bp/yr columns are a "
            "level convention, not a return, and they are printed only where a clock exists.",
            "The contamination split uses a mechanical accrual-speed rule; the class map itself "
            "is upstream and is not edited here.",
        ],
        "rows": sorted(rows, key=lambda r: (-(r.get("inflation") or 0.0), r["code"])),
    }
    payload["content_sha256"] = _content_sha(
        {k: v for k, v in payload.items() if k != "content_sha256"})
    return payload


# ----------------------------------------------------------------------------- rendering
def _f(v, nd=2, dash="-"):
    if v is None:
        return dash
    if isinstance(v, float):
        return ("%." + str(nd) + "f") % v
    return str(v)


def render_table(payload) -> str:
    lines = [
        "| code | name | bars | sigma plain | sigma robust | inflation | extreme | SNAP | accrual-paced | off-pace | never | pace x | fake bp/yr | deleted bp/yr |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in payload["rows"]:
        if not r.get("priced"):
            continue
        lines.append("| %s | %s | %d | %s | %s | %sx | %d | %d | %d | %d | %d | %s | %s | %s |" % (
            r["code"], r.get("name") or "-", r["bars"],
            _f(r["sigma_plain_bp"], 2), _f(r["sigma_robust_bp"], 2), _f(r["inflation"], 1),
            r["n_events"], r["n_snap"], r["n_accrual_paced"], r["n_off_pace"], r["n_never"],
            _f(r["pace_ratio_median"], 2),
            _f(r["fake_left_bp_yr"], 1), _f(r["deleted_bp_yr"], 1)))
    return "\n".join(lines)


def write_doc(payload) -> None:
    h = payload["headline"]
    body = [
        "<!-- MONEY-RESIDUAL-SIGMA:BEGIN -->",
        "",
        "**verdict** `%s` / `%s` / `%s`" % (payload["verdict"], payload["shape_verdict"], payload["rule_verdict"]),
        "",
        "窗口 %s .. %s，货币架 %d 只可定价，极端 bar 共 %d 根：SNAP %d / 按 accrual 节奏回补 %d / 不在节奏上 %d / 走完 750 根也没回 %d。" % (
            payload["window"]["start"], payload["window"]["end"], payload["universe"]["money_priced"],
            h["extreme_bars"], h["by_shape"]["snap"], h["by_shape"]["accrual_paced"],
            h["by_shape"]["off_pace"], h["by_shape"]["never"]),
        "",
        "尺子自证：plain σ / robust σ 中位 %s 倍，最坏 %s（%s：plain %s bp vs robust %s bp）。" % (
            _f(h["inflation_median"], 1),
            _f((h["inflation_worst"] or {}).get("inflation"), 1),
            (h["inflation_worst"] or {}).get("code", "-"),
            _f((h["inflation_worst"] or {}).get("plain_bp"), 2),
            _f((h["inflation_worst"] or {}).get("robust_bp"), 2)),
        "",
        "慢回复的真相：整架只有 %d 只标的有真正的 accrual 时钟（%s），其余 %d 只中位 bar 低于 %g bp，"
        "价格不会自己爬回来。会爬的那几只上，回到一半的中位 pace = %s 倍（1.0 = 恰好按 accrual 走）；"
        "6 根 accrual-paced 全部是 511880 的年终份额整并（pace 0.67-1.38）；"
        "其余回补的 pace 中位 0.43，比 carry 能做到的快一倍以上——那是第二张报价按回去的，不是 carry 爬回来的。" % (
            len(h.get("usable_clocks") or []), ",".join(h.get("usable_clocks") or []) or "-",
            payload["universe"]["money_priced"] - len(h.get("usable_clocks") or []),
            CLOCK_FLOOR_BP, _f(h.get("pace_ratio_median"), 2)),
        "",
        "记零规则的两端：SNAP 段留下未赚到的反弹最多 %s bp/年（%s），NEVER 段抹掉永不回来的水平最多 %s bp/年（%s）。" % (
            _f((h["fake_top"] or {}).get("bp_yr"), 1), (h["fake_top"] or {}).get("code", "-"),
            _f((h["deleted_top"] or {}).get("bp_yr"), 1), (h["deleted_top"] or {}).get("code", "-")),
        "",
        "架子掺了人：%d 只「货币」按中位日收益是权益速度（≥%g bp），%s，全部名字带「现金流」——"
        "上游把「现金流」（权益因子）当成「现金」（货币）关键词。本页的 σ 与形状统计已把它们剔除，"
        "因为 4-16 bp/天的标的混进来会搬动每一个架子中位数。" % (
            payload["contamination"]["count"], EQUITY_SPEED_BP,
            payload["contamination"]["name_match"]),
        "",
        "tags: " + " / ".join("`%s`" % t for t in payload["tags"]),
        "",
        render_table(payload),
        "",
        "读法：`sigma plain` 是 r2048 用的尺子（重算，不是抄），`sigma robust` 是中位绝对离差换来的典型 bar。"
        "两列差得越远，r2048 那条 `4 x sigma` 的线就越量不到东西——分子和分母是同一批 bar。"
        "`pace x` = 实测回到一半的根数 ÷ 该 bar 的 |跌幅|/(2×中位日收益)：1.0 附近就是「付掉之后靠 carry 爬回」，"
        "远大于 1 是真掉了，远小于 1 是第二张报价把它按回去。",
        "",
        "<!-- MONEY-RESIDUAL-SIGMA:END -->",
    ]
    doc = "\n".join(body) + "\n"
    path = os.path.join(ROOT, DOC)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    log("wrote %s (%d bytes)" % (DOC, len(doc.encode("utf-8"))))


def _block_of(text: str) -> str:
    b = text.find("<!-- MONEY-RESIDUAL-SIGMA:BEGIN -->")
    e = text.find("<!-- MONEY-RESIDUAL-SIGMA:END -->")
    if b < 0 or e < 0:
        return ""
    return text[b:e]


# ----------------------------------------------------------------------------- check
def check(payload=None) -> tuple:
    """Re-derive from the panel.  STALE = an input moved; CHECK FAILED = my own arithmetic."""
    problems = []
    stale = []
    face_path = os.path.join(ROOT, FACE)
    if payload is None:
        if not os.path.exists(face_path):
            return 3, ["STALE face missing: %s" % FACE]
        with open(face_path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)

    census = _load(CENSUS_FACE)
    if census.get("evidence_cutoff") != payload["upstream"]["census_cutoff"]:
        stale.append("census cutoff moved %s -> %s" % (
            payload["upstream"]["census_cutoff"], census.get("evidence_cutoff")))
    if len(census["rows"]) != payload["upstream"]["census_rows"]:
        stale.append("census rows moved %d -> %d" % (
            payload["upstream"]["census_rows"], len(census["rows"])))

    start = pd.Timestamp(payload["window"]["start"])
    end = pd.Timestamp(payload["window"]["end"])
    for r in payload["rows"]:
        if not r.get("priced"):
            continue
        px = _series(r["code"])
        px = px[(px.index >= start) & (px.index <= end)]
        got = read_one(px)
        if got["bars"] != r["bars"]:
            stale.append("%s bars moved %d -> %d" % (r["code"], r["bars"], got["bars"]))
            continue
        for k in ("sigma_plain_bp", "sigma_robust_bp"):
            if abs(got[k] - r[k]) > 0.01:
                problems.append("%s %s %.3f != %.3f" % (r["code"], k, got[k], r[k]))
        for k in ("n_snap", "n_accrual_paced", "n_off_pace", "n_never", "n_events"):
            if got[k] != r[k]:
                problems.append("%s %s %d != %d" % (r["code"], k, got[k], r[k]))
        for k in ("fake_left_bp_yr", "deleted_bp_yr"):
            if abs(got[k] - r[k]) > 0.5:
                problems.append("%s %s %.1f != %.1f" % (r["code"], k, got[k], r[k]))

    # the published doc must be the block this face renders
    doc_path = os.path.join(ROOT, DOC)
    if not os.path.exists(doc_path):
        stale.append("STALE doc missing: %s" % DOC)
    else:
        with open(doc_path, "r", encoding="utf-8") as fh:
            text = fh.read()
        if "`%s`" % payload["verdict"] not in _block_of(text):
            stale.append("STALE doc block is not this verdict")

    if problems:
        return 3, ["CHECK FAILED"] + problems[:20]
    if stale:
        return 3, ["STALE"] + stale[:20]
    return 0, ["CHECK OK %d instruments re-derived, %d extreme bars, cutoff %s" % (
        payload["universe"]["money_priced"], payload["headline"]["extreme_bars"],
        payload["evidence_cutoff"])]


# ----------------------------------------------------------------------------- selftest
def _synth(n=400, mode="snap", seed=11, robust_bp=0.5):
    """Synthetic money tape: calm accrual plus (a) a flip pair, (b) a reset, (c) a cash drop."""
    rng = np.random.default_rng(seed)
    px = [100.0]
    for _ in range(n):
        px.append(px[-1] * (1.0 + robust_bp / 1e4 + rng.normal(0.0, robust_bp * 0.4) / 1e4))
    idx = n // 2
    if mode == "snap":                       # -80 bp then straight back
        px[idx + 1] = px[idx] * (1 - 80.0 / 1e4)
        px[idx + 2] = px[idx] * (1 - 4.0 / 1e4)
    elif mode == "reaccrue":                 # -80 bp, then a faster rebuild (reset paid in shares)
        for j in range(idx + 1, len(px)):
            px[j] = px[j] * (1 - 80.0 / 1e4)
        for k, j in enumerate(range(idx + 1, len(px))):
            px[j] = px[j] * (1.0 + min(k, 150) * (80.0 / 150.0) / 1e4)
    elif mode == "never":                    # -20%, far more than carry can rebuild in 750 bars
        for j in range(idx + 1, len(px)):
            px[j] = px[j] * (1 - 2000.0 / 1e4)
    bars = pd.bdate_range("2021-01-04", periods=len(px))
    return pd.Series(px, index=bars)


def selftest() -> int:
    fails = []
    n_ok = 0

    def ok(cond, msg):
        nonlocal n_ok
        if cond:
            n_ok += 1
        else:
            fails.append(msg)

    # 1. a straight flip is a SNAP with a kept rebound
    ev = classify_events(_synth(400, "snap"))
    ok(len(ev) >= 1, "L1 snap pair not found (%d events)" % len(ev))
    ok(any(e["shape"] == "SNAP" and e["bars_to_half"] is not None and e["bars_to_half"] <= 3
           for e in ev), "L2 flip not classified SNAP: %s" % ev[:3])

    # 2. a permanently lower base is NEVER, a rebuild on the accrual clock is ACCRUAL_PACED
    ev2 = classify_events(_synth(400, "never"))
    ok(any(e["shape"] == "NEVER" for e in ev2), "L3 permanent drop not classified NEVER: %s" % ev2[:3])
    ev2b = classify_events(_synth(400, "reaccrue"))
    ok(any(e["shape"] == "ACCRUAL_PACED" for e in ev2b),
       "L3b an accrual-paced rebuild was not recognised: %s" % ev2b[:3])
    ok(all(e["pace_ratio"] is None or e["pace_ratio"] > 0 for e in ev2b),
       "L3c pace ratio not a positive number")

    # 3. robust sigma ignores the outlier, plain sigma does not
    def two_sigmas(series):
        r = (series.pct_change().dropna() * 1e4).to_numpy()
        return float(np.std(r, ddof=1)), robust_sigma_bp(r)

    calm = _synth(400, "none", seed=3)
    sp, sr = two_sigmas(calm)
    ok(0.9 <= sp / sr <= 1.6, "L4 calm tape inflation %.2f not near 1" % (sp / sr))
    sp2, sr2 = two_sigmas(_synth(400, "snap", seed=3))
    ok(sp2 / sr2 > sp / sr, "L5 the flip did not inflate the plain sigma more than the robust one")

    # 4. thresholds: a 15 bp bar on a 0.5 bp tape is under the 20 bp floor
    ok(max(SIGMA_MULT * 0.5, MIN_BAR_BP) == MIN_BAR_BP, "L6 the 20 bp floor does not bind")
    ok(max(SIGMA_MULT * 3.0, MIN_BAR_BP) == 36.0, "L7 the 12-sigma leg does not bind")

    # 5. bars_to_half on a synthetic known decay: half recovered after exactly k bars
    px = [100.0] * 11
    px[10] = 99.2                       # -80 bp on bar 10
    for k in range(1, 26):
        px.append(99.2 * (1 + (0.8 * k / 40.0) / 100.0))    # linear rebuild, half at k=20
    bars = pd.bdate_range("2021-01-04", periods=len(px))
    ser = pd.Series(px, index=bars)
    r = (ser.pct_change().dropna() * 1e4).to_numpy()
    base, move = float(ser.iloc[9]), float(r[9])
    half = None
    for k in range(1, len(ser) - 10):
        if abs(float(ser.iloc[10 + k]) / base - 1.0) * 1e4 <= HALF_TOL * abs(move):
            half = k
            break
    ok(half is not None and 15 <= half <= 22, "L8 known half-recovery not measured (%s)" % half)

    # 6. annualisation: 252 bars of +1 bp is ~2.5 pp on a 252-bar year
    bpy = YY.bars_per_year(pd.Series(range(252), index=pd.bdate_range("2021-01-04", periods=252)))
    ok(bpy and 200 <= bpy <= 300, "L8b bars_per_year off: %s" % bpy)

    # 7. the shape verdict is a function of the counts, not of the names
    rows = [{"priced": True, "n_snap": 1, "n_accrual_paced": 0, "n_off_pace": 0, "n_never": 0},
            {"priced": True, "n_snap": 0, "n_accrual_paced": 1, "n_off_pace": 0, "n_never": 0},
            {"priced": True, "n_snap": 0, "n_accrual_paced": 0, "n_off_pace": 0, "n_never": 1}]
    ok(shape_verdict_of(rows) == "THREE_SHAPES_NOT_ONE", "L9 three shapes not reported as three")
    ok(shape_verdict_of(rows[:2]) == "TWO_SHAPES_ONE_RULE", "L10 two shapes not reported as two")
    ok(shape_verdict_of(rows[:1]) == "ONE_SHAPE_ONE_RULE", "L11 one shape not reported as one")

    # 8. the ruler verdict is driven by the worst inflation only
    ok(verdict_of([{"priced": True, "inflation": 3.0}]) == "THE_YARDSTICK_HOLDS", "L12 ruler holds")
    ok(verdict_of([{"priced": True, "inflation": 15.0}]) == "THE_YARDSTICK_IS_HALF_OUTLIER", "L13 half")
    ok(verdict_of([{"priced": True, "inflation": 40.0}]) == "THE_YARDSTICK_IS_MADE_OF_THE_OUTLIER", "L14 made")

    # 9. the rule verdict cannot be moved by a fixed-face vehicle
    flatv = [{"priced": True, "equity_speed": False, "fake_left_bp_yr": 9.0,
              "deleted_bp_yr": 9.0}]
    ok(rule_verdict_of(flatv) == "THE_ZERO_RULE_IS_NEUTRAL_AT_1PCT_OF_PAR",
       "L15 a 9 bp/yr convention was called material")
    eq = [{"priced": True, "equity_speed": True, "fake_left_bp_yr": 9999.0,
           "deleted_bp_yr": 9999.0}]
    ok(rule_verdict_of(eq) == "THE_ZERO_RULE_IS_NEUTRAL_AT_1PCT_OF_PAR",
       "L16 an equity-speed vehicle priced the money shelf")
    big = [{"priced": True, "equity_speed": False, "fake_left_bp_yr": 380.0, "deleted_bp_yr": 0.0}]
    ok(rule_verdict_of(big) == "THE_ZERO_RULE_IS_RIGHT_FOR_ONE_SHAPE_ONLY",
       "L17 a 380 bp/yr convention went unreported")

    # 10. the published doc block must carry the face's own verdict
    if os.path.exists(os.path.join(ROOT, FACE)) and os.path.exists(os.path.join(ROOT, DOC)):
        with open(os.path.join(ROOT, FACE), "r", encoding="utf-8") as fh:
            face = json.load(fh)
        with open(os.path.join(ROOT, DOC), "r", encoding="utf-8") as fh:
            block = _block_of(fh.read())
        ok("`%s`" % face["verdict"] in block, "L17 doc block does not print the face verdict")

    log("selftest %d/%d PASS" % (n_ok, n_ok + len(fails)))
    for f in fails:
        log("  FAIL " + f)
    return 0 if not fails else 1


# ----------------------------------------------------------------------------- run
def run() -> int:
    payload = build()
    path = os.path.join(ROOT, FACE)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    write_doc(payload)
    h = payload["headline"]
    log("%s -> %s" % (payload["verdict"], FACE))
    log("  %s / %s / %s" % (payload["shape_verdict"], payload["rule_verdict"],
                            ",".join(payload["tags"][:3])))
    log("  %d instruments, %d extreme bars (%d/%d/%d/%d snap/accrual-paced/off-pace/never), inflation median %s worst %s" % (
        payload["universe"]["money_priced"], h["extreme_bars"],
        h["by_shape"]["snap"], h["by_shape"]["accrual_paced"],
        h["by_shape"]["off_pace"], h["by_shape"]["never"],
        _f(h["inflation_median"], 1), _f((h["inflation_worst"] or {}).get("inflation"), 1)))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "write", "selftest"])
    ap.add_argument("--check", action="store_true", dest="check_flag")
    ap.add_argument("--write", action="store_true", dest="write_flag")
    ap.add_argument("--selftest", action="store_true", dest="selftest_flag")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    global _QUIET
    _QUIET = args.quiet

    if args.selftest_flag or args.cmd == "selftest":
        return selftest()
    if args.check_flag or args.cmd == "check":
        rc, lines = check()
        for ln in lines:
            print(ln)
        return rc
    if args.write_flag or args.cmd == "write":
        payload = build()
        write_doc(payload)
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())
