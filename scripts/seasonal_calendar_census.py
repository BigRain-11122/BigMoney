"""SEASONAL-CALENDAR CENSUS (descriptive probe)

Question this batch answers (one line): on the local A-share daily panel, do
the classic domestic calendar windows (turn-of-month "month-end / month-start",
long-holiday pre/post, month-of-year, day-of-week) carry a return differential
against the unconditional close-to-close baseline -- and is that differential
large enough to survive the round-trip cost of a timing overlay?

Consumer plan (TRIAL_LABOR_LAW sec.4 meaning gate -- named consumers):
  (1) seasonal family supply line: the trial-labor standing agenda needs its
      next-wave grammar; this census is the cheap screen that must exist
      before any seasonal entry-mask family can be drafted (same role the
      E21 leg-3 conditioned overnight census played for W21);
  (2) marking/monitoring timing for the paper lanes (P4 DCA, grid marking,
      daily_report context): calendar windows are the plainest possible
      "why does this week look different" reference;
  (3) the CEO research-orientation law (O-20260928-1522) asks for domestic
      folk judgments to be formalized as numeric faces before they are
      believed -- "month-end / holiday effect" is exactly such a folk claim.

Scope discipline: ZERO prereg, ZERO judged face, ZERO pool write, ZERO
network, ZERO engine touch, ZERO cost-model claim. L1 deterministic; rerun
byte-identical. Runs off the local numpy build of the T-87 forward panel
(data/cache/p1c_local, r1056 lineage) so the whole census stays a fast L1
pass instead of a pooled multi-minute burn.

Measurement rules (frozen here, descriptive only):
  * panel = data/cache/p1c_local/{open,high,low,close}.npy + dates.npy +
    symbols.json (local build of data/astock_daily/per, cutoff 2026-10-19).
  * return under test = close(T)/close(T-1) - 1 (close-to-close, qfq).
  * the return earned on day T is attributed to the calendar variants that
    day T belongs to (a day may belong to several families at once).
  * exclusions (overnight-census lineage, frozen): non-positive prices,
    suspension-resume transitions (the symbol's previous grid row is empty),
    one-price bars (open==high==low==close), and |r|>=75% adjustment
    artifacts.
  * baseline = every usable stock-day (unconditional pooled mean). Variant
    excess = variant mean - baseline mean; the t on the excess uses the
    independence-ignorant standard error sqrt(se_v^2 + se_base^2) and is
    disclosed as such (windows overlap in time).
  * era split uses lu_prem_census.era_of (single source); year stability
    counts years whose variant mean beat that same year's baseline.
  * 23 variants are enumerated (6 turn-of-month + 4 holiday + 12 month +
    5 day-of-week). This is an uncorrected descriptive scan: no multiplicity
    correction is applied and none should be read into the output.
  * economic arithmetic is reported ONLY for the turn-of-month and holiday
    families (they are what a timing overlay would trade); the month and
    weekday rows are conditioning labels, not executable switches.

usage:
    python scripts/seasonal_calendar_census.py run        # full census
    python scripts/seasonal_calendar_census.py selftest   # hermetic legs
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from lu_prem_census import board_of, era_of          # single-source lineage

try:                                                  # cost single source
    from ce_transfer import COST_X1_RATE
except Exception:                                     # pragma: no cover
    COST_X1_RATE = None

TZ = timezone(timedelta(hours=8))
PANEL_DIR = os.path.join(_ROOT, "data", "cache", "p1c_local")
OUT_DIR = os.path.join(_ROOT, "results", "seasonal_calendar_census")
CUTOFF_EXPECTED = "2026-10-19"
CSV_PANEL_DIR = os.path.join(_ROOT, "data", "astock_daily", "per")
CAL_SOURCES = ("600000.csv", "000001.csv")
# a break of >=4 calendar days between consecutive trading days is a holiday
# (weekend-only gaps are at most 3 days: Fri -> Mon)
HOLIDAY_GAP_DAYS = 4
TOM_DEPTH = 3
HOLIDAY_DEPTH = 2
DOW_NAMES = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
CHUNK = 512
ONE_PRICE_TOL = 1e-12
MAX_ABS_R = 0.75

VARIANT_ORDER = (
    ["tom_end%d" % k for k in range(1, TOM_DEPTH + 1)]
    + ["tom_start%d" % k for k in range(1, TOM_DEPTH + 1)]
    + ["hol_pre%d" % k for k in range(1, HOLIDAY_DEPTH + 1)]
    + ["hol_post%d" % k for k in range(1, HOLIDAY_DEPTH + 1)]
    + ["m%02d" % m for m in range(1, 13)]
    + ["dow_%s" % d for d in DOW_NAMES[:5]]
)
FAMILY_OF = {}
for _v in VARIANT_ORDER:
    if _v.startswith("tom_"):
        FAMILY_OF[_v] = "turn_of_month"
    elif _v.startswith("hol_"):
        FAMILY_OF[_v] = "holiday"
    elif _v.startswith("m"):
        FAMILY_OF[_v] = "month_of_year"
    else:
        FAMILY_OF[_v] = "day_of_week"
BOARDS = ("main", "chinext", "star", "other")


def now_iso() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


# ---------------------------------------------------------------- calendar
def annotate_calendar(cal) -> tuple[dict, list]:
    """Map each trading day -> set of calendar variants; also return the
    holiday-break list (pre/post windows are placed around each break)."""
    variants: dict = {d: set() for d in cal}
    by_month: dict = {}
    for d in cal:
        by_month.setdefault((d.year, d.month), []).append(d)
    for _, days in by_month.items():
        n = len(days)
        for pos, d in enumerate(days):
            end_left = n - 1 - pos                     # 0 == last day
            if end_left < TOM_DEPTH:
                variants[d].add("tom_end%d" % (end_left + 1))
            if pos < TOM_DEPTH:
                variants[d].add("tom_start%d" % (pos + 1))
    for d in cal:
        variants[d].add("m%02d" % d.month)
        if d.weekday() < 5:
            variants[d].add("dow_%s" % DOW_NAMES[d.weekday()])
    breaks = []
    for i in range(1, len(cal)):
        gap = (cal[i] - cal[i - 1]).days
        if gap >= HOLIDAY_GAP_DAYS:
            breaks.append({"before": cal[i - 1].strftime("%Y-%m-%d"),
                           "after": cal[i].strftime("%Y-%m-%d"),
                           "gap_days": gap})
            for k in range(1, HOLIDAY_DEPTH + 1):
                j = i - k
                if j >= 0:
                    variants[cal[j]].add("hol_pre%d" % k)
                j = i + k - 1
                if j < len(cal):
                    variants[cal[j]].add("hol_post%d" % k)
    return variants, breaks


# ------------------------------------------------------------------ panel
def load_panel(panel_dir: str = PANEL_DIR) -> dict:
    def _p(name):
        return os.path.join(panel_dir, name)

    with open(_p("meta.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    with open(_p("symbols.json"), encoding="utf-8") as fh:
        symbols = json.load(fh)
    raw = np.load(_p("dates.npy"))
    if np.issubdtype(raw.dtype, np.datetime64):
        dates = pd.to_datetime(raw)
    else:
        # the panel stores integer epochs; the unit has drifted across
        # pandas versions, so infer it from the magnitude and disclose
        ints = raw.astype("int64")
        mag = float(np.nanmedian(np.abs(ints)))
        unit = ("ns" if mag > 1e17 else "us" if mag > 1e14
                else "ms" if mag > 1e11 else "s")
        dates = pd.to_datetime(ints, unit=unit)
    arrays = {k: np.load(_p(k + ".npy"), mmap_mode="r")
              for k in ("open", "high", "low", "close")}
    return {"meta": meta, "symbols": symbols,
            "dates": pd.DatetimeIndex(dates), "arrays": arrays}


def _blank() -> dict:
    return {"n": 0.0, "sum": 0.0, "sum2": 0.0, "win": 0.0}


def _stats(b: dict) -> dict:
    n = int(b["n"])
    if n <= 0:
        return {"n": 0}
    m = b["sum"] / n
    v = max(b["sum2"] / n - m * m, 0.0)
    se = math.sqrt(v / n) if n > 1 else float("nan")
    return {"n": n, "mean": m, "sd": math.sqrt(v),
            "se": se, "t_own": (m / se) if se else None,
            "win": b["win"] / n}


def scan_panel(panel: dict, variants: dict, date_index: dict) -> dict:
    """Vectorized per-day accumulation, then variant attribution."""
    dates = panel["dates"]
    arr = panel["arrays"]
    n_days = len(dates)
    symbols = panel["symbols"]
    per_day = {k: np.zeros(n_days) for k in ("n", "s1", "s2", "win")}
    per_board = {b: {k: np.zeros(n_days) for k in ("n", "s1", "s2", "win")}
                 for b in BOARDS}
    meta = {"files": len(symbols), "bars": 0, "obs": 0, "bad_px": 0,
            "resume_skipped": 0, "one_price_skipped": 0,
            "extreme_skipped": 0, "priced_cells": 0}
    board_of_sym = [board_of(s) for s in symbols]
    for start in range(0, len(symbols), CHUNK):
        sl = slice(start, min(start + CHUNK, len(symbols)))
        o = np.asarray(arr["open"][:, sl], dtype=np.float64)
        h = np.asarray(arr["high"][:, sl], dtype=np.float64)
        lo = np.asarray(arr["low"][:, sl], dtype=np.float64)
        c = np.asarray(arr["close"][:, sl], dtype=np.float64)
        prev_c = np.vstack([np.full((1, c.shape[1]), np.nan), c[:-1]])
        with np.errstate(invalid="ignore", divide="ignore"):
            r = c / prev_c - 1.0
        meta["bars"] += int(np.count_nonzero(np.isfinite(c)))
        finite_ok = (np.isfinite(c) & np.isfinite(prev_c) & (c > 0)
                     & (prev_c > 0) & np.isfinite(o) & (o > 0))
        meta["bad_px"] += int(np.count_nonzero(
            np.isfinite(c) & np.isfinite(prev_c) & ~finite_ok))
        # resume transition: the symbol has a price today but no previous
        # price -> its "return" spans an unknown gap
        meta["resume_skipped"] += int(np.count_nonzero(
            np.isfinite(c) & ~np.isfinite(prev_c)))
        one_price = (np.abs(o - c) <= ONE_PRICE_TOL) & \
                    (np.abs(h - lo) <= ONE_PRICE_TOL)
        meta["one_price_skipped"] += int(np.count_nonzero(finite_ok & one_price))
        extreme = np.abs(r) >= MAX_ABS_R
        meta["extreme_skipped"] += int(np.count_nonzero(finite_ok & extreme))
        valid = finite_ok & ~one_price & ~extreme & np.isfinite(r)
        rr = np.where(valid, r, 0.0)
        per_day["n"] += valid.sum(axis=1)
        per_day["s1"] += rr.sum(axis=1)
        per_day["s2"] += (rr * rr).sum(axis=1)
        per_day["win"] += ((r > 0) & valid).sum(axis=1)
        for b in BOARDS:
            idx = [i for i, bb in enumerate(board_of_sym[sl])
                   if bb == b]
            if not idx:
                continue
            sub_v = valid[:, idx]
            sub_r = rr[:, idx]
            per_board[b]["n"] += sub_v.sum(axis=1)
            per_board[b]["s1"] += sub_r.sum(axis=1)
            per_board[b]["s2"] += (sub_r * sub_r).sum(axis=1)
            per_board[b]["win"] += ((r[:, idx] > 0) & sub_v).sum(axis=1)
    meta["grid_cells"] = int(n_days * len(symbols))
    meta["obs"] = int(per_day["n"].sum())

    # ---- variant attribution (day-level masks -> 23 x n_days matrix)
    M = np.zeros((len(VARIANT_ORDER), n_days), dtype=np.float64)
    for t, d in enumerate(dates):
        for v in variants.get(d, ()):
            M[VARIANT_ORDER.index(v), t] = 1.0
    agg = {"all": None, "by_variant": {}, "by_variant_era": {},
           "by_variant_year": {}, "by_year": {}, "by_board": {},
           "by_variant_board": {}}
    agg["all"] = {"n": per_day["n"].sum(), "sum": per_day["s1"].sum(),
                  "sum2": per_day["s2"].sum(), "win": per_day["win"].sum()}
    years = np.array([d.year for d in dates])
    eras = np.array([era_of(int(y)) for y in years])
    for vi, v in enumerate(VARIANT_ORDER):
        mask = M[vi]
        agg["by_variant"][v] = {
            "n": float((per_day["n"] * mask).sum()),
            "sum": float((per_day["s1"] * mask).sum()),
            "sum2": float((per_day["s2"] * mask).sum()),
            "win": float((per_day["win"] * mask).sum())}
        for era in set(eras.tolist()):
            em = mask * (eras == era)
            n = float((per_day["n"] * em).sum())
            if n <= 0:
                continue
            agg["by_variant_era"][(v, era)] = {
                "n": n, "sum": float((per_day["s1"] * em).sum()),
                "sum2": float((per_day["s2"] * em).sum()),
                "win": float((per_day["win"] * em).sum())}
        for b in BOARDS:
            bm = mask * 1.0
            n = float((per_board[b]["n"] * bm).sum())
            if n <= 0:
                continue
            agg["by_variant_board"][(v, b)] = {
                "n": n, "sum": float((per_board[b]["s1"] * bm).sum()),
                "sum2": float((per_board[b]["s2"] * bm).sum()),
                "win": float((per_board[b]["win"] * bm).sum())}
    for yr in sorted(set(years.tolist())):
        ym = (years == yr).astype(np.float64)
        agg["by_year"][int(yr)] = {
            "n": float((per_day["n"] * ym).sum()),
            "sum": float((per_day["s1"] * ym).sum()),
            "sum2": float((per_day["s2"] * ym).sum()),
            "win": float((per_day["win"] * ym).sum())}
        for vi, v in enumerate(VARIANT_ORDER):
            vm = M[vi] * ym
            n = float((per_day["n"] * vm).sum())
            if n <= 0:
                continue
            agg["by_variant_year"][(v, int(yr))] = {
                "n": n, "sum": float((per_day["s1"] * vm).sum()),
                "sum2": float((per_day["s2"] * vm).sum()),
                "win": float((per_day["win"] * vm).sum())}
    for b in BOARDS:
        agg["by_board"][b] = {
            "n": float(per_board[b]["n"].sum()),
            "sum": float(per_board[b]["s1"].sum()),
            "sum2": float(per_board[b]["s2"].sum()),
            "win": float(per_board[b]["win"].sum())}
    return {"agg": agg, "meta": meta}


def census(panel_dir: str = PANEL_DIR) -> dict:
    panel = load_panel(panel_dir)
    cal = [d.to_pydatetime() for d in panel["dates"]]
    variants, breaks = annotate_calendar(cal)
    variants_by_ts = {pd.Timestamp(d): v for d, v in variants.items()}
    scanned = scan_panel(panel, variants_by_ts,
                         {d: i for i, d in enumerate(cal)})
    meta = scanned["meta"]
    meta.update({
        "calendar_days": len(cal),
        "calendar_first": cal[0].strftime("%Y-%m-%d") if cal else None,
        "calendar_last": cal[-1].strftime("%Y-%m-%d") if cal else None,
        "holiday_breaks": len(breaks),
        "panel_cutoff": panel["meta"].get("cutoff"),
        "panel_start": panel["meta"].get("start"),
        "panel_shape": panel["meta"].get("shape"),
        "panel_source": panel["meta"].get("source"),
    })
    return {"ts": now_iso(), "probe": "seasonal_calendar_census",
            "panel_dir": os.path.relpath(panel_dir, _ROOT).replace("\\", "/"),
            "meta": meta, "agg": scanned["agg"], "breaks": breaks}


# --------------------------------------------------------------- economics
EVENTS_PER_YEAR = {"turn_of_month": 12.0, "holiday": 3.5}
WINDOW_BARS = {"turn_of_month": 1.0, "holiday": 1.0}


def _economics(variant: str, excess_per_bar, n_years: float) -> dict:
    fam = FAMILY_OF[variant]
    if fam not in EVENTS_PER_YEAR or excess_per_bar is None or not n_years:
        return {"applicable": False}
    events = EVENTS_PER_YEAR[fam]
    gross = excess_per_bar * WINDOW_BARS[fam] * events
    if COST_X1_RATE is None:
        return {"applicable": True, "gross_excess_per_year": gross,
                "round_trip_cost": None, "net_excess_per_year": None,
                "note": "cost single source unavailable -- gross only"}
    rt_cost = 2.0 * COST_X1_RATE
    net = gross - events * rt_cost
    return {"applicable": True,
            "events_per_year": events,
            "gross_excess_per_year": gross,
            "round_trip_cost_per_event": rt_cost,
            "annual_cost": events * rt_cost,
            "net_excess_per_year": net,
            "verdict": "COST_POSITIVE" if net > 0 else "COST_NEGATIVE"}


def build_face(raw: dict) -> dict:
    agg, meta = raw["agg"], raw["meta"]
    base = _stats(agg["all"])
    years = sorted(agg["by_year"].keys())
    variants = {}
    for v in VARIANT_ORDER:
        st = _stats(agg["by_variant"][v])
        if not st.get("n"):
            variants[v] = st
            continue
        ex = st["mean"] - base["mean"]
        se_ex = math.sqrt((st["se"] or 0.0) ** 2 + (base["se"] or 0.0) ** 2)
        era_means = {era: _stats(b)["mean"]
                     for (vv, era), b in sorted(agg["by_variant_era"].items())
                     if vv == v and b["n"] > 0}
        above = below = 0
        for yr in years:
            vb = agg["by_variant_year"].get((v, yr))
            yb = agg["by_year"].get(yr)
            if not vb or vb["n"] < 5 or not yb or yb["n"] < 5:
                continue
            if vb["sum"] / vb["n"] > yb["sum"] / yb["n"]:
                above += 1
            else:
                below += 1
        variants[v] = {
            "family": FAMILY_OF[v],
            "n": st["n"],
            "mean": st["mean"],
            "excess_vs_baseline": ex,
            "excess_t_ignoring_overlap": (ex / se_ex) if se_ex else None,
            "win_rate": st["win"],
            "by_era": era_means,
            "by_board": {b: _stats(bb)["mean"]
                         for (vv, b), bb in sorted(
                             agg["by_variant_board"].items())
                         if vv == v and bb["n"] > 0},
            "years_above_baseline": above,
            "years_below_baseline": below,
            "economics": _economics(v, ex, len(years)),
        }
    return {
        "ts": raw["ts"],
        "probe": raw["probe"],
        "law_ref": "TRIAL_LABOR_LAW sec.2 cheap-census-first (descriptive; "
                   "no prereg, no judged face, no pool write)",
        "evidence_cutoff": str(meta.get("calendar_last") or ""),
        "universe": {
            "panel": raw["panel_dir"],
            "panel_cutoff": meta.get("panel_cutoff"),
            "panel_start": meta.get("panel_start"),
            "panel_shape": meta.get("panel_shape"),
            "panel_source": meta.get("panel_source"),
            "symbols": meta["files"],
            "priced_cells": meta["bars"],
            "calendar_days": meta["calendar_days"],
            "calendar_first": meta["calendar_first"],
            "calendar_last": meta["calendar_last"],
            "holiday_breaks": meta["holiday_breaks"],
        },
        "coverage": {
            "obs_used": meta["obs"],
            "priced_cells": meta["bars"],
            "grid_cells": meta.get("grid_cells"),
            "resume_skipped": meta["resume_skipped"],
            "one_price_skipped": meta["one_price_skipped"],
            "extreme_skipped": meta["extreme_skipped"],
            "bad_px": meta["bad_px"],
            "usable_share_of_priced": (meta["obs"] / meta["bars"])
            if meta["bars"] else None,
        },
        "definition": {
            "r": "close(T)/close(T-1) - 1 (qfq, close-to-close)",
            "baseline": "every usable stock-day (pooled, equal weight)",
            "excess": "variant mean - baseline mean",
            "t_on_excess": "independence-ignorant sqrt(se_v^2 + se_base^2); "
                           "windows overlap in time -- disclosed, not corrected",
            "variants": len(VARIANT_ORDER),
        },
        "baseline": base,
        "variants": variants,
        "by_year": {str(k): _stats(v) for k, v in sorted(agg["by_year"].items())},
        "by_board": {k: _stats(v) for k, v in sorted(agg["by_board"].items())},
        "holiday_breaks": raw["breaks"][:400],
        "disclosures": [
            "panel = local numpy build of the T-87 forward panel "
            "(data/cache/p1c_local, cutoff 2026-10-19); qfq close-to-close "
            "returns absorb cash-dividend adjustments (sidecars cash-only "
            "per r1067; raw close not reconstructable)",
            "suspension-resume transitions excluded (empty previous grid row)",
            "one-price bars excluded (limit boards are unexecutable and would "
            "concentrate into the calendar windows non-randomly)",
            "23 enumerated variants, zero multiplicity correction -- this is a "
            "descriptive scan, not a judged face and not a claim",
            "windows overlap in time (a day can be month-end + pre-holiday + "
            "Monday at once); variant counts therefore do not sum to the panel",
            "economic arithmetic is reported for turn-of-month and holiday "
            "families only; month/weekday rows are conditioning labels",
            "holiday breaks are derived from the trading calendar itself "
            "(gap >= 4 calendar days), not from an announcement table",
            "t values are inflated by cross-sectional correlation: the "
            "observation count is stock-days, not independent draws, so read "
            "the t as a ranking aid and the win-rate / year-stability columns "
            "as the honest strength signal (effective t is far smaller)",
            "the panel is the local rebuild, so this face is not byte-"
            "comparable with the r1074/r1076 CSV-panel censuses (same source "
            "family, different assembly)",
        ],
    }


def _round(obj, nd=8):
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        return round(v, nd) if math.isfinite(v) else None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, dict):
        return {str(k): _round(v, nd) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_round(v, nd) for v in obj]
    return obj


def write_outputs(face: dict, out_dir: str = OUT_DIR) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    fpath = os.path.join(out_dir, "CENSUS-%s.json" % face["evidence_cutoff"])
    body = json.dumps(_round(face), ensure_ascii=False, indent=1,
                      sort_keys=True)
    with open(fpath, "w", encoding="utf-8") as fh:
        fh.write(body)
    with open(os.path.join(out_dir, "latest.json"), "w",
              encoding="utf-8") as fh:
        fh.write(body)
    csv = os.path.join(out_dir, "by_variant.csv")
    with open(csv, "w", encoding="utf-8", newline="") as fh:
        fh.write("variant,family,n,mean,excess,t_ignoring_overlap,win_rate,"
                 "years_above,years_below,econ_net_per_year\n")
        for v in VARIANT_ORDER:
            s = face["variants"].get(v) or {}
            if not s.get("n"):
                fh.write("%s,%s,0,,,,,,,\n" % (v, FAMILY_OF[v]))
                continue
            econ = s.get("economics") or {}
            fh.write("%s,%s,%d,%.8f,%.8f,%s,%.4f,%d,%d,%s\n" % (
                v, s["family"], s["n"], s["mean"], s["excess_vs_baseline"],
                "" if s.get("excess_t_ignoring_overlap") is None
                else "%.3f" % s["excess_t_ignoring_overlap"],
                s["win_rate"], s["years_above_baseline"],
                s["years_below_baseline"],
                "" if econ.get("net_excess_per_year") is None
                else "%.6f" % econ["net_excess_per_year"]))
    return {"face": fpath, "by_variant": csv}


# --------------------------------------------------------------- selftest
def _write_panel(tmp: str, dates, symbols, ohlc: dict) -> str:
    pdir = os.path.join(tmp, "panel")
    os.makedirs(pdir, exist_ok=True)
    idx = ((pd.to_datetime(dates) - pd.Timestamp("1970-01-01"))
           // pd.Timedelta("1us")).astype("int64")
    np.save(os.path.join(pdir, "dates.npy"), idx)
    with open(os.path.join(pdir, "symbols.json"), "w", encoding="utf-8") as fh:
        json.dump(symbols, fh)
    shape = (len(dates), len(symbols))
    for k in ("open", "high", "low", "close"):
        np.save(os.path.join(pdir, k + ".npy"),
                np.asarray(ohlc[k], dtype=np.float32).reshape(shape))
    with open(os.path.join(pdir, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump({"shape": list(shape), "n_symbols": len(symbols),
                   "cutoff": str(pd.Timestamp(dates[-1]).date()),
                   "start": str(pd.Timestamp(dates[0]).date()),
                   "source": "synthetic"}, fh)
    return pdir


def selftest() -> int:
    tmp = tempfile.mkdtemp(prefix="scc_selftest_")
    legs: list = []
    try:
        days = ["2020-01-20", "2020-01-21", "2020-01-22",
                "2020-02-03", "2020-02-04", "2020-02-05", "2020-02-06",
                "2020-02-07",
                "2020-03-02", "2020-03-03"]
        cal = pd.to_datetime(days).tolist()
        variants, breaks = annotate_calendar(cal)
        d = [pd.Timestamp(x) for x in days]
        legs.append(("L1 calendar day count 10", len(cal) == 10))
        legs.append(("L2 two holiday breaks (12d and 24d gaps)",
                     len(breaks) == 2
                     and [b["gap_days"] for b in breaks] == [12, 24]))
        legs.append(("L3 tom_end1 = last trading day of each month",
                     {str(x.date()) for x in d
                      if "tom_end1" in variants[x]} ==
                     {"2020-01-22", "2020-02-07", "2020-03-03"}))
        legs.append(("L4 tom_start1 = first trading day of each month",
                     {str(x.date()) for x in d
                      if "tom_start1" in variants[x]} ==
                     {"2020-01-20", "2020-02-03", "2020-03-02"}))
        legs.append(("L5 hol_pre1 = last day before each break, hol_post1 = "
                     "first after",
                     sorted(str(x.date()) for x in d
                            if "hol_pre1" in variants[x]) ==
                     ["2020-01-22", "2020-02-07"]
                     and sorted(str(x.date()) for x in d
                                if "hol_post1" in variants[x]) ==
                     ["2020-02-03", "2020-03-02"]))
        legs.append(("L6 dow/month mapping: 2020-01-20 Monday, 02-03 February",
                     "dow_mon" in variants[d[0]] and "m01" in variants[d[0]]
                     and "m02" in variants[d[3]]))
        # synthetic panel: 600000 carries prices, 000001 mirrors the grid,
        # 688001 is suspended on one grid row (empty cells)
        nan = np.nan
        close = [
            [10.0, 20.0, 30.0],
            [10.2, 20.0, 30.0],
            [10.2, 20.2, 30.3],          # month-end
            [10.3, 20.2, 30.3],          # post-holiday / month-start
            [10.3, 20.3, 30.6],          # one-price row for 600000
            [10.4, 20.4, 30.9],
            [10.5, 20.4, 31.2],
            [10.5, 20.4, 31.5],          # month-end
            [10.6, 20.5, 31.8],          # month-start
            [10.7, 20.5, 32.1],
        ]
        open_ = [
            [10.0, 20.0, 30.0],
            [10.0, 20.0, 30.0],
            [10.2, 20.0, 30.0],
            [10.2, 20.1, 30.0],
            [10.3, 20.2, 30.3],          # one-price
            [10.3, 20.3, 30.4],
            [10.4, 20.3, 30.6],
            [10.4, 20.3, 30.9],
            [10.4, 20.4, 31.2],
            [10.5, 20.4, 31.5],
        ]
        high = [[v + 0.1 for v in row] for row in close]
        low = [[v - 0.1 for v in row] for row in close]
        # make the one-price row truly one-price on 600000
        high[4][0] = low[4][0] = close[4][0]
        # suspension: 688001 has no price on 2020-01-21
        close[1][2] = nan
        open_[1][2] = nan
        high[1][2] = nan
        low[1][2] = nan
        pdir = _write_panel(tmp, days, ["600000", "000001", "688001"],
                            {"open": open_, "high": high, "low": low,
                             "close": close})
        raw = census(panel_dir=pdir)
        face = build_face(raw)
        cov = face["coverage"]
        legs.append(("L7 panel_load + calendar 10 days",
                     face["universe"]["calendar_days"] == 10))
        legs.append(("L8 exactly one one-price bar excluded",
                     cov["one_price_skipped"] == 1))
        legs.append(("L9 resume transitions excluded (3 first rows + 1 resume)",
                     cov["resume_skipped"] == 4))
        # usable obs: grid has 10 rows; row 0 unusable for all three
        # symbols, 688001 loses its resume row, 600000 loses one-price
        legs.append(("L10 usable obs == 10*3 - 3(first row) - 1 - 1 = 25",
                     cov["obs_used"] == 24))
        # month-end bars with the frozen exclusions applied:
        #   01-22: 600000 0.0 ; 000001 +1.00% ; 688001 resume -> dropped
        #   02-07: 600000 0.0 ; 000001 0.0 ; 688001 +0.9615%
        #   03-03: 600000 +0.9434% ; 000001 0.0 ; 688001 +0.9434%
        exp = (0.0 + (20.2 / 20.0 - 1.0)
               + 0.0 + 0.0 + (31.5 / 31.2 - 1.0)
               + (10.7 / 10.6 - 1.0) + 0.0 + (32.1 / 31.8 - 1.0)) / 8.0
        got = face["variants"]["tom_end1"]
        legs.append(("L11 tom_end1 mean exact on 8 usable month-end stock-days",
                     got["n"] == 8 and abs(got["mean"] - exp) < 1e-6))
        legs.append(("L12 baseline n == usable obs",
                     face["baseline"]["n"] == cov["obs_used"]))
        f2 = _round(build_face(census(panel_dir=pdir)))
        f1 = _round(face)
        f1.pop("ts")
        f2.pop("ts")
        legs.append(("L13 deterministic rerun", f1 == f2))
        out = write_outputs(face, out_dir=os.path.join(tmp, "out"))
        legs.append(("L14 artifacts written",
                     all(os.path.exists(p) for p in out.values())))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = 0
    for name, passed in legs:
        print(("PASS " if passed else "FAIL ") + name)
        ok += 1 if passed else 0
    print("selftest: %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ------------------------------------------------------------------- main
def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: seasonal_calendar_census.py [run|selftest]")
        return 2
    if not os.path.isdir(PANEL_DIR):
        print("FAIL panel dir absent: %s" % PANEL_DIR)
        return 2
    raw = census()
    face = build_face(raw)
    paths = write_outputs(face)
    base = face["baseline"]
    cov = face["coverage"]
    print("panel symbols=%d bars=%d obs=%d (usable %.2f%%) breaks=%d"
          % (face["universe"]["symbols"], face["universe"]["priced_cells"],
             cov["obs_used"], 100.0 * (cov["usable_share_of_priced"] or 0.0),
             face["universe"]["holiday_breaks"]))
    print("baseline mean=%.6f/bar (win %.4f)" % (base["mean"], base["win"]))
    for v in VARIANT_ORDER:
        s = face["variants"].get(v) or {}
        if not s.get("n"):
            continue
        econ = s.get("economics") or {}
        print("%-12s n=%8d excess=%+.6f t=%6s win=%.4f yrs=%d/%d net/yr=%s"
              % (v, s["n"], s["excess_vs_baseline"],
                 "n/a" if s["excess_t_ignoring_overlap"] is None
                 else "%.2f" % s["excess_t_ignoring_overlap"],
                 s["win_rate"], s["years_above_baseline"],
                 s["years_above_baseline"] + s["years_below_baseline"],
                 "n/a" if econ.get("net_excess_per_year") is None
                 else "%.4f" % econ["net_excess_per_year"]))
    print("cutoff=%s -> %s" % (face["evidence_cutoff"], paths["face"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))