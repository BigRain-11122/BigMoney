"""SEASONAL HORIZON & STABILITY CENSUS (descriptive probe, E23)

Question this batch answers (one line): E22 measured the calendar windows on
the pooled stock-day face and flagged that its t values are inflated by
cross-sectional correlation -- so, on a daily equal-weight index face (one
observation per trading day, no cross-sectional pooling), do the same calendar
windows still carry an excess return, how far does the excess extend (hold
horizon 1..5 bars), does it decay by era, and does it survive the round-trip
cost of a timing overlay?

Consumer plan (TRIAL_LABOR_LAW sec.4 meaning gate -- named consumers):
  (1) seasonal family supply line: E22's reading (month-first day +41.8bp
      pooled, month-second-to-last -28.9bp) is the candidate grammar for the
      next trial-labour wave; before drafting W22 this census must tell the
      drafter (a) whether the effect is an artefact of the pooled weighting,
      (b) which holding period to freeze in the prereg exit axis;
  (2) marking/monitoring timing for the paper lanes (P4 DCA, grid marking,
      daily_report context) -- same consumer as E22, now on a daily face;
  (3) CEO research-orientation law (O-20260928-1522): domestic folk judgments
      formalized as numeric faces before belief. E22 gave the first face; this
      one is the same claim measured where the independence assumption holds.

Scope discipline: ZERO prereg, ZERO judged face, ZERO pool write, ZERO
network, ZERO engine touch. L1 deterministic; rerun byte-identical. Reads the
same local panel build as E22 (data/cache/p1c_local, T-87 forward lineage).

Measurement rules (frozen here, descriptive only):
  * panel = same loader as scripts/seasonal_calendar_census.py (single source).
  * DAILY FACE = equal-weight mean of close-to-close returns over all usable
    stock-days of that date (exclusions identical to E22: non-positive price,
    suspension-resume, one-price bar, |r|>=75%). One observation per day, so
    the t on a daily series is not inflated by cross-sectional dependence
    (overlapping horizons h>1 are still autocorrelated -- disclosed).
  * variant day sets = E22's annotate_calendar (single source), restricted to
    the executable families: turn_of_month and holiday.
  * horizon h: forward h-bar cumulative daily-face return starting on day t;
    a window is used only when all h days are valid. Baseline for the same h
    is the unconditional mean over every valid h-window on the face.
  * excess = variant mean - baseline mean (same h). t uses
    sqrt(se_v^2 + se_b^2), disclosed as overlap-ignorant for h>1.
  * era split = lu_prem_census.era_of (single source); per-year table at h=1.
  * cost: one round trip per contiguous spell, charged at 2 x COST_X1_RATE
    (ce_transfer single source, 13.041bp per side); annual gross/cost/net are
    scaled by the face's calendar span.
  * cells = |variants| x h. This is an uncorrected descriptive scan; N is
    reported and no multiplicity correction is claimed.

usage:
    python scripts/seasonal_horizon_stability.py run        # full census
    python scripts/seasonal_horizon_stability.py selftest   # hermetic legs
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from seasonal_calendar_census import (          # single-source lineage
    MAX_ABS_R, ONE_PRICE_TOL, PANEL_DIR, annotate_calendar, load_panel,
)
from lu_prem_census import era_of               # single-source lineage

try:                                            # cost single source
    from ce_transfer import COST_X1_RATE
except Exception:                               # pragma: no cover
    COST_X1_RATE = None
COST_FALLBACK = 0.0013041

TZ = timezone(timedelta(hours=8))
OUT_DIR = os.path.join(_ROOT, "results", "seasonal_horizon_stability")
DIGEST_DIR = os.path.join(_ROOT, "research", "digests")
CUTOFF_EXPECTED = "2026-10-19"
HORIZONS = (1, 2, 3, 4, 5)
VARIANT_ORDER = (
    ["tom_end%d" % k for k in (1, 2)]
    + ["tom_start%d" % k for k in (1, 2, 3)]
    + ["hol_pre%d" % k for k in (1, 2)]
    + ["hol_post%d" % k for k in (1, 2)]
)
CHUNK = 512


def now_iso() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def cost_rate() -> float:
    return float(COST_X1_RATE) if COST_X1_RATE else COST_FALLBACK


# ------------------------------------------------------------- daily face
def daily_face(panel: dict) -> dict:
    """Equal-weight daily close-to-close return with E22's exclusions."""
    arr = panel["arrays"]
    close = arr["close"]
    open_ = arr["open"]
    high = arr["high"]
    low = arr["low"]
    n_day, n_sym = close.shape          # panel is (dates, symbols)
    cnt = np.zeros(n_day, dtype=np.int64)
    s1 = np.zeros(n_day, dtype=np.float64)
    skipped = {"bad_px": 0, "resume": 0, "one_price": 0, "extreme": 0}
    for a in range(0, n_sym, CHUNK):
        b = min(a + CHUNK, n_sym)
        c = np.asarray(close[:, a:b], dtype=np.float64)
        hi = np.asarray(high[:, a:b], dtype=np.float64)
        lo = np.asarray(low[:, a:b], dtype=np.float64)
        prev = np.empty_like(c)
        prev[0, :] = np.nan
        prev[1:, :] = c[:-1, :]
        with np.errstate(invalid="ignore", divide="ignore"):
            r = c / prev - 1.0
        ok = (np.isfinite(c) & np.isfinite(prev) & (c > 0) & (prev > 0)
              & np.isfinite(r))
        skipped["bad_px"] += int(np.count_nonzero(~ok))
        resume = ok & ~np.isfinite(prev)
        skipped["resume"] += int(np.count_nonzero(resume))
        one_price = ok & (np.abs(hi - lo) <= ONE_PRICE_TOL)
        skipped["one_price"] += int(np.count_nonzero(one_price))
        extreme = ok & (np.abs(r) >= MAX_ABS_R)
        skipped["extreme"] += int(np.count_nonzero(extreme))
        ok &= ~(one_price | extreme)
        r = np.where(ok, r, 0.0)
        cnt += np.count_nonzero(ok, axis=1)
        s1 += r.sum(axis=1)
    valid = cnt > 0
    d = np.where(valid, s1 / np.maximum(cnt, 1), np.nan)
    return {"dates": panel["dates"], "d": d, "valid": valid,
            "count": cnt, "skipped": skipped}


def horizon_matrix(d: np.ndarray, valid: np.ndarray, h: int):
    """Forward h-bar cumulative return + validity mask."""
    n = len(d)
    out = np.full(n, np.nan)
    ok = np.zeros(n, dtype=bool)
    if h <= 0 or n < h:
        return out, ok
    for t in range(0, n - h + 1):
        win = d[t:t + h]
        if valid[t:t + h].all():
            out[t] = float(np.sum(win))
            ok[t] = True
    return out, ok


def _moments(x: np.ndarray) -> dict:
    x = np.asarray(x, dtype=np.float64)
    n = int(x.size)
    if n <= 0:
        return {"n": 0}
    m = float(np.mean(x))
    if n > 1:
        var = float(np.var(x, ddof=1))
        se = math.sqrt(var / n)
    else:
        var, se = 0.0, float("nan")
    return {"n": n, "mean": m, "sd": math.sqrt(var), "se": se,
            "win": float(np.mean(x > 0)) if n else None}


def switch_count(flags: np.ndarray) -> int:
    """0 -> 1 transitions on the ordered trading-day grid."""
    if flags.size == 0:
        return 0
    prev = np.concatenate(([False], flags[:-1]))
    return int(np.count_nonzero(flags & ~prev))


def variant_table(face: dict, variants: dict, cost: float) -> dict:
    dates = face["dates"]
    d = face["d"]
    valid = face["valid"]
    years_span = max((dates[-1] - dates[0]).days / 365.25, 1e-9) if len(dates) else 1.0
    variant_sets = {}
    for name in VARIANT_ORDER:
        flags = np.array([name in variants.get(dt.date(), ()) for dt in dates],
                         dtype=bool)
        variant_sets[name] = flags
    rows = {}
    for h in HORIZONS:
        fwd, ok = horizon_matrix(d, valid, h)
        base = _moments(fwd[ok])
        for name in VARIANT_ORDER:
            sel = variant_sets[name] & ok
            if int(np.count_nonzero(sel)) < 2 or base.get("n", 0) < 2:
                rows["%s@h%d" % (name, h)] = {"variant": name, "h": h, "n": 0}
                continue
            v = _moments(fwd[sel])
            se = math.sqrt((v["se"] ** 2) + (base["se"] ** 2)) if v["se"] and base["se"] else float("nan")
            excess = v["mean"] - base["mean"]
            rows["%s@h%d" % (name, h)] = {
                "variant": name, "h": h, "n": v["n"], "n_days_face": base["n"],
                "variant_mean": v["mean"], "baseline_mean": base["mean"],
                "excess": excess, "t_naive": (excess / se) if se and math.isfinite(se) and se > 0 else None,
                "variant_win": v["win"],
                "excess_per_year": excess * v["n"] / years_span,
            }
    # horizon-1 economics per variant (spells + cost), and era/year split
    fwd1, ok1 = horizon_matrix(d, valid, 1)
    base1 = _moments(fwd1[ok1])
    per_variant = {}
    for name in VARIANT_ORDER:
        flags = variant_sets[name]
        sel = flags & ok1
        n_v = int(np.count_nonzero(sel))
        switches = switch_count(flags)
        m_excess = float(np.mean(fwd1[sel]) - base1["mean"]) if n_v else None
        gross = (m_excess * n_v / years_span) if n_v else 0.0
        annual_cost = switches * 2.0 * cost / years_span
        yrs = {}
        if n_v:
            for dt, val in zip(dates[sel], fwd1[sel]):
                yrs.setdefault(str(dt.year), []).append(float(val))
        per_year = {}
        base_by_year = {}
        for dt, val in zip(dates[ok1], fwd1[ok1]):
            base_by_year.setdefault(str(dt.year), []).append(float(val))
        for y, vals in yrs.items():
            b = base_by_year.get(y) or []
            if b:
                per_year[y] = float(np.mean(vals) - np.mean(b))
        eras = {}
        for y, ex in per_year.items():
            eras.setdefault(era_of(int(y)), []).append(ex)
        per_variant[name] = {
            "n": n_v, "switches": switches,
            "excess_h1": m_excess,
            "gross_annual": gross,
            "cost_annual": annual_cost,
            "net_annual": gross - annual_cost,
            "cost_positive": bool(gross - annual_cost > 0),
            "years_above_baseline": sum(1 for v in per_year.values() if v > 0),
            "years_total": len(per_year),
            "by_year": {k: per_year[k] for k in sorted(per_year)},
            "by_era": {k: float(np.mean(v)) for k, v in sorted(eras.items())},
            "decay_slope_per_year": _slope(per_year),
        }
    return {"horizon_table": rows, "per_variant": per_variant,
            "baseline_h1": base1, "years_span": years_span,
            "cells": len(VARIANT_ORDER) * len(HORIZONS)}


def _slope(per_year: dict) -> float | None:
    if len(per_year) < 3:
        return None
    xs = np.array([float(k) for k in sorted(per_year)], dtype=np.float64)
    ys = np.array([per_year[k] for k in sorted(per_year)], dtype=np.float64)
    xm, ym = xs.mean(), ys.mean()
    den = float(np.sum((xs - xm) ** 2))
    if den <= 0:
        return None
    return float(np.sum((xs - xm) * (ys - ym)) / den)


# ------------------------------------------------------------------ driver
def census(panel_dir: str = PANEL_DIR) -> dict:
    panel = load_panel(panel_dir)
    dates = panel["dates"]
    cal = [dt.date() for dt in dates]
    variants, breaks = annotate_calendar(cal)
    face = daily_face(panel)
    cost = cost_rate()
    table = variant_table(face, variants, cost)
    cutoff = dates[-1].strftime("%Y-%m-%d")
    face_meta = {
        "panel": os.path.relpath(panel_dir, _ROOT).replace("\\", "/"),
        "symbols": int(len(panel["symbols"])),
        "dates": int(len(dates)),
        "start": dates[0].strftime("%Y-%m-%d"),
        "cutoff": cutoff,
        "cutoff_expected": CUTOFF_EXPECTED,
        "holiday_breaks": len(breaks),
        "stock_days_used": int(np.sum(face["count"])),
        "days_usable": int(np.count_nonzero(face["valid"])),
        "skipped": face["skipped"],
        "cost_per_side": cost,
        "exclusions": "E22 lineage: bad px / suspension-resume / one-price / |r|>=75%",
    }
    return {
        "batch": "seasonal-horizon-stability",
        "series": "E23",
        "generated": now_iso(),
        "evidence_cutoff": cutoff,
        "scope": "descriptive census; zero prereg / zero judged / zero pool write",
        "face": face_meta,
        "variants": VARIANT_ORDER,
        "horizons": list(HORIZONS),
        "cells": table["cells"],
        "baseline_h1": table["baseline_h1"],
        "years_span": table["years_span"],
        "horizon_table": table["horizon_table"],
        "per_variant": table["per_variant"],
    }


def _r8(obj):
    if isinstance(obj, float):
        if obj != obj or obj in (float("inf"), float("-inf")):
            return None
        return round(obj, 8)
    if isinstance(obj, dict):
        return {k: _r8(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_r8(v) for v in obj]
    return obj


def write_outputs(face: dict, out_dir: str = OUT_DIR) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    payload = _r8(face)
    stem = "CENSUS-%s" % face["evidence_cutoff"]
    js = os.path.join(out_dir, stem + ".json")
    with open(js, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    shutil.copyfile(js, os.path.join(out_dir, "latest.json"))
    csv = os.path.join(out_dir, "by_horizon.csv")
    lines = ["variant,h,n,variant_mean,baseline_mean,excess,t_naive,excess_per_year"]
    for key in sorted(payload["horizon_table"]):
        row = payload["horizon_table"][key]
        if not row.get("n"):
            lines.append("%s,%s,0,,,,," % (row.get("variant"), row.get("h")))
            continue
        lines.append("%s,%d,%d,%s,%s,%s,%s,%s" % (
            row["variant"], row["h"], row["n"],
            _fmt(row.get("variant_mean")), _fmt(row.get("baseline_mean")),
            _fmt(row.get("excess")), _fmt(row.get("t_naive")),
            _fmt(row.get("excess_per_year"))))
    with open(csv, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines) + "\n")
    return {"json": js, "csv": csv}


def _fmt(v) -> str:
    return "" if v is None else ("%.6f" % v)


# --------------------------------------------------------------- selftest
def _toy_panel(tmp: str) -> str:
    """8 trading days spanning a month boundary, 3 symbols, known returns."""
    dates = pd.to_datetime(["2020-01-29", "2020-01-30", "2020-01-31",
                            "2020-02-03", "2020-02-04", "2020-02-05",
                            "2020-02-06", "2020-02-07"])
    # close paths: symbol A +1% per day, B +0%, C written with a one-price bar
    n_day = len(dates)
    close = np.zeros((n_day, 3))
    base = 10.0
    for t in range(n_day):
        close[t, 0] = base * (1.01 ** t)
        close[t, 1] = base
        close[t, 2] = base * (1.0 + 0.002 * t)
    close[3, 2] = close[2, 2]          # one-price bar on day 3 (column C)
    open_ = close.copy()
    high = close * 1.005                    # ordinary bars are not one-price
    low = close * 0.995
    high[3, 2] = low[3, 2] = close[3, 2]    # day 3 on C: one-price bar
    open_[3, 2] = close[3, 2]
    os.makedirs(tmp, exist_ok=True)
    np.save(os.path.join(tmp, "dates.npy"),
            dates.values.astype("datetime64[ns]").astype("int64"))
    for name, arr in (("open", open_), ("high", high), ("low", low),
                      ("close", close)):
        np.save(os.path.join(tmp, name + ".npy"), arr.astype("float32"))
    with open(os.path.join(tmp, "symbols.json"), "w", encoding="utf-8") as fh:
        json.dump(["000001", "000002", "000003"], fh)
    with open(os.path.join(tmp, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump({"symbols": 3, "dates": n_day}, fh)
    return tmp


def selftest() -> int:
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1. switch counting
    leg("switch_count basic", switch_count(np.array([0, 1, 1, 0, 1], dtype=bool)) == 2)
    leg("switch_count empty", switch_count(np.zeros(0, dtype=bool)) == 0)

    # 2. moments
    m = _moments(np.array([0.01, -0.01, 0.02]))
    leg("moments mean", abs(m["mean"] - 0.0066666667) < 1e-9)
    leg("moments n", m["n"] == 3)
    leg("moments win", abs(m["win"] - 2.0 / 3.0) < 1e-12)

    # 3. horizon matrix + tail validity
    d = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    valid = np.array([True, True, True, False, True])
    fwd, ok = horizon_matrix(d, valid, 2)
    leg("horizon t0 sums", ok[0] and abs(fwd[0] - 0.03) < 1e-12)
    leg("horizon t2 blocked by invalid", not ok[2])
    leg("horizon tail blocked", not ok[4])

    # 4. slope sign
    leg("decay slope negative", (_slope({"2018": 0.002, "2019": 0.001,
                                         "2020": 0.0}) or 0) < 0)

    # 5. panel face on toy data: one-price bar excluded, mean computed
    tmp = tempfile.mkdtemp(prefix="shs_selftest_")
    try:
        _toy_panel(tmp)
        panel = load_panel(tmp)
        face = daily_face(panel)
        leg("toy dates", len(face["dates"]) == 8)
        leg("toy one-price skipped", face["skipped"]["one_price"] >= 1)
        leg("toy day1 invalid", not face["valid"][0])
        # day 1 (index 1): A +1.0%, B +0%, C +0.2% -> mean 0.4%
        leg("toy daily mean", abs(face["d"][1] - 0.004) < 2e-6)
        # day 3 has the one-price bar on C -> A +1%, B 0% -> mean 0.5%
        leg("toy exclusion mean", abs(face["d"][3] - 0.005) < 2e-6)
        cal = [dt.date() for dt in face["dates"]]
        variants, breaks = annotate_calendar(cal)
        leg("toy month boundary variants",
            "tom_end1" in variants[cal[2]] and "tom_start1" in variants[cal[3]])
        table = variant_table(face, variants, 0.0013041)
        leg("toy cells", table["cells"] == len(VARIANT_ORDER) * len(HORIZONS))
        row = table["per_variant"]["tom_start1"]
        leg("toy tom_start1 n", row["n"] >= 1)
        leg("toy cost arithmetic",
            row["switches"] >= 1 and row["net_annual"] <= row["gross_annual"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 6. rounding helper nulls NaN
    leg("round nulls nan", _r8({"a": float("nan")})["a"] is None)

    bad = [n for n, ok_ in legs if not ok_]
    for n, ok_ in legs:
        print(("PASS " if ok_ else "FAIL ") + n)
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: seasonal_horizon_stability.py [run|selftest]")
        return 2
    face = census()
    paths = write_outputs(face)
    print("CENSUS %s cells=%d cutoff=%s" % (face["series"], face["cells"],
                                            face["evidence_cutoff"]))
    print("json=%s" % os.path.relpath(paths["json"], _ROOT))
    pv = face["per_variant"]
    for name in VARIANT_ORDER:
        row = pv[name]
        print("%-12s n=%4d excess_h1=%+8.2fbp net=%+7.2f%%/yr years_above=%d/%d"
              % (name, row["n"],
                 (row["excess_h1"] or 0.0) * 1e4,
                 (row["net_annual"] or 0.0) * 100,
                 row["years_above_baseline"], row["years_total"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))