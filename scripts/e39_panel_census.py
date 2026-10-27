"""E39 panel census (descriptive; NO judgment, NO prereg).

Three read-only legs over ``data/daily``, all deterministic and offline:

  stale  -- the coverage face counts 1,723 of 1,725 panels as current and
            cannot say whether the last two are dead listings or refresh
            failures. Decide it from the rows on disk.
  mtime  -- the 2026-10-17/10-21 refresh wave moved the whole panel. Size it:
            how many files were rewritten, how many bars arrived, and which
            days did the writing.
  ladder -- every wide-book spread in E34/E36/E37/E38 is quoted "vs ladder5",
            yet the denominator has only ever been ann/vol/Sharpe. Describe it
            properly: drawdown, worst month, cash-leg share. The curve comes
            from importing the E24/E27 engine, never a re-implementation.

Every face is descriptive: no gate, no verdict on a strategy, no prereg, no
trial count consumed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

DAILY = os.path.join(ROOT, "data", "daily")
BULK_IMPORT_DATE = "2026-09-22"   # the one-off full-panel pull, see E30 coverage face
REFRESH_WAVE_DATE = "2026-10-17"  # first mtime of the 2026-10-21 refresh pass


def read_bars(path):
    """-> list of {date, close, volume, amount} with numeric coercion."""
    out = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            d = (row.get("date") or "").strip()
            if not d:
                continue
            def num(key):
                try:
                    return float((row.get(key) or "").strip())
                except ValueError:
                    return None
            out.append({"date": d, "close": num("close"),
                        "volume": num("volume"), "amount": num("amount")})
    out.sort(key=lambda r: r["date"])
    return out


def panel_files():
    return sorted(f for f in os.listdir(DAILY) if f.lower().endswith(".csv"))


def panel_calendar():
    import e24_ladder_weighting as base
    return base.load_panel()[0]


def _quant(seq, q):
    if not seq:
        return None
    s = sorted(seq)
    k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]


# ---------------------------------------------------------------- leg: stale

def classify_stale(name, bars, cal, cutoff):
    """Mechanical criteria, applied to rows on disk only.

    PINNED_SLOT_COPY  -- the file carries a '_tag' suffix and its rows sit
                         inside another live panel's date range: a frozen
                         snapshot, not a universe member.
    SOURCE_SIDE_GAP   -- last bar predates the 2026-09-22 bulk import and the
                         last bars still carried normal turnover, so the source
                         never had those rows to import: a listing that stopped
                         printing, not a refresh that failed.
    REFRESH_FAILURE   -- last bar is the bulk-import date itself with normal
                         turnover: the in-chain updater skipped it afterwards.
    """
    if not bars:
        return {"class": "EMPTY_FILE", "why": "no parseable rows"}
    last = bars[-1]["date"]
    tail = bars[-20:]
    vols = [b["volume"] for b in tail if b["volume"] is not None]
    tail_vol_med = _quant(vols, 0.5)
    amts = [b["amount"] for b in tail if b["amount"] is not None]
    tail_amt_med = _quant(amts, 0.5)
    missing = [d for d in cal if d > last] if cal else []
    stem = os.path.splitext(name)[0]
    tagged = "_" in stem
    normal_turnover = bool(tail_vol_med and tail_vol_med > 0)
    if tagged:
        cls, why = "PINNED_SLOT_COPY", "filename carries a '_tag' slot suffix"
    elif last == BULK_IMPORT_DATE and normal_turnover:
        cls, why = "REFRESH_FAILURE", "stopped exactly at the bulk-import date"
    elif last < BULK_IMPORT_DATE and normal_turnover:
        cls, why = "SOURCE_SIDE_GAP", "last bars still traded, so the source never offered rows after it"
    elif not normal_turnover:
        cls, why = "DEAD_LISTING", "tail turnover is zero (no trades printed)"
    else:
        cls, why = "UNCLASSIFIED", "no criterion matched"
    return {
        "class": cls, "why": why, "rows": len(bars),
        "first_bar": bars[0]["date"], "last_bar": last,
        "calendar_days_missing_after_last_bar": len(missing),
        "tail20_volume_median": tail_vol_med, "tail20_amount_median": tail_amt_med,
        "tail5": [{"date": b["date"], "close": b["close"], "volume": b["volume"]} for b in bars[-5:]],
        "last_bar_vs_cutoff_days": (
            (datetime.fromisoformat(cutoff) - datetime.fromisoformat(last)).days if cutoff else None),
    }


def run_stale(outdir):
    cal = panel_calendar()
    cutoff = cal[-1]
    rows = []
    for f in panel_files():
        bars = read_bars(os.path.join(DAILY, f))
        if not bars:
            continue
        last = bars[-1]["date"]
        lag = len([d for d in cal if d > last])
        if lag < 1:
            continue  # on the panel cutoff: current, not a stale-panel question
        rows.append((f, bars, lag))
    faces = []
    for f, bars, lag in rows:
        rec = {"file": f, "bars_behind_calendar": lag}
        rec.update(classify_stale(f, bars, cal, cutoff))
        faces.append(rec)

    # cross-check: is a tagged copy actually a duplicate of a live panel?
    dup = None
    for rec in faces:
        if rec["class"] != "PINNED_SLOT_COPY":
            continue
        stem = os.path.splitext(rec["file"])[0]
        for live in panel_files():
            ls = os.path.splitext(live)[0]
            if ls == stem.split("_")[0] or ls == "sh" + stem.split("_")[0]:
                a = read_bars(os.path.join(DAILY, live))
                b = read_bars(os.path.join(DAILY, rec["file"]))
                am = {r["date"]: r["close"] for r in a}
                bm = {r["date"]: r["close"] for r in b}
                common = set(am) & set(bm)
                same = sum(1 for d in common if am[d] == bm[d])
                dup = {"live_panel": live, "common_dates": len(common),
                       "identical_closes": same,
                       "live_last_bar": a[-1]["date"] if a else None,
                       "copy_last_bar": b[-1]["date"] if b else None}
                break
        if dup:
            break

    face = {
        "study": "e39_stale_two_census",
        "evidence_cutoff": cutoff,
        "calendar_bars": len(cal),
        "thresholds": {"stale_if_bars_behind_calendar": ">=1 (strictly behind the panel cutoff)",
                       "bulk_import_date": BULK_IMPORT_DATE},
        "panel_files": len(panel_files()),
        "stale_panels": len(faces),
        "findings": faces,
        "pinned_copy_crosscheck": dup,
        "denominator_advice": [
            "PINNED_SLOT_COPY is not a universe member: drop it from any coverage denominator.",
            "SOURCE_SIDE_GAP is a listing that stopped printing: keep it in the universe file, "
            "but never count it as a refresh obligation.",
            "REFRESH_FAILURE is the only class that is our own defect.",
        ],
        "honest": [
            "classification reads rows on disk only; no vendor metadata, no listing notices",
            "a SOURCE_SIDE_GAP verdict is an inference from turnover, not a confirmed delisting",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }
    return face


# ---------------------------------------------------------------- leg: mtime

def run_mtime(outdir):
    files = panel_files()
    pockets = []
    day_hist = {}
    rows_total = 0
    bytes_total = 0
    advanced = unchanged = behind = 0
    reached_cutoff = None
    for f in files:
        p = os.path.join(DAILY, f)
        st = os.stat(p)
        bars = read_bars(p)
        if not bars:
            continue
        last = bars[-1]["date"]
        reached_cutoff = last if reached_cutoff is None or last > reached_cutoff else reached_cutoff
        rows_after_bulk = len([b for b in bars if b["date"] > BULK_IMPORT_DATE])
        mday = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d")
        day_hist[mday] = day_hist.get(mday, 0) + 1
        rows_total += len(bars)
        bytes_total += st.st_size
        if last > BULK_IMPORT_DATE:
            advanced += 1
        elif last == BULK_IMPORT_DATE:
            unchanged += 1
        else:
            behind += 1
        pockets.append({
            "file": f, "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            "bytes": st.st_size, "rows": len(bars), "last_bar": last,
            "rows_after_bulk_import": rows_after_bulk,
        })
    touched = [p for p in pockets if p["mtime"][:10] >= REFRESH_WAVE_DATE]
    face = {
        "study": "e39_panel_mtime_census",
        "evidence_cutoff": reached_cutoff,
        "panel_files": len(pockets),
        "bulk_import_date": BULK_IMPORT_DATE,
        "refresh_wave_since": REFRESH_WAVE_DATE,
        "totals": {
            "rows": rows_total, "bytes": bytes_total,
            "files_advanced_past_bulk": advanced,
            "files_stopped_at_bulk": unchanged,
            "files_behind_bulk": behind,
        },
        "refresh_wave": {
            "files_touched": len(touched),
            "rows_after_bulk_import_carried": sum(p["rows_after_bulk_import"] for p in touched),
            "bytes_rewritten": sum(p["bytes"] for p in touched),
            "mtime_day_histogram": dict(sorted(day_hist.items())),
            "first_mtime": min((p["mtime"] for p in touched), default=None),
            "last_mtime": max((p["mtime"] for p in touched), default=None),
        },
        "largest_carriers": sorted(touched, key=lambda p: -p["rows_after_bulk_import"])[:10],
        "honest": [
            "mtime is a disk fact, not a provenance record: a rewrite that changed no row is invisible here",
            "rows_after_bulk_import counts bars dated after the bulk pull, so it is the bar payload of the wave",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }
    return face, pockets


# --------------------------------------------------------------- leg: ladder

def _month_ends(curve):
    out = []
    for d, v in curve:
        if out and out[-1][0][:7] == d[:7]:
            out[-1] = (d, v)
        else:
            out.append((d, v))
    return out


def risk_profile(curve, years):
    vals = [v for _, v in curve]
    peak = vals[0]
    peak_date = curve[0][0]
    max_dd = 0.0
    max_dd_span = None
    worst_dd_start = curve[0][0]
    for d, v in curve:
        if v > peak:
            peak, peak_date = v, d
        dd = v / peak - 1.0
        if dd < max_dd:
            max_dd = dd
            max_dd_span = (peak_date, d)
            worst_dd_start = peak_date
    # longest underwater run in sessions
    longest = cur = 0
    peak = vals[0]
    for _, v in curve:
        if v >= peak:
            peak = v
            cur = 0
        else:
            cur += 1
            longest = max(longest, cur)
    me = _month_ends(curve)
    mrets = [(me[k][0][:7], me[k][1] / me[k - 1][1] - 1.0) for k in range(1, len(me))]
    worst = min(mrets, key=lambda r: r[1]) if mrets else None
    best = max(mrets, key=lambda r: r[1]) if mrets else None
    neg = len([r for r in mrets if r[1] < 0])
    return {
        "years": round(years, 2),
        "ann_return_pct": round((vals[-1] / vals[0]) ** (1.0 / years) * 100 - 100, 2) if years else None,
        "max_drawdown_pct": round(max_dd * 100, 2),
        "max_drawdown_span": list(max_dd_span) if max_dd_span else None,
        "longest_underwater_sessions": longest,
        "worst_month": {"month": worst[0], "return_pct": round(worst[1] * 100, 2)} if worst else None,
        "best_month": {"month": best[0], "return_pct": round(best[1] * 100, 2)} if best else None,
        "months": len(mrets),
        "negative_months": neg,
        "monthly_win_rate_pct": round((len(mrets) - neg) / len(mrets) * 100, 1) if mrets else None,
    }


def run_ladder(outdir, starts=("2020-01-01", "2018-01-01")):
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw = e27.load_universe()
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    faces = {}
    for start in starts:
        cal = [d for d in cal_full if d >= start]
        years = len(cal) / 252.0
        prices = {}
        for s in base.LADDER:
            c = raw.get(s, ({}, {}))[0] if s in raw else {}
            if not c:
                c = base.load_panel(s)[1].get(s, {})
            prices[s] = [c.get(d) for d in cal]
        cash = base.load_cash_series(cal)
        curve, aux, holdings = e27.simulate(cal, prices, {}, base.LADDER, cash, None, 1.0, {})
        m = base.metrics(curve, years)
        prof = risk_profile(curve, years)
        # cash-leg share: bars where at least one ladder member had no close
        gaps = [d for k, d in enumerate(cal[1:]) if any(prices[s][k + 1] is None for s in base.LADDER)]
        cash_map = cash["series"] if cash else {}
        cash_rates = [cash_map[d] for d in cal if d in cash_map]
        prof.update({
            "start": start, "bars": len(cal),
            "metrics_engine": m,
            "turnover_per_year": aux["turnover_total"] / years if years else None,
            "cost_per_year_bp": aux["cost_paid_frac"] / years * 1e4 if years else None,
            "cash_leg": {
                "bars_with_a_missing_member": len(gaps),
                "missing_member_bars": {
                    s: sum(1 for k, d in enumerate(cal) if prices[s][k] is None)
                    for s in base.LADDER},
                "cash_leg_share_pct": round(len(gaps) / max(1, len(cal) - 1) * 100, 2),
                "mean_daily_cash_return_bp": round(sum(cash_rates) / len(cash_rates) * 1e4, 4) if cash_rates else None,
                "mean_annual_cash_rate_pct": round(sum(cash_rates) / len(cash_rates) * 252 * 100, 2) if cash_rates else None,
            },
            "last_holdings": holdings,
        })
        faces[start] = prof
    return {
        "study": "e39_ladder_risk_profile",
        "evidence_cutoff": cutoff,
        "baseline": base.LADDER,
        "cost_bp_per_side": base.COST_BP_SIDE,
        "windows": faces,
        "honest": [
            "the curve is the E24/E27 engine's own curve (module import), not a re-implementation",
            "drawdown is measured on the daily equity curve; months are month-end marks",
            "cash-leg share is the fraction of bars with a missing ladder member price, "
            "not a discretionary cash position",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ------------------------------------------------------- leg: month attribution

def run_month(outdir, month):
    """Attribute one calendar month of the ladder from rows only.

    Decomposes the equal-weight month into per-member contributions and flags
    data anomalies (zero-volume days, single-bar jumps the panel cannot
    explain) so a bad month can be read as a market move or as a panel defect.
    """
    import e24_ladder_weighting as base

    cal = base.load_panel()[0]
    days = [d for d in cal if d.startswith(month)]
    if not days:
        return None
    prev = [d for d in cal if d < month]
    start_day = prev[-1] if prev else days[0]
    members = {}
    for s in base.LADDER:
        p = os.path.join(DAILY, s + ".csv")
        bars = read_bars(p) if os.path.exists(p) else []
        by = {b["date"]: b for b in bars}
        first = by.get(start_day) or by.get(days[0])
        last = by.get(days[-1])
        if not first or not last or not first["close"] or not last["close"]:
            members[s] = {"status": "MISSING_ROW"}
            continue
        r = last["close"] / first["close"] - 1.0
        window = [by[d] for d in days if d in by]
        jumps = []
        for k in range(1, len(window)):
            a, b = window[k - 1]["close"], window[k]["close"]
            if a and b and abs(b / a - 1.0) > 0.10:
                jumps.append({"date": window[k]["date"], "ret_pct": round((b / a - 1) * 100, 2)})
        members[s] = {
            "status": "OK",
            "month_return_pct": round(r * 100, 2),
            "bars": len(window),
            "missing_bars": len(days) - len(window),
            "zero_volume_days": len([w for w in window if not w["volume"]]),
            "first_close": first["close"], "last_close": last["close"],
            "single_bar_jumps_over_10pct": jumps,
        }
    live = {s: v for s, v in members.items() if v.get("status") == "OK"}
    eq = (sum(v["month_return_pct"] for v in live.values()) / len(live)) if live else None
    return {
        "study": "e39_month_attribution",
        "evidence_cutoff": days[-1],
        "month": month,
        "entry_mark": start_day,
        "bars_in_month": len(days),
        "members": members,
        "equal_weight_month_return_pct": round(eq, 2) if eq is not None else None,
        "anomaly_flags": sorted(
            {"%s:zero_volume" % s for s, v in live.items() if v["zero_volume_days"]}
            | {"%s:jump" % s for s, v in live.items() if v["single_bar_jumps_over_10pct"]}
            | {"%s:missing_bars" % s for s, v in live.items() if v["missing_bars"]}),
        "honest": [
            "equal weight at entry mark, no rebalance inside the month: a contribution view, not the engine curve",
            "anomaly flags are mechanical (zero volume, >10% single-bar moves), not proof of a data defect",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ----------------------------------------------------- leg: pair drawdown path

def run_pair(outdir, starts=("2020-01-01", "2018-01-01"), pick_n=9999,
             exclude=("sh511",)):
    """Read the E34-E38 wide-book spread on the drawdown path, not on its mean.

    Same calendar, same cost, same spec, one shared rank cache: ladder5 and the
    wide book (top-N of the eligible universe) are simulated side by side and
    then profiled by the identical function, so max drawdown, underwater run
    and worst month are comparable line for line. A third profile is taken on
    the ratio of the two equity curves -- the spread itself, which every
    vs-ladder number quotes but never measures.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    wide_name = "wide_top%d" % pick_n
    windows = {}
    for start in starts:
        cal = [d for d in cal_full if d >= start]
        years = len(cal) / 252.0
        all_syms = sorted(set(base.LADDER) | set(raw_all))
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = raw_all.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms if s in raw_all]
        cash = base.load_cash_series(cal)
        rank_cache = {}
        curves = {}
        for name, univ, n in (("ladder5", base.LADDER, None),
                              (wide_name, universe, pick_n)):
            curve, _aux, _hold = e27.simulate(cal, prices, amounts, univ, cash,
                                              n, 1.0, rank_cache)
            curves[name] = curve
        lad = curves["ladder5"]
        lmap = dict(lad)
        ratio = [(d, v / lmap[d]) for d, v in curves[wide_name]
                 if d in lmap and lmap[d] > 0]
        prof = {k: risk_profile(c, years) for k, c in
                (("ladder5", lad), (wide_name, curves[wide_name]),
                 ("spread_ratio", ratio))}
        prof["ladder5"]["engine_metrics"] = base.metrics(lad, years)
        prof[wide_name]["engine_metrics"] = base.metrics(curves[wide_name], years)
        answers = {
            "ann_spread_pct": round(prof[wide_name]["ann_return_pct"]
                                    - prof["ladder5"]["ann_return_pct"], 2),
            "maxdd_delta_pct": round(prof[wide_name]["max_drawdown_pct"]
                                     - prof["ladder5"]["max_drawdown_pct"], 2),
            "underwater_delta_sessions": (
                prof[wide_name]["longest_underwater_sessions"]
                - prof["ladder5"]["longest_underwater_sessions"]),
            "worst_month_same_month": (
                (prof[wide_name]["worst_month"] or {}).get("month")
                == (prof["ladder5"]["worst_month"] or {}).get("month")),
            "spread_maxdd_pct": prof["spread_ratio"]["max_drawdown_pct"],
            "spread_longest_underwater_sessions":
                prof["spread_ratio"]["longest_underwater_sessions"],
            "spread_worst_month": prof["spread_ratio"]["worst_month"],
        }
        windows[start] = {"bars": len(cal), "years": round(years, 2),
                          "profiles": prof, "answers": answers}
    return {
        "study": "e40_pair_drawdown",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_mult": 1.0, "cost_bp_per_side": base.COST_BP_SIDE,
                 "starts": list(starts)},
        "windows": windows,
        "honest": [
            "both curves come from the E24/E27 engine (module import), one calendar, one rank cache",
            "spread_ratio is a ratio of equity curves, not a tradable sleeve: it prices the "
            "vs-ladder claim, it does not add a portfolio",
            "drawdown is measured on daily equity; months are month-end marks",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ------------------------------------------------------- leg: cash-leg drag

def _scale_cash(cash, mult):
    """Scale a load_cash_series payload's daily returns. None stays None (0%)."""
    if cash is None or not mult:
        return None if cash is None else {"series": {}}
    return {"series": {d: r * mult for d, r in cash["series"].items()}}


def run_cashdrag(outdir, starts=("2020-01-01",), pick_n=9999, exclude=("sh511",),
                 rate_mults=(0.0, 1.0, 3.0)):
    """How much of the ladder/wide verdict is the repo leg actually paying for?

    The engine accrues cash only on the un-invested weight: it is 1.0 before the
    first monthly decision and (1 - sum(weights)) afterwards, which is zero for
    an equal-weight book that rebalanced into a non-empty live set. So this leg
    re-runs the identical spec at repo multipliers 0x / 1x / 3x and reads the
    annualised column, which bounds the cash leg's contribution to the verdict
    instead of asserting it.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    wide_name = "wide_top%d" % pick_n
    windows = {}
    for start in starts:
        cal = [d for d in cal_full if d >= start]
        years = len(cal) / 252.0
        all_syms = sorted(set(base.LADDER) | set(raw_all))
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = raw_all.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms if s in raw_all]
        cash_panel = base.load_cash_series(cal)
        rebal = base.month_end_indices(cal)
        # The cash weight is the un-invested weight, and the first rebalance that
        # actually trades is NOT the first month end: eligibility needs a burn-in,
        # so empty live sets keep the book in repo for far longer. Measure it.
        first_trade_idx = None
        for ri in rebal:
            if any(base.elig(prices[s], ri) for s in base.LADDER):
                first_trade_idx = ri
                break
        cash_bars = (first_trade_idx + 1) if first_trade_idx is not None else len(cal) - 1
        rank_cache = {}
        table = {}
        for name, univ, n in (("ladder5", base.LADDER, None),
                              (wide_name, universe, pick_n)):
            rows = {}
            for k in rate_mults:
                cash = _scale_cash(cash_panel, k)
                curve, aux, holdings = e27.simulate(
                    cal, prices, amounts, univ, cash, n, 1.0, rank_cache)
                prof = risk_profile(curve, years)
                m = base.metrics(curve, years)
                rows["x%g" % k] = {
                    "ann_return_pct": prof["ann_return_pct"],
                    "ann_vs_x0_bp": None,  # filled below
                    "vol_pct": m.get("ann_vol_pct"),
                    "sharpe": m.get("sharpe"),
                    "max_drawdown_pct": prof["max_drawdown_pct"],
                    "cost_per_year_bp": (aux["cost_paid_frac"] / years * 1e4
                                         if years else None),
                    "curve_first": curve[0][1],
                    "curve_last": curve[-1][1],
                }
            zero = rows.get("x0", {}).get("ann_return_pct")
            for key, row in rows.items():
                if zero is not None and row["ann_return_pct"] is not None:
                    row["ann_vs_x0_bp"] = round((row["ann_return_pct"] - zero) * 100, 2)
            table[name] = rows
        cash_map = (cash_panel or {}).get("series", {})
        rates = [cash_map[d] for d in cal if d in cash_map]
        windows[start] = {
            "bars": len(cal),
            "years": round(years, 2),
            "schemes": table,
            "cash_mechanism": {
                "first_rebalance_index": rebal[0] if rebal else None,
                "first_trading_rebalance_index": first_trade_idx,
                "first_invested_bar": (cal[first_trade_idx + 1]
                                       if first_trade_idx is not None else None),
                "cash_bars": cash_bars,
                "cash_bar_share_pct": round(cash_bars / max(1, len(cal) - 1) * 100, 2),
                "rebalance_decisions": len(rebal),
                "panel_covered_days": (cash_panel or {}).get("covered_days"),
                "panel_ffilled_days": (cash_panel or {}).get("ffilled_days"),
                "panel_first": (cash_panel or {}).get("first"),
                "panel_last": (cash_panel or {}).get("last"),
                "mean_daily_cash_bp": round(sum(rates) / len(rates) * 1e4, 4) if rates else None,
                "mean_annual_cash_rate_pct": (round(sum(rates) / len(rates) * 252 * 100, 2)
                                              if rates else None),
                "cash_is_discretionary": False,
                "why": ("the engine holds cash only for the un-invested weight: 1.0 until the first "
                        "rebalance whose live set is non-empty (eligibility needs a burn-in, "
                        "so that is far later than the first month end), then 0.0 after an "
                        "equal-weight rebalance, because the weight is taken over the live "
                        "names only"),
            },
            "answers": {
                "ladder_cash_attributable_bp": table["ladder5"].get("x1", {}).get("ann_vs_x0_bp"),
                "wide_cash_attributable_bp": table[wide_name].get("x1", {}).get("ann_vs_x0_bp"),
                "ladder_x3_delta_bp": table["ladder5"].get("x3", {}).get("ann_vs_x0_bp"),
                "wide_x3_delta_bp": table[wide_name].get("x3", {}).get("ann_vs_x0_bp"),
                "maxdd_moves_with_cash": {
                    name: round((table[name].get("x1", {}).get("max_drawdown_pct") or 0)
                                - (table[name].get("x0", {}).get("max_drawdown_pct") or 0), 2)
                    for name in table},
            },
        }
    return {
        "study": "e40_cashleg_drag",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "rate_mults": list(rate_mults), "starts": list(starts),
                 "cost_bp_per_side": base.COST_BP_SIDE},
        "windows": windows,
        "honest": [
            "the repo leg is not a discretionary allocation: it is the un-invested weight of "
            "the same engine, so 'cash drag' here means the accrual rate on dead weight",
            "x0 reproduces the historical zero-cash convention (cash=None -> 0.0 daily return)",
            "a multiplier is a counterfactual rate, not a rate that ever existed",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ------------------------------------------------------- leg: size tilt (E40)

TILT_LARGE = ("sh510300", "sh510050")
TILT_SMALL = ("sh510500", "sh512100", "sh588000")
# four-member reach-back skin: sh588000 has no bars before 2020-11-13, so the
# five-member tilt cannot be measured on pre-2021 months (E43-TILT-4MEMBER-HISTORY)
TILT4_SMALL = ("sh510500", "sh512100")


def _tilt_series(mem, brk, months, large, small):
    """Monthly (small_mean - large_mean) on the months both legs can be priced.

    Returns (used_months, {month: tilt}, dropped) where a dropped month is one
    whose legs are missing a member or carry a >20% single-day corporate action
    on a member's own rows. Shared by the five-member and four-member skins so
    the two faces cannot drift apart.
    """
    used, tilt, dropped = [], {}, []
    for m in months:
        lg = [mem[s][m] for s in large if m in mem[s] and m not in brk[s]]
        sm = [mem[s][m] for s in small if m in mem[s] and m not in brk[s]]
        if not lg or not sm:
            dropped.append({
                "month": m,
                "members_with_break": [s for s in list(large) + list(small) if m in brk[s]],
                "members_missing": [s for s in list(large) + list(small) if m not in mem[s]],
            })
            continue
        used.append(m)
        tilt[m] = sum(sm) / len(sm) - sum(lg) / len(lg)
    return used, tilt, dropped


def _compose_counts(live, large, small):
    """Weight shares of one equal-weight book by the ladder's own size legs."""
    n = len(live)
    if not n:
        return {"n": 0}
    ns = sum(1 for s in live if s in small)
    nl = sum(1 for s in live if s in large)
    return {
        "n": n,
        "ladder_small_names": ns,
        "ladder_large_names": nl,
        "ladder_small_weight_pct": round(ns / n * 100, 4),
        "ladder_large_weight_pct": round(nl / n * 100, 4),
        "other_weight_pct": round((n - ns - nl) / n * 100, 4),
    }


def _month_rets(curve):
    """[(YYYY-MM, return)] from month-end marks of an equity curve."""
    me = _month_ends(curve)
    return [(me[k][0][:7], me[k][1] / me[k - 1][1] - 1.0) for k in range(1, len(me))]


def _member_monthly(cal, sym, raw):
    """{YYYY-MM: return} for one member, from its own month-end closes."""
    c = raw.get(sym, ({}, {}))[0] if sym in raw else {}
    if not c:
        c = {}
    marks = []
    for i, d in enumerate(cal):
        if i == len(cal) - 1 or cal[i + 1][:7] != d[:7]:
            marks.append((d[:7], c.get(d)))
    out = {}
    for k in range(1, len(marks)):
        prev, cur = marks[k - 1][1], marks[k][1]
        if prev and cur and prev > 0:
            out[marks[k][0]] = cur / prev - 1.0
    return out


def _moments(xs):
    n = len(xs)
    if n < 2:
        return {"n": n, "mean": (xs[0] if xs else None), "sd": None}
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return {"n": n, "mean": m, "sd": var ** 0.5}


def _member_break_months(cal, sym, raw, thresh=0.20):
    """{YYYY-MM} where the member's own rows carry a >thresh single-day jump.

    The panel is as-traded: a share split / unit conversion shows up as a one-day
    scale change (e.g. sh510500 2015-04-15 +248.6%, sh512100 2022-09-05 +176.3%).
    Those months are not a size move, so they are excluded from the spread and
    disclosed instead of being silently averaged in.
    """
    c = raw.get(sym, ({}, {}))[0] if sym in raw else {}
    out = set()
    prev = None
    for d in cal:
        v = c.get(d)
        if v and prev and prev > 0 and abs(v / prev - 1.0) > thresh:
            out.add(d[:7])
        if v:
            prev = v
    return out


def run_tilt(outdir, starts=("2020-01-01", "2018-01-01")):
    """Measure the ladder's size tilt, so a vs-ladder spread can be read net of it.

    The ladder is five equal weights across the size ladder, so it is not a
    neutral baseline: it carries 3/5 mid/small/STAR and 2/5 large-cap. This leg
    decomposes its monthly return into the size legs, measures the monthly
    large-vs-small spread as a series, and reports how much of the ladder's
    monthly variance that spread explains. The ladder curve itself is the
    E24/E27 engine's (module import), the members' monthly returns are marks
    from the panel rows.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw = e27.load_universe()
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    w_large = len(TILT_LARGE) / float(len(base.LADDER))
    w_small = len(TILT_SMALL) / float(len(base.LADDER))
    windows = {}
    for start in starts:
        cal = [d for d in cal_full if d >= start]
        years = len(cal) / 252.0
        prices = {}
        for s in base.LADDER:
            c = raw.get(s, ({}, {}))[0] if s in raw else {}
            if not c:
                c = base.load_panel(s)[1].get(s, {})
            prices[s] = [c.get(d) for d in cal]
        cash = base.load_cash_series(cal)
        curve, aux, _hold = e27.simulate(cal, prices, {}, base.LADDER, cash, None, 1.0, {})
        eng = dict(_month_rets(curve))
        mem = {s: _member_monthly(cal, s, raw) for s in base.LADDER}
        brk = {s: _member_break_months(cal, s, raw) for s in base.LADDER}
        months = sorted(m for m in eng if all(m in mem[s] for s in base.LADDER))
        used, dropped = [], []
        large_m, small_m = [], []
        for m in months:
            lg = [mem[s][m] for s in TILT_LARGE if m not in brk[s]]
            sm = [mem[s][m] for s in TILT_SMALL if m not in brk[s]]
            if lg and sm:
                used.append(m)
                large_m.append(sum(lg) / len(lg))
                small_m.append(sum(sm) / len(sm))
            else:
                dropped.append({"month": m,
                                "members_with_break": [s for s in base.LADDER if m in brk[s]]})
        months = used
        break_events = [{"member": s, "months": sorted(brk[s])}
                        for s in base.LADDER if brk[s]]
        tilt_m = [sm - lm for lm, sm in zip(large_m, small_m)]
        ladder_m = [w_large * lm + w_small * sm for lm, sm in zip(large_m, small_m)]
        eng_m = [eng[m] for m in months]
        recon = max((abs(a - b) for a, b in zip(eng_m, ladder_m)), default=None)
        tl = _moments(tilt_m)
        lv = _moments(eng_m)
        beta = None
        alpha = None
        r2 = None
        if tl["sd"] and lv["sd"] and len(months) > 2:
            cov = sum((t - tl["mean"]) * (l - lv["mean"])
                      for t, l in zip(tilt_m, eng_m)) / (len(months) - 1)
            beta = cov / (tl["sd"] ** 2)
            alpha = lv["mean"] - beta * tl["mean"]
            r2 = (cov ** 2) / (tl["sd"] ** 2 * lv["sd"] ** 2)
        worst_i = min(range(len(eng_m)), key=lambda i: eng_m[i]) if eng_m else None
        best_i = max(range(len(eng_m)), key=lambda i: eng_m[i]) if eng_m else None
        cum = 1.0
        for t in tilt_m:
            cum *= 1.0 + t
        windows[start] = {
            "bars": len(cal), "years": round(years, 2), "months": len(months),
            "size_weights": {"large": round(w_large, 4), "small": round(w_small, 4),
                             "large_legs": list(TILT_LARGE), "small_legs": list(TILT_SMALL)},
            "break_guard": {"single_day_threshold_pct": 20.0,
                            "member_break_events": break_events,
                            "excluded_months": dropped},
            "monthly": {
                "ladder_mean_pct": round(lv["mean"] * 100, 4) if lv["mean"] is not None else None,
                "ladder_sd_pct": round(lv["sd"] * 100, 4) if lv["sd"] is not None else None,
                "tilt_mean_bp": round(tl["mean"] * 1e4, 2) if tl["mean"] is not None else None,
                "tilt_sd_bp": round(tl["sd"] * 1e4, 2) if tl["sd"] is not None else None,
                "tilt_annualised_bp": round(tl["mean"] * 12 * 1e4, 2) if tl["mean"] is not None else None,
                "tilt_share_positive_pct": round(
                    sum(1 for t in tilt_m if t > 0) / len(tilt_m) * 100, 1) if tilt_m else None,
                "tilt_cumulative_pct": round((cum - 1.0) * 100, 2) if months else None,
                "tilt_best_month": ({"month": months[max(range(len(tilt_m)), key=lambda i: tilt_m[i])],
                                     "spread_pct": round(tilt_m[max(range(len(tilt_m)), key=lambda i: tilt_m[i])] * 100, 2)}
                                    if tilt_m else None),
                "tilt_worst_month": ({"month": months[min(range(len(tilt_m)), key=lambda i: tilt_m[i])],
                                      "spread_pct": round(tilt_m[min(range(len(tilt_m)), key=lambda i: tilt_m[i])] * 100, 2)}
                                     if tilt_m else None),
            },
            "exposure_regression": {
                "beta_ladder_on_tilt": round(beta, 3) if beta is not None else None,
                "alpha_monthly_bp": round(alpha * 1e4, 2) if alpha is not None else None,
                "r_squared": round(r2, 4) if r2 is not None else None,
                "tilt_explains_ladder_var_pct": round(r2 * 100, 2) if r2 is not None else None,
                "identity_reconciliation_max_abs_diff": (round(recon, 12)
                                                         if recon is not None else None),
                "reconciliation_note": ("largest gap between the engine's monthly curve and the "
                                        "marks-implied 0.4*large+0.6*small month; a non-zero gap is "
                                        "eligibility burn-in / rebalance-timing, not an identity "
                                        "failure"),
            },
            "worst_month_diagnostic": ({
                "month": months[worst_i],
                "ladder_pct": round(eng_m[worst_i] * 100, 2),
                "large_leg_pct": round(large_m[worst_i] * 100, 2),
                "small_leg_pct": round(small_m[worst_i] * 100, 2),
                "tilt_spread_pct": round(tilt_m[worst_i] * 100, 2),
                "members": {s: round(mem[s][months[worst_i]] * 100, 2) for s in base.LADDER},
            } if worst_i is not None else None),
            "best_month_diagnostic": ({
                "month": months[best_i],
                "ladder_pct": round(eng_m[best_i] * 100, 2),
                "tilt_spread_pct": round(tilt_m[best_i] * 100, 2),
            } if best_i is not None else None),
            "engine_metrics": base.metrics(curve, years),
            "turnover_per_year": aux["turnover_total"] / years if years else None,
        }
    return {
        "study": "e40_ladder_size_tilt",
        "evidence_cutoff": cutoff,
        "spec": {"ladder": base.LADDER, "large": list(TILT_LARGE), "small": list(TILT_SMALL),
                 "decomposition": "ladder_monthly = 0.4*large_mean + 0.6*small_mean",
                 "starts": list(starts), "cost_bp_per_side": base.COST_BP_SIDE},
        "windows": windows,
        "answers": {k: {
            "tilt_annualised_bp": v["monthly"]["tilt_annualised_bp"],
            "tilt_sd_bp": v["monthly"]["tilt_sd_bp"],
            "beta_ladder_on_tilt": v["exposure_regression"]["beta_ladder_on_tilt"],
            "tilt_explains_ladder_var_pct": v["exposure_regression"]["tilt_explains_ladder_var_pct"],
            "worst_month": v["worst_month_diagnostic"]["month"] if v["worst_month_diagnostic"] else None,
        } for k, v in windows.items()},
        "honest": [
            "the ladder curve is the E24/E27 engine's own (module import); members' monthly "
            "returns are month-end marks from panel rows, so the reconciliation row prices the gap",
            "large/small split is a naming choice (two broad-cap legs vs mid/small/STAR), not a "
            "factor-model exposure estimate",
            "the regression is descriptive: it says how much monthly variance moves with the "
            "spread, not that the spread causes anything",
            "corporate-action guard: a member month carrying a >20% single-day jump on its own "
            "rows is dropped from that month's leg mean (the panel is as-traded, so a share "
            "split or unit conversion reads as a 100%+ return)",
            "both start windows resolve to the same member months: the common-month set is "
            "bounded by sh588000's first bar, so the 2018 window adds engine months that carry "
            "no member marks and cannot enter the spread",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ------------------------------------------------ leg: rebalance-day shift

def _shift_indices(idxs, k, n):
    """Shift rebalance indices by k sessions, clamped into [0, n-1], deduped."""
    return sorted({min(max(i + k, 0), n - 1) for i in idxs})


def _mid_month_indices(cal, day=15):
    """First trading index of each month whose day-of-month is >= day."""
    out, seen = [], set()
    for i, d in enumerate(cal):
        m = d[:7]
        if m in seen or int(d[8:10]) < day:
            continue
        seen.add(m)
        out.append(i)
    return out


def run_rebalday(outdir, starts=("2020-01-01", "2018-01-01"), pick_n=9999,
                 exclude=("sh511",), mid_day=15):
    """Does the verdict survive moving the decision calendar by one session?

    Every number in E34-E40 rests on one decision calendar: month-end. This leg
    re-runs the identical spec (same universe, same rank cache, same cost) on
    month-end-1 / month-end / month-end+1 and on a mid-month date, for the
    ladder and the wide book alike, so a day-of-month artefact cannot hide
    inside a quoted spread. The engine's own semantics apply: it reads the
    rebalance set as "the close of index (i-1) is the decision", so a shift of
    k sessions moves decision and trade together.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    wide_name = "wide_top%d" % pick_n
    windows = {}
    for start in starts:
        cal = [d for d in cal_full if d >= start]
        years = len(cal) / 252.0
        all_syms = sorted(set(base.LADDER) | set(raw_all))
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = raw_all.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms if s in raw_all]
        cash = base.load_cash_series(cal)
        rank_cache = {}
        month_ends = base.month_end_indices(cal)
        variants = [
            ("me_m1", _shift_indices(month_ends, -1, len(cal))),
            ("me", sorted(set(month_ends))),
            ("me_p1", _shift_indices(month_ends, 1, len(cal))),
            ("mid%d" % mid_day, _mid_month_indices(cal, mid_day)),
        ]
        rows = {}
        for vname, idxs in variants:
            rebal = set(idxs)
            rows[vname] = {"rebalances": len(rebal)}
            for scheme, univ, n in (("ladder5", base.LADDER, None),
                                    (wide_name, universe, pick_n)):
                curve, aux, _hold = e27.simulate(cal, prices, amounts, univ, cash,
                                                 n, 1.0, rank_cache, rebal)
                prof = risk_profile(curve, years)
                rows[vname][scheme] = {
                    "ann_return_pct": prof["ann_return_pct"],
                    "max_drawdown_pct": prof["max_drawdown_pct"],
                    "monthly_win_rate_pct": prof["monthly_win_rate_pct"],
                    "rebalances": aux["rebalances"],
                    "turnover_per_year": round(aux["turnover_total"] / years, 3) if years else None,
                }
            rows[vname]["vs_ladder_spread_bp"] = round(
                (rows[vname][wide_name]["ann_return_pct"]
                 - rows[vname]["ladder5"]["ann_return_pct"]) * 100, 1)
        lad = [r["ladder5"]["ann_return_pct"] for r in rows.values()]
        wid = [r[wide_name]["ann_return_pct"] for r in rows.values()]
        spr = [r["vs_ladder_spread_bp"] for r in rows.values()]
        windows[start] = {
            "bars": len(cal), "years": round(years, 2),
            "variants": rows,
            "answers": {
                "ladder_ann_range_bp": round((max(lad) - min(lad)) * 100, 1),
                "wide_ann_range_bp": round((max(wid) - min(wid)) * 100, 1),
                "spread_range_bp": round(max(spr) - min(spr), 1),
                "spread_all_positive": all(x > 0 for x in spr),
                "spread_min_bp": min(spr), "spread_max_bp": max(spr),
                "spread_at_month_end_bp": rows["me"]["vs_ladder_spread_bp"],
                "universe_members": len(universe),
            },
        }
    return {
        "study": "e41_rebalance_day_sensitivity",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_mult": 1.0, "cost_bp_per_side": base.COST_BP_SIDE,
                 "starts": list(starts), "mid_month_day": mid_day,
                 "variants": ["me_m1", "me", "me_p1", "mid%d" % mid_day]},
        "windows": windows,
        "answers": {k: v["answers"] for k, v in windows.items()},
        "honest": [
            "the engine reads the rebalance set as a decision at the close of index (i-1), so a "
            "one-session shift moves decision and trade together; this leg does not test a "
            "decision-only shift",
            "all four variants share one calendar, one universe and one rank cache, so the only "
            "moving part is the set of decision sessions",
            "mid-month is a single fixed date (day %d), not a sweep: it prices a wrong-calendar "
            "cost, it does not search for a better one" % mid_day,
            "spread is the annualised column difference in bp, the same convention as E34-E40; "
            "the ratio curve's path is not re-measured here",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ---------------------------------------------------- leg: spread era decay

def _slice_curve(curve, lo, hi):
    return [(d, v) for d, v in curve if (lo is None or d >= lo) and (hi is None or d <= hi)]


def _rebase(curve):
    if not curve:
        return []
    base = curve[0][1]
    return [(d, v / base) for d, v in curve] if base else []


def _era_curves(raw_all, cal, pick_n, cost_mult=1.0):
    """(E41/E76/E77) the ladder5 and wide-top-N curves on one calendar.

    Factored out of run_era so the E76 screen leg can replay the identical book
    from a repaired universe: the two faces then differ only in the closes
    handed in, not in any book convention.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    cash = base.load_cash_series(cal)
    rank_cache = {}
    curves = {}
    for name, univ, n in (("ladder5", base.LADDER, None),
                          ("wide_top%d" % pick_n, universe, pick_n)):
        curves[name], _aux, _hold = e27.simulate(cal, prices, amounts, univ, cash,
                                                 n, cost_mult, rank_cache)
    lad = curves["ladder5"]
    wide = curves["wide_top%d" % pick_n]
    lmap = dict(lad)
    ratio = [(d, v / lmap[d]) for d, v in wide if d in lmap and lmap[d] > 0]
    return lad, wide, ratio


def _era_rows(lad, wide, ratio, eras):
    """Era-partitioned risk profile of the ladder, the wide book and their ratio."""
    rows = {}
    for name, lo, hi in eras:
        seg_l = _rebase(_slice_curve(lad, lo, hi))
        seg_w = _rebase(_slice_curve(wide, lo, hi))
        seg_r = _rebase(_slice_curve(ratio, lo, hi))
        if len(seg_l) < 2 or len(seg_w) < 2 or len(seg_r) < 2:
            rows[name] = {"bars": len(seg_l), "skipped": "fewer than 2 bars in this era"}
            continue
        yrs = len(seg_l) / 252.0
        pl = risk_profile(seg_l, yrs)
        pw = risk_profile(seg_w, yrs)
        pr = risk_profile(seg_r, yrs)
        rows[name] = {
            "from": seg_l[0][0], "to": seg_l[-1][0], "bars": len(seg_l),
            "years": round(yrs, 2),
            "ladder_ann_pct": pl["ann_return_pct"],
            "wide_ann_pct": pw["ann_return_pct"],
            "spread_ann_bp": round((pw["ann_return_pct"] - pl["ann_return_pct"]) * 100, 1),
            "spread_positive": (pw["ann_return_pct"] - pl["ann_return_pct"]) > 0,
            "ratio_path": {
                "ann_pct": pr["ann_return_pct"],
                "max_drawdown_pct": pr["max_drawdown_pct"],
                "max_drawdown_span": pr["max_drawdown_span"],
                "longest_underwater_sessions": pr["longest_underwater_sessions"],
                "worst_month": pr["worst_month"],
                "monthly_win_rate_pct": pr["monthly_win_rate_pct"],
                "months": pr["months"],
            },
            "ladder_max_drawdown_pct": pl["max_drawdown_pct"],
            "wide_max_drawdown_pct": pw["max_drawdown_pct"],
        }
    return rows


def run_era(outdir, pick_n=9999, exclude=("sh511",),
            eras=(("pre2017", None, "2016-12-31"),
                  ("2017_2020", "2017-01-01", "2020-12-31"),
                  ("2021_2023", "2021-01-01", "2023-12-31"),
                  ("2024_now", "2024-01-01", None))):
    """Is the vs-ladder spread a regime or a constant?

    The 2020+ pair leg measured the spread's own -13.04% drawdown, which already
    says it is not a constant. This leg splits the same ratio curve by era and
    profiles each slice on its own (re-based at the era's first bar), so a
    single full-sample number cannot stand in for a path.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal = base.load_panel()[0]
    cutoff = cal[-1]
    lad, wide, ratio = _era_curves(raw_all, cal, pick_n)
    rows = _era_rows(lad, wide, ratio, eras)
    spreads = [r["spread_ann_bp"] for r in rows.values() if "spread_ann_bp" in r]
    return {
        "study": "e41_spread_era_decay",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_mult": 1.0, "cost_bp_per_side": base.COST_BP_SIDE,
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
                 "calendar_from": cal[0]},
        "eras": rows,
        "answers": {
            "spread_positive_eras": sum(1 for r in rows.values() if r.get("spread_positive")),
            "eras_with_data": len(spreads),
            "spread_range_bp": (round(max(spreads) - min(spreads), 1) if spreads else None),
            "spread_min_bp": min(spreads) if spreads else None,
            "spread_max_bp": max(spreads) if spreads else None,
            "era_of_worst_ratio_drawdown": min(
                (r for r in rows.values() if "ratio_path" in r),
                key=lambda r: r["ratio_path"]["max_drawdown_pct"])["from"]
            if any("ratio_path" in r for r in rows.values()) else None,
        },
        "honest": [
            "eras are calendar partitions of one continuous curve; each slice is re-based at its "
            "own first bar, so era ann% are not additive and do not compound to the full-sample number",
            "the last era is open-ended (2024-01-01 to the cutoff) and is therefore the shortest "
            "and the least stable",
            "the ratio curve is a ratio of equity curves, not a tradable sleeve",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ------------------------------------ leg: E42 spread net of the size tilt
#
# E40 measured the ladder's own size tilt (beta 0.62 on the small-minus-large
# month, +612bp/yr) and E41 measured a spread that is 4.7x thinner in the newest
# era than at its 2017-2020 peak. Both are quoted against the same ladder
# denominator, so neither can be read alone: this leg decomposes the spread and
# reports the intercept, which is what the wide book pays when the size leg is
# flat. Then it splits the tilt itself by the same four eras, so one full-sample
# exposure number cannot stand in for a regime. Monthly additive convention
# throughout, so every bp column is directly comparable.

ERAS = (("pre2017", None, "2016-12-31"),
        ("2017_2020", "2017-01-01", "2020-12-31"),
        ("2021_2023", "2021-01-01", "2023-12-31"),
        ("2024_now", "2024-01-01", None))

# E74: the panel carries some names unadjusted, so a share split prints as a
# -90% "return". Any single-session move beyond any A-share/ETF daily limit is
# treated as a corporate-action artefact and excluded from the priced tail.
ARTEFACT_JUMP = 0.30


def _in_era(month, lo, hi):
    """Month (YYYY-MM) inside an era whose bounds are dates (YYYY-MM-DD) or None."""
    if lo and month < lo[:7]:
        return False
    if hi and month > hi[:7]:
        return False
    return True


def _ols(y, x):
    """OLS y = alpha + beta*x -> (beta, alpha, r2); None when under-determined."""
    if len(y) < 3:
        return None, None, None
    my, mx = _moments(y), _moments(x)
    # a constant series has sd ~1e-17 from float rounding, not 0.0 -- compare to a tolerance
    if my["sd"] is None or mx["sd"] is None or my["sd"] <= 1e-15 or mx["sd"] <= 1e-15:
        return None, None, None
    cov = sum((a - my["mean"]) * (b - mx["mean"]) for a, b in zip(y, x)) / (len(y) - 1)
    beta = cov / (mx["sd"] ** 2)
    alpha = my["mean"] - beta * mx["mean"]
    r2 = (cov ** 2) / (mx["sd"] ** 2 * my["sd"] ** 2)
    return beta, alpha, r2


def _monthly_core(pick_n=9999, exclude=("sh511",), raw_all=None):
    """One shared build: both engine curves plus the member tilt series.

    The two E42 product legs read this object so their faces cannot drift apart
    and the expensive panel pass happens once per process.

    ``raw_all`` lets a screen leg hand in a repaired universe (E81). With the
    default ``None`` this calls ``e27.load_universe()`` exactly as before, so
    every published face keeps reading the untouched loader.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    if raw_all is None:
        raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal = base.load_panel()[0]
    cutoff = cal[-1]
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    cash = base.load_cash_series(cal)
    rank_cache = {}
    wide_name = "wide_top%d" % pick_n
    curves = {}
    for name, univ, n in (("ladder5", base.LADDER, None), (wide_name, universe, pick_n)):
        curves[name], _aux, _hold = e27.simulate(cal, prices, amounts, univ, cash,
                                                 n, 1.0, rank_cache)
    lad_m = dict(_month_rets(curves["ladder5"]))
    wide_m = dict(_month_rets(curves[wide_name]))
    mem = {s: _member_monthly(cal, s, raw_all) for s in base.LADDER}
    brk = {s: _member_break_months(cal, s, raw_all) for s in base.LADDER}
    five_ok = [m for m in sorted(lad_m)
               if m in wide_m and all(m in mem[s] for s in base.LADDER)]
    months, tilt, dropped = _tilt_series(mem, brk, five_ok, TILT_LARGE, TILT_SMALL)
    four_ok = [m for m in sorted(lad_m)
               if m in wide_m and all(m in mem[s] for s in TILT_LARGE + TILT4_SMALL)]
    months4, tilt4, dropped4 = _tilt_series(mem, brk, four_ok, TILT_LARGE, TILT4_SMALL)
    return {"cutoff": cutoff, "cal": cal, "curves": curves, "wide_name": wide_name,
            "lad_m": lad_m, "wide_m": wide_m, "months": months, "tilt": tilt,
            "months4": months4, "tilt4": tilt4, "dropped4": dropped4,
            "dropped": dropped, "universe": len(universe),
            # per-member monthly returns + break months, so a leg can rebuild any
            # sub-skin without a second panel pass (E44 leave-one-out)
            "mem": mem, "brk": brk,
            "years": len(cal) / 252.0}


def run_spreadsize(outdir, core=None, eras=ERAS):
    """Restate the vs-ladder spread net of the size tilt, per era."""
    core = core or _monthly_core()
    rows = {}
    for name, lo, hi in list(eras) + [("full", None, None)]:
        ms = [m for m in core["months"] if _in_era(m, lo, hi)]
        if len(ms) < 3:
            rows[name] = {"months": len(ms), "skipped": "fewer than 3 usable months"}
            continue
        spread = [core["wide_m"][m] - core["lad_m"][m] for m in ms]
        tilt = [core["tilt"][m] for m in ms]
        raw_ann = sum(spread) / len(spread) * 12.0 * 1e4
        beta, alpha, r2 = _ols(spread, tilt)
        tilt_ann = sum(tilt) / len(tilt) * 12.0 * 1e4
        size_part = beta * tilt_ann if beta is not None else None
        # reconciliation against the E41 era leg: the geometric ann% difference on the
        # same era slice. The additive monthly mean and the compounded difference are
        # two conventions of one quantity, so the gap is disclosed, never averaged away.
        seg_l = _rebase(_slice_curve(core["curves"]["ladder5"], lo, hi))
        seg_w = _rebase(_slice_curve(core["curves"][core["wide_name"]], lo, hi))
        eng_diff = None
        if len(seg_l) > 1 and len(seg_w) > 1:
            yrs = len(seg_l) / 252.0
            eng_diff = round((risk_profile(seg_w, yrs)["ann_return_pct"]
                              - risk_profile(seg_l, yrs)["ann_return_pct"]) * 100, 1)
        rows[name] = {
            "months": len(ms), "from": ms[0], "to": ms[-1],
            "raw_spread_ann_bp": round(raw_ann, 1),
            "size_neutral_ann_bp": round(alpha * 12.0 * 1e4, 1) if alpha is not None else None,
            "size_component_ann_bp": round(size_part, 1) if size_part is not None else None,
            "beta_spread_on_tilt": round(beta, 3) if beta is not None else None,
            "alpha_monthly_bp": round(alpha * 1e4, 2) if alpha is not None else None,
            "r_squared": round(r2, 4) if r2 is not None else None,
            "tilt_explains_spread_var_pct": round(r2 * 100, 2) if r2 is not None else None,
            "tilt_ann_bp_in_era": round(tilt_ann, 1),
            "share_of_spread_from_size_pct": (
                round(size_part / raw_ann * 100, 1) if size_part is not None and raw_ann else None),
            "engine_ann_diff_bp": eng_diff,
            "arithmetic_vs_geometric_gap_bp": (
                round(raw_ann - eng_diff, 1) if eng_diff is not None else None),
        }
    per_era = {k: v for k, v in rows.items() if k != "full" and "raw_spread_ann_bp" in v}
    neutral = [v["size_neutral_ann_bp"] for v in per_era.values() if v.get("size_neutral_ann_bp") is not None]
    return {
        "study": "e42_spread_size_neutral",
        "evidence_cutoff": core["cutoff"],
        "spec": {"pick_n": 9999, "exclude_prefixes": ["sh511"], "cost_mult": 1.0,
                 "calendar": "month-end decision, the E24/E27 default",
                 "decomposition": "spread_m = alpha + beta * tilt_m; "
                                  "size_neutral = alpha*12*1e4 bp, size = beta*tilt_mean*12*1e4 bp",
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
                 "universe_members": core["universe"]},
        "eras": rows,
        "answers": {
            "size_neutral_range_bp": (round(max(neutral) - min(neutral), 1) if neutral else None),
            "size_neutral_min_bp": min(neutral) if neutral else None,
            "size_neutral_max_bp": max(neutral) if neutral else None,
            "eras_positive_size_neutral": sum(1 for x in neutral if x > 0),
            "eras_with_data": len(neutral),
            "max_arithmetic_vs_geometric_gap_bp": max(
                (abs(v["arithmetic_vs_geometric_gap_bp"]) for v in per_era.values()
                 if v.get("arithmetic_vs_geometric_gap_bp") is not None), default=None),
            "alpha_equals_raw_minus_size_row_check": all(
                abs((v["raw_spread_ann_bp"] or 0) - (v["size_neutral_ann_bp"] or 0)
                    - (v["size_component_ann_bp"] or 0)) <= 0.25
                for v in per_era.values() if "raw_spread_ann_bp" in v),
        },
        "honest": [
            "the tilt is a naming split (2 broad-cap legs vs 3 mid/small/STAR legs), not a "
            "factor-model exposure; beta is descriptive, it does not claim the size spread causes "
            "the ladder/wide gap",
            "the two engine curves are the E24/E27 engine's own (module import); the tilt series is "
            "month-end marks from the panel rows",
            "monthly convention: raw = size_neutral + size component holds on the arithmetic mean, "
            "so the columns do not compound to the era-leg's geometric ann% difference",
            "member months carrying a >20% single-day corporate-action jump are dropped from the "
            "tilt mean (as-traded panel), and the dropped set is disclosed below",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
        "dropped_months": core["dropped"],
    }


SPREAD_COLUMNS = ("raw_spread_ann_bp", "size_neutral_ann_bp",
                  "size_component_ann_bp", "beta_spread_on_tilt", "r_squared")


def _spread_delta_rows(base_label, faces, modes, eras):
    """Column-by-column unscreened vs screened table for the E42 spread face.

    Pure function of the built faces, so the selftest can pin the arithmetic
    without touching the panel.
    """
    rows = []
    base_face = faces[base_label]["eras"]
    order = [n for n, _lo, _hi in list(eras) + [("full", None, None)]]
    for era in order:
        era_row = base_face.get(era) or {}
        for col in SPREAD_COLUMNS:
            u = era_row.get(col)
            row = {"era": era, "column": col, "unscreened": u}
            for mode in modes:
                v = (faces[mode]["eras"].get(era) or {}).get(col)
                row[mode] = v
                # one delta column per arm, not per cell column: a single
                # ``delta_<column>`` key would keep only the last arm's figure
                row["delta_" + mode] = (round(v - u, 4)
                                        if isinstance(v, (int, float))
                                        and isinstance(u, (int, float)) else None)
            rows.append(row)
    return rows


def run_screenspread(outdir, pick_n=9999, exclude=("sh511",),
                     modes=("neutralise_int", "neutralise", "neutralise_persist"),
                     eras=ERAS):
    """E81 leg 2: replay the size-neutral spread from the repaired universe.

    E42's newest-era size-neutral spread is the number the chain quotes as its
    surviving claim, and it is an equal-weight figure read from the as-traded
    panel -- so a share-split print inside the wide book is charged at weight
    1/n, exactly the defect E81 screened out of the calendar face. This leg
    rebuilds the whole monthly core per arm (engine curves *and* the member tilt
    series, so the regression and its regressor move together) and publishes the
    screened column beside the unscreened one. No published face is rewritten.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    arms = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        arms[mode] = repaired

    faces = {}
    for label, univ in arms.items():
        core = _monthly_core(pick_n=pick_n, exclude=(), raw_all=univ)
        face = run_spreadsize(None, core=core, eras=eras)
        faces[label] = {"universe_size": len(univ),
                        "months": len(core["months"]),
                        "eras": face["eras"],
                        "answers": face["answers"]}

    delta = _spread_delta_rows("unscreened", faces, modes, eras)
    order = [n for n, _lo, _hi in list(eras) + [("full", None, None)]]

    def _neutral(arm, era):
        return (faces[arm]["eras"].get(era) or {}).get("size_neutral_ann_bp")

    levels = {arm: {era: _neutral(arm, era) for era in order} for arm in faces}
    per_era = [n for n, _lo, _hi in eras]

    def _band(arm):
        xs = [levels[arm][e] for e in per_era if levels[arm][e] is not None]
        return (round(max(xs) - min(xs), 1) if len(xs) >= 2 else None)

    def _level(arm):
        xs = [levels[arm][e] for e in per_era if levels[arm][e] is not None]
        return round(sum(xs) / len(xs), 1) if xs else None

    def _all_positive(arm):
        xs = [levels[arm][e] for e in per_era if levels[arm][e] is not None]
        return all(x > 0 for x in xs) if xs else None

    # E82: a moved cell must be nameable. Count the repaired prints by era and
    # carry the newest-era names, so the reader can check the dates themselves.
    def _era_event_census(mode):
        counts = {n: 0 for n, _lo, _hi in list(eras) + [("full", None, None)]}
        named = []
        for entry in reports[mode].get("names") or []:
            if entry.get("action") != "neutralise":
                continue
            for pr in entry.get("prints") or []:
                if pr.get("factor_applied") is None:
                    continue
                era = _era_of(pr.get("date"), eras) or "full"
                counts[era] = counts.get(era, 0) + 1
                counts["full"] = counts.get("full", 0) + 1
                if era == "2024_now" and len(named) < 8:
                    named.append({"name": entry["name"], "date": pr.get("date"),
                                  "ret_pct": pr.get("ret_pct"),
                                  "ratio": round(pr.get("ratio") or 0.0, 4),
                                  "nearest_int": pr.get("nearest_int")})
        return {"events_by_era": counts, "newest_era_names_sample": named}

    flips = {}
    for mode in modes:
        flips[mode] = [e for e in per_era
                       if levels["unscreened"][e] is not None
                       and levels[mode][e] is not None
                       and (levels["unscreened"][e] > 0) != (levels[mode][e] > 0)]
    moves = []
    for mode in modes:
        for r in delta:
            if r["column"] == "size_neutral_ann_bp" and r.get("delta_" + mode):
                x = dict(r)
                x["arm"] = mode
                x["delta_bp"] = r["delta_" + mode]
                moves.append(x)
    widest = max(moves, key=lambda r: abs(r["delta_bp"])) if moves else None
    return {
        "study": "e42_spread_size_neutral_screened",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude), "cost_mult": 1.0,
                 "modes": list(modes),
                 "calendar": "month-end decision, the E24/E27 default",
                 "decomposition": "spread_m = alpha + beta * tilt_m; "
                                  "size_neutral = alpha*12*1e4 bp, size = beta*tilt_mean*12*1e4 bp",
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
                 "screen": {m: reports[m] for m in modes}},
        "arms": faces,
        "delta": delta,
        "answers": {
            "size_neutral_by_arm_era_bp": levels,
            "level_mean_over_eras_bp": {arm: _level(arm) for arm in faces},
            "band_max_minus_min_bp": {arm: _band(arm) for arm in faces},
            "all_eras_positive": {arm: _all_positive(arm) for arm in faces},
            "sign_flips_vs_unscreened": flips,
            "era_event_census": {m: _era_event_census(m) for m in modes},
            "full_sample_size_neutral_bp": {arm: levels[arm].get("full") for arm in faces},
            "widest_correction": widest,
            "delta_cells": len(delta),
            "non_zero_delta_cells": sum(
                1 for r in delta
                if any(r.get("delta_" + m) not in (None, 0, 0.0) for m in modes)),
            "arm_alpha_identity_holds": {
                arm: faces[arm]["answers"]["alpha_equals_raw_minus_size_row_check"]
                for arm in faces},
        },
        "honest": [
            "repairing an integer-ratio print is a sensitivity, not a correction: an ETF whose "
            "daily limit differs from the 10%/20% stock band can print >30% for real",
            "the screen repairs both the wide book and the tilt members, so a moved alpha is net "
            "of both legs and is not attributable to one of them",
            "the unscreened arm is rebuilt here rather than copied from the published face: it is "
            "the same code path on the same panel, and the published COST/NEUTRAL files stay "
            "untouched",
            "level and band are published together: max-min over eras is blind to a common shift, "
            "which is exactly how the E81 calendar leg first hid a tripled level",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


def run_tilt_era(outdir, core=None, eras=ERAS):
    """Split the ladder's size tilt and its beta/R2 by the same four eras."""
    core = core or _monthly_core()
    rows = {}
    for name, lo, hi in list(eras) + [("full", None, None)]:
        ms = [m for m in core["months"] if _in_era(m, lo, hi)]
        if len(ms) < 3:
            rows[name] = {"months": len(ms), "skipped": "fewer than 3 usable months"}
            continue
        tilt = [core["tilt"][m] for m in ms]
        lad = [core["lad_m"][m] for m in ms]
        tm = _moments(tilt)
        beta, alpha, r2 = _ols(lad, tilt)
        cum = 1.0
        for t in tilt:
            cum *= 1.0 + t
        pos = sum(1 for t in tilt if t > 0)
        i_max = max(range(len(tilt)), key=lambda i: tilt[i])
        i_min = min(range(len(tilt)), key=lambda i: tilt[i])
        rows[name] = {
            "months": len(ms), "from": ms[0], "to": ms[-1],
            "tilt_annualised_bp": round(tm["mean"] * 12 * 1e4, 1) if tm["mean"] is not None else None,
            "tilt_sd_bp": round(tm["sd"] * 1e4, 1) if tm["sd"] is not None else None,
            "tilt_positive_share_pct": round(pos / len(tilt) * 100, 1),
            "tilt_cumulative_pct": round((cum - 1.0) * 100, 2),
            "tilt_best_month": {"month": ms[i_max], "spread_pct": round(tilt[i_max] * 100, 2)},
            "tilt_worst_month": {"month": ms[i_min], "spread_pct": round(tilt[i_min] * 100, 2)},
            "beta_ladder_on_tilt": round(beta, 3) if beta is not None else None,
            "alpha_monthly_bp": round(alpha * 1e4, 2) if alpha is not None else None,
            "r_squared": round(r2, 4) if r2 is not None else None,
            "tilt_explains_ladder_var_pct": round(r2 * 100, 2) if r2 is not None else None,
            "ladder_mean_month_pct": round(_moments(lad)["mean"] * 100, 4),
        }
    per_era = {k: v for k, v in rows.items() if k != "full" and "tilt_annualised_bp" in v}
    tilts = [v["tilt_annualised_bp"] for v in per_era.values()]
    return {
        "study": "e42_ladder_tilt_by_era",
        "evidence_cutoff": core["cutoff"],
        "spec": {"ladder": ["sh510300", "sh510050", "sh510500", "sh512100", "sh588000"],
                 "large": list(TILT_LARGE), "small": list(TILT_SMALL),
                 "decomposition": "ladder_monthly ~ alpha + beta*(small_mean - large_mean)",
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras]},
        "eras": rows,
        "answers": {
            "tilt_range_bp": (round(max(tilts) - min(tilts), 1) if tilts else None),
            "tilt_min_bp": min(tilts) if tilts else None,
            "tilt_max_bp": max(tilts) if tilts else None,
            "eras_positive_tilt": sum(1 for t in tilts if t > 0),
            "eras_with_data": len(tilts),
            "peak_era": (max(per_era, key=lambda k: per_era[k]["tilt_annualised_bp"])
                         if per_era else None),
            "newest_era_tilt_vs_peak_pct": (
                round(per_era["2024_now"]["tilt_annualised_bp"]
                      / max(v["tilt_annualised_bp"] for v in per_era.values()) * 100, 1)
                if "2024_now" in per_era and tilts else None),
        },
        "honest": [
            "eras are calendar partitions of one continuous monthly series; each row is measured "
            "on its own months, so the era tilt bp do not add up to the full-sample number",
            "the decomposition is the E40 identity (2/5 large + 3/5 small) applied per era; the "
            "regression is descriptive, not a factor-model estimate",
            "the newest era is open-ended and the shortest, so its beta carries the widest error",
            "corporate-action guard as in E40: months with a >20% single-day member jump are dropped",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
        "dropped_months": core["dropped"],
    }


# ------------------------------------ leg: E95 newest-era cell stability

NEWEST_ERA = ("2024_now", "2024-01-01", None)


def _tilt_stats(core, months):
    """The E42 tilt cell measured on an explicit list of months.

    Factored out so the stability leg and the published face cannot disagree
    about what the cell *is*: run_tilt_era keeps its own body (its published
    output must stay bit-identical), and the selftest pins this helper to the
    same number on the same month list.
    """
    if len(months) < 3:
        return {"months": len(months), "skipped": "fewer than 3 usable months"}
    tilt = [core["tilt"][m] for m in months]
    lad = [core["lad_m"][m] for m in months]
    tm = _moments(tilt)
    beta, alpha, r2 = _ols(lad, tilt)
    pos = sum(1 for t in tilt if t > 0)
    return {
        "months": len(months), "from": months[0], "to": months[-1],
        "tilt_annualised_bp": round(tm["mean"] * 12 * 1e4, 1),
        "tilt_sd_bp": round(tm["sd"] * 1e4, 1) if tm["sd"] is not None else None,
        "tilt_positive_share_pct": round(pos / len(tilt) * 100, 1),
        "beta_ladder_on_tilt": round(beta, 3) if beta is not None else None,
        "alpha_monthly_bp": round(alpha * 1e4, 2) if alpha is not None else None,
        "r_squared": round(r2, 4) if r2 is not None else None,
    }


def _published_tilt_readings(outdir):
    """Every newest-era tilt reading this repo has already published, read back
    off the faces themselves (no transcription, no memory)."""
    out = []
    if not os.path.isdir(outdir):
        return out
    for name in sorted(os.listdir(outdir)):
        if not (name.startswith("TILT-ERA-") and name.endswith(".json")):
            continue
        try:
            with open(os.path.join(outdir, name), encoding="utf-8") as fh:
                face = json.load(fh)
        except (OSError, ValueError):
            continue
        row = (face.get("eras") or {}).get("2024_now") or {}
        val = row.get("tilt_annualised_bp")
        if val is None:
            continue
        out.append({"file": name, "cutoff": face.get("evidence_cutoff"),
                    "months": row.get("months"), "tilt_annualised_bp": val})
    return out


def _stability_verdict(observed_bp, span_bp):
    """Is the spread of published readings inside what moving the end alone does?"""
    if observed_bp is None or span_bp is None:
        return None
    return "inside_end_choice_span" if observed_bp <= span_bp else "beyond_end_choice_span"


def run_tilt_stable(outdir, core=None, ends=12, era=NEWEST_ERA):
    """Rolling-window stability of the newest-era tilt cell (E95).

    Same panel, same code path, only the *evaluation end* moves. If the whole
    spread of already-published readings fits inside the spread this grid
    produces, the cell is being re-derived, not re-measured.
    """
    core = core or _monthly_core()
    name, lo, hi = era
    era_months = [m for m in core["months"] if _in_era(m, lo, hi)]
    full = _tilt_stats(core, era_months)
    end_months = era_months[-int(ends):] if era_months else []
    rows = []
    for end in end_months:
        ms = [m for m in era_months if m <= end]
        row = _tilt_stats(core, ms)
        row["window_end"] = end
        rows.append(row)
    vals = [r["tilt_annualised_bp"] for r in rows
            if r.get("tilt_annualised_bp") is not None]
    span = round(max(vals) - min(vals), 1) if len(vals) >= 2 else None
    published = _published_tilt_readings(outdir or os.path.join(ROOT, "results", "e42_tilt_era"))
    readings = [p["tilt_annualised_bp"] for p in published
                if p.get("tilt_annualised_bp") is not None]
    if full.get("tilt_annualised_bp") is not None:
        readings.append(full["tilt_annualised_bp"])
    observed = (round(max(readings) - min(readings), 1) if len(readings) >= 2 else None)
    verdict = _stability_verdict(observed, span)
    return {
        "study": "e95_newest_era_cell_stability",
        "evidence_cutoff": core["cutoff"],
        "spec": {"era": name, "era_from": lo, "era_to": hi,
                 "cell": "ladder monthly size tilt, annualised bp",
                 "end_grid": "the last %d era month-ends, same panel, same loader"
                             % len(end_months),
                 "panel_months": len(core["months"])},
        "cell_now": full,
        "end_choice_series": rows,
        "end_choice_answers": {
            "ends": len(rows), "span_bp": span,
            "min_bp": min(vals) if vals else None,
            "max_bp": max(vals) if vals else None,
            "sd_bp": (round(_moments(vals)["sd"], 1) if len(vals) >= 2 else None),
            "latest_end_bp": vals[-1] if vals else None,
        },
        "published_readings": published,
        "stability_answers": {
            "published_n": len(readings),
            "observed_spread_bp": observed,
            "end_choice_span_bp": span,
            "verdict": verdict,
            "reads_as": (
                "the spread of published readings is no larger than what moving the "
                "evaluation end alone produces -- read the cell as re-derived, not re-measured"
                if verdict == "inside_end_choice_span" else
                "published readings spread wider than the end-choice grid -- at least part "
                "of the move is not an end-choice artefact"
                if verdict == "beyond_end_choice_span" else None),
        },
        "honest": [
            "one panel, one loader, one cutoff: the grid moves the evaluation end only, so it "
            "cannot see panel-arrival effects (E-register r1110) or a changed universe",
            "the newest era is open-ended and the shortest, so its beta carries the widest error "
            "and its own early months are the ones each truncated window drops first",
            "published readings are read back from the faces verbatim; a face that was never "
            "written is absent here rather than guessed",
            "descriptive census only: no gate, no verdict on the strategy, no prereg, no trial",
        ],
        "dropped_months": core["dropped"],
    }


# ------------------------------------ leg: E98 end-choice slack on every era

def _published_era_readings(outdir, era):
    """Every already-published cell for one era, read back off the faces.

    Two schemas share this directory: the plain E42 face keeps its ``eras`` at
    the top level, the E81 screened face keeps one full copy per screening arm
    under ``faces``. Both are read here, because a reader that only knows the
    flat shape reports zero published readings for the whole screened family --
    and "nothing was published" is the one answer a stability question must
    never invent.
    """
    out = []
    if not os.path.isdir(outdir):
        return out
    for name in sorted(os.listdir(outdir)):
        if not (name.startswith("TILT-ERA-") and name.endswith(".json")):
            continue
        try:
            with open(os.path.join(outdir, name), encoding="utf-8") as fh:
                face = json.load(fh)
        except (OSError, ValueError):
            continue
        containers = []
        if isinstance(face.get("eras"), dict):
            containers.append((None, face["eras"]))
        for arm, sub in sorted((face.get("faces") or {}).items()):
            if isinstance(sub, dict) and isinstance(sub.get("eras"), dict):
                containers.append((arm, sub["eras"]))
        for arm, eras in containers:
            row = eras.get(era) or {}
            val = row.get("tilt_annualised_bp")
            if val is None:
                continue
            out.append({"file": name, "arm": arm,
                        "cutoff": face.get("evidence_cutoff"),
                        "months": row.get("months"),
                        "tilt_annualised_bp": val})
    return out


def _endchoice_era_row(core, era, ends, outdir):
    """One era's end-choice grid: same panel, same loader, only the end moves.

    An era the panel does not reach is reported as structurally empty rather
    than measured on borrowed months -- the E42 panel opens in 2020-12, so two
    of the four era names carry no months at all and cannot be swept.
    """
    name, lo, hi = era
    era_months = [m for m in core["months"] if _in_era(m, lo, hi)]
    row = {"era": name, "era_from": lo, "era_to": hi,
           "panel_months": len(era_months)}
    if len(era_months) < 3:
        row.update({"skipped": "the panel carries fewer than 3 months in this era",
                    "grid_ends": 0, "span_bp": None, "verdict": None,
                    "end_choice_series": [], "published": [],
                    "observed_spread_bp": None, "span_over_monthly_sd": None})
        return row
    full = _tilt_stats(core, era_months)
    grid = era_months[-int(ends):]
    series = []
    for end in grid:
        ms = [m for m in era_months if m <= end]
        r = _tilt_stats(core, ms)
        r["window_end"] = end
        series.append(r)
    vals = [r["tilt_annualised_bp"] for r in series
            if r.get("tilt_annualised_bp") is not None]
    span = round(max(vals) - min(vals), 1) if len(vals) >= 2 else None
    # how much of the era each truncated run throws away at most
    dropped = (len(era_months) - min(r["months"] for r in series
                                     if r.get("months"))) if series else None
    monthly_sd = None
    tm = _moments([core["tilt"][m] for m in era_months])
    if tm["sd"] is not None:
        monthly_sd = round(tm["sd"] * 1e4, 1)
    published = _published_era_readings(outdir, name)
    readings = [p["tilt_annualised_bp"] for p in published]
    observed = round(max(readings) - min(readings), 1) if len(readings) >= 2 else None
    row.update({
        "cell_now": full,
        "grid_ends": len(series),
        "months_dropped_max": dropped,
        "span_bp": span,
        "min_bp": min(vals) if vals else None,
        "max_bp": max(vals) if vals else None,
        "sd_bp": round(_moments(vals)["sd"], 1) if len(vals) >= 2 else None,
        "latest_end_bp": vals[-1] if vals else None,
        "monthly_sd_bp": monthly_sd,
        # E95's own denominator, now per era: a span can only be called wide
        # relative to how much this era actually moves month to month.
        "span_over_monthly_sd": (round(span / monthly_sd, 2)
                                 if span is not None and monthly_sd else None),
        "published": published,
        "published_n": len(readings),
        "observed_spread_bp": observed,
        "verdict": _stability_verdict(observed, span),
        "end_choice_series": series,
    })
    return row


def run_endchoice_all_eras(outdir, core=None, ends=12):
    """E98: run the E95 end-choice grid on every era, not just the newest one.

    The question E95 could not answer: is "the cell is re-derived, not
    re-measured" a property of the newest era or of the instrument? Same panel,
    same loader, same end grid width; only the era window changes.
    """
    core = core or _monthly_core()
    rows = [_endchoice_era_row(core, era, ends, outdir) for era in ERAS]
    measured = [r for r in rows if r.get("span_bp") is not None]
    empty = [r["era"] for r in rows if r.get("skipped")]
    widest = (max(measured, key=lambda r: r["span_bp"]) if measured else None)
    # a span is only comparable to another span once both are stated against
    # the month-to-month movement of their own era
    ratios = {r["era"]: r["span_over_monthly_sd"] for r in measured}
    verdicts = {r["era"]: r["verdict"] for r in measured}
    return {
        "study": "e98_end_choice_slack_by_era",
        "evidence_cutoff": core["cutoff"],
        "spec": {"grid": "the last %d month-ends of each era, same panel, same loader"
                         % int(ends),
                 "eras": [e[0] for e in ERAS],
                 "cell": "ladder monthly size tilt, annualised bp",
                 "identity": "the grid moves the evaluation end only; the era window "
                             "is the only thing that differs between rows"},
        "eras": rows,
        "answers": {
            "measured_eras": [r["era"] for r in measured],
            "structurally_empty_eras": empty,
            "spans_bp": {r["era"]: r["span_bp"] for r in measured},
            "span_over_monthly_sd": ratios,
            "verdicts": verdicts,
            "widest_era": widest["era"] if widest else None,
            "widest_span_bp": widest["span_bp"] if widest else None,
            "any_era_quotable_by_level": (
                any(r["verdict"] == "beyond_end_choice_span" for r in measured)
                if measured else None),
            "reads_as": (
                "every era the panel reaches re-derives under its own end grid -- the "
                "E95 caveat is a property of the instrument, not of the newest years, so "
                "no era level may be quoted as a measurement"
                if measured and not any(r["verdict"] == "beyond_end_choice_span"
                                        for r in measured) else
                "at least one era survives its own end grid, so the caveat is local to "
                "the eras that do not and must be cited per era"
                if measured else None),
        },
        "honest": [
            "one panel, one loader, one cutoff: this cannot see panel-arrival effects "
            "or a changed universe, only the choice of end",
            "two of the four era names carry no months on the E42 panel (it opens in "
            "2020-12), so they are reported structurally empty rather than swept",
            "short eras lose a larger share of themselves to the same 12-end grid, so "
            "the span is also stated against the era's own monthly sd",
            "published readings are read back from the faces verbatim, both schemas; a "
            "reading never written is absent here rather than guessed",
            "descriptive census only: no gate, no verdict on the strategy, no prereg, "
            "no trial, no ledger booking",
        ],
        "dropped_months": core["dropped"],
    }


# ------------------------------------ leg: E42 calendar band at cost x3

def _calcost_face(raw_all, cal_full, start="2020-01-01", pick_n=9999,
                  exclude=("sh511",), mid_day=15, cost_mults=(1.0, 3.0)):
    """The E42 calendar-cost face from an already loaded universe.

    Split out of ``run_calcost`` so the E81 screened twins can replay the exact
    same face from a repaired universe without a second copy of the body.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]
    years = len(cal) / 252.0
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    wide_name = "wide_top%d" % pick_n
    cash = base.load_cash_series(cal)
    rank_cache = {}
    month_ends = base.month_end_indices(cal)
    variants = [("me_m1", _shift_indices(month_ends, -1, len(cal))),
                ("me", sorted(set(month_ends))),
                ("me_p1", _shift_indices(month_ends, 1, len(cal))),
                ("mid%d" % mid_day, _mid_month_indices(cal, mid_day))]
    rows = {}
    for mult in cost_mults:
        tag = "cost_x%g" % mult
        rows[tag] = {}
        for vname, idxs in variants:
            rebal = set(idxs)
            cell = {"rebalances": len(rebal)}
            for scheme, univ, n in (("ladder5", base.LADDER, None),
                                    (wide_name, universe, pick_n)):
                curve, aux, _hold = e27.simulate(cal, prices, amounts, univ, cash,
                                                 n, mult, rank_cache, rebal)
                prof = risk_profile(curve, years)
                cell[scheme] = {
                    "ann_return_pct": prof["ann_return_pct"],
                    "max_drawdown_pct": prof["max_drawdown_pct"],
                    "rebalances": aux["rebalances"],
                    "turnover_per_year": round(aux["turnover_total"] / years, 3) if years else None,
                    "cost_per_year_bp": round(aux["cost_paid_frac"] / years * 1e4, 1) if years else None,
                }
            cell["vs_ladder_spread_bp"] = round(
                (cell[wide_name]["ann_return_pct"] - cell["ladder5"]["ann_return_pct"]) * 100, 1)
            rows[tag][vname] = cell
    summary = {}
    for tag, table in rows.items():
        spr = [c["vs_ladder_spread_bp"] for c in table.values()]
        ladder = [c["ladder5"]["ann_return_pct"] for c in table.values()]
        summary[tag] = {
            "spread_range_bp": round(max(spr) - min(spr), 1),
            "spread_all_positive": all(x > 0 for x in spr),
            "spread_min_bp": min(spr), "spread_max_bp": max(spr),
            "spread_at_me_bp": table["me"]["vs_ladder_spread_bp"],
            "ladder_ann_range_bp": round((max(ladder) - min(ladder)) * 100, 1),
            "cost_per_year_bp": {
                "ladder5": table["me"]["ladder5"]["cost_per_year_bp"],
                wide_name: table["me"][wide_name]["cost_per_year_bp"]},
            "turnover_per_year": {
                "ladder5": table["me"]["ladder5"]["turnover_per_year"],
                wide_name: table["me"][wide_name]["turnover_per_year"]},
        }
    tags = sorted(summary)
    return {
        "study": "e42_calendar_band_cost",
        "evidence_cutoff": cutoff,
        "spec": {"start": start, "bars": len(cal), "years": round(years, 2),
                 "pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_bp_per_side": base.COST_BP_SIDE, "cost_mults": list(cost_mults),
                 "mid_month_day": mid_day,
                 "variants": [v for v, _ in variants],
                 "universe_members": len(universe)},
        "calendars": rows,
        "answers": {
            "band_by_cost": {t: summary[t]["spread_range_bp"] for t in tags},
            "band_delta_top_vs_base_bp": (
                round(summary[tags[-1]]["spread_range_bp"]
                      - summary[tags[0]]["spread_range_bp"], 1) if len(tags) > 1 else None),
            "spread_all_positive": {t: summary[t]["spread_all_positive"] for t in tags},
            "level_shift_bp": {t: summary[t]["spread_at_me_bp"] for t in tags},
            "cost_per_year_bp": {t: summary[t]["cost_per_year_bp"] for t in tags},
            "summary": summary,
        },
        "honest": [
            "the engine reads a rebalance index as a decision at the close of that index, so the "
            "variants differ in session choice only -- universe, ranks and calendar are shared",
            "cost x3 scales the engine's own 13.041bp/side constant; it is a stress multiplier, "
            "not a measured fee schedule",
            "a wider band at x3 is consistent with turnover explaining it, but the two readings "
            "are not exclusive and nothing here selects a calendar",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


def run_calcost(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                mid_day=15, cost_mults=(1.0, 3.0)):
    """Is the calendar band in the spread a fee artefact? Re-run it at cost x3.

    E41 moved the decision calendar by one session and the spread band moved
    26bp while the ladder level moved 52bp on one shift. If the band is pricing
    (different sessions hold different names) the fee tripling leaves the band
    roughly where it is; if it is turnover-driven the band widens with the fee.
    Both readings are descriptive -- nothing here decides which calendar to use.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    return _calcost_face(raw_all, cal_full, start=start, pick_n=pick_n,
                         exclude=exclude, mid_day=mid_day,
                         cost_mults=cost_mults)


CALCOST_CELL_COLUMNS = ("ann_return_pct", "max_drawdown_pct",
                        "turnover_per_year", "cost_per_year_bp")


def _calcost_cell(faces, arm, tag, variant, scheme, col):
    """One published cell of one arm; scheme None reads the calendar cell."""
    table = (faces.get(arm) or {}).get("calendars") or {}
    cell = (table.get(tag) or {}).get(variant) or {}
    if scheme is None:
        return cell.get(col)
    return (cell.get(scheme) or {}).get(col)


def _calcost_delta_rows(faces, base="unscreened"):
    """(E81) unscreened vs each screened arm, one row per published cell.

    The spread cell and every per-scheme column are read through the same
    accessor, so a renamed scheme shows up as a missing cell instead of a
    silently dropped row.
    """
    rows = []
    others = sorted(k for k in faces if k != base)
    for tag in sorted((faces[base].get("calendars") or {})):
        for variant in sorted(faces[base]["calendars"][tag]):
            cell = faces[base]["calendars"][tag][variant]
            pairs = [(None, "vs_ladder_spread_bp")]
            for scheme in sorted(cell):
                if isinstance(cell[scheme], dict):
                    pairs.extend((scheme, c) for c in CALCOST_CELL_COLUMNS)
            for scheme, col in pairs:
                u = _calcost_cell(faces, base, tag, variant, scheme, col)
                row = {"cost_tag": tag, "calendar": variant,
                       "scheme": scheme or "spread", "column": col,
                       "unscreened": u}
                for arm in others:
                    v = _calcost_cell(faces, arm, tag, variant, scheme, col)
                    row[arm] = v
                    row["delta_" + arm] = (
                        round(v - u, 4)
                        if isinstance(v, (int, float))
                        and isinstance(u, (int, float)) else None)
                rows.append(row)
    return rows


def run_calcost_screenreg(outdir, start="2020-01-01", pick_n=9999,
                          exclude=("sh511",), mid_day=15,
                          cost_mults=(1.0, 3.0),
                          modes=("neutralise_int", "neutralise")):
    """(E81) replay the E42 calendar-cost face from a screened universe.

    E79's matrix found 33 census modes reading the per-name loader with no raw
    hook, so the fee-channel reading of the calendar band was still charged by
    unadjusted prints. The E76 twin (``run_screenreg``) covers the era spread;
    this leg covers the calendar band. Each screened arm is published BESIDE
    the untouched column and the published COST-<cutoff>.json is never
    rewritten in place.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    faces = {"unscreened": _calcost_face(raw_all, cal_full, start=start,
                                         pick_n=pick_n, exclude=exclude,
                                         mid_day=mid_day, cost_mults=cost_mults)}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw_all, mode=mode,
                                                        cal=cal_full)
        reports[mode] = report
        faces[mode] = _calcost_face(repaired, cal_full, start=start,
                                    pick_n=pick_n, exclude=exclude,
                                    mid_day=mid_day, cost_mults=cost_mults)

    delta = _calcost_delta_rows(faces)
    arms = ["unscreened"] + list(modes)
    widest = None
    for row in delta:
        mag = max([abs(row["delta_" + m]) for m in modes
                   if isinstance(row.get("delta_" + m), (int, float))] or [0])
        if mag and (widest is None or mag > widest["abs_delta_bp"]):
            widest = {"calendar": row["calendar"], "cost_tag": row["cost_tag"],
                      "scheme": row["scheme"], "column": row["column"],
                      "unscreened": row["unscreened"],
                      "abs_delta_bp": round(mag, 4),
                      "arms": {m: row.get(m) for m in modes}}

    bands = {arm: (faces[arm]["answers"]["band_by_cost"]) for arm in arms}
    widening = {arm: faces[arm]["answers"]["band_delta_top_vs_base_bp"]
                for arm in arms}
    return {
        "study": "e81_calcost_screenreg",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "mid_day": mid_day,
            "exclude_prefixes": list(exclude), "modes": list(modes),
            "cost_bp_per_side": base.COST_BP_SIDE,
            "cost_mults": list(cost_mults),
            "loader": "scripts/panel_screen.py (opt-in; the published COST face "
                      "still reads e27.load_universe() unmodified)",
            "faces": "E42 calendar band: ladder5 vs wide_topN at every cost "
                     "multiple and calendar variant",
        },
        "screen_reports": reports,
        "faces": faces,
        "delta": delta,
        "answers": {
            "band_by_cost": bands,
            "band_widening_x1_to_x3_bp": widening,
            "spread_all_positive": {arm: faces[arm]["answers"]["spread_all_positive"]
                                    for arm in arms},
            "level_shift_bp": {arm: faces[arm]["answers"]["level_shift_bp"]
                               for arm in arms},
            "fee_channel_reading": {arm: (widening.get(arm) > 0
                                          if widening.get(arm) is not None else None)
                                    for arm in arms},
            "widest_correction": widest,
            "delta_cells": len(delta),
            "non_zero_delta_cells": len([
                r for r in delta
                if any(r.get("delta_" + m) not in (None, 0) for m in modes)]),
        },
        "honest": [
            "the screen repairs arithmetic impossibility only: a flagged ETF print "
            "may be genuine (ETF daily limits differ from the 10%/20% stock band), "
            "so every arm is a sensitivity face, not a corrected truth",
            "neutralise_int repairs only prints whose price ratio lands on an "
            "integer; neutralise repairs every adjacent print -- the range between "
            "them bounds the correction",
            "the screened book is not a pre-registration and books no trial: it is "
            "the same descriptive face replayed from a different input",
            "the band is a max-minus-min over four calendars, so a correction that "
            "moves every calendar alike leaves the band untouched -- read the "
            "level_shift_bp columns beside it",
            "a fee-channel verdict flips only if band_widening_x1_to_x3_bp changes "
            "sign; a smaller widening is not a refutation of the turnover reading",
            "descriptive census only: no gate, no verdict, no ledger booking, trial 0",
        ],
    }


def _tiltdelta_rows(faces, base="unscreened",
                    columns=("tilt_annualised_bp", "beta_ladder_on_tilt",
                             "alpha_monthly_bp", "r_squared")):
    """(E81) unscreened vs each screened arm, one row per era-and-column cell.

    Every cell keeps the unscreened value beside the arm values, so a reader can
    see whether the screen moved a level without re-deriving the face.
    """
    rows = []
    eras = list(faces[base]["eras"])
    arms = [a for a in faces if a != base]
    for era in eras:
        u_row = faces[base]["eras"].get(era) or {}
        for col in columns:
            u = u_row.get(col)
            row = {"era": era, "column": col, "unscreened": u}
            for arm in arms:
                v = (faces[arm]["eras"].get(era) or {}).get(col)
                row[arm] = v
                row["delta_" + arm] = (round(v - u, 4)
                                       if isinstance(u, (int, float))
                                       and isinstance(v, (int, float)) else None)
            rows.append(row)
    return rows


def run_screentilt(outdir, pick_n=9999, exclude=("sh511",),
                   modes=("neutralise_int", "neutralise"), eras=ERAS):
    """(E81) replay the E42 tilt-era face from a screened universe.

    E79's matrix left ``era``/``calcost``/``neutralrob`` exposed; the calendar
    band and the robustness grid now have screened twins, and this leg covers the
    remaining member-tilt decomposer -- the face that reads "how much of the
    ladder's monthly return is a size tilt, and what is left over". It rebuilds
    the whole monthly core per arm (engine curves *and* the member tilt series
    move together), publishes each arm BESIDE the untouched column, and never
    rewrites the published ``TILT-ERA-<cutoff>.json`` in place.
    """
    import e27_universe_expansion as e27
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw_all = e27.load_universe()
    cal_full = base.load_panel()[0]
    faces = {"unscreened": run_tilt_era(None, core=_monthly_core(
        pick_n, exclude, raw_all), eras=eras)}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw_all, mode=mode,
                                                        cal=cal_full)
        reports[mode] = report
        faces[mode] = run_tilt_era(None, core=_monthly_core(
            pick_n, exclude, repaired), eras=eras)

    delta = _tiltdelta_rows(faces)
    arms = ["unscreened"] + list(modes)
    per_era = [e[0] for e in eras]

    tilt_by_arm = {arm: {era: (faces[arm]["eras"].get(era) or {}).get(
        "tilt_annualised_bp") for era in per_era} for arm in arms}
    beta_by_arm = {arm: {era: (faces[arm]["eras"].get(era) or {}).get(
        "beta_ladder_on_tilt") for era in per_era} for arm in arms}
    r2_by_arm = {arm: {era: (faces[arm]["eras"].get(era) or {}).get(
        "r_squared") for era in per_era} for arm in arms}

    def _range(vals):
        nums = [v for v in vals if isinstance(v, (int, float))]
        return round(max(nums) - min(nums), 1) if len(nums) > 1 else None

    flips = []
    for era in per_era:
        u = tilt_by_arm["unscreened"].get(era)
        for arm in modes:
            v = tilt_by_arm[arm].get(era)
            if isinstance(u, (int, float)) and isinstance(v, (int, float)) \
                    and (u > 0) != (v > 0):
                flips.append({"era": era, "arm": arm,
                              "unscreened_bp": u, "screened_bp": v})

    widest = None
    for row in delta:
        mag = max([abs(row["delta_" + m]) for m in modes
                   if isinstance(row.get("delta_" + m), (int, float))] or [0])
        if mag and (widest is None or mag > widest["abs_delta"]):
            widest = {"era": row["era"], "column": row["column"],
                      "unscreened": row["unscreened"],
                      "abs_delta": round(mag, 4),
                      "arms": {m: row.get(m) for m in modes}}

    return {
        "study": "e81_tilt_era_screened",
        "evidence_cutoff": faces["unscreened"]["evidence_cutoff"],
        "spec": {
            "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "eras": [e[0] for e in eras],
            "decomposition": "ladder_monthly ~ alpha + beta*(small_mean - large_mean)",
            "loader": "scripts/panel_screen.py (opt-in; the published TILT-ERA "
                      "face still reads e27.load_universe() unmodified)",
            "faces": "E42 ladder tilt by era, rebuilt per arm from the same "
                     "monthly core builder the published twin uses",
        },
        "screen_reports": reports,
        "faces": faces,
        "delta": delta,
        "answers": {
            "tilt_by_arm_era_bp": tilt_by_arm,
            "tilt_range_by_arm_bp": {arm: _range(list(tilt_by_arm[arm].values()))
                                     for arm in arms},
            "beta_by_arm_era": beta_by_arm,
            "r_squared_by_arm_era": r2_by_arm,
            "sign_flips_vs_unscreened": flips,
            "widest_correction": widest,
            "delta_cells": len(delta),
            "non_zero_delta_cells": len([
                r for r in delta
                if any(r.get("delta_" + m) not in (None, 0) for m in modes)]),
        },
        "honest": [
            "the screen repairs arithmetic impossibility only: a flagged ETF print "
            "may be genuine (ETF daily limits differ from the 10%/20% stock band), "
            "so every arm is a sensitivity face, not a corrected truth",
            "neutralise_int repairs only prints whose price ratio lands on an "
            "integer; neutralise repairs every adjacent print -- the range between "
            "them bounds the correction",
            "eras are calendar partitions of one continuous monthly series; each "
            "row is measured on its own months, so era bp do not add up to the "
            "full-sample number",
            "the tilt regression is descriptive, not a factor-model estimate, and "
            "the newest era is the shortest so its beta carries the widest error",
            "the screened tilt is not a pre-registration and books no trial: it is "
            "the same descriptive face replayed from a different input",
            "descriptive census only: no gate, no verdict, no ledger booking, trial 0",
        ],
    }


# ------------------- leg: E43 four-member reach-back (tilt + neutral spread)

def run_tilt4(outdir, core=None, eras=ERAS):
    """Rebuild the tilt and the size-neutral spread on the four-member sub-ladder.

    E42 measured the era band on two of four eras: the five-member tilt needs
    sh588000, whose first bar is 2020-11-13, so pre2017 had 0 usable months and
    2017-2020 had 1. Dropping the STAR leg (2 broad-cap vs 2 mid/small) reaches
    back to 2013 while keeping the same identity, so the 2013-2020 leg is
    measured instead of skipped. The five-member rows are reported beside it
    wherever both skins can price the same era.
    """
    core = core or _monthly_core()
    rows = {}
    for name, lo, hi in list(eras) + [("full", None, None)]:
        ms = [m for m in core["months4"] if _in_era(m, lo, hi)]
        if len(ms) < 3:
            rows[name] = {"months": len(ms), "skipped": "fewer than 3 usable months"}
            continue
        tilt = [core["tilt4"][m] for m in ms]
        lad = [core["lad_m"][m] for m in ms]
        spread = [core["wide_m"][m] - core["lad_m"][m] for m in ms]
        tm = _moments(tilt)
        beta_l, alpha_l, r2_l = _ols(lad, tilt)
        beta_s, alpha_s, r2_s = _ols(spread, tilt)
        tilt_ann = tm["mean"] * 12.0 * 1e4 if tm["mean"] is not None else None
        raw_ann = sum(spread) / len(spread) * 12.0 * 1e4
        seg_l = _rebase(_slice_curve(core["curves"]["ladder5"], lo, hi))
        seg_w = _rebase(_slice_curve(core["curves"][core["wide_name"]], lo, hi))
        eng_diff = None
        if len(seg_l) > 1 and len(seg_w) > 1:
            yrs = len(seg_l) / 252.0
            eng_diff = round((risk_profile(seg_w, yrs)["ann_return_pct"]
                              - risk_profile(seg_l, yrs)["ann_return_pct"]) * 100, 1)
        pos = sum(1 for t in tilt if t > 0)
        i_max = max(range(len(tilt)), key=lambda i: tilt[i])
        i_min = min(range(len(tilt)), key=lambda i: tilt[i])
        rows[name] = {
            "months": len(ms), "from": ms[0], "to": ms[-1],
            "skin": "4-member (2 broad vs 510500/512100)",
            "tilt_annualised_bp": round(tilt_ann, 1) if tilt_ann is not None else None,
            "tilt_sd_bp": round(tm["sd"] * 1e4, 1) if tm["sd"] is not None else None,
            "tilt_positive_share_pct": round(pos / len(tilt) * 100, 1),
            "tilt_best_month": {"month": ms[i_max], "spread_pct": round(tilt[i_max] * 100, 2)},
            "tilt_worst_month": {"month": ms[i_min], "spread_pct": round(tilt[i_min] * 100, 2)},
            "beta_ladder_on_tilt": round(beta_l, 3) if beta_l is not None else None,
            "alpha_monthly_bp": round(alpha_l * 1e4, 2) if alpha_l is not None else None,
            "r_squared": round(r2_l, 4) if r2_l is not None else None,
            "tilt_explains_ladder_var_pct": round(r2_l * 100, 2) if r2_l is not None else None,
            "ladder_mean_month_pct": round(_moments(lad)["mean"] * 100, 4),
            "spread_raw_ann_bp": round(raw_ann, 1),
            "spread_size_neutral_ann_bp": (round(alpha_s * 12.0 * 1e4, 1)
                                           if alpha_s is not None else None),
            "spread_size_component_ann_bp": (round(beta_s * tilt_ann, 1)
                                             if beta_s is not None and tilt_ann is not None else None),
            "beta_spread_on_tilt": round(beta_s, 3) if beta_s is not None else None,
            "r_squared_spread": round(r2_s, 4) if r2_s is not None else None,
            "engine_ann_diff_bp": eng_diff,
            "arithmetic_vs_geometric_gap_bp": (
                round(raw_ann - eng_diff, 1) if eng_diff is not None else None),
        }
    # the same eras read on the five-member skin where it can be priced at all
    compare = {}
    for name, lo, hi in list(eras) + [("full", None, None)]:
        ms5 = [m for m in core["months"] if _in_era(m, lo, hi)]
        if len(ms5) < 3:
            compare[name] = {"months_5member": len(ms5), "note": "not measurable on 5-member skin"}
            continue
        t5 = [core["tilt"][m] for m in ms5]
        compare[name] = {
            "months_5member": len(ms5),
            "tilt_5member_ann_bp": round(_moments(t5)["mean"] * 12 * 1e4, 1),
            "tilt_4member_ann_bp_same_months": round(
                _moments([core["tilt4"][m] for m in ms5])["mean"] * 12 * 1e4, 1),
            "note": "same months, two skins -- the gap is the STAR leg, not a window effect",
        }
    measured = {k: v for k, v in rows.items() if k != "full" and "tilt_annualised_bp" in v}
    neutral4 = [v["spread_size_neutral_ann_bp"] for v in measured.values()
                if v.get("spread_size_neutral_ann_bp") is not None]
    return {
        "study": "e43_tilt_4member_history",
        "evidence_cutoff": core["cutoff"],
        "spec": {"large": list(TILT_LARGE), "small": list(TILT4_SMALL),
                 "five_member_small": list(TILT_SMALL),
                 "decomposition": "ladder_monthly ~ alpha + beta*(small_mean - large_mean), "
                                  "equal weight 0.5/0.5 on the four-member skin",
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
                 "pick_n": 9999, "exclude_prefixes": ["sh511"], "cost_mult": 1.0},
        "eras": rows,
        "skin_comparison": compare,
        "answers": {
            "eras_measured_4member": len(measured),
            "eras_measured_5member": sum(
                1 for v in compare.values() if v.get("months_5member", 0) >= 3),
            "era_names_measured_4member": sorted(measured),
            "eras_positive_tilt": sum(1 for v in measured.values() if v["tilt_annualised_bp"] > 0),
            "eras_positive_size_neutral": sum(1 for x in neutral4 if x > 0),
            "size_neutral_range_bp": (round(max(neutral4) - min(neutral4), 1) if neutral4 else None),
            "pre2021_eras_newly_measured": [
                k for k, v in measured.items() if v["to"] < "2021-01"][:8],
        },
        "honest": [
            "the four-member skin drops the STAR leg, so its tilt is a broad-vs-mid/small read, "
            "not the E40 five-member identity; the skin_comparison rows price that difference on "
            "the months both skins can see",
            "the ladder and wide curves are the E24/E27 engine's own (module import), unchanged by "
            "the skin choice -- only the tilt regressor changes, so any movement in the neutral "
            "column is the size adjustment, not a different book",
            "eras remain calendar partitions of one continuous monthly series and do not add up",
            "corporate-action guard as in E40 (drops >20% single-day member months)",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
        "dropped_months_4member": core["dropped4"],
    }


# ---------------------- leg: E43 wide-book size composition

def run_widecomp(outdir, core=None, pick_n=9999, exclude=("sh511",), eras=ERAS):
    """Explain the sign of the wide book's tilt beta from its own holdings.

    E42's regression says the wide book loses ground when small caps lead
    (beta -0.216 full, -0.289 in 2024-now). This leg measures the composition
    instead of inferring it: at every decision point, the holdings' weight share
    falling in the ladder's own small-cap legs, its two broad legs, and the rest
    of the book; then the same monthly regression run on the residual bucket
    (universe minus the five ladder members) so the sign is attributable.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    core = core or _monthly_core()
    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal = base.load_panel()[0]
    cutoff = cal[-1]
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    cash = base.load_cash_series(cal)
    rank_cache = {}
    wide_name = "wide_top%d" % pick_n
    curve, aux, _hold = e27.simulate(cal, prices, amounts, universe, cash,
                                     pick_n, 1.0, rank_cache)
    resid_univ = [s for s in universe if s not in base.LADDER]
    rcurve, raux, _rhold = e27.simulate(cal, prices, amounts, resid_univ, cash,
                                        None, 1.0, rank_cache)
    comp = []
    for idx in sorted(set(base.month_end_indices(cal))):
        live = e27._rank(idx, universe, prices, amounts, rank_cache)[:pick_n]
        row = {"date": cal[idx]}
        row.update(_compose_counts(live, TILT_LARGE, TILT_SMALL))
        comp.append(row)
    wide_m = dict(_month_rets(curve))
    resid_m = dict(_month_rets(rcurve))
    lad_m = core["lad_m"]

    def _reg(series, name):
        rows = {}
        for era, lo, hi in list(eras) + [("full", None, None)]:
            ms = [m for m in core["months4"] if _in_era(m, lo, hi) and m in series]
            if len(ms) < 3:
                rows[era] = {"months": len(ms), "skipped": "fewer than 3 usable months"}
                continue
            y = [series[m] for m in ms]
            x = [core["tilt4"][m] for m in ms]
            b, a, r2 = _ols(y, x)
            rows[era] = {
                "months": len(ms), "from": ms[0], "to": ms[-1],
                "mean_month_pct": round(_moments(y)["mean"] * 100, 4),
                "beta_on_tilt": round(b, 3) if b is not None else None,
                "r_squared": round(r2, 4) if r2 is not None else None,
                "ann_bp": round(_moments(y)["mean"] * 12 * 1e4, 1),
            }
        return rows

    spread_m = {m: wide_m[m] - lad_m[m] for m in wide_m if m in lad_m}
    shares = [c for c in comp if c.get("n")]
    avg = (lambda k: round(sum(c[k] for c in shares) / len(shares), 4)) if shares else (lambda k: None)
    return {
        "study": "e43_wide_size_composition",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "ladder_large_legs": list(TILT_LARGE),
                 "ladder_small_legs": list(TILT_SMALL),
                 "residual_bucket": "universe minus the five ladder members, equal weight",
                 "rebalances": len(shares), "holdings": wide_name},
        "composition": comp,
        "composition_summary": {
            "mean_holdings": avg("n"),
            "mean_ladder_small_weight_pct": avg("ladder_small_weight_pct"),
            "mean_ladder_large_weight_pct": avg("ladder_large_weight_pct"),
            "mean_other_weight_pct": avg("other_weight_pct"),
            "min_ladder_all_weight_pct": round(min(
                c["ladder_small_weight_pct"] + c["ladder_large_weight_pct"]
                for c in shares), 4) if shares else None,
            "max_ladder_all_weight_pct": round(max(
                c["ladder_small_weight_pct"] + c["ladder_large_weight_pct"]
                for c in shares), 4) if shares else None,
        },
        "regressions": {"wide_book": _reg(wide_m, "wide"),
                        "residual_bucket": _reg(resid_m, "resid"),
                        "spread_vs_ladder": _reg(spread_m, "spread")},
        "engine": {"wide": {"rebalances": aux["rebalances"],
                            "turnover_per_year": round(aux["turnover_total"] / core["years"], 3),
                            "cost_per_year_bp": round(aux["cost_paid_frac"] / core["years"] * 1e4, 1)},
                   "residual": {"rebalances": raux["rebalances"],
                                "turnover_per_year": round(raux["turnover_total"] / core["years"], 3)}},
        "answers": {
            "mean_ladder_all_weight_pct": (round(avg("ladder_small_weight_pct")
                                                 + avg("ladder_large_weight_pct"), 4)
                                           if shares else None),
            "beta_wide_full": _reg(wide_m, "wide")["full"].get("beta_on_tilt"),
            "beta_residual_full": _reg(resid_m, "resid")["full"].get("beta_on_tilt"),
            "beta_wide_2024_now": _reg(wide_m, "wide").get("2024_now", {}).get("beta_on_tilt"),
            "beta_residual_2024_now": _reg(resid_m, "resid").get("2024_now", {}).get("beta_on_tilt"),
            "sign_explained_by_residual": (
                abs((_reg(wide_m, "wide")["full"].get("beta_on_tilt") or 0)
                    - (_reg(resid_m, "resid")["full"].get("beta_on_tilt") or 0)) < 0.05),
        },
        "honest": [
            "the wide book is every eligible member at equal weight, so the ladder's five legs are "
            "a rounding error in it by construction; the beta therefore cannot come from holding "
            "them, and the residual-bucket regression is the direct measurement of where it does",
            "holdings are read with the engine's own ranking function on the engine's own rank "
            "cache at each decision index, so the composition rows and the simulated curve cannot "
            "disagree about which names were eligible",
            "the residual bucket re-ranks in its own universe, so it is a clean equal-weight "
            "read of non-ladder members, not a subtraction of two curves",
            "the tilt regressor is the four-member skin (E43 reach-back) wherever the five-member "
            "skin cannot be priced; both are reported in the E43 history face",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ---------------------- leg: E43 size-neutral robustness (calendar x cost)

def run_neutralrobust(outdir, core=None, start="2020-01-01", pick_n=9999,
                      exclude=("sh511",), mid_day=15, cost_mults=(1.0, 3.0),
                      raw_all=None):
    """Re-run the size-neutral spread on all four decision calendars at cost x3.

    E42's +181bp newest-era figure has survived neither a fee stress nor a
    calendar shift: E41 moved the calendar and the spread band moved 26bp, and
    E42's cost x3 moved the fee 3x. This leg crosses both axes and reports the
    size-neutral number per cell, so the only surviving claim is the one that
    clears both at once.

    ``raw_all`` lets a screen leg hand in a repaired universe (E81 leg 3). With
    the default ``None`` this calls ``e27.load_universe()`` exactly as before,
    so the published ROBUST face keeps reading the untouched loader.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    core = core or _monthly_core()
    if raw_all is None:
        raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]
    years = len(cal) / 252.0
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    cash = base.load_cash_series(cal)
    rank_cache = {}
    wide_name = "wide_top%d" % pick_n
    month_ends = base.month_end_indices(cal)
    variants = [("me_m1", _shift_indices(month_ends, -1, len(cal))),
                ("me", sorted(set(month_ends))),
                ("me_p1", _shift_indices(month_ends, 1, len(cal))),
                ("mid%d" % mid_day, _mid_month_indices(cal, mid_day))]
    cells = {}
    for mult in cost_mults:
        for vname, idxs in variants:
            rebal = set(idxs)
            curves = {}
            for scheme, univ, n in (("ladder5", base.LADDER, None),
                                    (wide_name, universe, pick_n)):
                curves[scheme], _aux, _h = e27.simulate(cal, prices, amounts, univ, cash,
                                                        n, mult, rank_cache, rebal)
            lm = dict(_month_rets(curves["ladder5"]))
            wm = dict(_month_rets(curves[wide_name]))
            cell = {"rebalances": len(rebal), "era": {}}
            for era, lo, hi in list(ERAS) + [("full", None, None)]:
                ms = [m for m in core["months4"]
                      if _in_era(m, lo, hi) and m in lm and m in wm]
                if len(ms) < 3:
                    cell["era"][era] = {"months": len(ms),
                                        "skipped": "fewer than 3 usable months"}
                    continue
                spread = [wm[m] - lm[m] for m in ms]
                tilt = [core["tilt4"][m] for m in ms]
                b, a, r2 = _ols(spread, tilt)
                raw_ann = sum(spread) / len(spread) * 12 * 1e4
                cell["era"][era] = {
                    "months": len(ms), "from": ms[0], "to": ms[-1],
                    "raw_spread_ann_bp": round(raw_ann, 1),
                    "size_neutral_ann_bp": (round(a * 12 * 1e4, 1) if a is not None else None),
                    "size_component_ann_bp": (round(b * _moments(tilt)["mean"] * 12 * 1e4, 1)
                                              if b is not None else None),
                    "beta_spread_on_tilt": round(b, 3) if b is not None else None,
                    "r_squared": round(r2, 4) if r2 is not None else None,
                }
            cells["cost_x%g|%s" % (mult, vname)] = cell
    newest = {k: v["era"].get("2024_now", {}).get("size_neutral_ann_bp")
              for k, v in cells.items()}
    newest_ok = {k: x for k, x in newest.items() if x is not None}
    full = {k: v["era"].get("full", {}).get("size_neutral_ann_bp") for k, v in cells.items()}
    full_ok = {k: x for k, x in full.items() if x is not None}
    return {
        "study": "e43_size_neutral_robustness",
        "evidence_cutoff": cutoff,
        "spec": {"start": start, "bars": len(cal), "years": round(years, 2),
                 "pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_bp_per_side": base.COST_BP_SIDE, "cost_mults": list(cost_mults),
                 "calendars": [v for v, _ in variants], "mid_month_day": mid_day,
                 "tilt_skin": "4-member (2 broad vs 510500/512100)",
                 "universe_members": len(universe)},
        "cells": cells,
        "answers": {
            "newest_era_size_neutral_by_cell_bp": newest,
            "newest_era_all_positive": (all(x > 0 for x in newest_ok.values())
                                        if newest_ok else None),
            "newest_era_min_bp": min(newest_ok.values()) if newest_ok else None,
            "newest_era_max_bp": max(newest_ok.values()) if newest_ok else None,
            "newest_era_range_bp": (round(max(newest_ok.values()) - min(newest_ok.values()), 1)
                                    if newest_ok else None),
            "full_size_neutral_all_positive": (all(x > 0 for x in full_ok.values())
                                               if full_ok else None),
            "full_min_bp": min(full_ok.values()) if full_ok else None,
            "at_cost_x3_all_positive": (
                all(x > 0 for k, x in newest_ok.items() if k.startswith("cost_x3"))
                if newest_ok else None),
            "cells_measured": len(newest_ok),
        },
        "honest": [
            "cost x3 scales the engine's own 13.041bp/side constant; it is a stress multiplier, "
            "not a measured fee schedule",
            "the calendars differ in session choice only -- universe, ranking and cost model are "
            "shared, so a surviving number is robust to decision timing, not to a different book",
            "the newest era is the shortest and open-ended, so its per-cell regression rests on "
            "the fewest months and carries the widest error",
            "the tilt regressor is the four-member skin; the five-member skin cannot price the "
            "pre-2021 months (E43 reach-back face)",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


def _robdelta_rows(base_label, faces, modes, eras):
    """Cell-by-cell unscreened vs screened table for the E43 robustness face.

    Same contract as ``_spread_delta_rows``: one delta column per arm (a single
    ``delta_<column>`` key would silently keep only the last arm), and a cell
    whose either side is unmeasured stays None rather than being priced as 0.
    """
    rows = []
    order = [n for n, _lo, _hi in list(eras) + [("full", None, None)]]
    base_cells = faces[base_label]["cells"]
    for cell in sorted(base_cells):
        for era in order:
            era_row = (((base_cells.get(cell) or {}).get("era") or {}).get(era)) or {}
            for col in SPREAD_COLUMNS:
                u = era_row.get(col)
                row = {"cell": cell, "era": era, "column": col, "unscreened": u}
                for mode in modes:
                    v = ((((faces[mode]["cells"].get(cell) or {}).get("era") or {})
                          .get(era)) or {}).get(col)
                    row[mode] = v
                    row["delta_" + mode] = (round(v - u, 4)
                                            if isinstance(v, (int, float))
                                            and isinstance(u, (int, float)) else None)
                rows.append(row)
    return rows


def run_screenrob(outdir, pick_n=9999, exclude=("sh511",),
                  modes=("neutralise_int", "neutralise"), eras=ERAS):
    """E81 leg 3: replay the E43 robustness face from the repaired universe.

    E43 is the face that decides whether the size-neutral spread survives
    twelve cells (four calendars x two fee levels), and it is read off the
    as-traded panel, so the same split-print defect E81 screened out of the
    calendar and spread faces lives inside every one of its cells. This leg
    rebuilds the whole cell grid per arm -- engine curves and the member tilt
    regressor together -- and publishes the screened grid beside the untouched
    one. No published face is rewritten.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    arms = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        arms[mode] = repaired

    faces = {}
    for label, univ in arms.items():
        core = _monthly_core(pick_n=pick_n, exclude=(), raw_all=univ)
        face = run_neutralrobust(None, core=core, pick_n=pick_n, exclude=(),
                                 raw_all=univ)
        faces[label] = {"universe_size": len(univ), "cells": face["cells"],
                        "answers": face["answers"]}

    delta = _robdelta_rows("unscreened", faces, modes, eras)

    def _cell_bp(arm, cell, era):
        return ((((faces[arm]["cells"].get(cell) or {}).get("era") or {})
                 .get(era)) or {}).get("size_neutral_ann_bp")

    cells = sorted(faces["unscreened"]["cells"])
    levels = {arm: {c: _cell_bp(arm, c, "2024_now") for c in cells} for arm in faces}

    def _positive(arm):
        xs = [x for x in levels[arm].values() if x is not None]
        return all(x > 0 for x in xs) if xs else None

    def _spread(arm):
        xs = [x for x in levels[arm].values() if x is not None]
        return (round(max(xs) - min(xs), 1) if len(xs) >= 2 else None)

    flips = {}
    for mode in modes:
        flips[mode] = [c for c in cells
                       if levels["unscreened"][c] is not None
                       and levels[mode][c] is not None
                       and (levels["unscreened"][c] > 0) != (levels[mode][c] > 0)]

    moves = []
    for mode in modes:
        best = None
        for c in cells:
            u, v = levels["unscreened"][c], levels[mode][c]
            if u is None or v is None:
                continue
            if best is None or abs(v - u) > abs(best["delta_bp"]):
                best = {"cell": c, "unscreened_bp": u, "screened_bp": v,
                        "delta_bp": round(v - u, 1)}
        moves.append({"arm": mode, "widest_cell_move": best,
                      "no_delta_cells": sum(
                          1 for r in delta
                          if r["column"] == "size_neutral_ann_bp"
                          and r["delta_" + mode] == 0.0)})

    def _era_event_census(mode):
        counts = {n: 0 for n, _lo, _hi in list(eras) + [("full", None, None)]}
        for entry in reports[mode].get("names") or []:
            if entry.get("action") != "neutralise":
                continue
            for pr in entry.get("prints") or []:
                if pr.get("factor_applied") is None:
                    continue
                era = _era_of(pr.get("date"), eras) or "full"
                counts[era] = counts.get(era, 0) + 1
                counts["full"] = counts.get("full", 0) + 1
        return counts

    return {
        "study": "e81_leg3_size_neutral_robustness_screened",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cells": cells, "arms": list(faces), "screen_modes": list(modes),
                 "cost_mults": [1.0, 3.0], "calendars": ["me_m1", "me", "me_p1", "mid15"]},
        "arms": {arm: {"universe_size": faces[arm]["universe_size"],
                       "newest_era_all_positive_by_cell": _positive(arm),
                       "newest_era_range_bp": _spread(arm),
                       "newest_era_by_cell_bp": levels[arm],
                       "delta_cells": 0 if arm == "unscreened" else 1,
                       "repair_events_by_era": (_era_event_census(arm)
                                                if arm in reports else {})}
                 for arm in faces},
        "answers": {
            "newest_era_by_arm_cell_bp": levels,
            "all_positive": {arm: _positive(arm) for arm in faces},
            "range_bp": {arm: _spread(arm) for arm in faces},
            "sign_flips_vs_unscreened": flips,
            "widest_moves": moves,
            "newest_era_unscreened_min_bp": min(
                [x for x in levels["unscreened"].values() if x is not None] or [None]),
            "newest_era_unscreened_max_bp": max(
                [x for x in levels["unscreened"].values() if x is not None] or [None]),
        },
        "delta_table": delta,
        "honest": [
            "screened arms repair integer-ratio prints inside the wide book; the ladder "
            "leg is untouched because its five members are never the repaired names",
            "cost x3 is the engine's own 13.041bp/side constant scaled, not a measured schedule",
            "the screen cannot recover a print that the source never published -- it only "
            "removes the ones the panel shows as integer-ratio jumps",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ------------------------------------- leg: E44 leave-one-out skin decomposition

def _skin_sets(drop=None):
    """(large, small) member legs after dropping one member (None = full skin)."""
    large = tuple(s for s in TILT_LARGE if s != drop)
    small = tuple(s for s in TILT_SMALL if s != drop)
    return large, small


def run_skinloo(outdir, core=None, eras=ERAS, members=None):
    """Price the size-neutral spread on every leave-one-out skin, per era.

    E43's four-member reach-back is itself one leave-one-out skin (STAR dropped),
    and it moved the newest-era size-neutral spread from +181.2bp to +38.5bp. A
    number that moves 4.7x on a naming decision cannot be quoted without the
    skin being disclosed, so every one-member drop is priced here on the same
    engine curves and the same months. The delta column is the answer to "which
    member carries the sign flip", not a new spread estimate.
    """
    core = core or _monthly_core()
    mem, brk = core["mem"], core["brk"]
    lad_m, wide_m = core["lad_m"], core["wide_m"]
    months_all = [m for m in sorted(lad_m) if m in wide_m]
    members = list(members or (TILT_LARGE + TILT_SMALL))

    def read_skin(large, small):
        used, tilt, dropped = _tilt_series(mem, brk, months_all, large, small)
        rows = {}
        for name, lo, hi in list(eras) + [("full", None, None)]:
            ms = [m for m in used if _in_era(m, lo, hi)]
            if len(ms) < 3:
                rows[name] = {"months": len(ms), "skipped": "fewer than 3 usable months"}
                continue
            t = [tilt[m] for m in ms]
            spread = [wide_m[m] - lad_m[m] for m in ms]
            tm = _moments(t)
            beta, alpha, r2 = _ols(spread, t)
            tilt_ann = tm["mean"] * 12.0 * 1e4
            rows[name] = {
                "months": len(ms), "from": ms[0], "to": ms[-1],
                "tilt_annualised_bp": round(tilt_ann, 1),
                "tilt_sd_bp": round(tm["sd"] * 1e4, 1) if tm["sd"] is not None else None,
                "spread_raw_ann_bp": round(sum(spread) / len(spread) * 12.0 * 1e4, 1),
                "spread_size_neutral_ann_bp": (round(alpha * 12.0 * 1e4, 1)
                                               if alpha is not None else None),
                "beta_spread_on_tilt": round(beta, 3) if beta is not None else None,
                "r_squared_spread": round(r2, 4) if r2 is not None else None,
            }
        return rows, dropped

    base_rows, base_dropped = read_skin(TILT_LARGE, TILT_SMALL)
    skins = {"full_5": {"drop": None, "skin": "5-member", "members": list(TILT_LARGE + TILT_SMALL),
                        "eras": base_rows}}
    for drop in members:
        large, small = _skin_sets(drop)
        if not large or not small:
            continue
        rows, dropped = read_skin(large, small)
        skins["drop_" + drop] = {
            "drop": drop,
            "skin": "%d-member" % (len(large) + len(small)),
            "members": list(large + small),
            "eras": rows,
            "dropped_months": len(dropped),
        }

    # per-era delta against the full skin: which member moves the number, and by how much
    delta = {}
    for name in skins:
        if name == "full_5":
            continue
        d = {}
        for era in ("2017_2020", "2021_2023", "2024_now", "full"):
            a = skins[name]["eras"].get(era, {}).get("spread_size_neutral_ann_bp")
            b = base_rows.get(era, {}).get("spread_size_neutral_ann_bp")
            d[era] = round(a - b, 1) if (a is not None and b is not None) else None
        delta[skins[name]["drop"]] = d

    def sign(x):
        if x is None:
            return None
        return 1 if x > 0 else (-1 if x < 0 else 0)

    flips = {}
    for era in ("2021_2023", "2024_now"):
        b = base_rows.get(era, {}).get("spread_size_neutral_ann_bp")
        flips[era] = {
            "full_skin_bp": b,
            "members_whose_removal_flips_sign": [
                m for m, d in delta.items()
                if d.get(era) is not None and sign(d[era] + (b or 0)) != sign(b)
            ],
            "largest_removal_effect": (
                sorted(((abs(d[era]), m) for m, d in delta.items() if d.get(era) is not None),
                       reverse=True) or [(None, None)])[0][1],
        }

    return {
        "leg": "e44_skin_loo",
        "evidence_cutoff": core["cutoff"],
        "engine": {"wide_book": core["wide_name"], "ladder": "ladder5",
                   "cost_bp_per_side": 13.041, "convention": "monthly additive bp"},
        "eras": [{"name": n, "lo": lo, "hi": hi} for n, lo, hi in eras],
        "skins": skins,
        "delta_vs_full_skin_bp": delta,
        "sign_flip_attribution": flips,
        "answers": {
            "which_member_carries_the_2021_2023_vs_2024_now_flip":
                flips["2024_now"]["largest_removal_effect"],
            "spread_range_across_skins_2024_now_bp": [
                min(r["eras"]["2024_now"]["spread_size_neutral_ann_bp"]
                    for r in skins.values()
                    if r["eras"].get("2024_now", {}).get("spread_size_neutral_ann_bp") is not None),
                max(r["eras"]["2024_now"]["spread_size_neutral_ann_bp"]
                    for r in skins.values()
                    if r["eras"].get("2024_now", {}).get("spread_size_neutral_ann_bp") is not None),
            ],
            "four_member_row_matches_e43": (
                "drop_sh588000 is exactly the E43 four-member skin; its 2024_now "
                "size-neutral number is the one E43 headlines"),
        },
        "honest": [
            "every skin is priced on the same engine curves, the same months and the same "
            "13.041bp/side constant -- only the tilt regressor changes",
            "a leave-one-out skin is not an alternative portfolio: it is the same wide book "
            "measured against a narrower size reference, so the spread levels are not tradeable "
            "alternatives to each other",
            "the sign-flip attribution is a decomposition, not a forecast; the newest era is the "
            "shortest and carries the widest error",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# -------------------------------- leg: E44 eligibility burn-in / missing years

def _first_eligible_idx(series, min_bars):
    """First index whose trailing ``min_bars`` window is fully priced.

    Mirrors ``e24_ladder_weighting.elig`` exactly: eligibility needs MIN_BARS of
    *consecutive, non-missing, in-window* closes, so it is window-relative -- the
    first ~250 sessions of any start window are structurally un-investable no
    matter how long the symbol's own history is.
    """
    run = 0
    for i, v in enumerate(series):
        run = run + 1 if v is not None else 0
        if run >= min_bars:
            return i
    return None


def _annual_rets(marks):
    """{year: pct} from month-end marks, each year chained off the prior year-end."""
    by_year = {}
    for m, v in marks:
        by_year[m[:4]] = v
    out = {}
    prev = None
    for y in sorted(by_year):
        if prev:
            out[y] = round((by_year[y] / prev - 1.0) * 100, 2)
        prev = by_year[y]
    return out


def run_burnin(outdir, starts=("2013-01-01", "2016-01-01", "2018-01-01", "2020-01-01"),
               pick_n=9999, exclude=("sh511",), min_bars=None):
    """Attribute the missing pre-2017 years to the eligibility gate, not to mystery.

    E40 measured that the book sits in repo for 263 of its first 1,645 bars and
    that the first invested bar is 2021-02-01 on a 2020 start. This leg measures
    the gate itself: how many sessions each start window spends un-invested, when
    the first eligible set actually arrives (and how many names it holds), how
    much of that is the 250-bar rule being window-relative versus the panel's own
    symbol start dates, and what 2013-2016 is worth on the same spec once the
    burn-in is paid outside the measured window (a warm run on the full calendar,
    sliced afterwards).
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    min_bars = int(min_bars or base.MIN_BARS)
    prev_min_bars = base.MIN_BARS
    base.MIN_BARS = min_bars   # e27.load_universe and base.elig both read this global
    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    universe = [s for s in all_syms if s in raw_all]

    def build(cal):
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = raw_all.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        return prices, amounts

    # one warm pair of curves on the whole calendar: the burn-in is paid before
    # the measured slice begins, so the slice prices the spec, not the gate.
    warm_prices, warm_amounts = build(cal_full)
    warm = {}
    for name, univ, n in (("ladder5", base.LADDER, None), ("wide", universe, pick_n)):
        curve, aux, _ = e27.simulate(cal_full, warm_prices, warm_amounts, univ,
                                     None, n, 1.0, {})
        warm[name] = curve

    def slice_faces(curve, lo, hi=None):
        part = [pt for pt in curve if pt[0] >= lo and (hi is None or pt[0] <= hi)]
        if len(part) < 3:
            return None
        me = _month_ends(part)
        if len(me) < 2:
            return None
        yrs = len(part) / 252.0
        return {
            "bars": len(part),
            "from": part[0][0], "to": part[-1][0],
            "ann_return_pct": round((part[-1][1] / part[0][1]) ** (1.0 / yrs) * 100 - 100, 2),
            "max_drawdown_pct": risk_profile(part, yrs)["max_drawdown_pct"],
            "annual_returns_pct": _annual_rets(me),
            "monthly_marks": len(me),
        }

    # calendar-year returns on the warm curve itself: a year's return chains off
    # the prior year-end mark, which a slice starting inside the year cannot see.
    warm_annual = {name: _annual_rets(_month_ends(warm[name])) for name in warm}

    windows = {}
    for start in starts:
        cal = [d for d in cal_full if d >= start]
        years = len(cal) / 252.0
        prices, amounts = build(cal)
        rebal = base.month_end_indices(cal)
        elig_series = []
        for ri in rebal:
            elig_series.append({
                "date": cal[ri], "idx": ri,
                "n_priced": sum(1 for s in universe if prices[s][ri] is not None),
                "n_eligible": sum(1 for s in universe if base.elig(prices[s], ri)),
            })
        first_trade_idx = next((ri for ri in rebal
                                if any(base.elig(prices[s], ri) for s in universe)), None)
        first_ladder_idx = next((ri for ri in rebal
                                 if any(base.elig(prices[s], ri) for s in base.LADDER)), None)
        # earliest decision the 250-bar rule can possibly allow in this window
        allowed = [ri for ri in rebal if ri >= min_bars]
        # per-symbol arrival of eligibility inside the window
        arrival = {}
        for s in universe:
            i = _first_eligible_idx(prices[s], min_bars)
            if i is not None:
                arrival[s] = cal[i]
        hist = {}
        for d in arrival.values():
            hist[d[:4]] = hist.get(d[:4], 0) + 1
        first_invested = (cal[first_trade_idx + 1] if first_trade_idx is not None else None)
        uninv = (first_trade_idx + 1) if first_trade_idx is not None else len(cal) - 1

        naive = {}
        for name, univ, n in (("ladder5", base.LADDER, None), ("wide", universe, pick_n)):
            curve, aux, _ = e27.simulate(cal, prices, amounts, univ, None, n, 1.0, {})
            naive[name] = {
                "ann_return_pct": risk_profile(curve, years)["ann_return_pct"],
                "first_curve_bar": curve[0][0],
            }
        windows[start] = {
            "bars": len(cal),
            "years": round(years, 2),
            "min_bars_gate": min_bars,
            "rebalance_decisions": len(rebal),
            "first_rebalance": cal[rebal[0]] if rebal else None,
            "earliest_possible_trading_decision": cal[allowed[0]] if allowed else None,
            "earliest_possible_gate_date": cal[min_bars] if len(cal) > min_bars else None,
            "first_trading_rebalance": cal[first_trade_idx] if first_trade_idx is not None else None,
            "first_invested_bar": first_invested,
            "sessions_uninvested": uninv,
            "sessions_uninvested_share_pct": round(uninv / max(1, len(cal) - 1) * 100, 2),
            "months_uninvested": round(uninv / 21.0, 1),
            "first_trading_rebalance_ladder5": (cal[first_ladder_idx]
                                                if first_ladder_idx is not None else None),
            "eligible_at_first_invested": next(
                (r["n_eligible"] for r in elig_series
                 if first_trade_idx is not None and r["idx"] == first_trade_idx), None),
            "first_rebalance_with_elig_ge_5": next(
                (r["date"] for r in elig_series if r["n_eligible"] >= 5), None),
            "first_rebalance_with_elig_ge_20": next(
                (r["date"] for r in elig_series if r["n_eligible"] >= 20), None),
            "eligibility_at_rebalances": elig_series,
            "symbol_first_eligible_hist_by_year": dict(sorted(hist.items())),
            "symbols_eligible": len(arrival),
            "symbols_in_universe": len(universe),
            "naive_start_curves": naive,
            "warm_slice": {name: slice_faces(warm[name], start) for name in warm},
        }

    # the question the E43/E44 line actually leaves open: is 2013-2016 worth
    # anything on the same spec, and how much of it does the gate eat?
    span = {}
    for lo, hi in (("2013-01-01", "2016-12-31"), ("2017-01-01", "2020-12-31"),
                   ("2021-01-01", None)):
        block = {"%s..%s" % (lo, hi or "now"): {}}
        for name in warm:
            face = slice_faces(warm[name], lo, hi)
            if face is not None:
                y0, y1 = lo[:4], (hi or "9999")[:4]
                face["calendar_year_returns_pct"] = {
                    y: v for y, v in warm_annual[name].items() if y0 <= y <= y1}
            block["%s..%s" % (lo, hi or "now")][name] = face
        span.update(block)

    base.MIN_BARS = prev_min_bars
    return {
        "study": "e44_eligibility_burnin",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "starts": list(starts), "min_bars": min_bars,
                 "cost_bp_per_side": base.COST_BP_SIDE,
                 "calendar_first": cal_full[0], "calendar_last": cal_full[-1]},
        "windows": windows,
        "era_spans_warm": span,
        "answers": {
            "gate_is_window_relative": True,
            "why_first_set_is_late": (
                "elig() needs %d consecutive non-missing closes measured inside the start "
                "window, so no decision before index %d can hold anything: the first "
                "possible invested bar is the session after the first month end at or "
                "past index %d" % (min_bars, min_bars, min_bars)),
            "sessions_uninvested_by_start": {
                s: windows[s]["sessions_uninvested"] for s in windows},
            "first_invested_bar_by_start": {
                s: windows[s]["first_invested_bar"] for s in windows},
            "warm_2013_2016_wide_ann_pct": (
                span["2013-01-01..2016-12-31"].get("wide") or {}).get("ann_return_pct"),
            "warm_2013_2016_ladder_ann_pct": (
                span["2013-01-01..2016-12-31"].get("ladder5") or {}).get("ann_return_pct"),
            "naive_2013_start_wide_ann_pct":
                windows["2013-01-01"]["naive_start_curves"]["wide"]["ann_return_pct"],
        },
        "honest": [
            "the burn-in is a property of the engine's membership rule, not a data defect: "
            "the same %d-bar rule gates every scheme" % min_bars,
            "warm slices pay the burn-in on bars outside the measured span; the naive "
            "columns are the same spec started cold, and the difference is the gate",
            "symbols_in_universe counts de-duplicated panels; eligibility arrival is per "
            "window because the rule is window-relative",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


def run_knife(outdir, starts=("2013-01-01", "2016-01-01", "2018-01-01", "2020-01-01"),
              knives=(60, 120, 250), pick_n=9999, exclude=("sh511",), resume=True):
    """E45: price the knife edge of the MIN_BARS eligibility rule.

    The 250-bar gate is a deliberate no-thin-history-listing rule, but nobody has
    measured what it buys against what it costs. Rerun the identical spec at
    MIN_BARS 60/120/250 and read two things per window: the annualised return the
    book earns once it is finally allowed to trade, and the size of the eligible
    set on that first trade. A cheaper gate that buys most of the return back
    without flooding the book with one-month-old listings means the 250 is a
    six-month tax; early bars that read as junk at 60 mean it is earning its keep.

    Per-knife checkpoints land as ``KNIFE-<cutoff>-mb<n>.json`` so a killed pass
    resumes instead of restarting; the assembled face is written once all knives
    are on disk. Descriptive only: no gate, no verdict, no prereg, no trials.
    """
    per_knife = {}
    for mb in knives:
        cached = None
        if resume:
            hit = [p for p in sorted(os.listdir(outdir) or [])
                   if p.startswith("KNIFE-") and p.endswith("-mb%d.json" % mb)] \
                if os.path.isdir(outdir) else []
            if hit:
                try:
                    with open(os.path.join(outdir, hit[-1]), encoding="utf-8") as fh:
                        cached = json.load(fh)
                except Exception:
                    cached = None
        if cached is None:
            cached = run_burnin(None, starts=starts, pick_n=pick_n,
                                exclude=exclude, min_bars=mb)
            write_json(outdir, "KNIFE-%s-mb%d.json"
                       % (cached["evidence_cutoff"].replace("-", ""), mb), cached)
        per_knife[mb] = cached

    cutoff = per_knife[knives[0]]["evidence_cutoff"]
    rows = {}
    for start in starts:
        rows[start] = {}
        for mb in knives:
            w = per_knife[mb]["windows"].get(start)
            if not w:
                continue
            rows[start][mb] = {
                "min_bars": mb,
                "sessions_uninvested": w["sessions_uninvested"],
                "sessions_uninvested_share_pct": w["sessions_uninvested_share_pct"],
                "first_invested_bar": w["first_invested_bar"],
                "eligible_at_first_invested": w["eligible_at_first_invested"],
                "symbols_in_universe": w["symbols_in_universe"],
                "wide_ann_return_pct": (w["naive_start_curves"]["wide"] or {}).get(
                    "ann_return_pct"),
                "ladder_ann_return_pct": (w["naive_start_curves"]["ladder5"] or {}).get(
                    "ann_return_pct"),
                "eligible_set_at_first_trade": w["eligible_at_first_invested"],
            }

    # the two questions the batch asks, answered off the same grid
    answers = {}
    for start, by_mb in rows.items():
        base_face = by_mb.get(250) or {}
        cheap = by_mb.get(120) or by_mb.get(60) or {}
        if not base_face or not cheap:
            continue
        answers[start] = {
            "return_gap_120_vs_250_pp": (
                round(cheap["wide_ann_return_pct"] - base_face["wide_ann_return_pct"], 2)
                if (cheap.get("wide_ann_return_pct") is not None
                    and base_face.get("wide_ann_return_pct") is not None) else None),
            "eligible_gap_120_vs_250": (
                cheap["eligible_at_first_invested"] - base_face["eligible_at_first_invested"]
                if (cheap.get("eligible_at_first_invested") is not None
                    and base_face.get("eligible_at_first_invested") is not None) else None),
        }

    return {
        "study": "e45_burnin_knife",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "starts": list(starts), "knives": list(knives),
                 "cost_bp_per_side": per_knife[knives[0]]["spec"]["cost_bp_per_side"]},
        "grid": rows,
        "answers": answers,
        "honest": [
            "the same spec runs at each knife; only the membership rule moves, so any "
            "return difference is the gate's price, not a different strategy",
            "a bigger eligible set at a cheaper gate is not automatically good: the "
            "question is whether the extra names are tradeable or one-month-old listings",
            "descriptive census only: no gate, no verdict, no prereg, no trials consumed",
        ],
    }


# ---------------------------- leg: E45 warm slices vs cold-start windows
#
# Every era spread since E41 is quoted off the E24/E27 engine, and r1120 measured
# that the 250-bar rule deletes 259-265 sessions (12.3 months) from the front of
# ANY start window. Both books share that dead block, so the spread itself should
# be immune -- but the block is not free: while the book holds nothing the engine
# carries cash at weight 1.0, so the dead block accrues at the repo rate for both
# books and it is a very different share of a 2024 window than of a 2013 one.
# This leg puts the two quotes side by side per era -- the warm slice (one curve
# on the full calendar, sliced afterwards, so the burn-in is paid outside the
# measured span) against the cold start (a fresh curve from the era's own start)
# -- and reports the dead block's size and what it accrued in each case.

def _bars_before(curve, date):
    """Bars in ``curve`` strictly before ``date``; 0 when ``date`` is unknown."""
    if not date:
        return 0
    return sum(1 for d, _v in curve if d < date)


def _curve_faces(curve):
    """Rebased annualised face of one slice; None when the slice is too short."""
    seg = _rebase(curve)
    if len(seg) < 3:
        return None
    prof = risk_profile(seg, len(seg) / 252.0)
    return {"from": seg[0][0], "to": seg[-1][0], "bars": len(seg),
            "ann_return_pct": prof["ann_return_pct"],
            "max_drawdown_pct": prof["max_drawdown_pct"]}


def _spread_bp(ladder_face, wide_face):
    """wide minus ladder in bp on the annualised column; None if either is missing."""
    if not ladder_face or not wide_face:
        return None
    return round((wide_face["ann_return_pct"] - ladder_face["ann_return_pct"]) * 100, 1)


def _cash_accrual_pct(cash, cal_x, upto_date):
    """Compounded cash return over the bars before ``upto_date``, in pct."""
    if not cash or not upto_date:
        return 0.0
    tot = 1.0
    for d in cal_x:
        if d >= upto_date:
            break
        tot *= (1.0 + cash["series"].get(d, 0.0))
    return round((tot - 1.0) * 100.0, 3)


def run_warmspread(outdir, eras=ERAS, pick_n=9999, exclude=("sh511",)):
    """E45: does the era ordering survive once the dead block is outside the window?"""
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal = base.load_panel()[0]
    cutoff = cal[-1]
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    wide_name = "wide_top%d" % pick_n
    books = (("ladder5", list(base.LADDER), None), (wide_name, universe, pick_n))

    def build(cal_x):
        px, ax = {}, {}
        for s in all_syms:
            c, a = raw_all.get(s, ({}, {}))
            px[s] = [c.get(d) for d in cal_x]
            ax[s] = [a.get(d) for d in cal_x]
        return px, ax

    def first_invested(cal_x, px, book_univ):
        """First bar the book can actually hold something on this calendar."""
        rebal = base.month_end_indices(cal_x)
        idx = next((ri for ri in rebal
                    if any(base.elig(px[s], ri) for s in book_univ)), None)
        if idx is None:
            return None
        return cal_x[idx + 1] if idx + 1 < len(cal_x) else None

    # warm: one pair of curves on the whole calendar, sliced per era afterwards
    warm, warm_first = {}, {}
    for name, univ, n in books:
        curve, _aux, _hold = e27.simulate(cal, prices, amounts, univ,
                                          base.load_cash_series(cal), n, 1.0, {})
        warm[name] = curve
        warm_first[name] = first_invested(cal, prices, univ)

    rows = {}
    for era_name, lo, hi in eras:
        cold_cal = [d for d in cal if lo is None or d >= lo]
        cpx, cax = build(cold_cal)
        ccash = base.load_cash_series(cold_cal)
        cold, cold_first = {}, {}
        for name, univ, n in books:
            curve, _aux, _hold = e27.simulate(cold_cal, cpx, cax, univ, ccash, n, 1.0, {})
            cold[name] = [pt for pt in curve if hi is None or pt[0] <= hi]
            cold_first[name] = first_invested(cold_cal, cpx, univ)
        warm_slice = {name: [pt for pt in warm[name]
                             if (lo is None or pt[0] >= lo) and (hi is None or pt[0] <= hi)]
                      for name, _u, _n in books}
        wl = _curve_faces(warm_slice["ladder5"])
        ww = _curve_faces(warm_slice[wide_name])
        cl = _curve_faces(cold["ladder5"])
        cw = _curve_faces(cold[wide_name])
        bars = max(len(warm_slice["ladder5"]), 1)
        warm_dead = _bars_before(warm_slice["ladder5"], warm_first["ladder5"])
        cold_dead = _bars_before(cold["ladder5"], cold_first["ladder5"])
        rows[era_name] = {
            "from": (wl or cl or {}).get("from"), "to": (wl or cl or {}).get("to"),
            "bars": bars,
            "warm": {"ladder": wl, "wide": ww, "spread_bp": _spread_bp(wl, ww),
                     "first_invested_bar": warm_first["ladder5"],
                     "dead_block_bars": warm_dead,
                     "dead_block_share_pct": round(warm_dead / max(1, bars - 1) * 100, 2)},
            "cold": {"ladder": cl, "wide": cw, "spread_bp": _spread_bp(cl, cw),
                     "first_invested_bar": cold_first["ladder5"],
                     "dead_block_bars": cold_dead,
                     "dead_block_share_pct": round(cold_dead / max(1, bars - 1) * 100, 2),
                     "cash_accrued_in_dead_block_pct": _cash_accrual_pct(
                         ccash, cold_cal, cold_first["ladder5"])},
        }
        if rows[era_name]["warm"]["spread_bp"] is not None \
                and rows[era_name]["cold"]["spread_bp"] is not None:
            rows[era_name]["warm_minus_cold_bp"] = round(
                rows[era_name]["warm"]["spread_bp"] - rows[era_name]["cold"]["spread_bp"], 1)

    # the cold newest-era number is the same market as a warm forward slice: from the
    # first allowed decision onward both books hold identical weights, so a warm slice
    # started at that bar must reproduce the cold reading -- if it does, the gap is the
    # skipped bars and nothing else.
    newest = eras[-1][0] if eras else None
    live_from = (rows.get(newest) or {}).get("cold", {}).get("first_invested_bar")
    live = {}
    if live_from:
        ls = [pt for pt in warm["ladder5"] if pt[0] >= live_from]
        ws = [pt for pt in warm[wide_name] if pt[0] >= live_from]
        lf, wf = _curve_faces(ls), _curve_faces(ws)
        live = {"from": live_from, "to": (lf or {}).get("to"), "bars": len(ls),
                "ladder": lf, "wide": wf, "spread_bp": _spread_bp(lf, wf)}
        if newest and "warm_live_window" not in rows[newest]:
            rows[newest]["warm_live_window"] = live

    warm_order = [(k, v["warm"]["spread_bp"]) for k, v in rows.items()
                  if v["warm"]["spread_bp"] is not None]
    cold_order = [(k, v["cold"]["spread_bp"]) for k, v in rows.items()
                  if v["cold"]["spread_bp"] is not None]
    warm_sorted = sorted(warm_order, key=lambda kv: kv[1])
    cold_sorted = sorted(cold_order, key=lambda kv: kv[1])
    return {
        "study": "e45_warm_spread",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_mult": 1.0, "cost_bp_per_side": base.COST_BP_SIDE,
                 "calendar_from": cal[0], "min_bars": base.MIN_BARS,
                 "warm": "one pair of curves on the full calendar, sliced per era",
                 "cold": "a fresh pair started at the era's own first bar, "
                         "measured over the same era span",
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
                 "universe_members": len(universe)},
        "eras": rows,
        "answers": {
            "warm_order_thinnest_to_widest": warm_sorted,
            "cold_order_thinnest_to_widest": cold_sorted,
            "newest_era_is_thinnest_warm": bool(warm_sorted) and warm_sorted[0][0] == "2024_now",
            "newest_era_is_thinnest_cold": bool(cold_sorted) and cold_sorted[0][0] == "2024_now",
            "ordering_preserved": [k for k, _v in warm_sorted] == [k for k, _v in cold_sorted],
            "newest_era_live_window": live,
            "cold_minus_live_bp": (
                round(rows[newest]["cold"]["spread_bp"] - live["spread_bp"], 1)
                if newest and live.get("spread_bp") is not None
                and rows[newest]["cold"]["spread_bp"] is not None else None),
            "max_warm_minus_cold_bp": max(
                (abs(v["warm_minus_cold_bp"]) for v in rows.values()
                 if "warm_minus_cold_bp" in v), default=None),
            "cold_dead_block_share_pct_by_era": {
                k: v["cold"]["dead_block_share_pct"] for k, v in rows.items()},
            "cold_cash_accrued_in_dead_block_pct_by_era": {
                k: v["cold"]["cash_accrued_in_dead_block_pct"] for k, v in rows.items()},
        },
        "honest": [
            "the warm slice pays the burn-in on bars before the measured span, so it prices the "
            "spec; the cold window is the same spec started at the era's own first bar, and the "
            "gap is the gate plus whatever the dead block accrued at the repo rate",
            "the pre2017 era starts where the panel starts, so its warm and cold quotes are the "
            "same curve by construction -- that is a disclosure, not a measurement",
            "the dead block is identified by the first decision the 250-bar rule allows, not by "
            "inspecting weights; no rebalance before it can hold a name",
            "the ratio of two rebased ann% is not a tradable sleeve, and era slices are not "
            "additive across eras",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ---------------------------- leg: E46 is the era edge front-loaded?
#
# E45 found the newest era's whole edge earned before the eligibility gate would
# let a cold book hold anything (2024-01..2025-01), with the live span negative.
# That is one era observed once. This leg asks the same question of every era and
# without any gate argument: split each era's slice of the same warm curve into
# halves and see whether the spread lives in one half or is spread through the
# era. A sign flip inside an era means the era's single number is an average of
# two different markets; a flat split means the number is a property of the era.

def _split_curve(curve, parts):
    """``parts`` contiguous chunks of a curve, the last one taking the remainder."""
    n = len(curve)
    if parts < 1 or n < parts * 2:
        return []
    step = n // parts
    return [curve[i * step:(i + 1) * step] for i in range(parts - 1)] + \
           [curve[(parts - 1) * step:]]


def _livespan_setup(exclude=("sh511",), pick_n=9999, cost_mult=1.0):
    """Warm pair (ladder vs wide book) on the full calendar, computed once.

    Shared by run_livespan (one cut per call) and run_cutcurve (parts 2..12
    over the same curves), so a cut sweep pays for the simulation once per
    cost level instead of once per cut.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal = base.load_panel()[0]
    cutoff = cal[-1]
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    wide_name = "wide_top%d" % pick_n
    curves = {}
    for name, univ, n in (("ladder5", list(base.LADDER), None), (wide_name, universe, pick_n)):
        curve, _aux, _hold = e27.simulate(cal, prices, amounts, univ,
                                          base.load_cash_series(cal), n, cost_mult, {})
        curves[name] = curve
    return {"cutoff": cutoff, "curves": curves, "universe": universe,
            "wide_name": wide_name}


def _livespan_rows(curves, eras, parts, wide_name):
    """Per-era part rows for one cut (the E46 split body)."""
    rows = {}
    for era_name, lo, hi in eras:
        lad = [pt for pt in curves["ladder5"]
               if (lo is None or pt[0] >= lo) and (hi is None or pt[0] <= hi)]
        wid = [pt for pt in curves[wide_name]
               if (lo is None or pt[0] >= lo) and (hi is None or pt[0] <= hi)]
        if len(lad) < 2 * parts or len(wid) != len(lad):
            rows[era_name] = {"bars": len(lad), "skipped": "too few bars to split"}
            continue
        chunks = []
        for k, (lc, wc) in enumerate(zip(_split_curve(lad, parts),
                                         _split_curve(wid, parts))):
            lf, wf = _curve_faces(lc), _curve_faces(wc)
            chunks.append({"part": k + 1, "from": (lf or {}).get("from"),
                           "to": (lf or {}).get("to"), "bars": len(lc),
                           "ladder": lf, "wide": wf, "spread_bp": _spread_bp(lf, wf)})
        whole = _spread_bp(_curve_faces(lad), _curve_faces(wid))
        spreads = [c["spread_bp"] for c in chunks if c["spread_bp"] is not None]
        rows[era_name] = {
            "from": lad[0][0], "to": lad[-1][0], "bars": len(lad),
            "era_spread_bp": whole, "parts": chunks,
            "part_spreads_bp": spreads,
            "sign_flips_inside_era": (len(spreads) > 1
                                      and min(spreads) < 0 < max(spreads)),
            "widest_part": (max(chunks, key=lambda c: c["spread_bp"] or -1e9)["part"]
                            if spreads else None),
            "part_band_bp": (round(max(spreads) - min(spreads), 1) if spreads else None),
        }
    return rows


def run_livespan(outdir, eras=ERAS, pick_n=9999, exclude=("sh511",), parts=2,
                 cost_mult=1.0):
    """E46: split every era in `parts` chunks and read where its spread is earned."""
    import e24_ladder_weighting as base

    setup = _livespan_setup(exclude=exclude, pick_n=pick_n, cost_mult=cost_mult)
    cutoff = setup["cutoff"]
    curves = setup["curves"]
    universe = setup["universe"]
    wide_name = setup["wide_name"]
    rows = _livespan_rows(curves, eras, parts, wide_name)
    flipped = [k for k, v in rows.items() if v.get("sign_flips_inside_era")]
    return {
        "study": "e46_live_span_split",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_mult": cost_mult, "cost_bp_per_side": base.COST_BP_SIDE,
                 "parts": parts,
                 "curve": "one warm pair on the full calendar, sliced per era then split",
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
                 "universe_members": len(universe)},
        "eras": rows,
        "answers": {
            "eras_split": len([v for v in rows.values() if v.get("parts")]),
            "eras_with_internal_sign_flip": flipped,
            "era_count_with_internal_sign_flip": len(flipped),
            "widest_part_by_era": {k: v.get("widest_part") for k, v in rows.items()
                                   if v.get("widest_part") is not None},
            "part_band_bp_by_era": {k: v.get("part_band_bp") for k, v in rows.items()
                                    if v.get("part_band_bp") is not None},
        },
        "honest": [
            "the split is by bar count, not by calendar year, so the halves are equal in "
            "sessions and unequal in spans only by trading density",
            "an internal sign flip does not say which half is the future; it says the era's "
            "single number is an average of two different markets and must be quoted as such",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


def _cut_summary(rows):
    """Cut-level roll-up of _livespan_rows: who flips, how wide, which parts are dead.

    Pure function so the sweep's arithmetic is testable without a panel.
    """
    flips = sorted(k for k, v in rows.items() if v.get("sign_flips_inside_era"))
    bands = {k: v.get("part_band_bp") for k, v in rows.items()
             if v.get("part_band_bp") is not None}
    dead = {}
    for k, v in rows.items():
        spreads = [s for s in (v.get("part_spreads_bp") or []) if s is not None]
        n_dead = sum(1 for s in spreads if abs(s) < 0.05)
        if n_dead:
            dead[k] = n_dead
    vals = sorted(bands.values())
    med = None
    if vals:
        n = len(vals)
        med = round(vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0, 1)
    return {"eras_flipping": flips,
            "flip_count": len(flips),
            "bands_bp": bands,
            "band_mean_bp": round(sum(vals) / len(vals), 1) if vals else None,
            "band_median_bp": med,
            "band_widest_era": max(bands, key=lambda k: bands[k]) if bands else None,
            "zero_spread_parts_by_era": dead}


def _widest_window(row):
    """'from..to' of an era's widest part, or None when the part is missing."""
    wid = row.get("widest_part")
    for p in (row.get("parts") or []):
        if p.get("part") == wid:
            return "%s..%s" % (p.get("from"), p.get("to"))
    return None


def run_cutcurve(outdir, eras=ERAS, pick_n=9999, exclude=("sh511",),
                 costs=(1.0, 3.0), parts_range=range(2, 13)):
    """E58: one face over the whole cut axis (parts 2..12 at each cost level).

    The eleven cuts exist as eleven single faces, so any claim about the band
    is a claim about which cut it was cut at. This leg replays the same warm
    pair once per cost level and slices it at every cut, so band-vs-cut,
    flip-vs-cut and the widest part's window are readable side by side.
    """
    import e24_ladder_weighting as base

    grid = {}
    cutoffs = set()
    for cost in costs:
        setup = _livespan_setup(exclude=exclude, pick_n=pick_n, cost_mult=cost)
        cutoffs.add(setup["cutoff"])
        per_cut = {}
        for parts in parts_range:
            rows = _livespan_rows(setup["curves"], eras, parts, setup["wide_name"])
            per_cut[str(parts)] = {
                "summary": _cut_summary(rows),
                "eras": {k: {"era_spread_bp": v.get("era_spread_bp"),
                             "part_band_bp": v.get("part_band_bp"),
                             "widest_part": v.get("widest_part"),
                             "widest_window": _widest_window(v),
                             "part_spreads_bp": v.get("part_spreads_bp")}
                         for k, v in rows.items()},
            }
        grid["x%g" % cost] = per_cut

    era_names = [n for n, _lo, _hi in eras]
    levels = {}
    drift = {}
    for key, cuts in grid.items():
        levels[key] = {e: sorted({c["eras"].get(e, {}).get("era_spread_bp")
                                  for c in cuts.values()}) for e in era_names}
        drift[key] = {}
        for e in era_names:
            vals = [c["eras"].get(e, {}).get("era_spread_bp") for c in cuts.values()]
            vals = [v for v in vals if v is not None]
            drift[key][e] = round(max(vals) - min(vals), 1) if vals else None

    series = {key: {f: {p: cuts[p]["summary"][f] for p in cuts}
                    for f in ("flip_count", "band_mean_bp", "band_median_bp",
                              "band_widest_era")}
              for key, cuts in grid.items()}
    return {
        "study": "e58_parts_cut_curve",
        "evidence_cutoff": sorted(cutoffs)[-1],
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_mult": list(costs), "cost_bp_per_side": base.COST_BP_SIDE,
                 "parts_swept": [min(parts_range), max(parts_range)],
                 "curve": "one warm pair per cost level, sliced at every cut",
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras]},
        "cuts": grid,
        "answers": {
            "era_level_by_cost": levels,
            "era_level_drift_bp": drift,
            "series_by_cost": series,
            "cuts_swept": len(list(parts_range)),
        },
        "honest": [
            "the cuts are bar-count splits of one warm curve, not separate books: the "
            "simulation is run once per cost level, so no cut can differ by engine state",
            "a band is max(part spread) - min(part spread); the sweep shows how that range "
            "moves with the cut, it does not convert a band into a risk or an error bar",
            "widest_window names the window at that cut and can move when the cut moves, "
            "so a window quoted without its cut is not reproducible",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# ------------------------------------------- leg: mid-month vs month-end churn

def _decision_sets(cal, prices, amounts, universe, pick_n, rebal_idxs, rank_cache):
    """[(decision_idx, holdings)] using the engine's own rank call.

    The P&L is never re-implemented here: this helper only asks the same
    function the engine asks, so the recorded book cannot drift from the
    book that produced the curve.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    out = []
    for i in sorted(rebal_idxs):
        if pick_n is None:
            live = [s for s in universe if s in prices and base.elig(prices[s], i)]
        else:
            live = e27._rank(i, universe, prices, amounts, rank_cache)[:pick_n]
        if live:
            out.append((i, sorted(live)))
    return out


def _era_of(date, eras=ERAS):
    """Era of a decision date. Bounds are truncated to YYYY-MM before comparing:
    a bare month is a string PREFIX of its own first day, so '2024-01' <
    '2024-01-01' and every era would silently lose its first month."""
    month = date[:7]
    for name, lo, hi in eras:
        lo_m = lo[:7] if lo else None
        hi_m = hi[:7] if hi else None
        if (lo_m is None or month >= lo_m) and (hi_m is None or month <= hi_m):
            return name
    return None


def _churn_stats(cal, prices, decisions, eras=ERAS, with_names=False):
    """Per-transition membership churn and the entrant-minus-exit sleeve.

    ``with_names`` adds the swapped tickers to each row so a caller can join a
    transition to an event list (E82 churn-gap amplification); the default drops
    them to keep the published face small.

    churn_alpha_bp measures what the swap itself bought: the mean forward
    return (decision to next decision) of the names brought in minus the mean
    forward return of the names dropped. It is a name-level read of the same
    window the book actually held, not a portfolio return.
    """
    rows = []
    for k in range(1, len(decisions)):
        i0, prev = decisions[k - 1]
        i1, cur = decisions[k]
        pset, cset = set(prev), set(cur)
        ent = [s for s in cur if s not in pset]
        ext = [s for s in prev if s not in cset]

        def fwd(s):
            series = prices.get(s)
            if not series:
                return None
            p0, p1 = series[i0], series[i1]
            if p0 is None or p1 is None or p0 <= 0:
                return None
            return p1 / p0 - 1.0

        fe = [x for x in (fwd(s) for s in ent) if x is not None]
        fx = [x for x in (fwd(s) for s in ext) if x is not None]
        union = cset | pset
        row = {
            "date": cal[i0], "next": cal[i1], "era": _era_of(cal[i0], eras),
            "members": len(cur), "entrants": len(ent), "exits": len(ext),
            "entrant_share_pct": round(100.0 * len(ent) / len(cur), 2) if cur else None,
            "membership_churn_pct": (round(100.0 * len(union - (cset & pset)) / len(union), 2)
                                     if union else None),
            "entrant_fwd_pct": round(100 * sum(fe) / len(fe), 3) if fe else None,
            "exit_fwd_pct": round(100 * sum(fx) / len(fx), 3) if fx else None,
            "churn_alpha_bp": (round(1e4 * (sum(fe) / len(fe) - sum(fx) / len(fx)), 1)
                               if fe and fx else None),
        }
        if with_names:
            row["entrant_names"] = sorted(ent)
            row["exit_names"] = sorted(ext)
        rows.append(row)

    agg = {}
    for name, _lo, _hi in eras:
        sub = [r for r in rows if r["era"] == name and r["churn_alpha_bp"] is not None]
        if not sub:
            continue
        alphas = sorted(r["churn_alpha_bp"] for r in sub)
        agg[name] = {
            "transitions": len(sub),
            "entrant_share_pct_mean": round(sum(r["entrant_share_pct"] for r in sub) / len(sub), 2),
            "membership_churn_pct_mean": round(sum(r["membership_churn_pct"] for r in sub) / len(sub), 2),
            "churn_alpha_bp_mean": round(sum(alphas) / len(alphas), 1),
            "churn_alpha_bp_median": round(alphas[len(alphas) // 2], 1),
            "negative_churn_share_pct": round(100.0 * sum(1 for a in alphas if a < 0) / len(alphas), 1),
        }
    return rows, agg


def run_midmonth(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                 mid_day=15, costs=(0.0, 1.0, 3.0), raw=None, full_churn=False):
    """E44: explain the mid-month calendar's weakness at name level.

    ``raw`` lets a caller supply a repaired universe (E80 feeds the split
    screen through here, the same opt-in hook ``run_midsweep`` got in E78);
    the default still reads the untouched loader.

    E43's robustness grid put mid15 at the bottom of every cost column. Two
    candidate mechanisms are separated here on one identical universe and one
    identical rank cache: (a) the mid-month book simply turns over more, so
    fees eat the difference; (b) it turns over the same amount but swaps into
    worse names inside each held window. The churn sleeve answers (b) directly
    and turnover-per-year answers (a).
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = raw if raw is not None else e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    years = len(cal) / 252.0
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    cash = base.load_cash_series(cal)
    rank_cache = {}
    wide_name = "wide_top%d" % pick_n

    calendars = [("me", sorted(set(base.month_end_indices(cal)))),
                 ("mid%d" % mid_day, _mid_month_indices(cal, mid_day))]

    books = {}
    for label, idxs in calendars:
        decisions = _decision_sets(cal, prices, amounts, universe, pick_n,
                                   idxs, rank_cache)
        churn_rows, churn_agg = _churn_stats(cal, prices, decisions,
                                             with_names=full_churn)
        arms = {}
        for cm in costs:
            curve, aux, _hold = e27.simulate(cal, prices, amounts, universe, cash,
                                             pick_n, cm, rank_cache, set(idxs))
            eras = {}
            for name, lo, hi in ERAS:
                sub = _slice_curve(curve, lo, hi)
                if len(sub) < 2:
                    eras[name] = {"bars": len(sub), "skipped": "too few bars"}
                    continue
                prof = risk_profile(_rebase(sub), len(sub) / 252.0)
                eras[name] = {"bars": len(sub),
                              "ann_return_pct": prof["ann_return_pct"],
                              "max_drawdown_pct": prof["max_drawdown_pct"],
                              "monthly_win_rate_pct": prof["monthly_win_rate_pct"]}
            arms["x%g" % cm] = {
                "rebalances": aux["rebalances"],
                "turnover_per_year": round(aux["turnover_total"] / years, 3) if years else None,
                "full_window_ann_pct": risk_profile(curve, years)["ann_return_pct"],
                "eras": eras,
            }
        books[label] = {
            "decision_days": len(idxs),
            "arms": arms,
            "churn": churn_agg,
            "churn_transitions": len(churn_rows),
            "recent_transitions": churn_rows[-6:],
        }
        if full_churn:
            books[label]["churn_rows"] = churn_rows

    me, mid = books["me"], books["mid%d" % mid_day]
    eras_out = {}
    for name, _lo, _hi in ERAS:
        row = {}
        for label, book in (("me", me), ("mid", mid)):
            churn = book["churn"].get(name, {})
            row[label] = {
                "x0_ann_pct": book["arms"]["x0"]["eras"].get(name, {}).get("ann_return_pct"),
                "x1_ann_pct": book["arms"]["x1"]["eras"].get(name, {}).get("ann_return_pct"),
                "x3_ann_pct": book["arms"]["x3"]["eras"].get(name, {}).get("ann_return_pct"),
                "churn_alpha_bp_mean": churn.get("churn_alpha_bp_mean"),
                "negative_churn_share_pct": churn.get("negative_churn_share_pct"),
                "entrant_share_pct_mean": churn.get("entrant_share_pct_mean"),
            }
        for cm in ("x0", "x1", "x3"):
            a, b = row["me"][cm + "_ann_pct"], row["mid"][cm + "_ann_pct"]
            row["gap_%s_bp" % cm] = (round((b - a) * 100, 1)
                                    if a is not None and b is not None else None)
        ca, cb = row["me"]["churn_alpha_bp_mean"], row["mid"]["churn_alpha_bp_mean"]
        row["churn_alpha_gap_bp"] = (round(cb - ca, 1)
                                     if ca is not None and cb is not None else None)
        eras_out[name] = row

    # (a) turnover mechanism vs (b) membership mechanism, same units (bp/yr)
    turn_gap = (mid["arms"]["x1"]["turnover_per_year"] or 0) - (me["arms"]["x1"]["turnover_per_year"] or 0)
    fee_per_turn_bp = 2 * base.COST_BP_SIDE  # one round turn on the swapped half
    fee_gap_bp = 100.0 * turn_gap * base.COST_BP_SIDE / 2.0  # bp/yr, half-turn convention
    newest = eras_out.get("2024_now", {})
    return {
        "study": "e44_midmonth_churn",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "cost_mult_list": list(costs), "cost_bp_per_side": base.COST_BP_SIDE,
                 "start": start, "mid_month_day": mid_day,
                 "calendars": [c[0] for c in calendars],
                 "universe_members": len(universe)},
        "books": books,
        "eras": eras_out,
        "answers": {
            "turnover_per_year_me": me["arms"]["x1"]["turnover_per_year"],
            "turnover_per_year_mid": mid["arms"]["x1"]["turnover_per_year"],
            "turnover_gap_per_year": round(turn_gap, 3),
            "fee_gap_bp_per_year_implied": round(fee_gap_bp, 1),
            "full_window_gap_x1_bp": round(
                (mid["arms"]["x1"]["full_window_ann_pct"]
                 - me["arms"]["x1"]["full_window_ann_pct"]) * 100, 1),
            "newest_era_gap_x1_bp": newest.get("gap_x1_bp"),
            "newest_era_churn_alpha_gap_bp": newest.get("churn_alpha_gap_bp"),
            "newest_era_me_negative_churn_share_pct":
                eras_out.get("2024_now", {}).get("me", {}).get("negative_churn_share_pct"),
            "newest_era_mid_negative_churn_share_pct":
                eras_out.get("2024_now", {}).get("mid", {}).get("negative_churn_share_pct"),
        },
        "honest": [
            "the churn sleeve is an equal-weight mean over the swapped names, not a portfolio "
            "return: it says whether the names taken in beat the names given up inside that "
            "window, not how much money the book made",
            "both calendars share one calendar, one universe and one rank cache, so the only "
            "moving part is the set of decision sessions",
            "mid-month is a single fixed date (day %d), not a sweep: it prices a wrong-calendar "
            "cost, it does not search for a better one" % mid_day,
            "the fee_gap figure is an order-of-magnitude conversion of the turnover difference "
            "into bp/yr, not a reconciliation of the measured gap",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# --------------------------------- leg: name the mid-month swaps (E57 detail)

CHASE_BUCKETS = ("other_drops_next", "other_still_holds", "disjoint")


def _next_decision_idx(decisions, bar_idx):
    """Index of the first decision taken strictly after ``bar_idx``, or None.

    Strictly-after matters: the two calendars can decide on the same session, and
    the question here is what the other book does *next*, not what it did at the
    same instant.
    """
    for j, (i, _hold) in enumerate(decisions):
        if i > bar_idx:
            return j
    return None


def _classify_entrants(entrants, next_hold, drop_next):
    """Bucket one decision's entrants against the other calendar's next book.

    other_drops_next -- the other calendar sheds the name at its very next
        rebalance, so this book bought what the other was about to give up
    other_still_holds      -- the other calendar still holds it, so this book is
        early on a name rather than wrong about it
    disjoint    -- the name is in neither the other book's next holdings
        nor its next drop set: the two calendars read different slices
    """
    nxt = set(next_hold or ())
    drop = set(drop_next or ())
    out = {k: [] for k in CHASE_BUCKETS}
    for s in entrants:
        if s in drop:
            out["other_drops_next"].append(s)
        elif s in nxt:
            out["other_still_holds"].append(s)
        else:
            out["disjoint"].append(s)
    return out


def _chase_rows(cal, prices, decisions, other, eras=ERAS):
    """Per-transition entrants with their forward return and their bucket.

    ``other`` is the same-calendar decision list of the other rebalance timing.
    The bucketing reads that book's next two decisions, which is the only
    counterfactual available without re-pricing a portfolio.
    """
    rows = []
    for k in range(1, len(decisions)):
        i0, prev = decisions[k - 1]
        i1, cur = decisions[k]
        pset = set(prev)
        ent = [s for s in cur if s not in pset]
        ext = [s for s in prev if s not in set(cur)]
        j = _next_decision_idx(other, i0)
        next_hold = other[j][1] if j is not None else None
        drop_next = None
        if j is not None and j + 1 < len(other):
            drop_next = sorted(set(other[j][1]) - set(other[j + 1][1]))
        buckets = _classify_entrants(ent, next_hold, drop_next)

        def fwd(s):
            series = prices.get(s)
            if not series:
                return None
            p0, p1 = series[i0], series[i1]
            if p0 is None or p1 is None or p0 <= 0:
                return None
            return p1 / p0 - 1.0

        bucket_of = {}
        for b, syms in buckets.items():
            for s in syms:
                bucket_of[s] = b
        entrants = []
        for s in ent:
            r = fwd(s)
            entrants.append({"symbol": s, "bucket": bucket_of.get(s),
                             "fwd_pct": None if r is None else round(100 * r, 3)})
        exits = [{"symbol": s, "fwd_pct": (None if fwd(s) is None
                                           else round(100 * fwd(s), 3))} for s in ext]
        rows.append({
            "date": cal[i0], "next": cal[i1], "era": _era_of(cal[i0], eras),
            "members": len(cur), "entrants": entrants, "exits": exits,
            "other_next": (cal[other[j][0]] if j is not None else None),
            "other_drop_next_size": len(drop_next) if drop_next is not None else None,
        })
    return rows


def _chase_era(rows, eras=ERAS):
    """Per-era bucket shares and the return of each bucket, plus named swaps."""
    out = {}
    for name, _lo, _hi in eras:
        sub = [r for r in rows if r["era"] == name]
        if not sub:
            continue
        flat = [(r["date"], e) for r in sub for e in r["entrants"]]
        per_bucket = {}
        for b in CHASE_BUCKETS:
            vals = [e["fwd_pct"] for _d, e in flat
                    if e["bucket"] == b and e["fwd_pct"] is not None]
            per_bucket[b] = {
                "entrants": sum(1 for _d, e in flat if e["bucket"] == b),
                "share_pct": (round(100.0 * sum(1 for _d, e in flat if e["bucket"] == b)
                                    / len(flat), 2) if flat else None),
                "priced": len(vals),
                "fwd_pct_mean": round(sum(vals) / len(vals), 3) if vals else None,
                "negative_share_pct": (round(100.0 * sum(1 for v in vals if v < 0) / len(vals), 1)
                                       if vals else None),
            }
        priced = [(d, e) for d, e in flat if e["fwd_pct"] is not None]
        priced.sort(key=lambda x: (-x[1]["fwd_pct"], x[0], x[1]["symbol"]))
        named = lambda seq: [{"date": d, "symbol": e["symbol"], "bucket": e["bucket"],
                              "fwd_pct": e["fwd_pct"]} for d, e in seq]
        uniq = set(e["symbol"] for _d, e in flat)
        out[name] = {
            "transitions": len(sub),
            "entrant_slots": len(flat),
            "unique_entrants": len(uniq),
            "repeat_entrant_share_pct": (round(100.0 * (len(flat) - len(uniq)) / len(flat), 1)
                                         if flat else None),
            "buckets": per_bucket,
            "top10_entrants": named(priced[:10]),
            "bottom10_entrants": named(priced[-10:]),
        }
    return out


def run_chase(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",), mid_day=15):
    """E57: name the mid-month swaps and test the chase reading.

    r1132 showed the calendars turn over the same amount and that the mid-month
    book's swaps lose -123.7bp while the month-end book's swaps earn +95.6bp.
    Counts cannot say whether those entrants are names the month-end book sheds
    at its next rebalance (a chase into what is being given up), names it keeps
    anyway (being early), or a different slice of the universe. This leg emits
    the symbol lists themselves for both calendars and buckets every entrant
    against the other calendar's next book.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    rank_cache = {}

    calendars = [("me", sorted(set(base.month_end_indices(cal)))),
                 ("mid%d" % mid_day, _mid_month_indices(cal, mid_day))]
    decisions = {}
    for label, idxs in calendars:
        decisions[label] = _decision_sets(cal, prices, amounts, universe, pick_n,
                                          idxs, rank_cache)
    mid_label = "mid%d" % mid_day
    rows_me = _chase_rows(cal, prices, decisions["me"], decisions[mid_label])
    rows_mid = _chase_rows(cal, prices, decisions[mid_label], decisions["me"])
    era_me = _chase_era(rows_me)
    era_mid = _chase_era(rows_mid)
    newest = "2024_now"
    return {
        "study": "e57_midmonth_chase_names",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude), "start": start,
                 "mid_month_day": mid_day, "calendars": [c[0] for c in calendars],
                 "universe_members": len(universe),
                 "bucket_definition": {
                     "other_drops_next": "entrant is in the other calendar's drop set at its next rebalance",
                     "other_still_holds": "entrant is still held by the other calendar at its next rebalance",
                     "disjoint": "entrant is in neither the other book's next holdings nor its next drop set"}},
        "decision_days": {"me": len(decisions["me"]), mid_label: len(decisions[mid_label])},
        "eras": {"me": era_me, mid_label: era_mid},
        "recent_transitions": {mid_label: rows_mid[-3:], "me": rows_me[-2:]},
        "answers": {
            "newest_era_mid_bucket_share_pct": {
                b: era_mid.get(newest, {}).get("buckets", {}).get(b, {}).get("share_pct")
                for b in CHASE_BUCKETS},
            "newest_era_mid_bucket_fwd_pct": {
                b: era_mid.get(newest, {}).get("buckets", {}).get(b, {}).get("fwd_pct_mean")
                for b in CHASE_BUCKETS},
            "newest_era_me_bucket_share_pct": {
                b: era_me.get(newest, {}).get("buckets", {}).get(b, {}).get("share_pct")
                for b in CHASE_BUCKETS},
            "newest_era_me_bucket_fwd_pct": {
                b: era_me.get(newest, {}).get("buckets", {}).get(b, {}).get("fwd_pct_mean")
                for b in CHASE_BUCKETS},
            "newest_era_mid_unique_entrants": era_mid.get(newest, {}).get("unique_entrants"),
            "newest_era_me_unique_entrants": era_me.get(newest, {}).get("unique_entrants"),
            "newest_era_mid_repeat_entrant_share_pct":
                era_mid.get(newest, {}).get("repeat_entrant_share_pct"),
            "newest_era_me_repeat_entrant_share_pct":
                era_me.get(newest, {}).get("repeat_entrant_share_pct"),
        },
        "honest": [
            "bucket membership is decided on the other calendar's book, not on a "
            "re-priced counterfactual: it says what the other book did with the name, "
            "not what the money would have done",
            "fwd_pct is the raw decision-to-decision return of the name, before any "
            "weighting, cost or cash leg",
            "one mid-month date (day %d) against one month-end date: the calendars are "
            "fixed, not swept" % mid_day,
            "the last transition of each calendar has no full forward window if the "
            "panel ends mid-window; those rows carry null returns rather than zeros",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }


# --------------------------------- leg: sweep the off-cycle calendar (E59)

MID_SWEEP_DAYS = (5, 10, 15, 20, 25)


def _calendar_offsets(cal, idxs, me_idxs):
    """Sessions from each decision to the next month-end decision.

    An off-cycle book is not "one date", it is a distance from the boundary the
    month-end book trades on. Recording that distance lets a gap be read against
    the calendar offset instead of against one chosen day.
    """
    offs = []
    for i in idxs:
        nxt = next((j for j in me_idxs if j >= i), None)
        if nxt is not None:
            offs.append(nxt - i)
    if not offs:
        return {"decisions": 0, "mean_sessions_to_month_end": None,
                "min_sessions": None, "max_sessions": None}
    return {"decisions": len(offs),
            "mean_sessions_to_month_end": round(sum(offs) / float(len(offs)), 2),
            "min_sessions": min(offs), "max_sessions": max(offs)}


def _sweep_gaps(books, cost="x1", eras=ERAS):
    """Gap versus the month-end book, per sweep day, at one cost level."""
    me_arm = books.get("me", {}).get("arms", {}).get(cost, {})
    me_full = me_arm.get("full_window_ann_pct")
    me_eras = me_arm.get("eras", {})
    out = {}
    for label in sorted(books):
        if label == "me":
            continue
        arm = books[label].get("arms", {}).get(cost, {})
        full = arm.get("full_window_ann_pct")
        row_eras = {}
        for name, _lo, _hi in eras:
            a = me_eras.get(name, {}).get("ann_return_pct")
            b = arm.get("eras", {}).get(name, {}).get("ann_return_pct")
            row_eras[name] = {"ann_pct": b,
                              "gap_bp": round((b - a) * 100, 1)
                              if a is not None and b is not None else None}
        out[label] = {
            "offset": books[label].get("offset", {}),
            "turnover_per_year": arm.get("turnover_per_year"),
            "cost_per_year_bp": arm.get("cost_per_year_bp"),
            "full_window_ann_pct": full,
            "full_window_gap_bp": round((full - me_full) * 100, 1)
            if full is not None and me_full is not None else None,
            "eras": row_eras,
        }
    return out


def _cost_face(gaps, lo_tag, hi_tag, eras=ERAS):
    """E63: does the off-cycle gap survive when the fee is switched off?

    A gap that is unchanged between cost levels is a price-path effect -- the
    off-cycle book holds different names over the same months. A gap that moves
    with the fee is the trading cost of the date. Both faces of every sweep day
    are reported; nothing here decides which reading is right.
    """
    out = {}
    for label in sorted(gaps.get(hi_tag, {})):
        a = gaps.get(lo_tag, {}).get(label, {})
        b = gaps.get(hi_tag, {}).get(label, {})
        fa, fb = a.get("full_window_gap_bp"), b.get("full_window_gap_bp")
        row = {"full_window_gap_bp": {lo_tag: fa, hi_tag: fb},
               "full_window_shift_bp": round(fb - fa, 1)
               if fa is not None and fb is not None else None,
               "turnover_per_year": {lo_tag: a.get("turnover_per_year"),
                                     hi_tag: b.get("turnover_per_year")},
               "cost_per_year_bp": {lo_tag: a.get("cost_per_year_bp"),
                                    hi_tag: b.get("cost_per_year_bp")},
               "eras": {}}
        for name, _lo, _hi in eras:
            ea = a.get("eras", {}).get(name, {}).get("gap_bp")
            eb = b.get("eras", {}).get(name, {}).get("gap_bp")
            row["eras"][name] = {lo_tag: ea, hi_tag: eb,
                                 "shift_bp": round(eb - ea, 1)
                                 if ea is not None and eb is not None else None}
        out[label] = row
    return out


def _weekly_indices(cal):
    """First trading session of each ISO week.

    The weekly rule is the densest calendar already in the price panel, so it
    is the natural place to ask whether a month-end book is anything more than
    a re-timed weekly book. Weeks are ISO (Monday-anchored), so the label does
    not drift with the year boundary.
    """
    out, seen = [], set()
    for i, d in enumerate(cal):
        key = datetime.strptime(d, "%Y-%m-%d").isocalendar()[:2]
        if key in seen:
            continue
        seen.add(key)
        out.append(i)
    return out


def _nearest_weekly_to_month_end(week_idxs, me_idxs):
    """The weekly session closest to each month-end decision, deduped.

    This is the weekly grid read at monthly cadence: same names, same cost,
    only traded once a month on the weekly date nearest the boundary. If it
    reproduces the month-end book the calendar is a re-timing; if it loses,
    the boundary date itself carries the information.
    """
    if not week_idxs or not me_idxs:
        return []
    wk = sorted(set(week_idxs))
    out = set()
    for me in sorted(set(me_idxs)):
        out.add(min(wk, key=lambda w: (abs(w - me), w)))
    return sorted(out)


def run_midsweep(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                 days=MID_SWEEP_DAYS, costs=(1.0,), lags=(), weekly=False,
                 raw=None):
    """E59: is the off-cycle penalty day 15's, or any off-cycle date's?

    E44 priced one mid-month date against month-end and E57 showed the two
    calendars buy the same kind of name, so the remaining question is whether
    the gap is a property of the 15th or a property of trading away from the
    month boundary. Five dates are burned here on ONE universe, ONE rank cache
    and ONE cost level: if the gap tracks the distance to month-end the effect
    belongs to the boundary; if it is flat across all five, the boundary is
    simply the right date.

    ``raw`` lets a caller supply a repaired universe (E78 feeds the split
    screen through here); the default still reads the untouched loader.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = raw if raw is not None else e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    years = len(cal) / 252.0
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    cash = base.load_cash_series(cal)
    rank_cache = {}
    me_idxs = sorted(set(base.month_end_indices(cal)))

    calendars = [("me", me_idxs)]
    for d in days:
        calendars.append(("mid%d" % d, _mid_month_indices(cal, d)))
    for k in lags:
        calendars.append(("me_lag%d" % k, _shift_indices(me_idxs, k, len(cal))))
    if weekly:
        wk_idxs = _weekly_indices(cal)
        calendars.append(("week", wk_idxs))
        calendars.append(("week_near_me", _nearest_weekly_to_month_end(wk_idxs, me_idxs)))

    books = {}
    for label, idxs in calendars:
        arms = {}
        for cm in costs:
            curve, aux, _hold = e27.simulate(cal, prices, amounts, universe, cash,
                                            pick_n, cm, rank_cache, set(idxs))
            era_rows = {}
            for name, lo, hi in ERAS:
                sub = _slice_curve(curve, lo, hi)
                if len(sub) < 2:
                    era_rows[name] = {"bars": len(sub), "skipped": "too few bars"}
                    continue
                prof = risk_profile(_rebase(sub), len(sub) / 252.0)
                era_rows[name] = {"bars": len(sub),
                                  "ann_return_pct": prof["ann_return_pct"],
                                  "max_drawdown_pct": prof["max_drawdown_pct"]}
            arms["x%g" % cm] = {
                "rebalances": aux["rebalances"],
                "turnover_per_year": round(aux["turnover_total"] / years, 3) if years else None,
                "cost_per_year_bp": round(aux["cost_paid_frac"] / years * 1e4, 1)
                if years else None,
                "full_window_ann_pct": risk_profile(curve, years)["ann_return_pct"],
                "eras": era_rows,
            }
        books[label] = {"decision_days": len(idxs),
                        "offset": _calendar_offsets(cal, idxs, me_idxs),
                        "arms": arms}

    gaps = {("x%g" % cm): _sweep_gaps(books, "x%g" % cm) for cm in costs}
    newest = "2024_now"
    newest_gap = {lab: gaps[("x%g" % costs[0])][lab]["eras"].get(newest, {}).get("gap_bp")
                  for lab in gaps[("x%g" % costs[0])]}
    # does the gap track the calendar offset, or is it flat across off-cycle days?
    pts = [(gaps[("x%g" % costs[0])][lab]["offset"]["mean_sessions_to_month_end"], v)
           for lab, v in newest_gap.items() if v is not None]
    spread = (max(v for _o, v in pts) - min(v for _o, v in pts)) if len(pts) > 1 else None
    cost_face = (_cost_face(gaps, "x%g" % costs[0], "x%g" % costs[-1])
                 if len(costs) > 1 else None)
    face = {
        "study": "e59_midday_sweep",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude), "start": start,
                 "cost_bp_per_side": base.COST_BP_SIDE, "cost_mult_list": list(costs),
                 "sweep_days": list(days), "delay_lags": list(lags),
                 "calendars": [c[0] for c in calendars],
                 "universe_members": len(universe)},
        "books": {lab: {"decision_days": b["decision_days"], "offset": b["offset"],
                        "arms": b["arms"]} for lab, b in books.items()},
        "gaps": gaps,
        "cost_face": cost_face,
        "answers": {
            "baseline_calendar": "me",
            "sweep_days": list(days),
            "delay_lags": list(lags),
            "cost_levels": list(costs),
            "full_window_gap_bp": {lab: g["full_window_gap_bp"]
                                   for lab, g in gaps[("x%g" % costs[0])].items()},
            "newest_era_gap_bp": newest_gap,
            "newest_era_gap_spread_bp": round(spread, 1) if spread is not None else None,
            "offset_sessions": {lab: g["offset"]["mean_sessions_to_month_end"]
                                for lab, g in gaps[("x%g" % costs[0])].items()},
            "cost_gap_shift_bp": ({lab: v["full_window_shift_bp"]
                                   for lab, v in cost_face.items()}
                                  if cost_face else None),
        },
        "honest": [
            ("one cost level by default: the sweep is about the calendar axis, and the "
             "cost signature of these cuts has been the same -8..-13bp since thirds")
            if len(costs) == 1 else
            ("two cost levels: x%g switches the engine fee off entirely, so a gap that "
             "survives x%g is a price-path effect and not the cost of trading on that "
             "date; the x%g column is the same sweep with the fee switched back on"
             % (costs[0], costs[0], costs[-1])),
            "the five days are fixed dates, not a fitted optimum: no date here is "
            "searched for and none may be read as a recommendation",
            "both calendars share one universe and one rank cache, so the only moving "
            "part is the set of decision sessions",
            "gap spread across days is a range statistic over five points, not a test",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }
    if weekly:
        wk = sorted(set(_weekly_indices(cal)))
        mes = sorted(set(me_idxs))
        face["answers"]["week_overlap"] = {
            "weekly_days": len(wk),
            "me_days": len(mes),
            "exact_coincidence": len(set(wk) & set(mes)),
            "within_1_session": len([i for i in wk
                                     if any(abs(i - j) <= 1 for j in mes)]),
            "within_2_sessions": len([i for i in wk
                                      if any(abs(i - j) <= 2 for j in mes)]),
            "within_5_sessions": len([i for i in wk
                                      if any(abs(i - j) <= 5 for j in mes)]),
        }
        face["honest"].append(
            "the weekly calendar is the ISO first-session grid (Monday-anchored); a "
            "month-end decision and a weekly decision almost never land on the same "
            "session, so 'overlap' here means proximity, not the same trade")
    return face


# --------------------------------- leg: delay the month-end decision (E65)

def run_entrydelay(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                   lags=(1, 3, 5, 10), costs=(1.0,)):
    """E65: is the off-cycle penalty the calendar, or simply being late?

    E59/E63 showed every off-cycle date loses 60-90bp and that the fee cannot
    explain it, so the remaining candidate is lateness itself. This leg holds
    the spec, universe and rank cache fixed and only moves the month-end
    decision forward by 1/3/5/10 sessions. The lag moves the DECISION session
    as well as the entry, so the delayed book is re-ranked on the delayed date:
    this prices "decided and bought k sessions later", not "the same names
    bought later".
    """
    face = run_midsweep(outdir, start=start, pick_n=pick_n, exclude=exclude,
                        days=(), costs=costs, lags=tuple(lags))
    rows = {}
    for k in lags:
        lab = "me_lag%d" % k
        arm = face["gaps"].get("x%g" % costs[0], {}).get(lab)
        if arm is None:
            continue
        rows[lab] = {"full_window_gap_bp": arm.get("full_window_gap_bp"),
                     "turnover_per_year": arm.get("turnover_per_year"),
                     "eras": {name: v.get("gap_bp")
                              for name, v in (arm.get("eras") or {}).items()}}
    face["study"] = "e65_entrydelay_ladder"
    face["answers"]["delay_rows"] = rows
    face["answers"]["delay_gap_bp"] = {lab: r["full_window_gap_bp"]
                                       for lab, r in rows.items()}
    face["honest"].append(
        "the lag moves the decision session as well as the entry, so the delayed "
        "book is re-ranked on the delayed date; an entry-only lag would need an "
        "execution-lag hook the engine does not have")
    return face


# --------------------------------- leg: decide EARLY instead (E66)

def _early_label(k):
    """Row label for a k-session EARLY decision (positive k = earlier)."""
    return "me_m%d" % k


def _lag_label(k):
    """Row label for a k-session LATE decision (positive k = later)."""
    return "me_lag%d" % k


def _read_delay_face(outdir, kind, cutoff, start):
    """Read a burned delay ladder (ENTRYDELAY/NEIGHBORHOOD) for cutoff+start."""
    tag = "" if start == "2020-01-01" else "-s%s" % start.replace("-", "")
    p = os.path.join(outdir or os.path.join(ROOT, "results", "e44_midmonth"),
                     "%s-%s%s.json" % (kind, cutoff.replace("-", ""), tag))
    if not os.path.exists(p):
        return None, p
    with open(p, encoding="utf-8") as fh:
        return json.load(fh), p


def _read_late_face(outdir, cutoff, start):
    """Read the E65 late ladder for the same cutoff+start, if it was burned."""
    return _read_delay_face(outdir, "ENTRYDELAY", cutoff, start)


def _read_early_face(outdir, cutoff, start):
    """Read the E66 early ladder for the same cutoff+start, if it was burned."""
    return _read_delay_face(outdir, "EARLYDELAY", cutoff, start)


def _delay_face_any(outdir, kind, cutoff, start):
    """Read a delay ladder face, falling back to the newest older burn.

    A neighbourhood leg burned on a newer panel cutoff has no exact-cutoff
    bounds, and refusing the bracket would throw away a burned face over one
    extra bar. The fallback is explicit: it returns the cutoff it actually
    used so the caller can disclose the mismatch instead of hiding it.
    """
    face, p = _read_delay_face(outdir, kind, cutoff, start)
    if face is not None:
        return face, p, cutoff
    import glob
    import re
    tag = "" if start == "2020-01-01" else "-s%s" % start.replace("-", "")
    pat = os.path.join(os.path.dirname(p), "%s-*%s.json" % (kind, tag))
    best = None
    rx = re.compile(r"^%s-(\d{8})%s\.json$" % (kind, re.escape(tag)))
    for c in glob.glob(pat):
        m = rx.match(os.path.basename(c))
        if not m:
            continue
        if best is None or m.group(1) > best[0]:
            best = (m.group(1), c)
    if best is None:
        return None, p, None
    with open(best[1], encoding="utf-8") as fh:
        return json.load(fh), best[1], best[0]


def _bracket_shape(vals, tol=2.0):
    """Is a three-point ladder [k1, k2, k3] a spike, a ramp, or flat?

    vals are gaps in bp at increasing distance from the boundary on ONE side.
    A spike means the middle point comes back to ~zero while both ends pay; a
    ramp means the middle sits between the ends (monotone), i.e. the first
    session already pays something and later sessions pay more.
    """
    if len(vals) != 3 or any(v is None for v in vals):
        return "incomplete"
    a, b, c = vals
    if abs(a) <= tol and abs(b) <= tol and abs(c) <= tol:
        return "flat"
    if abs(b) <= tol and abs(a) > 2 * tol and abs(c) > 2 * tol:
        return "spike"
    if a - tol <= b <= c + tol or a + tol >= b >= c - tol:
        return "ramp"
    return "non_monotone"


def run_earlydelay(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                   early=(1, 3, 5, 10), costs=(1.0,)):
    """E66: price the other side of the month-end boundary.

    E65 held the spec fixed and moved the month-end decision LATER by
    1/3/5/10 sessions, reading a cliff in the newest era. This leg moves the
    same decision EARLIER by the same amounts on the same universe and rank
    cache. Early is not late with a minus sign: a name that is already
    published at the earlier date is a different candidate set, so the two
    sides together say whether the month boundary is a deadline (only late
    pays) or a point (both sides pay).
    """
    face = run_midsweep(outdir, start=start, pick_n=pick_n, exclude=exclude,
                        days=(), costs=costs, lags=tuple(-k for k in early))
    lvl = "x%g" % costs[0]
    gaps = face["gaps"].get(lvl, {})
    rows = {}
    for k in early:
        arm = gaps.get(_lag_label(-k))
        if arm is None:
            continue
        rows[_early_label(k)] = {"full_window_gap_bp": arm.get("full_window_gap_bp"),
                                 "turnover_per_year": arm.get("turnover_per_year"),
                                 "eras": {name: v.get("gap_bp")
                                          for name, v in (arm.get("eras") or {}).items()}}
    late_face, late_path = _read_late_face(outdir, face["evidence_cutoff"], start)
    late_rows = (late_face or {}).get("answers", {}).get("delay_rows") or {}
    asym = {}
    for k in early:
        e_row = rows.get(_early_label(k))
        l_row = late_rows.get(_lag_label(k))
        if not e_row or not l_row:
            continue
        e_era = e_row["eras"].get("2024_now")
        l_era = l_row["eras"].get("2024_now")
        asym[_early_label(k)] = {
            "full_window_early_minus_late_bp":
                None if (e_row["full_window_gap_bp"] is None
                         or l_row["full_window_gap_bp"] is None)
                else round(e_row["full_window_gap_bp"] - l_row["full_window_gap_bp"], 1),
            "newest_era_early_minus_late_bp":
                None if (e_era is None or l_era is None) else round(e_era - l_era, 1),
        }
    face["study"] = "e66_earlydelay_ladder"
    face["answers"]["early_rows"] = rows
    face["answers"]["early_gap_bp"] = {lab: r["full_window_gap_bp"]
                                       for lab, r in rows.items()}
    face["answers"]["early_newest_era_gap_bp"] = {
        lab: r["eras"].get("2024_now") for lab, r in rows.items()}
    face["answers"]["late_rows_source"] = (os.path.relpath(late_path, ROOT)
                                           if late_face else None)
    face["answers"]["asymmetry_bp"] = asym
    face["honest"].append(
        "the early lag also moves the decision session, so the book is re-ranked on "
        "the earlier date on names that had already published then; the late column "
        "is read from the E65 face at the same cutoff+start (%s), not re-burned"
        % (face["answers"]["late_rows_source"] or "absent"))
    face["honest"].append(
        "an early decision is not the same book one session sooner: it can only buy "
        "what is already eligible, so a flat/or positive early side means the "
        "boundary is a publication deadline, not a price path")
    return face


# --------------------------------- leg: the month-end NEIGHBOURHOOD (E67)

def run_neighborhood(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                     costs=(1.0,), neighbors=(2,)):
    """E67: is the one-session penalty a spike on one session, or a ramp?

    E65 (late) and E66 (early) each priced 1/3/5/10 sessions off the boundary
    and both read a cost at every magnitude, which leaves the shape between
    one and three unresolved. This leg burns only the missing k-session arms
    (early k = `me_mK`, late k = `me_pK`) on the same universe and rank cache,
    then brackets each against the nearest already-burned magnitudes on the
    E65/E66 faces to say whether the penalty is a point kick or a ramp.
    """
    neighbors = tuple(int(k) for k in neighbors)
    lags = tuple(sorted({-k for k in neighbors} | {k for k in neighbors}))
    face = run_midsweep(outdir, start=start, pick_n=pick_n, exclude=exclude,
                        days=(), costs=costs, lags=lags)
    lvl = "x%g" % costs[0]
    gaps = face["gaps"].get(lvl, {})
    rows = {}
    for k in neighbors:
        for lab, arm_lab in ((_early_label(k), _lag_label(-k)),
                             ("me_p%d" % k, _lag_label(k))):
            arm = gaps.get(arm_lab)
            if arm is None:
                continue
            rows[lab] = {"source_row": arm_lab,
                         "full_window_gap_bp": arm.get("full_window_gap_bp"),
                         "turnover_per_year": arm.get("turnover_per_year"),
                         "eras": {name: v.get("gap_bp")
                                  for name, v in (arm.get("eras") or {}).items()}}
    early_face, early_path, early_cut = _delay_face_any(
        outdir, "EARLYDELAY", face["evidence_cutoff"], start)
    late_face, late_path, late_cut = _delay_face_any(
        outdir, "ENTRYDELAY", face["evidence_cutoff"], start)
    early_rows = ((early_face or {}).get("answers", {}).get("early_rows") or {})
    late_rows = ((late_face or {}).get("answers", {}).get("delay_rows") or {})

    def _pick(rowset, lab, field, era=None):
        row = rowset.get(lab)
        if not row:
            return None
        if era:
            return (row.get("eras") or {}).get(era)
        return row.get(field)

    def _value(side, k, rowset, era=None):
        # this leg's own rows first, then the E65/E66 faces at the same cutoff+start
        lab = "me_m%d" % k if side == "early" else "me_p%d" % k
        if lab in rows:
            row = rows[lab]
            return (row.get("eras") or {}).get(era) if era else row["full_window_gap_bp"]
        src = "me_m%d" % k if side == "early" else _lag_label(k)
        return _pick(rowset, src, "full_window_gap_bp", era)

    brackets = {}
    for side, rowset in (("early", early_rows), ("late", late_rows)):
        side_src = os.path.relpath(early_path if side == "early" else late_path, ROOT) \
            if (early_face if side == "early" else late_face) else None
        for k in neighbors:
            seq = (k - 1, k, k + 1)
            brackets["%s_k%d" % (side, k)] = {
                "labels": ["me_m%d" % s if side == "early" else "me_p%d" % s
                           for s in seq],
                "full_window_bp": [_value(side, s, rowset) for s in seq],
                "newest_era_bp": [_value(side, s, rowset, "2024_now") for s in seq],
                "full_window_shape": _bracket_shape(
                    [_value(side, s, rowset) for s in seq]),
                "newest_era_shape": _bracket_shape(
                    [_value(side, s, rowset, "2024_now") for s in seq]),
                "neighbor_rows_source": side_src,
            }

    face["study"] = "e67_monthend_neighborhood"
    face["answers"]["neighbor_rows"] = rows
    face["answers"]["neighbor_gap_bp"] = {lab: r["full_window_gap_bp"]
                                          for lab, r in rows.items()}
    face["answers"]["neighbor_newest_era_gap_bp"] = {
        lab: r["eras"].get("2024_now") for lab, r in rows.items()}
    face["answers"]["brackets"] = brackets
    face["answers"]["bound_rows_cutoff"] = {"early": early_cut, "late": late_cut}
    face["answers"]["bound_rows_source"] = {
        "early": os.path.relpath(early_path, ROOT) if early_face else None,
        "late": os.path.relpath(late_path, ROOT) if late_face else None}
    face["honest"].append(
        "the bracket bounds are read from the E65/E66 faces (%s / %s), not re-burned; "
        "only the k-session arms here are new" % (
            ("%s @%s" % (os.path.relpath(early_path, ROOT), early_cut)) if early_face
            else "early absent",
            ("%s @%s" % (os.path.relpath(late_path, ROOT), late_cut)) if late_face
            else "late absent"))
    if (early_face and early_cut != face["evidence_cutoff"]) or (
            late_face and late_cut != face["evidence_cutoff"]):
        face["honest"].append(
            "the bracket faces were burned on an older panel cutoff (%s/%s) than this "
            "leg (%s), so the bracket mixes one extra bar of data and is a shape "
            "reading, not a same-cutoff comparison"
            % (early_cut, late_cut, face["evidence_cutoff"]))
    face["honest"].append(
        "shape labels come from a +/-2bp tolerance on three points: they describe the "
        "ladder, they are not a test and no arm here is a recommendation")
    return face


# --------------------------------- leg: month-end vs the weekly grid (E69/E70)

def _weekly_cal_rows(face, tag, labels=("week", "week_near_me")):
    """E70: the calendar rows of one cost level, keyed by book label.

    Kept pure so the cost-level wiring is testable without a burn: the fee
    question (does switching the multiplier move the calendar gap) needs the
    same rows at two levels, and reading them out of one dict is the only way
    to be sure the comparison is not two different burns.
    """
    gaps = (face.get("gaps") or {}).get(tag) or {}
    books = face.get("books") or {}
    out = {}
    for lab in labels:
        g = gaps.get(lab) or {}
        out[lab] = {
            "decision_days": (books.get(lab) or {}).get("decision_days"),
            "full_window_gap_bp": g.get("full_window_gap_bp"),
            "turnover_per_year": g.get("turnover_per_year"),
            "cost_per_year_bp": g.get("cost_per_year_bp"),
            "eras": {name: v.get("gap_bp")
                     for name, v in (g.get("eras") or {}).items()},
        }
    return out


def run_weeklyclash(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                    costs=(1.0,)):
    """E69: is month-end a calendar of its own, or a re-timed weekly book?

    E68 put the plateau at the first week off the boundary, which is exactly
    where a weekly rebalance sits. Two readings are priced on one universe,
    one rank cache and one cost level: `week` (the full ISO weekly grid, the
    densest rule in the panel) and `week_near_me` (the SAME weekly grid cut to
    one decision per month, taken at the weekly session nearest the boundary).
    If the monthly-cadence weekly book matches month-end, adopting month-end is
    a re-timing; if it loses, the boundary date carries the information. The
    turnover/cost columns answer the second half of the question directly:
    does the month-end calendar trade more than the weekly one, or less.
    """
    face = run_midsweep(outdir, start=start, pick_n=pick_n, exclude=exclude,
                        days=(), costs=costs, lags=(), weekly=True)
    tags = ["x%g" % c for c in costs]
    lvl = tags[0]
    # E70: every cost level keeps its own row set, so the fee question is answered
    # inside the face instead of by hand-diffing two burns.
    rows_by_cost = {tag: _weekly_cal_rows(face, tag) for tag in tags}
    rows = rows_by_cost[lvl]
    me_turn = face["books"].get("me", {}).get("arms", {}).get(lvl, {}).get(
        "turnover_per_year")
    me_turn_by_cost = {tag: face["books"].get("me", {}).get("arms", {}).get(
        tag, {}).get("turnover_per_year") for tag in tags}

    def _ratio(lab, ref=None, tag=lvl):
        t = rows_by_cost.get(tag, {}).get(lab, {}).get("turnover_per_year")
        m = me_turn if ref is None else ref
        if t is None or not m:
            return None
        return round(t / m, 3)

    cost_face = _cost_face(face["gaps"], tags[0], tags[-1]) if len(tags) > 1 else None

    face["study"] = "e70_monthend_weekly_costface" if cost_face else \
        "e69_monthend_weekly_clash"
    face["answers"]["calendar_rows"] = rows
    if cost_face:
        face["answers"]["calendar_rows_by_cost"] = rows_by_cost
        face["answers"]["cost_face"] = cost_face
        face["answers"]["cost_shift_bp"] = {
            lab: (cost_face.get(lab) or {}).get("full_window_shift_bp")
            for lab in ("week", "week_near_me")}
        face["answers"]["turnover_ratio_vs_me_by_cost"] = {
            tag: {"week": _ratio("week", me_turn_by_cost.get(tag), tag),
                  "week_near_me": _ratio("week_near_me",
                                         me_turn_by_cost.get(tag), tag)}
            for tag in tags}
    face["answers"]["me_turnover_per_year"] = me_turn
    face["answers"]["turnover_ratio_vs_me"] = {"week": _ratio("week"),
                                               "week_near_me": _ratio("week_near_me")}
    face["answers"]["retiming_gap_bp"] = rows["week_near_me"]["full_window_gap_bp"]
    face["answers"]["retiming_gap_bp_newest_era"] = \
        rows["week_near_me"]["eras"].get("2024_now")
    face["honest"].append(
        "the weekly book rebalances ~4.3x more often than month-end, so a return gap "
        "against it mixes calendar with trading frequency; only `week_near_me` holds "
        "frequency fixed and prices the DATE")
    face["honest"].append(
        "`week_near_me` snaps each month-end to the nearest weekly session, so its "
        "decisions sit 1-3 sessions inside the boundary rather than on it -- the "
        "residual offset is the price of being on the weekly grid, not noise")
    return face


# --------------------------- leg: what each calendar actually holds (E71)

def _overlap_stats(base_names, other_names):
    """(E71) name overlap of two held sets, with the entrant/exit split.

    Directional on purpose: entrants are names the OTHER book holds and the
    base book does not, exits the reverse, so a row reads as "what the second
    book does differently", not as a symmetric distance.
    """
    a, b = set(base_names or ()), set(other_names or ())
    inter, union = a & b, a | b
    return {"held_base": len(a), "held_other": len(b), "common": len(inter),
            "entrants": len(b - a), "exits": len(a - b),
            "share_of_base": round(len(inter) / float(len(a)), 4) if a else None,
            "share_of_other": round(len(inter) / float(len(b)), 4) if b else None,
            "jaccard": round(len(inter) / float(len(union)), 4) if union else None}


def _pair_to_grid(targets, grid):
    """(E71) map each decision to the nearest session of another grid."""
    g = sorted(set(grid or ()))
    if not g:
        return {}
    return {t: min(g, key=lambda x: (abs(x - t), x))
            for t in sorted(set(targets or ()))}


def _name_churn_stats(held_sets):
    """(E71) how much a book's own membership moves between its decisions."""
    if not held_sets or len(held_sets) < 2:
        return {"steps": 0, "mean_names_kept_share": None,
                "mean_names_changed": None, "max_names_changed": None}
    kept, changed = [], []
    for prev, cur in zip(held_sets, held_sets[1:]):
        a, b = set(prev or ()), set(cur or ())
        if not a and not b:
            continue
        u = a | b
        kept.append(len(a & b) / float(len(u)) if u else None)
        changed.append(len(a ^ b))
    if not kept:
        return {"steps": 0, "mean_names_kept_share": None,
                "mean_names_changed": None, "max_names_changed": None}
    vals = [k for k in kept if k is not None]
    return {"steps": len(kept),
            "mean_names_kept_share": round(sum(vals) / len(vals), 4) if vals else None,
            "mean_names_changed": round(sum(changed) / float(len(changed)), 2),
            "max_names_changed": max(changed)}


def _stale_hold_stats(idxs, held_sets):
    """(E71) how long a dropped name is still held before the next decision.

    A book can only drop a name when it rebalances, so the sessions a dead name
    lingers is exactly the gap between two decisions. That is the membership
    channel a monthly book carries and a weekly book does not, and a per-date
    name overlap cannot see it.
    """
    if not idxs or len(idxs) != len(held_sets) or len(idxs) < 2:
        return {"exits": 0, "mean_sessions_held_after_exit": None,
                "max_sessions_held_after_exit": None}
    tot, n, worst = 0, 0, 0
    for k in range(1, len(idxs)):
        gone = len(set(held_sets[k - 1]) - set(held_sets[k]))
        gap = idxs[k] - idxs[k - 1]
        tot += gone * gap
        n += gone
        if gone:
            worst = max(worst, gap)
    return {"exits": n,
            "mean_sessions_held_after_exit": round(tot / float(n), 2) if n else None,
            "max_sessions_held_after_exit": worst or None}


def _pair_summary(pairs):
    """(E71) aggregate a list of per-pair overlap rows."""
    if not pairs:
        return {"n_pairs": 0, "same_session_pairs": 0, "mean_share_of_base": None,
                "min_share_of_base": None, "max_share_of_base": None,
                "mean_entrants": None, "mean_exits": None,
                "total_entrants": 0, "total_exits": 0}
    shares = [p.get("share_of_base") for p in pairs
              if p.get("share_of_base") is not None]
    return {"n_pairs": len(pairs),
            "same_session_pairs": len([p for p in pairs if p.get("same_session")]),
            "mean_share_of_base": round(sum(shares) / len(shares), 4) if shares else None,
            "min_share_of_base": min(shares) if shares else None,
            "max_share_of_base": max(shares) if shares else None,
            "mean_entrants": round(sum(p.get("entrants", 0) for p in pairs)
                                   / float(len(pairs)), 2),
            "mean_exits": round(sum(p.get("exits", 0) for p in pairs)
                                / float(len(pairs)), 2),
            "total_entrants": sum(p.get("entrants", 0) for p in pairs),
            "total_exits": sum(p.get("exits", 0) for p in pairs)}


def _tail_guard(counts, flat=0.5):
    """(E71) decide which book decisions are priced on a complete panel bar.

    The panel can be mid-arrival: on the day's unfinished bar only a handful of
    members carry a close, so a decision taken there holds a stub book and reads
    as a name explosion against any other calendar. The test is LOCAL -- a
    decision is dropped when its live count collapses against its neighbours --
    because the live universe legitimately grows through the window and a
    global-median test would throw away the early burn-in instead.
    """
    n = len(counts)
    if not n:
        return []
    out = []
    for i, c in enumerate(counts):
        if c is None:
            out.append(True)
            continue
        ref = max([c] + [counts[j] for j in (i - 1, i + 1)
                         if 0 <= j < n and counts[j] is not None])
        out.append(c >= flat * ref)
    return out


def _membership_reading(share, same_flat=0.95):
    """(E71) label a per-date name overlap: same book or diverging books."""
    if share is None:
        return "insufficient"
    return "same_names" if share >= same_flat else "diverging_names"


def _cum_return(series, i0, i1):
    """(E72) close-to-close return between two session indices, or None.

    An unpriced end (missing bar, zero/negative base) is None, never zero: a
    zero here would silently price a dead name as a flat hold.
    """
    if series is None or i0 is None or i1 is None:
        return None
    if i0 < 0 or i1 < 0 or i0 >= len(series) or i1 >= len(series):
        return None
    a, b = series[i0], series[i1]
    if a is None or b is None or a <= 0:
        return None
    return b / float(a) - 1.0


def _week_hold_positions(wk_idxs, wk_books):
    """(E72) name -> ascending list of weekly decision positions holding it."""
    pos = {}
    for p, names in enumerate(wk_books or ()):
        for s in names:
            pos.setdefault(s, []).append(p)
    return pos


def _last_hold_at_or_before(positions, target_idx, wk_idxs):
    """(E72) last weekly position whose session is <= the target session."""
    best = None
    for p in positions or ():
        if p < len(wk_idxs) and wk_idxs[p] <= target_idx:
            best = p
        else:
            break
    return best


def _stale_hold_events(me_idxs, me_books, wk_idxs, wk_books, ret_fn,
                       book_ret_fn=None):
    """(E72) price every stale exit: sessions held past the weekly drop, and bp.

    A monthly book can only drop an ineligible name at its next decision, so a
    name the weekly book already sold keeps a weight for weeks. Each event is
    charged at the book's equal weight (1/n_held_before) times the name's own
    return over the extra sessions, i.e. the bp a weekly drop would have saved.

    E74 adds the RELATIVE face: when `book_ret_fn` is supplied the same span is
    also charged against the wide book's own return, so an event that simply
    moved with the market nets to ~0 instead of reading as a name effect.
    """
    pos = _week_hold_positions(wk_idxs, wk_books)
    events, unpriced, no_weekly, unpriced_book = [], 0, 0, 0
    for k in range(1, len(me_idxs or ())):
        prev, cur = list(me_books[k - 1]), set(me_books[k])
        exits = [s for s in prev if s not in cur]
        if not exits or not prev:
            continue
        w = 1.0 / float(len(prev))
        for s in exits:
            p = _last_hold_at_or_before(pos.get(s, []), me_idxs[k], wk_idxs)
            if p is None:
                no_weekly += 1
                continue
            extra = me_idxs[k] - wk_idxs[p]
            if extra <= 0:
                continue
            r = ret_fn(s, wk_idxs[p], me_idxs[k])
            if r is None:
                unpriced += 1
                continue
            events.append({"me_session": me_idxs[k],
                           "weekly_session": wk_idxs[p],
                           "name": s,
                           "extra_sessions": extra,
                           "return_pct": round(r * 100.0, 4),
                           "weight_pct": round(w * 100.0, 4),
                           "bp_contrib": round(10000.0 * w * r, 3)})
            if book_ret_fn is not None:
                b = book_ret_fn(wk_idxs[p], me_idxs[k])
                if b is None:
                    unpriced_book += 1
                    continue
                events[-1]["book_return_pct"] = round(b * 100.0, 4)
                events[-1]["excess_return_pct"] = round((r - b) * 100.0, 4)
                events[-1]["relative_bp_contrib"] = round(10000.0 * w * (r - b), 3)
    return events, {"unpriced": unpriced, "never_in_weekly_book": no_weekly,
                    "unpriced_book": unpriced_book}


def _years_between(d0, d1):
    """(E72) calendar years between two ISO dates, or None if unusable."""
    try:
        a = datetime.strptime(d0, "%Y-%m-%d")
        b = datetime.strptime(d1, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None
    days = (b - a).days
    return days / 365.25 if days > 0 else None


def _stale_aggregate(events, years, key="bp_contrib", ret_key="return_pct"):
    """(E72/E74) summarise stale-exit events into total bp and per-event stats.

    E74 re-reads the same events on the relative key (`relative_bp_contrib`), so
    the key and the return column are parameters; events missing that key are
    dropped rather than silently counted as a zero excess.
    """
    rows = [e for e in events if key in e] if key != "bp_contrib" else list(events)
    if not rows:
        return {"events": 0, "total_bp": 0.0, "bp_per_year": None,
                "mean_return_pct": None, "negative_share": None,
                "mean_extra_sessions": None, "max_extra_sessions": None,
                "worst_event": None}
    tot = sum(e[key] for e in rows)
    neg = len([e for e in rows if e[ret_key] < 0])
    worst = min(rows, key=lambda e: e[key])
    return {"events": len(rows),
            "total_bp": round(tot, 3),
            "bp_per_year": round(tot / years, 3) if years else None,
            "mean_return_pct": round(sum(e[ret_key] for e in rows)
                                     / float(len(rows)), 4),
            "negative_share": round(neg / float(len(rows)), 4),
            "mean_extra_sessions": round(sum(e["extra_sessions"] for e in rows)
                                         / float(len(rows)), 2),
            "max_extra_sessions": max(e["extra_sessions"] for e in rows),
            "worst_event": {"date": worst.get("date"),
                            "name": worst["name"],
                            "extra_sessions": worst["extra_sessions"],
                            "return_pct": worst.get(ret_key),
                            "bp_contrib": worst[key]}}


def run_weeknames(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",)):
    """E71: the weekly book's -45bp price-path residual -- timing or names?

    E70 switched the fee off and left a -45bp residual on the full weekly grid
    against month-end. Two channels fit that number: WHEN the book trades, or
    WHAT it holds. Both books here equal-weight the whole live universe, so
    membership can only diverge through the eligibility flow -- names that
    appear or drop out between one decision and the next. This census measures
    both: name overlap at paired sessions (the timing question) and the
    sessions a dropped name is still held (the membership question).
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    rank_cache = {}
    me_idxs = sorted(set(base.month_end_indices(cal)))
    wk_idxs = sorted(set(_weekly_indices(cal)))
    wnm_idxs = sorted(set(_nearest_weekly_to_month_end(wk_idxs, me_idxs)))

    def held(idx):
        return e27._rank(idx, universe, prices, amounts, rank_cache)[:pick_n]

    # a mid-arrival tail bar holds a stub book; drop those decisions instead of
    # letting one incomplete session read as a name explosion
    raw_me = {i: held(i) for i in me_idxs}
    raw_wk = {i: held(i) for i in wk_idxs}
    keep_me = _tail_guard([len(raw_me[i]) for i in me_idxs])
    keep_wk = _tail_guard([len(raw_wk[i]) for i in wk_idxs])
    me_idxs = [i for i, k in zip(me_idxs, keep_me) if k]
    wk_idxs = [i for i, k in zip(wk_idxs, keep_wk) if k]
    dropped = {"me": keep_me.count(False), "week": keep_wk.count(False)}
    wnm_idxs = sorted(set(i for i in wnm_idxs if i in set(wk_idxs)))
    books = {"me": me_idxs, "week": wk_idxs, "week_near_me": wnm_idxs}

    held_by_book = {lab: [held(i) for i in idxs] for lab, idxs in books.items()}

    nearest = _pair_to_grid(me_idxs, wk_idxs)
    pairs_week, pairs_wnm, seen_partner = [], [], set()
    for me_i in me_idxs:
        wk_i = nearest.get(me_i)
        if wk_i is None:
            continue
        base_names = held_by_book["me"][me_idxs.index(me_i)]
        week_names = held_by_book["week"][wk_idxs.index(wk_i)]
        row = _overlap_stats(base_names, week_names)
        row.update({"date": cal[me_i], "partner_date": cal[wk_i],
                    "session_offset": wk_i - me_i,
                    "same_session": wk_i == me_i})
        pairs_week.append(row)
        if wk_i not in seen_partner:
            seen_partner.add(wk_i)
            row2 = dict(row)
            row2["wnm_index"] = wnm_idxs.index(wk_i) if wk_i in wnm_idxs else None
            pairs_wnm.append(row2)

    def _by_era(pairs):
        out = {}
        for name, lo, hi in ERAS:
            rows = [p for p in pairs if _in_era(p["date"][:7], lo, hi)]
            if rows:
                out[name] = _pair_summary(rows)
        return out

    churn = {lab: _name_churn_stats(held_by_book[lab]) for lab in books}
    stale = {lab: _stale_hold_stats(books[lab], held_by_book[lab]) for lab in books}
    unions = {lab: sorted(set().union(*[set(h) for h in sets]))
              if sets else [] for lab, sets in held_by_book.items()}

    summ_week = _pair_summary(pairs_week)
    summ_wnm = _pair_summary(pairs_wnm)
    face = {
        "study": "e71_monthend_weekly_names",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "start": start, "universe_members": len(universe),
                 "dropped_decisions": dropped,
                 "calendars": {lab: len(idxs) for lab, idxs in books.items()}},
        "books": {lab: {"decision_days": len(books[lab]),
                        "union_names_ever_held": len(unions[lab]),
                        "self_churn": churn[lab],
                        "stale_hold": stale[lab]} for lab in books},
        "pairs": {"me_vs_week_nearest": {"summary": summ_week,
                                         "eras": _by_era(pairs_week)},
                  "me_vs_week_near_me": {"summary": summ_wnm,
                                         "eras": _by_era(pairs_wnm)}},
        "exclusive_names": {
            "week_only": len(set(unions["week"]) - set(unions["me"])),
            "me_only": len(set(unions["me"]) - set(unions["week"])),
            "both": len(set(unions["week"]) & set(unions["me"])),
        },
        "answers": {
            "share_me_vs_week_nearest": summ_week["mean_share_of_base"],
            "share_me_vs_week_near_me": summ_wnm["mean_share_of_base"],
            "membership_reading": _membership_reading(summ_week["mean_share_of_base"]),
            "names_changed_per_week_step": churn["week"]["mean_names_changed"],
            "names_changed_per_me_step": churn["me"]["mean_names_changed"],
            "stale_hold_sessions_week": stale["week"]["mean_sessions_held_after_exit"],
            "stale_hold_sessions_near_me":
                stale["week_near_me"]["mean_sessions_held_after_exit"],
            "stale_hold_sessions_me": stale["me"]["mean_sessions_held_after_exit"],
            "mean_entrants_per_pair": summ_week["mean_entrants"],
            "mean_exits_per_pair": summ_week["mean_exits"],
            "same_session_pairs": summ_week["same_session_pairs"],
        },
        "honest": [
            "both books equal-weight the entire live universe (pick_n=%d), so this "
            "census measures the eligibility flow and not a top-N selection rule"
            % pick_n,
            "the overlap rows compare each month-end decision with the nearest weekly "
            "session; where those coincide the overlap is exact by construction and "
            "the coincident pairs are counted separately, not averaged away",
            "stale_hold is truncated at the window ends -- the last exit of the series "
            "has no following decision and is never counted",
            "`week_near_me` reuses the same pairing as the nearest-weekly read, deduped "
            "on the weekly session, because that is exactly how its calendar is built",
            "membership_reading is a 0.95 flat threshold on the mean overlap: a label, "
            "not a test, and no prereg covers it",
            "decisions priced on a mid-arrival bar or on an empty cash book (live count "
            "collapsing against its neighbours) are dropped and counted in "
            "spec.dropped_decisions -- without that guard one unfinished session "
            "reads as a +1200-name entrant wave",
            "an era missing from the pair table was dropped as a cash/stub block, not "
            "censused as perfect agreement: the eligibility burn-in leaves the early "
            "window in cash, the same cash-slice signature E59/E64 print as an exact "
            "0.0bp gap",
            "descriptive census only: no gate, no verdict, no ledger booking, trial 0",
        ],
    }
    return face


def _stale_hold_inputs(start, pick_n, exclude):
    """(E72/E74) shared panel, calendars and books for both stale legs.

    Factored out so the absolute (E72) and relative (E74) reads cannot drift
    onto two different panels or two different decision calendars.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw_all = e27.load_universe()
    if exclude:
        raw_all = {s: v for s, v in raw_all.items()
                   if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    all_syms = sorted(set(base.LADDER) | set(raw_all))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw_all.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw_all]
    rank_cache = {}
    me_idxs = sorted(set(base.month_end_indices(cal)))
    wk_idxs = sorted(set(_weekly_indices(cal)))

    def held(idx):
        return e27._rank(idx, universe, prices, amounts, rank_cache)[:pick_n]

    raw_me = {i: held(i) for i in me_idxs}
    raw_wk = {i: held(i) for i in wk_idxs}
    keep_me = _tail_guard([len(raw_me[i]) for i in me_idxs])
    keep_wk = _tail_guard([len(raw_wk[i]) for i in wk_idxs])
    me_idxs = [i for i, k in zip(me_idxs, keep_me) if k]
    wk_idxs = [i for i, k in zip(wk_idxs, keep_wk) if k]
    return {"cal": cal, "cutoff": cutoff, "prices": prices,
            "universe": universe, "me_idxs": me_idxs, "wk_idxs": wk_idxs,
            "dropped": {"me": keep_me.count(False),
                        "week": keep_wk.count(False)},
            "me_books": [raw_me[i] for i in me_idxs],
            "wk_books": [raw_wk[i] for i in wk_idxs]}


def run_stalehold(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",)):
    """E72: what is the stale-hold tail actually worth, in bp?

    E71 found the last membership channel left between the month-end and weekly
    books: a name dropped by the weekly book lingers in the monthly book for the
    rest of the month (20.7 vs 4.9 sessions). This leg prices that tail instead
    of counting it -- for every exit event it compounds the name's own return
    over the sessions the monthly book still holds it after the weekly book has
    sold, charged at the book's equal weight, and reports the total in bp and
    bp/yr against the -45bp residual E70 left on the full weekly grid.
    """
    ds = _stale_hold_inputs(start, pick_n, exclude)
    cal, cutoff, prices = ds["cal"], ds["cutoff"], ds["prices"]
    me_idxs, me_books = ds["me_idxs"], ds["me_books"]
    wk_idxs, wk_books = ds["wk_idxs"], ds["wk_books"]
    universe, dropped = ds["universe"], ds["dropped"]

    events, skipped = _stale_hold_events(
        me_idxs, me_books, wk_idxs, wk_books,
        lambda s, a, b: _cum_return(prices.get(s), a, b))
    for e in events:
        e["date"] = cal[e["me_session"]]
        e["weekly_exit_date"] = cal[e["weekly_session"]]

    years = _years_between(cal[me_idxs[0]], cal[me_idxs[-1]]) if me_idxs else None
    overall = _stale_aggregate(events, years)
    by_era = {}
    for name, lo, hi in ERAS:
        rows = [e for e in events if _in_era(e["date"][:7], lo, hi)]
        era_years = (_years_between(rows[0]["date"], rows[-1]["date"])
                     if len(rows) > 1 else None)
        by_era[name] = _stale_aggregate(rows, era_years)

    # the same tail read as an average drag per calendar year of holding
    sessions_span = (me_idxs[-1] - me_idxs[0]) if len(me_idxs) > 1 else 0
    stable = {
        "events": overall["events"],
        "total_bp": overall["total_bp"],
        "bp_per_year": overall["bp_per_year"],
        "mean_return_pct": overall["mean_return_pct"],
        "negative_share": overall["negative_share"],
        "mean_extra_sessions": overall["mean_extra_sessions"],
        "max_extra_sessions": overall["max_extra_sessions"],
        "worst_event": overall["worst_event"],
    }
    face = {
        "study": "e72_stale_hold_price",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "start": start, "universe_members": len(universe),
                 "dropped_decisions": dropped,
                 "calendars": {"me": len(me_idxs), "week": len(wk_idxs)},
                 "sessions_span": sessions_span, "years": years,
                 "charge": "1/n_held_before of the monthly book, name's own return "
                           "from the weekly drop session to the monthly drop session"},
        "tail": stable,
        "by_era": by_era,
        "skipped": skipped,
        "answers": {
            "stale_events": overall["events"],
            "tail_total_bp": overall["total_bp"],
            "tail_bp_per_year": overall["bp_per_year"],
            "tail_mean_return_pct": overall["mean_return_pct"],
            "tail_negative_share": overall["negative_share"],
            "stale_sessions_mean": overall["mean_extra_sessions"],
            "newest_era_tail_bp": by_era.get("2024_now", {}).get("total_bp"),
            "newest_era_tail_bp_per_year":
                by_era.get("2024_now", {}).get("bp_per_year"),
            "residual_to_explain_bp": -45.0,
            "residual_source": "E70 weeklyclash cost face (full weekly grid vs "
                               "month-end, x0/x3 residual, 2020 start)",
        },
        "honest": [
            "the tail is priced as name return x equal weight over the extra "
            "sessions; it is not a re-run of either book's P&L, so it cannot "
            "double-count the calendar gaps E65-E69 already priced",
            "an event needs a priced base at the weekly drop session and a priced "
            "close at the monthly drop session; unpriced ends are counted in "
            "skipped.unpriced instead of being charged as a flat hold",
            "names held by the monthly book that never appear in the weekly book "
            "are counted in skipped.never_in_weekly_book and excluded -- they are "
            "not a stale tail, they are a coverage difference",
            "events are charged once each, at the decision that sees the exit, so "
            "a name that enters and exits repeatedly contributes several events",
            "bp_per_year divides the window total by the calendar span, which "
            "understates a concentrated tail in a short era and overstates a "
            "tail diluted over a long one -- read it beside per-era totals",
            "the -45bp residual is quoted from the E70 face as published; no "
            "attempt is made here to recompute it",
            "descriptive census only: no gate, no verdict, no ledger booking, trial 0",
        ],
    }
    return face


def _wide_session_returns(prices, universe, n_sessions):
    """(E74) equal-weight return of the live universe at every session.

    The reference book for the relative stale tail: for session t it averages
    the close-to-close return of every universe member priced at both t-1 and t.
    A session with no priced member is None, and a None anywhere in a span makes
    the compounded span None -- a gap is disclosed, never filled with zero.
    """
    out = [None] * int(n_sessions)
    for t in range(1, int(n_sessions)):
        vals = []
        for s in universe:
            r = _cum_return(prices.get(s), t - 1, t)
            if r is not None:
                vals.append(r)
        if vals:
            out[t] = sum(vals) / float(len(vals))
    return out


def _compound_between(rets, i0, i1):
    """(E74) compound the wide book from session i0 to i1 (exclusive of i0)."""
    if not rets or i0 is None or i1 is None or i1 <= i0:
        return None
    if i0 < 0 or i1 >= len(rets):
        return None
    acc = 1.0
    for t in range(i0 + 1, i1 + 1):
        if rets[t] is None:
            return None
        acc *= (1.0 + rets[t])
    return acc - 1.0


def _max_session_jump(series, i0, i1):
    """(E74) largest absolute move between two consecutive PRICED closes.

    The panel carries some names unadjusted, so a share split prints as a -90%
    "return" and a stale-tail total can be one corporate action. Missing bars
    are skipped rather than aborting the screen: the split itself often hides a
    suspension gap (a None session sits right beside it), so a None-blind scan
    would miss the very artefact it is looking for. Fewer than two priced closes
    in the span leaves the event unjudged (None), never clean.
    """
    if series is None or i0 is None or i1 is None or i1 <= i0:
        return None
    if i0 < 0 or i1 >= len(series):
        return None
    worst, last, n_priced = 0.0, None, 0
    for t in range(i0, i1 + 1):
        v = series[t]
        if v is None or v <= 0:
            continue
        n_priced += 1
        if last is not None:
            r = v / float(last) - 1.0
            if abs(r) > worst:
                worst = abs(r)
        last = v
    return worst if n_priced >= 2 else None


def _relative_reading(raw_bp, rel_bp, shrink_share=0.25, floor_bp=5.0):
    """(E74) label whether a raw tail collapses once the book is subtracted.

    A label, not a test: 'collapsed' when the relative number is inside
    max(floor_bp, shrink_share * |raw|), 'survives' when it keeps at least half
    the raw magnitude with the same sign, 'partial' otherwise.
    """
    if raw_bp is None or rel_bp is None:
        return "insufficient"
    mag = max(floor_bp, shrink_share * abs(raw_bp))
    if abs(rel_bp) <= mag:
        return "collapsed"
    if (raw_bp > 0) == (rel_bp > 0) and abs(rel_bp) >= 0.5 * abs(raw_bp):
        return "survives"
    return "partial"


def run_staletail(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",)):
    """E74: is the stale tail a name effect, or the market's own path?

    E72 priced the tail raw and its sign flipped era to era (+282bp/yr pre2017,
    -226bp/yr 2021_2023, +1.6bp/yr 2024_now), which is the signature of beta
    rather than a membership mechanism. This leg re-charges the SAME events
    against the wide book over the identical sessions: an event that merely
    moved with the market nets to ~0, and only a surviving excess is a name
    effect worth naming.
    """
    ds = _stale_hold_inputs(start, pick_n, exclude)
    cal, cutoff, prices = ds["cal"], ds["cutoff"], ds["prices"]
    me_idxs, me_books = ds["me_idxs"], ds["me_books"]
    wk_idxs, wk_books = ds["wk_idxs"], ds["wk_books"]
    universe, dropped = ds["universe"], ds["dropped"]
    rets = _wide_session_returns(prices, universe, len(cal))

    events, skipped = _stale_hold_events(
        me_idxs, me_books, wk_idxs, wk_books,
        lambda s, a, b: _cum_return(prices.get(s), a, b),
        book_ret_fn=lambda a, b: _compound_between(rets, a, b))
    for e in events:
        e["date"] = cal[e["me_session"]]
        e["weekly_exit_date"] = cal[e["weekly_session"]]
        jump = _max_session_jump(prices.get(e["name"]), e["weekly_session"],
                                 e["me_session"])
        e["max_session_jump_pct"] = (round(jump * 100.0, 3)
                                     if jump is not None else None)
        e["artefact"] = jump is not None and jump > ARTEFACT_JUMP
    n_artefact = len([e for e in events if e["artefact"]])

    years = _years_between(cal[me_idxs[0]], cal[me_idxs[-1]]) if me_idxs else None
    raw_all = _stale_aggregate(events, years)
    rel_all = _stale_aggregate(events, years, key="relative_bp_contrib",
                               ret_key="excess_return_pct")
    clean = [e for e in events if not e.get("artefact")]
    raw_clean = _stale_aggregate(clean, years)
    rel_clean = _stale_aggregate(clean, years, key="relative_bp_contrib",
                                 ret_key="excess_return_pct")
    raw_overall, rel_overall = raw_clean, rel_clean
    by_era, by_era_raw = {}, {}
    for name, lo, hi in ERAS:
        rows_all = [e for e in events if _in_era(e["date"][:7], lo, hi)]
        rows = [e for e in rows_all if not e.get("artefact")]
        era_years = (_years_between(rows[0]["date"], rows[-1]["date"])
                     if len(rows) > 1 else None)
        by_era_raw[name] = _stale_aggregate(rows_all, era_years)
        rel = _stale_aggregate(rows, era_years, key="relative_bp_contrib",
                               ret_key="excess_return_pct")
        rel["reading"] = _relative_reading(
            _stale_aggregate(rows, era_years)["bp_per_year"],
            rel["bp_per_year"])
        rel["artefacts_excluded"] = len(rows_all) - len(rows)
        by_era[name] = rel

    sessions_span = (me_idxs[-1] - me_idxs[0]) if len(me_idxs) > 1 else 0
    face = {
        "study": "e74_stale_hold_relative",
        "evidence_cutoff": cutoff,
        "spec": {"pick_n": pick_n, "exclude_prefixes": list(exclude),
                 "start": start, "universe_members": len(universe),
                 "dropped_decisions": dropped,
                 "calendars": {"me": len(me_idxs), "week": len(wk_idxs)},
                 "sessions_span": sessions_span, "years": years,
                 "wide_book": "equal weight of every universe member priced at "
                              "both t-1 and t, compounded over the event span",
                 "charge": "1/n_held_before of the monthly book, name's own "
                           "return minus the wide book's return over the same "
                           "sessions",
                 "artefact_guard": "event excluded from the priced tail when the "
                                   "largest single-session move inside its span "
                                   "exceeds %.0f%% (a corporate action printed on "
                                   "an unadjusted series)" % (100.0 * ARTEFACT_JUMP)},
        "tail": {"raw_all_events": raw_all, "raw_clean": raw_clean,
                 "relative_all_events": rel_all, "relative_clean": rel_clean},
        "artefacts": {"excluded_events": n_artefact,
                      "jump_threshold_pct": round(100.0 * ARTEFACT_JUMP, 2),
                      "events": [{"date": e["date"], "name": e["name"],
                                  "return_pct": e["return_pct"],
                                  "max_session_jump_pct": e["max_session_jump_pct"],
                                  "bp_contrib": e["bp_contrib"]}
                                 for e in events if e["artefact"]]},
        "by_era": by_era,
        "by_era_raw": by_era_raw,
        "skipped": skipped,
        "answers": {
            "stale_events": raw_clean["events"],
            "stale_events_all": raw_all["events"],
            "artefacts_excluded": n_artefact,
            "raw_total_bp": raw_clean["total_bp"],
            "raw_bp_per_year": raw_clean["bp_per_year"],
            "raw_all_events_total_bp": raw_all["total_bp"],
            "raw_all_events_bp_per_year": raw_all["bp_per_year"],
            "relative_total_bp": rel_clean["total_bp"],
            "relative_bp_per_year": rel_clean["bp_per_year"],
            "relative_negative_share": rel_clean["negative_share"],
            "relative_share_of_raw": (
                round(rel_clean["bp_per_year"] / raw_clean["bp_per_year"], 4)
                if raw_clean["bp_per_year"] else None),
            "relative_reading": _relative_reading(raw_clean["bp_per_year"],
                                                  rel_clean["bp_per_year"]),
            "relative_all_events_bp_per_year": rel_all["bp_per_year"],
            "era_relative_reading": {k: v["reading"] for k, v in by_era.items()},
            "era_relative_bp_per_year": {k: v["bp_per_year"]
                                         for k, v in by_era.items()},
            "era_raw_bp_per_year": {k: v["bp_per_year"]
                                    for k, v in by_era_raw.items()},
            "newest_era_relative_bp": by_era.get("2024_now", {}).get("total_bp"),
            "residual_to_explain_bp": -45.0,
            "residual_source": "E70 weeklyclash cost face (full weekly grid vs "
                               "month-end, x0/x3 residual, 2020 start)",
        },
        "honest": [
            "the wide book is the whole live universe equal weight, which is the "
            "same book both calendars hold here (pick_n=%d); the relative face "
            "therefore measures the cross-sectional excess of the exiting names, "
            "not a size or style mismatch" % pick_n,
            "relative bp = name return minus the wide book's compounded return "
            "over the identical sessions, still charged at 1/n of the dropping "
            "book; it is an arithmetic difference, not a hedged P&L",
            "events whose span contains a session with no priced universe member "
            "are counted in skipped.unpriced_book and excluded from the relative "
            "columns only -- the raw columns keep them",
            "reading labels come from a 0.25 shrink share with a 5bp floor and "
            "are published as labels, not as a test; no prereg covers them",
            "an era with a handful of events (pre2017 rests on ~19) gives a "
            "bp/yr that divides a small total by a short span -- read the event "
            "count beside any era rate",
            "the -45bp residual is quoted from the E70 face as published; the "
            "relative tail is reported in its own bp/yr and is never added to it",
            "the artefact guard is a daily-limit screen, not an adjustment: a name "
            "whose series is unadjusted prints a split as a -90% tail, and such an "
            "event is excluded from the priced columns and listed in `artefacts` "
            "with its largest single-session move -- the all-events columns are "
            "kept beside the guarded ones so nothing is silently dropped",
            "descriptive census only: no gate, no verdict, no ledger booking, trial 0",
        ],
    }
    return face


# --------------------------------------------------------------- E75 panel splits

def _panel_inputs(start, exclude):
    """(E75) raw closes on the decision calendar -- no book, no rank, nothing dropped.

    The split audit must see every name a census leg could ever charge, so it
    skips the monthly/weekly book machinery and reads the closes directly.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items()
               if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    prices = {}
    for s in sorted(raw):
        closes = raw[s][0]
        prices[s] = [closes.get(d) for d in cal]
    return cal, prices, sorted(raw), cal[-1]


def _breadth(prices, universe, n_sessions):
    """(E75) priced-member count per session -- the equal-weight book's divisor."""
    out = [0] * int(n_sessions)
    for s in universe:
        for i, v in enumerate(prices.get(s) or []):
            if v is not None and v > 0 and i < len(out):
                out[i] += 1
    return out


def _split_ratio(ret):
    """(E75) implied share ratio of a flagged move and its distance to an integer.

    A 12:1 split prints as -91.7% and 1/(1+r) recovers the 12.0, so a move that
    lands near an integer is a corporate action. One that does not is a
    resumption, a restatement or a misprint -- a different thing to disclose.
    """
    if ret is None or ret <= -1.0:
        return None
    ratio = 1.0 / (1.0 + ret)
    if ratio < 1.0:
        ratio = 1.0 / ratio
    nearest = int(round(ratio))
    if nearest < 1:
        nearest = 1
    resid = abs(ratio / float(nearest) - 1.0)
    return {"ratio": round(ratio, 4), "nearest_int": nearest,
            "resid_pct": round(100.0 * resid, 3),
            "integer_like": nearest >= 2 and resid <= 0.02}


def _split_events(cal, prices, universe, breadth, thresh=ARTEFACT_JUMP):
    """(E75) every panel-wide single-session move past the daily-limit screen.

    Bars are compared against the previous PRICED close (a split frequently sits
    next to a suspension bar, so a None-abort scan misses it -- the E74 lesson),
    and the gap is carried on the event: an adjacent-session move past the limit
    cannot be a real A-share print, while a gapped one can be a resumption.
    """
    events = []
    for s in universe:
        last, last_i = None, None
        for i, v in enumerate(prices.get(s) or []):
            if v is None or v <= 0:
                continue
            if last is not None:
                r = v / float(last) - 1.0
                if abs(r) > thresh:
                    n = breadth[i] if i < len(breadth) else 0
                    events.append({
                        "name": s,
                        "date": cal[i],
                        "prev_date": cal[last_i],
                        "prev_close": round(last, 4),
                        "close": round(v, 4),
                        "ret_pct": round(100.0 * r, 2),
                        "direction": "down" if r < 0 else "up",
                        "gap_sessions": i - last_i,
                        "adjacent": (i - last_i) == 1,
                        "era": _era_of(cal[i]),
                        "breadth": n,
                        "book_impact_bp": (round(10000.0 * abs(r) / n, 2)
                                           if n else None),
                        "implied_ratio": _split_ratio(r),
                    })
            last, last_i = v, i
    return events


def _split_summary(events, years):
    """(E75) book-level cost of the flagged prints: one name in an n-name book."""
    rows = [e for e in events if e.get("book_impact_bp") is not None]
    impacts = [e["book_impact_bp"] for e in rows]
    total = sum(impacts)
    integer_like = [e for e in rows
                    if (e.get("implied_ratio") or {}).get("integer_like")]
    return {
        "events": len(rows),
        "names": len(set(e["name"] for e in rows)),
        "adjacent": len([e for e in rows if e["adjacent"]]),
        "gapped": len([e for e in rows if not e["adjacent"]]),
        "down": len([e for e in rows if e["direction"] == "down"]),
        "up": len([e for e in rows if e["direction"] == "up"]),
        "integer_ratio_events": len(integer_like),
        "non_integer_events": len(rows) - len(integer_like),
        "total_book_bp": round(total, 2),
        "bp_per_year": (round(total / years, 2) if years and years > 0 else None),
        "max_event_bp": (round(max(impacts), 2) if impacts else None),
        "median_event_bp": (round(_quant(impacts, 0.5), 2) if impacts else None),
        "years": years,
    }


def run_panelsplit(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                   top_n=15):
    """E75: how many published census numbers sit on unadjusted corporate actions?

    E74 found 19 of 128 stale-tail events were unadjusted splits and that they
    alone flipped an era column's sign. This leg asks the panel-wide version:
    every single-session move past the 30% daily-limit screen, who it belongs to,
    whether it lands on an integer share ratio, and what it costs an equal-weight
    book (one name charges |r|/n).
    """
    cal, prices, universe, cutoff = _panel_inputs(start, exclude)
    breadth = _breadth(prices, universe, len(cal))
    events = _split_events(cal, prices, universe, breadth)
    years = _years_between(cal[0], cal[-1]) if cal else None

    by_era = {}
    for name, lo, hi in ERAS:
        rows = sorted([e for e in events if e.get("era") == name],
                      key=lambda e: e["date"])
        era_years = (_years_between(rows[0]["date"], rows[-1]["date"])
                     if len(rows) > 1 else None)
        by_era[name] = _split_summary(rows, era_years)
    by_year = {}
    for e in events:
        y = e["date"][:4]
        by_year[y] = by_year.get(y, 0) + 1

    ranked = sorted([e for e in events if e.get("book_impact_bp") is not None],
                    key=lambda e: -e["book_impact_bp"])
    live_breadth = [b for b in breadth if b > 0]
    face = {
        "study": "e75_panel_split_audit",
        "evidence_cutoff": cutoff,
        "spec": {"start": start, "exclude_prefixes": list(exclude),
                 "panel_names": len(universe), "sessions": len(cal),
                 "years": years,
                 "screen": "consecutive PRICED closes, missing bars skipped and "
                           "never filled; flag |return| > %.0f%%"
                           % (100.0 * ARTEFACT_JUMP),
                 "charge": "an equal-weight book of n live names absorbs one "
                           "name's move as |r|/n; breadth is the priced-member "
                           "count at that session",
                 "pick_n": "accepted for CLI parity and unused -- this leg "
                           "audits every panel name"},
        "panel": {"events": len(events),
                  "names": len(set(e["name"] for e in events)),
                  "breadth_median": _quant(live_breadth, 0.5),
                  "breadth_min": min(live_breadth) if live_breadth else None,
                  "breadth_max": max(live_breadth) if live_breadth else None},
        "summary": _split_summary(events, years),
        "by_era": by_era,
        "events_per_year": dict(sorted(by_year.items())),
        "top_events": ranked[:top_n],
        "screening": {
            "screened_legs": ["staletail (E74: events inside the stale tail)"],
            "unscreened_rule": "every census leg in this file charges per-name "
                               "returns out of the same e27.load_universe() "
                               "closes, so an unadjusted print enters any "
                               "equal-weight number at weight 1/n; only staletail "
                               "screens for it",
            "selection_channel": "rank/_rank sorts on traded amount, and a split "
                                 "re-prices the share, so the amount leg is "
                                 "distorted on the same date as the return leg"},
        "answers": dict(_split_summary(events, years), **{
            "panel_names": len(universe),
            "top_event": ({"name": ranked[0]["name"], "date": ranked[0]["date"],
                           "ret_pct": ranked[0]["ret_pct"],
                           "book_impact_bp": ranked[0]["book_impact_bp"]}
                          if ranked else None)}),
        "honest": [
            "the screen flags arithmetic impossibilities, not confirmed corporate "
            "actions: an adjacent-session move past 30% cannot be a real A-share "
            "return under the 10%/20% limits, but the panel also carries ETFs and "
            "bonds whose daily limits differ, so a flagged ETF print may be genuine",
            "the integer-ratio fingerprint is inferred from the price ratio alone "
            "with a 2% band and no announcement feed; non-integer events are listed "
            "as unclassified, never as clean",
            "book impact assumes equal weight at 1/n of the live breadth: it sizes "
            "the distortion, it is not a correction to any published number",
            "gapped events (a resumption after suspension) can be real; the "
            "adjacent flag is the hard screen and the gap is published on every row",
            "pick_n is unused here by design -- the audit covers the whole panel so "
            "no book construction can hide a print",
            "descriptive census only: no gate, no verdict, no ledger booking, trial 0",
        ],
    }
    return face


# ------------------------------------------- leg: E76 screen-regrade (opt-in)
#
# E75 sized the problem: 135 adjacent-session prints past the 30% screen on 152
# names, ~216bp/yr of equal-weight book impact -- 4.8x the -45bp residual the
# chain had been chasing. But E75 only *sized* it; every published ladder and
# era-spread number still charges the unadjusted prints. This leg is the other
# half: the same two headline faces replayed from a repaired universe, with the
# unscreened column kept beside them so the correction is measured, not claimed.

LADDER_COLUMNS = ("ann_pct", "vol_pct", "sharpe", "max_drawdown_pct",
                  "worst_month_return_pct", "turnover_per_year",
                  "cost_per_year_bp")
ERA_COLUMNS = ("spread_ann_bp", "ladder_ann_pct", "wide_ann_pct")
ERA_RATIO_COLUMNS = ("max_drawdown_pct", "ann_pct")


def _ladder_window(raw, cal, start):
    """One ladder5 window (the E39 columns) from an already loaded universe."""
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    years = len(cal) / 252.0
    prices = {}
    for s in base.LADDER:
        c = raw.get(s, ({}, {}))[0] if s in raw else {}
        if not c:
            c = base.load_panel(s)[1].get(s, {})
        prices[s] = [c.get(d) for d in cal]
    cash = base.load_cash_series(cal)
    curve, aux, _hold = e27.simulate(cal, prices, {}, base.LADDER, cash, None, 1.0, {})
    m = base.metrics(curve, years)
    prof = risk_profile(curve, years)
    return {
        "start": start, "bars": len(cal),
        "ann_pct": m.get("ann_return_pct"),
        "vol_pct": m.get("ann_vol_pct"),
        "sharpe": m.get("sharpe"),
        "max_drawdown_pct": prof["max_drawdown_pct"],
        "worst_month_return_pct": (prof["worst_month"] or {}).get("return_pct"),
        "turnover_per_year": (round(aux["turnover_total"] / years, 4) if years else None),
        "cost_per_year_bp": (round(aux["cost_paid_frac"] / years * 1e4, 2) if years else None),
    }


def _screen_face(raw, cal_full, pick_n, eras, ladder_starts):
    """The two headline faces (ladder windows + era spread) from one universe."""
    ladder = {}
    for start in ladder_starts:
        cal = [d for d in cal_full if d >= start]
        ladder[start] = _ladder_window(raw, cal, start)
    lad, wide, ratio = _era_curves(raw, cal_full, pick_n)
    return {"ladder": ladder, "eras": _era_rows(lad, wide, ratio, eras)}


def _delta_rows(base_label, faces):
    """Column-by-column unscreened vs screened table, one row per cell."""
    rows = []
    base_face = faces[base_label]
    others = [k for k in faces if k != base_label]

    def cell(row, key, u, v):
        row[key] = v
        row["delta_" + key] = (round(v - u, 4)
                               if isinstance(v, (int, float)) and isinstance(u, (int, float))
                               else None)

    for start in sorted(base_face["ladder"]):
        u = base_face["ladder"][start]
        for col in LADDER_COLUMNS:
            row = {"face": "ladder@%s" % start, "column": col,
                   "unscreened": u.get(col)}
            for mode in others:
                cell(row, mode, u.get(col), faces[mode]["ladder"][start].get(col))
            rows.append(row)
    for era in base_face["eras"]:
        u = base_face["eras"][era]
        if "spread_ann_bp" not in u:
            continue
        for col in ERA_COLUMNS:
            row = {"face": "era:%s" % era, "column": col, "unscreened": u.get(col)}
            for mode in others:
                cell(row, mode, u.get(col), faces[mode]["eras"][era].get(col))
            rows.append(row)
        for col in ERA_RATIO_COLUMNS:
            ur = (u.get("ratio_path") or {}).get(col)
            row = {"face": "era:%s" % era, "column": "ratio_" + col,
                   "unscreened": ur}
            for mode in others:
                cell(row, mode, ur,
                     (faces[mode]["eras"][era].get("ratio_path") or {}).get(col))
            rows.append(row)
    return rows


def _member_print_face(closes, cal, thresh=None):
    """(E76) how many adjacent/gapped artefact prints one series carries."""
    import panel_screen
    if not closes:
        return {"adjacent": 0, "gapped": 0, "prints": []}
    events = panel_screen.split_events(closes, cal=cal)
    adj = [e for e in events if e["adjacent"]]
    return {"adjacent": len(adj), "gapped": len(events) - len(adj),
            "prints": [{"date": e["date"], "ret_pct": round(e["ret_pct"], 2),
                        "adjacent": e["adjacent"]} for e in events]}


def run_screenreg(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                  modes=("neutralise_int", "neutralise", "drop"), eras=ERAS,
                  ladder_starts=("2020-01-01", "2018-01-01")):
    """E76: re-derive the ladder + era-spread headline with the split screen on.

    The loader is opt-in (``scripts/panel_screen.py``); this leg is the only
    caller in the census chain, and it publishes the unscreened column beside
    every screened one. A screened number without its unscreened twin would let
    one silent repair move the whole book.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    faces = {"unscreened": _screen_face(raw, cal_full, pick_n, eras, ladder_starts)}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        faces[mode] = _screen_face(repaired, cal_full, pick_n, eras, ladder_starts)

    delta = _delta_rows("unscreened", faces)

    def _biggest(pred):
        rows = [r for r in delta if pred(r)]
        if not rows:
            return None
        best = max(rows, key=lambda r: max(
            abs(r["delta_" + m]) for m in modes if r.get("delta_" + m) is not None))
        out = {"face": best["face"], "column": best["column"],
               "unscreened": best["unscreened"]}
        for m in modes:
            out[m] = best.get(m)
            out["delta_" + m] = best.get("delta_" + m)
        return out

    flipped = sorted(era for era in faces["unscreened"]["eras"]
                     if "spread_ann_bp" in faces["unscreened"]["eras"][era]
                     and any((faces[m]["eras"][era].get("spread_ann_bp") or 0)
                             * (faces["unscreened"]["eras"][era]["spread_ann_bp"] or 0) < 0
                             for m in modes))

    return {
        "study": "e76_panelscreen_regrade",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "cost_bp_per_side": base.COST_BP_SIDE,
            "ladder_starts": list(ladder_starts),
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "loader": "scripts/panel_screen.py (opt-in; every other leg still "
                      "reads e27.load_universe() unmodified)",
            "books": "ladder5 = E39 engine call on the five ladder members; era "
                     "spread = E41 ladder5 vs wide_topN on the full calendar",
        },
        "screen_reports": reports,
        "faces": faces,
        "delta": delta,
        "answers": {
            "ladder_worst_correction": _biggest(
                lambda r: r["face"].startswith("ladder@")),
            "ladder_member_prints": {
                s: _member_print_face(raw.get(s, ({}, {}))[0], cal_full)
                for s in base.LADDER if s in raw},
            "era_worst_correction": _biggest(
                lambda r: r["face"].startswith("era:") and r["column"] == "spread_ann_bp"),
            "eras_whose_spread_changes_sign": flipped,
            "delta_cells": len(delta),
            "non_zero_delta_cells": len([r for r in delta
                                         if any(r.get("delta_" + m) not in (None, 0)
                                                for m in modes)]),
        },
        "honest": [
            "the screen repairs arithmetic impossibility only: a flagged ETF print "
            "may be genuine (ETF daily limits differ from the 10%/20% stock band), "
            "so 'neutralise' is a sensitivity face, not a corrected truth",
            "three columns are published for that reason: neutralise_int repairs only "
            "the prints whose price ratio lands on an integer (a share ratio with no "
            "announcement feed), neutralise repairs every adjacent print, drop removes "
            "the name -- the range between them bounds the correction",
            "a slashed >30% sequence may need more than one event to clear; the "
            "loader applies every adjacent event it finds, and the report lists them",
            "the screened book is not a pre-registration and books no trial: it is "
            "the same descriptive face replayed from a different input",
            "drop mode changes the universe (n and eligibility), so its delta mixes "
            "the correction with a composition change; neutralise isolates it",
            "gapped prints are deliberately not repaired -- a resumption after "
            "suspension can be a real market print, and on this panel both ladder5 "
            "corporate actions sit behind a suspension bar, which is why the ladder "
            "column does not move at all (ladder_member_prints shows each one)",
            "descriptive census only: no gate, no verdict, no ledger booking, trial 0",
        ],
    }


def _screengapera_rows(faces, base="unscreened", adjacent="neutralise"):
    """(E93) One row per era: the published spread under every arm, with the
    delta against BOTH the untouched column and the adjacent-only column.

    The adjacent-only delta is the one the E92 chain needed: it isolates what
    the gap-tolerant repair adds, because the adjacent-only arm already
    carries the default screen. Rows only exist for eras that actually publish
    a spread (a wide leg with no live member cannot)."""
    rows = []
    for era in faces[base]["eras"]:
        u = faces[base]["eras"][era]
        if "spread_ann_bp" not in u:
            continue
        adj = (faces.get(adjacent, {}).get("eras", {}).get(era) or {}).get(
            "spread_ann_bp")
        row = {"era": era, "unscreened_spread_ann_bp": u.get("spread_ann_bp"),
               "adjacent_only_spread_ann_bp": adj}
        for arm in faces:
            if arm in (base, adjacent):
                continue
            v = (faces[arm]["eras"].get(era) or {}).get("spread_ann_bp")
            row[arm + "_spread_ann_bp"] = v
            row["delta_vs_unscreened_" + arm] = (
                round(v - u["spread_ann_bp"], 4)
                if isinstance(v, (int, float)) else None)
            row["delta_vs_adjacent_only_" + arm] = (
                round(v - adj, 4)
                if isinstance(v, (int, float)) and isinstance(adj, (int, float))
                else None)
        rows.append(row)
    return rows


def run_screengapera(outdir, start="2020-01-01", pick_n=9999,
                     exclude=("sh511",), eras=ERAS,
                     ladder_starts=("2020-01-01", "2018-01-01"),
                     gap_limits=(1, 5)):
    """E93: re-derive the era-SPREAD face (the number the chain publishes as
    an edge) with the gap-tolerant screen beside the untouched and the
    adjacent-only columns.

    E92 showed the churn LEVELS move while the churn GAP does not, but the
    churn sleeve is a name-level mean -- this leg reads the ladder-vs-wide era
    spread itself under gap_limit 1 and 5. No arm is overwritten: each arm is
    a separately labelled column, and both the unscreened and the adjacent-only
    spreads are carried into every row so no arm can be silently swapped.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    arms = ["unscreened", "neutralise", "neutralise_int"]
    arms += ["neutralise_gap@%d" % g for g in gap_limits]
    faces = {"unscreened": _screen_face(raw, cal_full, pick_n, eras,
                                        ladder_starts)}
    reports = {}
    for mode in ("neutralise", "neutralise_int"):
        repaired, report = panel_screen.screen_universe(raw, mode=mode,
                                                        cal=cal_full)
        reports[mode] = report
        faces[mode] = _screen_face(repaired, cal_full, pick_n, eras,
                                   ladder_starts)
    for g in gap_limits:
        repaired, report = panel_screen.screen_universe(
            raw, mode="neutralise_gap", cal=cal_full, gap_limit=g)
        arm = "neutralise_gap@%d" % g
        reports[arm] = report
        faces[arm] = _screen_face(repaired, cal_full, pick_n, eras,
                                  ladder_starts)

    rows = _screengapera_rows(faces)
    gap_arms = [a for a in arms if a.startswith("neutralise_gap@")]

    def _signs_against(col):
        out = []
        for r in rows:
            u = r[col]
            if not isinstance(u, (int, float)) or u == 0:
                continue
            for a in gap_arms:
                v = r.get(a + "_spread_ann_bp")
                if isinstance(v, (int, float)) and v * u < 0:
                    out.append({"era": r["era"], "arm": a,
                                col: u, "arm_spread_ann_bp": v})
                    break
        return out

    worst = None
    for r in rows:
        for a in gap_arms:
            d = r.get("delta_vs_unscreened_" + a)
            if d is None:
                continue
            if worst is None or abs(d) > abs(worst["delta_vs_unscreened"]):
                worst = {"era": r["era"], "arm": a,
                         "unscreened": r["unscreened_spread_ann_bp"],
                         "arm_spread_ann_bp": r.get(a + "_spread_ann_bp"),
                         "delta_vs_unscreened": d,
                         "delta_vs_adjacent_only":
                             r.get("delta_vs_adjacent_only_" + a)}
    marginal = []
    if len(gap_limits) >= 2:
        lo, hi = "neutralise_gap@%d" % gap_limits[0], \
                 "neutralise_gap@%d" % gap_limits[-1]
        for r in rows:
            a, b = r.get(lo + "_spread_ann_bp"), r.get(hi + "_spread_ann_bp")
            marginal.append({"era": r["era"], "arm_low": lo, "arm_high": hi,
                             "delta": (round(b - a, 4)
                                       if isinstance(a, (int, float))
                                       and isinstance(b, (int, float)) else None)})

    return {
        "study": "e93_screengap_era_spread",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n,
            "exclude_prefixes": list(exclude), "arms": arms,
            "gap_limits_sessions": list(gap_limits),
            "cost_bp_per_side": base.COST_BP_SIDE,
            "ladder_starts": list(ladder_starts),
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": "era spread = E41 ladder5 vs wide_topN on the full "
                     "calendar (same face E76 published); ladder windows "
                     "carried for completeness",
            "loader": "scripts/panel_screen.py (opt-in, integer-ratio gate)",
        },
        "screen_reports": reports,
        "era_rows": rows,
        "ladder_faces": {a: faces[a]["ladder"] for a in arms},
        "answers": {
            "eras_whose_spread_changes_sign_vs_unscreened":
                _signs_against("unscreened_spread_ann_bp"),
            "eras_whose_spread_changes_sign_vs_adjacent_only":
                _signs_against("adjacent_only_spread_ann_bp"),
            "worst_era_correction": worst,
            "gap_limit_marginal": marginal,
            "eras_compared": len(rows),
            "gap_arms": gap_arms,
        },
        "honest": [
            "descriptive census only: no gate, no verdict, no ledger booking, "
            "trial 0 (a re-read of an already published face, not a new claim)",
            "the gap-tolerant arm repairs only prints whose implied ratio lands "
            "on an integer and that sit within gap_limit sessions of the last "
            "priced close; everything else is left alone",
            "the adjacent-only and unscreened arms are re-derived, never "
            "rewritten: SCREENREG/SCREENGAP files on disk are untouched",
            "era spread is a sleeve-level mean of a name-level book, so a "
            "shift here is a composition-and-print effect on the same members, "
            "not a strategy change",
        ],
    }


# ------------------------------------------------------------ E77 wide screen

WIDE_COLUMNS = ("wide_ann_pct", "wide_total_return_pct", "wide_vol_pct",
                "wide_sharpe", "ladder_ann_pct", "vs_ladder_bp_annualised",
                "turnover_per_year", "cost_per_year_bp", "mean_bp", "t")
WIDE_ERA_COLUMNS = ("wide_ann_pct", "ladder_ann_pct", "spread_ann_bp",
                    "ratio_ann_pct", "ratio_max_drawdown_pct")


def _wide_headline(face, pick_n=9999):
    """(E77) the wide-book headline columns out of one e27 universe face."""
    w = (face.get("schemes") or {}).get("top%d" % pick_n) or {}
    lad = (face.get("schemes") or {}).get("ladder5") or {}
    m = w.get("metrics") or {}
    a = w.get("aux") or {}
    rel = w.get("vs_ladder") or {}
    return {
        "wide_ann_pct": m.get("ann_return_pct"),
        "wide_total_return_pct": m.get("total_return_pct"),
        "wide_vol_pct": m.get("ann_vol_pct"),
        "wide_sharpe": m.get("sharpe"),
        "ladder_ann_pct": (lad.get("metrics") or {}).get("ann_return_pct"),
        "vs_ladder_bp_annualised": w.get("vs_ladder_bp_annualised"),
        "turnover_per_year": a.get("turnover_per_year"),
        "cost_per_year_bp": a.get("cost_per_year_bp"),
        "months": rel.get("months"),
        "mean_bp": rel.get("mean_bp"),
        "t": rel.get("t"),
        "universe_size": face.get("universe_size"),
        "bars": face.get("bars"),
    }


def _wide_era_headline(rows):
    """(E77) flatten _era_rows into the wide-book era column set."""
    out = {}
    for era, r in rows.items():
        if "spread_ann_bp" not in r:
            out[era] = {"skipped": r.get("skipped"), "bars": r.get("bars")}
            continue
        ratio = r.get("ratio_path") or {}
        out[era] = {
            "wide_ann_pct": r.get("wide_ann_pct"),
            "ladder_ann_pct": r.get("ladder_ann_pct"),
            "spread_ann_bp": r.get("spread_ann_bp"),
            "ratio_ann_pct": ratio.get("ann_pct"),
            "ratio_max_drawdown_pct": ratio.get("max_drawdown_pct"),
            "from": r.get("from"), "to": r.get("to"), "bars": r.get("bars"),
        }
    return out


def _wide_delta_rows(base_label, faces, modes, starts, costs, eras):
    """(E77) one row per (window|era, cost, column) with every screen beside it."""
    rows = []
    u = faces[base_label]

    def emit(face, column, unscreened, pick):
        row = {"face": face, "column": column, "unscreened": unscreened}
        for m in modes:
            v = pick(faces[m])
            row[m] = v
            row["delta_" + m] = (round(v - unscreened, 4)
                                 if isinstance(v, (int, float))
                                 and isinstance(unscreened, (int, float)) else None)
        rows.append(row)

    for start in starts:
        for cost in costs:
            key = "x%g" % cost
            uw = ((u["windows"].get(start) or {}).get(key) or {})
            for col in WIDE_COLUMNS:
                emit("wide@%s@%s" % (start, key), col, uw.get(col),
                     lambda f, s=start, k=key, c=col:
                     ((f["windows"].get(s) or {}).get(k) or {}).get(c))
    for cost in costs:
        key = "x%g" % cost
        ue = u["eras"].get(key) or {}
        for era in eras:
            ename = era[0]
            urow = ue.get(ename) or {}
            for col in WIDE_ERA_COLUMNS:
                emit("era:%s@%s" % (ename, key), col, urow.get(col),
                     lambda f, k=key, e=ename, c=col:
                     ((f["eras"].get(k) or {}).get(e) or {}).get(c))
    return rows


def run_screenwide(outdir, pick_n=9999, exclude=("sh511",),
                   modes=("neutralise_int", "neutralise", "drop"),
                   starts=("2020-01-01", "2018-01-01"), costs=(1.0, 3.0),
                   eras=ERAS):
    """E77: replay the wide-book headline from the repaired universe.

    E76 showed the era *spread* moves when the split screen is on. This leg asks
    the narrower question the pool asked: do the wide-book columns themselves
    (both start windows, both cost levels, per era) move, and does the
    correction survive costs. The unscreened column sits beside every screened
    one; no published face is rewritten.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    universes = {"unscreened": (raw, None)}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        universes[mode] = (repaired, mode)

    faces, n_runs = {}, 0
    for label, (univ_raw, _mode) in universes.items():
        windows = {}
        for start in starts:
            windows[start] = {}
            for cost in costs:
                face = e27.run(ns=(pick_n,), start=start, cost_mult=cost,
                               exclude=exclude, raw=univ_raw)
                n_runs += 1
                windows[start]["x%g" % cost] = _wide_headline(face, pick_n)
        era_faces = {}
        for cost in costs:
            lad, wide, ratio = _era_curves(univ_raw, cal_full, pick_n, cost_mult=cost)
            n_runs += 2
            era_faces["x%g" % cost] = _wide_era_headline(
                _era_rows(lad, wide, ratio, eras))
        faces[label] = {"windows": windows, "eras": era_faces,
                        "universe_size": len(univ_raw)}

    delta = _wide_delta_rows("unscreened", faces, modes, starts, costs, eras)

    def _biggest(pred):
        rows = [r for r in delta if pred(r)]
        if not rows:
            return None
        best = max(rows, key=lambda r: max(
            abs(r["delta_" + m]) for m in modes if r.get("delta_" + m) is not None))
        out = {"face": best["face"], "column": best["column"],
               "unscreened": best["unscreened"]}
        for m in modes:
            out[m] = best.get(m)
            out["delta_" + m] = best.get("delta_" + m)
        return out

    newest = eras[-1][0]
    era_cells = {}
    for label in faces:
        era_cells[label] = {}
        for cost in costs:
            key = "x%g" % cost
            row = (faces[label]["eras"].get(key) or {}).get(newest) or {}
            era_cells[label][key] = {"wide_ann_pct": row.get("wide_ann_pct"),
                                     "spread_ann_bp": row.get("spread_ann_bp")}

    flipped = sorted(
        era[0] for era in eras
        if any((((faces["unscreened"]["eras"].get("x%g" % cost) or {})
                 .get(era[0]) or {}).get("spread_ann_bp") or 0)
               * (((faces[m]["eras"].get("x%g" % cost) or {})
                   .get(era[0]) or {}).get("spread_ann_bp") or 0) < 0
               for m in modes for cost in costs))

    # does the correction survive the cost multiplier?
    cost_shift = []
    for label in ["unscreened"] + list(modes):
        for start in starts:
            a = (faces[label]["windows"][start].get("x1") or {}).get("wide_ann_pct")
            b = (faces[label]["windows"][start].get("x3") or {}).get("wide_ann_pct")
            cost_shift.append({
                "mode": label, "start": start,
                "x1_ann_pct": a, "x3_ann_pct": b,
                "shift_pct": (round(b - a, 3)
                              if isinstance(a, (int, float))
                              and isinstance(b, (int, float)) else None)})

    return {
        "study": "e77_screened_wide_era",
        "evidence_cutoff": cutoff,
        "spec": {
            "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "starts": list(starts), "costs": list(costs),
            "cost_bp_per_side": base.COST_BP_SIDE,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "loader": "scripts/panel_screen.py via e27.run(raw=...) (opt-in)",
            "books": "wide_topN = e27 universe book; ladder5 = the five ladder "
                     "members; the spread/ratio read comes from _era_rows",
            "runs": n_runs,
        },
        "screen_reports": reports,
        "faces": faces,
        "delta": delta,
        "cost_shift": cost_shift,
        "answers": {
            "wide_worst_correction": _biggest(lambda r: r["face"].startswith("wide@")),
            "era_worst_correction": _biggest(
                lambda r: r["face"].startswith("era:") and r["column"] == "spread_ann_bp"),
            "newest_era_cells": era_cells,
            "eras_whose_spread_changes_sign": flipped,
            "delta_cells": len(delta),
            "non_zero_delta_cells": len([r for r in delta
                                         if any(r.get("delta_" + m) not in (None, 0)
                                                for m in modes)]),
            "max_abs_delta_by_column": {
                col: max([abs(r.get("delta_" + m) or 0) for r in delta
                          if r["column"] == col for m in modes] or [0])
                for col in sorted(set(WIDE_COLUMNS) | set(WIDE_ERA_COLUMNS))},
        },
        "honest": [
            "the screen repairs arithmetic impossibility only; a flagged ETF print "
            "may be genuine, so 'neutralise' is a sensitivity face, not a truth",
            "drop mode changes the universe size, so its delta mixes the correction "
            "with a composition change; the two neutralise columns isolate it",
            "gapped prints are never repaired, and both ladder5 corporate actions sit "
            "behind a suspension bar, so the ladder column is expected to be flat",
            "the wide book is a trailing-turnover top-N equal-weight book, not a "
            "cap-weighted index; its ann% is a book return, not a market return",
            "cost x3 is a stress face on the frozen 13.041bp/side, not a fee forecast",
            "descriptive census only: no gate, no verdict, no prereg, no trial booking",
        ],
    }


# --------------------------------------------------- E78 screened weekly residual

WEEK_COLUMNS = ("full_window_gap_bp", "turnover_per_year", "cost_per_year_bp")


def _week_delta_rows(base_label, faces, modes, costs, labels=("week", "week_near_me"),
                     eras=ERAS):
    """(E78) unscreened-vs-screened weekly residual, one row per cell.

    Pure so the residual arithmetic is testable without a burn: the weekly
    calendar and its month-end-near twin are the two books whose gap the
    six-round chain has been pricing, and every screened cell keeps the
    unscreened twin it is a delta against.
    """
    rows = []
    u = faces[base_label]["calendar_rows"]

    def emit(face, column, unscreened, pick):
        row = {"face": face, "column": column, "unscreened": unscreened}
        for m in modes:
            v = pick(faces[m])
            row[m] = v
            row["delta_" + m] = (round(v - unscreened, 4)
                                 if isinstance(v, (int, float))
                                 and isinstance(unscreened, (int, float)) else None)
        rows.append(row)

    for cost in costs:
        tag = "x%g" % cost
        for lab in labels:
            urow = (u.get(tag) or {}).get(lab) or {}
            for col in WEEK_COLUMNS:
                emit("%s@%s" % (lab, tag), col, urow.get(col),
                     lambda f, t=tag, l=lab, c=col:
                     ((f["calendar_rows"].get(t) or {}).get(l) or {}).get(c))
            for era in eras:
                ename = era[0]
                uv = (urow.get("eras") or {}).get(ename)
                emit("era:%s@%s@%s" % (lab, ename, tag), "gap_bp", uv,
                     lambda f, t=tag, l=lab, e=ename:
                     (((f["calendar_rows"].get(t) or {}).get(l) or {})
                      .get("eras") or {}).get(e))
    return rows


def run_screenweek(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                   modes=("neutralise_int", "neutralise", "drop"),
                   costs=(1.0, 3.0), eras=ERAS, labels=("week", "week_near_me")):
    """E78: does the weekly-vs-monthly residual survive the split screen?

    E77 showed the split screen moves the wide book exactly in 2021_2023 and
    2024_now -- the two eras where the weekly-vs-monthly chain (E63/E69/E70)
    priced its residual. That residual is re-derived here from the repaired
    universe at both cost levels, through the same run_midsweep wiring, so the
    only moving part is the input book. Every screened cell keeps its
    unscreened twin and no published WEEKCLASH face is rewritten.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    universes = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        universes[mode] = repaired

    tags = ["x%g" % c for c in costs]
    faces, n_runs = {}, 0
    for label, univ in universes.items():
        clash = run_midsweep(outdir, start=start, pick_n=pick_n, exclude=exclude,
                             days=(), costs=costs, lags=(), weekly=True, raw=univ)
        n_runs += 1
        rows_by_cost = {tag: _weekly_cal_rows(clash, tag, labels) for tag in tags}
        me_turn = {}
        for tag in tags:
            arms = ((clash.get("books") or {}).get("me") or {}).get("arms") or {}
            me_turn[tag] = (arms.get(tag) or {}).get("turnover_per_year")
        faces[label] = {"calendar_rows": rows_by_cost,
                        "me_turnover_by_cost": me_turn,
                        "universe_size": len(univ),
                        "week_overlap": clash["answers"].get("week_overlap")}

    delta = _week_delta_rows("unscreened", faces, modes, costs, labels, eras)

    def _biggest(pred):
        rows = [r for r in delta if pred(r)
                and any(r.get("delta_" + m) is not None for m in modes)]
        if not rows:
            return None
        best = max(rows, key=lambda r: max(
            abs(r["delta_" + m]) for m in modes
            if r.get("delta_" + m) is not None))
        out = {"face": best["face"], "column": best["column"],
               "unscreened": best["unscreened"]}
        for m in modes:
            out[m] = best.get(m)
            out["delta_" + m] = best.get("delta_" + m)
        return out

    # the residual itself, at every cost level, per mode
    residual = {label: {tag: ((faces[label]["calendar_rows"].get(tag) or {})
                              .get("week_near_me") or {}).get("full_window_gap_bp")
                        for tag in tags} for label in faces}
    full_gap = {label: {tag: ((faces[label]["calendar_rows"].get(tag) or {})
                              .get("week") or {}).get("full_window_gap_bp")
                        for tag in tags} for label in faces}

    surv = {}
    for tag in tags:
        base_bp = residual["unscreened"].get(tag)
        surv[tag] = {}
        for m in modes:
            v = residual[m].get(tag)
            surv[tag][m] = {
                "unscreened_bp": base_bp, "screened_bp": v,
                "delta_bp": (round(v - base_bp, 2)
                             if isinstance(v, (int, float))
                             and isinstance(base_bp, (int, float)) else None),
                "surviving_share_pct": (round(100.0 * v / base_bp, 1)
                                        if isinstance(v, (int, float)) and base_bp
                                        else None)}

    newest = eras[-1][0]
    era_residual = {tag: {label: ((faces[label]["calendar_rows"].get(tag) or {})
                                  .get("week_near_me") or {}).get("eras", {})
                             .get(newest)
                          for label in faces} for tag in tags}

    flipped = sorted(
        era[0] for era in eras
        if any(((((faces["unscreened"]["calendar_rows"].get(tag) or {})
                  .get("week_near_me") or {}).get("eras") or {}).get(era[0]) or 0)
               * ((((faces[m]["calendar_rows"].get(tag) or {})
                    .get("week_near_me") or {}).get("eras") or {}).get(era[0]) or 0) < 0
               for m in modes for tag in tags))

    return {
        "study": "e78_screened_weekclash_residual",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "costs": list(costs), "labels": list(labels),
            "cost_bp_per_side": base.COST_BP_SIDE,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "loader": "scripts/panel_screen.py via run_midsweep(raw=...) (opt-in)",
            "books": "week = full ISO weekly grid; week_near_me = the same grid cut "
                     "to one decision per month at the weekly session nearest the "
                     "boundary; the gap is each book against month-end",
            "runs": n_runs,
        },
        "screen_reports": reports,
        "faces": faces,
        "delta": delta,
        "answers": {
            "residual_bp_by_cost": residual,
            "full_week_gap_bp_by_cost": full_gap,
            "residual_survival": surv,
            "newest_era_residual_bp": era_residual,
            "worst_correction": _biggest(lambda r: True),
            "residual_worst_correction": _biggest(
                lambda r: r["face"].startswith("week_near_me@")),
            "eras_whose_residual_changes_sign": flipped,
            "delta_cells": len(delta),
            "non_zero_delta_cells": len([r for r in delta
                                         if any(r.get("delta_" + m) not in (None, 0)
                                                for m in modes)]),
        },
        "honest": [
            "the screen repairs arithmetic impossibility only; a flagged ETF print "
            "may be genuine, so 'neutralise' is a sensitivity face, not a truth",
            "drop mode changes the universe size, so its delta mixes the correction "
            "with a composition change; the two neutralise columns isolate it",
            "week_near_me holds the trading frequency fixed against month-end, so it "
            "is the book that prices the DATE; the raw weekly gap mixes calendar "
            "with a ~4.3x higher rebalance rate and is published for context only",
            "turnover columns are the control that the screen moves the return path "
            "and not the traded book",
            "cost x3 is a stress face on the frozen 13.041bp/side, not a fee forecast",
            "gapped prints are never repaired, so a residual carried by a "
            "behind-suspension print would read flat here rather than corrected",
            "descriptive census only: no gate, no verdict, no prereg, no trial booking",
        ],
    }


# ------------------------------------------------------ E80 screened mid-month


def _dig(face, *path):
    """Walk a nested dict, returning None the moment the path breaks."""
    cur = face
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def _mid_delta_rows(base_label, faces, modes, eras, costs=(0.0, 1.0, 3.0),
                    mid_label="mid15"):
    """(E80) unscreened-vs-screened mid-month churn rows, one row per cell.

    Pure so the delta arithmetic is testable without a burn: every screened cell
    keeps the unscreened twin it is a delta against, at the same book, era and
    cost column. ``mid_label`` is the book key the face actually publishes
    (``mid15``), not a nickname -- the arms rows live under it.
    """
    rows = []
    u = faces.get(base_label) or {}
    era_names = [e[0] for e in eras]
    books = (("me", "me"), (mid_label, "mid"))

    def emit(face, column, unscreened, pick):
        row = {"face": face, "column": column, "unscreened": unscreened}
        for m in modes:
            v = pick(faces.get(m) or {})
            row[m] = v
            row["delta_" + m] = (round(v - unscreened, 4)
                                 if isinstance(v, (int, float))
                                 and isinstance(unscreened, (int, float)) else None)
        rows.append(row)

    for tag in ["x%g" % c for c in costs]:
        for key, lab in books:
            for col in ("turnover_per_year", "full_window_ann_pct"):
                emit("%s@%s" % (lab, tag), col,
                     _dig(u, "books", key, "arms", tag, col),
                     lambda f, t=tag, k=key, c=col:
                     _dig(f, "books", k, "arms", t, c))
            for era in era_names:
                emit("era:%s@%s@%s" % (lab, era, tag), "ann_return_pct",
                     _dig(u, "books", key, "arms", tag, "eras", era, "ann_return_pct"),
                     lambda f, t=tag, k=key, e=era:
                     _dig(f, "books", k, "arms", t, "eras", e, "ann_return_pct"))
        for era in era_names:
            key = "gap_%s_bp" % tag
            emit("gap:%s@%s" % (era, tag), "gap_bp", _dig(u, "eras", era, key),
                 lambda f, e=era, c=key: _dig(f, "eras", e, c))

    for era in era_names:
        for lab in ("me", "mid"):
            emit("churn:%s@%s" % (lab, era), "churn_alpha_bp_mean",
                 _dig(u, "eras", era, lab, "churn_alpha_bp_mean"),
                 lambda f, e=era, l=lab:
                 _dig(f, "eras", e, l, "churn_alpha_bp_mean"))
            emit("negchurn:%s@%s" % (lab, era), "negative_churn_share_pct",
                 _dig(u, "eras", era, lab, "negative_churn_share_pct"),
                 lambda f, e=era, l=lab:
                 _dig(f, "eras", e, l, "negative_churn_share_pct"))
        emit("churngap:%s" % era, "churn_alpha_gap_bp",
             _dig(u, "eras", era, "churn_alpha_gap_bp"),
             lambda f, e=era: _dig(f, "eras", e, "churn_alpha_gap_bp"))
    return rows


def _mid_flip_eras(faces, modes, eras, pick):
    """Eras whose unscreened value and a screened value straddle zero."""
    out = []
    u = faces.get("unscreened") or {}
    for era in [e[0] for e in eras]:
        uv = pick(u, era)
        if not isinstance(uv, (int, float)) or uv == 0:
            continue
        for m in modes:
            v = pick(faces.get(m) or {}, era)
            if isinstance(v, (int, float)) and uv * v < 0:
                out.append(era)
                break
    return sorted(out)


def run_midscreen(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                  modes=("neutralise_int", "neutralise", "drop"), mid_day=15,
                  costs=(0.0, 1.0, 3.0), eras=ERAS):
    """E80: does the mid-month membership claim survive the split screen?

    E44 put the 2024_now mid-month gap (-87bp/yr) on membership -- the book turns
    over the same amount but swaps into worse names -- and E77/E78 showed the
    split screen moves exactly that era. The churn rows are re-derived here from
    the repaired universe, with the unscreened column kept beside every screened
    one, so the membership claim is measured rather than assumed. No published
    MIDMONTH face is rewritten.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    universes = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        universes[mode] = repaired

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(outdir, start=start, pick_n=pick_n,
                                    exclude=exclude, mid_day=mid_day,
                                    costs=costs, raw=univ)

    delta = _mid_delta_rows("unscreened", faces, modes, eras, costs,
                            mid_label="mid%d" % mid_day)

    def _biggest(pred):
        rows = [r for r in delta if pred(r)
                and any(r.get("delta_" + m) is not None for m in modes)]
        if not rows:
            return None
        best = max(rows, key=lambda r: max(
            abs(r["delta_" + m]) for m in modes
            if r.get("delta_" + m) is not None))
        out = {"face": best["face"], "column": best["column"],
               "unscreened": best["unscreened"]}
        for m in modes:
            out[m] = best.get(m)
            out["delta_" + m] = best.get("delta_" + m)
        return out

    newest = eras[-1][0]
    gap_by_label = {label: _dig(faces[label], "answers", "newest_era_gap_x1_bp")
                    for label in faces}
    churn_by_label = {label: _dig(faces[label], "eras", newest, "churn_alpha_gap_bp")
                      for label in faces}
    negchurn_by_label = {
        label: {"me": _dig(faces[label], "eras", newest, "me", "negative_churn_share_pct"),
                "mid": _dig(faces[label], "eras", newest, "mid", "negative_churn_share_pct")}
        for label in faces}
    turn_by_label = {label: {"me": _dig(faces[label], "books", "me", "arms", "x1",
                                             "turnover_per_year"),
                             "mid": _dig(faces[label], "books", "mid%d" % mid_day,
                                         "arms", "x1", "turnover_per_year")}
                     for label in faces}

    base_gap = gap_by_label.get("unscreened")
    surv = {}
    for m in modes:
        v = gap_by_label.get(m)
        surv[m] = {
            "unscreened_bp": base_gap, "screened_bp": v,
            "delta_bp": (round(v - base_gap, 1)
                         if isinstance(v, (int, float))
                         and isinstance(base_gap, (int, float)) else None),
            "surviving_share_pct": (round(100.0 * v / base_gap, 1)
                                    if isinstance(v, (int, float)) and base_gap else None)}

    return {
        "study": "e80_screened_midmonth_churn",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "costs": list(costs), "mid_month_day": mid_day,
            "cost_bp_per_side": base.COST_BP_SIDE,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "loader": "scripts/panel_screen.py via run_midmonth(raw=...) (opt-in)",
            "books": "me = month-end decisions; mid%d = first session on/after the "
                     "%dth of each month; both on one calendar, one rank cache" % (mid_day, mid_day),
            "runs": len(universes),
        },
        "screen_reports": reports,
        "eras": {label: faces[label].get("eras") for label in faces},
        "answers": {label: faces[label].get("answers") for label in faces},
        "delta": delta,
        "results": {
            "newest_era_gap_x1_bp": gap_by_label,
            "gap_survival": surv,
            "newest_era_churn_alpha_gap_bp": churn_by_label,
            "newest_era_negative_churn_share_pct": negchurn_by_label,
            "turnover_per_year_control": turn_by_label,
            "eras_whose_gap_changes_sign": _mid_flip_eras(
                faces, modes, eras, lambda f, e: _dig(f, "eras", e, "gap_x1_bp")),
            "eras_whose_churn_gap_changes_sign": _mid_flip_eras(
                faces, modes, eras, lambda f, e: _dig(f, "eras", e, "churn_alpha_gap_bp")),
            "worst_correction": _biggest(lambda r: True),
            "delta_cells": len(delta),
            "non_zero_delta_cells": len([r for r in delta
                                         if any(r.get("delta_" + m) not in (None, 0)
                                                for m in modes)]),
        },
        "honest": [
            "the screen repairs arithmetic impossibility only; a flagged ETF print may be "
            "genuine, so 'neutralise' is a sensitivity face, not a corrected truth",
            "drop mode changes the universe size, so its delta mixes the correction with a "
            "composition change and its eligibility set differs from the twin",
            "the churn sleeve is an equal-weight mean over the swapped names, not a "
            "portfolio return: it prices whether the names taken in beat the names given "
            "up inside that window",
            "the turnover column is the control that the screen moves the return path and "
            "not the traded book; a screened turnover that differs from its twin means the "
            "screen changed eligibility, not the calendar",
            "gapped prints are never repaired, so a churn carried by a behind-suspension "
            "print reads flat here rather than corrected",
            "descriptive census only: no gate, no verdict, no prereg, no trial booking",
        ],
    }


# ------------------------------- leg: who carries the churn-gap amplification (E82)


def _event_dates(universe, cal):
    """name -> sorted print-event dates, scanned on consecutive priced closes."""
    import panel_screen

    out = {}
    for s, pair in universe.items():
        closes = pair[0] if isinstance(pair, tuple) else pair
        ev = panel_screen.split_events(closes, cal=cal)
        if ev:
            out[s] = sorted({e["date"] for e in ev})
    return out


def _transition_hits(d0, d1, swapped, event_dates):
    """Swapped names whose print event sits inside (d0, d1] -- the priced window.

    Exclusive start, inclusive end: the sleeve prices ``date -> next``, so an
    event on the decision day itself belongs to the previous window.
    """
    hits = []
    for s in swapped:
        for d in event_dates.get(s, ()):
            if d0 < d <= d1:
                hits.append({"name": s, "date": d})
                break
    return hits


def _churn_join(base_rows, mode_rows, event_dates, eras=ERAS):
    """Per-transition delta (mode minus baseline) tagged hit / clean.

    hit  -- at least one swapped name carried a print event inside the window
    clean-- no swapped name did, so a repair cannot be the cause of the move
    """
    m_by = {r["date"]: r for r in mode_rows}
    out = []
    for b in base_rows:
        m = m_by.get(b["date"])
        if m is None:
            continue
        swapped = sorted(set(b.get("entrant_names") or ())
                         | set(b.get("exit_names") or ()))
        hits = _transition_hits(b["date"], b["next"], swapped, event_dates)
        a0, a1 = b.get("churn_alpha_bp"), m.get("churn_alpha_bp")
        out.append({
            "date": b["date"], "next": b["next"], "era": b.get("era"),
            "hit": bool(hits), "hit_names": [h["name"] for h in hits],
            "alpha_base_bp": a0, "alpha_mode_bp": a1,
            "delta_bp": (round(a1 - a0, 1)
                         if isinstance(a0, (int, float))
                         and isinstance(a1, (int, float)) else None),
        })

    agg = {}
    for name, _lo, _hi in eras:
        sub = [r for r in out if r["era"] == name and r["delta_bp"] is not None]
        if not sub:
            continue
        hit = [r["delta_bp"] for r in sub if r["hit"]]
        clean = [r["delta_bp"] for r in sub if not r["hit"]]
        total = sum(r["delta_bp"] for r in sub)
        agg[name] = {
            "transitions": len(sub),
            "hit_transitions": len(hit),
            "hit_share_pct": round(100.0 * len(hit) / len(sub), 1),
            "delta_mean_all_bp": round(total / len(sub), 1),
            "delta_mean_hit_bp": round(sum(hit) / len(hit), 1) if hit else None,
            "delta_mean_clean_bp": round(sum(clean) / len(clean), 1) if clean else None,
            "delta_sum_hit_bp": round(sum(hit), 1) if hit else 0.0,
            "delta_sum_clean_bp": round(sum(clean), 1) if clean else 0.0,
            "hit_share_of_delta_pct": (round(100.0 * sum(hit) / total, 1)
                                       if hit and total else None),
        }
    return out, agg


def _worst_transitions(rows, n=8):
    """The n largest |delta| transitions, kept with their hit tag and window."""
    live = [r for r in rows if r["delta_bp"] is not None]
    live.sort(key=lambda r: -abs(r["delta_bp"]))
    return live[:n]


def run_churngap(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                 modes=("neutralise_int", "neutralise", "drop"), mid_day=15,
                 eras=ERAS):
    """E82: break the churn-gap amplification down per transition.

    E80 left an asymmetry -- the newest-era churn alpha gap widens under
    neutralise (-211 -> -457bp per swap) but collapses under drop (-24bp). If
    the amplification lives on the transitions whose swapped names hold a print
    event, it is a repair effect; if it is spread over clean transitions, it is
    a composition effect of the repaired universe. Both books (month-end and
    mid-month) are joined transition-by-transition against the raw event list;
    no published face is rewritten.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    event_dates = _event_dates(raw, cal_full)

    universes = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        universes[mode] = repaired

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(outdir, start=start, pick_n=pick_n,
                                    exclude=exclude, mid_day=mid_day,
                                    raw=univ, full_churn=True)

    book_labels = ["me", "mid%d" % mid_day]
    joins, summary = {}, {}
    for book in book_labels:
        base_rows = faces["unscreened"]["books"][book]["churn_rows"]
        joins[book] = {}
        summary[book] = {}
        for mode in modes:
            mode_rows = faces[mode]["books"][book]["churn_rows"]
            rows, agg = _churn_join(base_rows, mode_rows, event_dates, eras)
            joins[book][mode] = {"eras": agg,
                                 "worst_transitions": _worst_transitions(rows),
                                 "transitions": len(rows)}
            newest = agg.get(eras[-1][0], {})
            summary[book][mode] = {
                "transitions_joined": len(rows),
                "transitions_with_a_repair": len([r for r in rows if r["hit"]]),
                "newest_era_delta_mean_all_bp": newest.get("delta_mean_all_bp"),
                "newest_era_delta_mean_hit_bp": newest.get("delta_mean_hit_bp"),
                "newest_era_delta_mean_clean_bp": newest.get("delta_mean_clean_bp"),
                "newest_era_hit_share_of_delta_pct": newest.get("hit_share_of_delta_pct"),
            }

    # the amplification itself, re-read on the joined transitions: mode minus
    # baseline for the same book, so the two columns cannot be two different burns
    return {
        "study": "e82_churn_gap_amplification",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "mid_month_day": mid_day,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": book_labels,
            "joins": "churn rows from run_midmonth(full_churn=True) joined by "
                     "decision date against panel_screen.split_events on the raw prints",
            "hit_window": "event date d counts when decision date < d <= next decision date",
            "cost_mult_list": [0.0, 1.0, 3.0],
            "why_this_cost_set": "the churn sleeve is a name-level mean, not a "
                                 "portfolio return, so no cost multiplier can move it; the "
                                 "standard triple is kept so the sleeve lands beside the "
                                 "turnover control of the same burn",
            "universe_members": len(raw),
            "events_indexed": len(event_dates),
            "runs": len(universes),
        },
        "screen_reports": reports,
        "events_by_name": {k: v for k, v in sorted(event_dates.items())},
        "joins": joins,
        "results": summary,
        "honest": [
            "a hit transition says a print event sits inside the priced window; it does "
            "not say the book traded that name on that bar",
            "the churn sleeve is an equal-weight mean over the swapped names, so a single "
            "large print can move one transition's alpha by more than a clean year",
            "drop mode removes names entirely, so its delta mixes repair with composition "
            "and is not comparable cell-for-cell with the neutralise arms",
            "transitions are counted, not weighted: a period with more rebalances "
            "contributes more rows, and the era means are unweighted",
            "the event index comes from the raw prints, so a name that never traded a "
            "suspicious bar is clean by construction and cannot explain anything here",
            "descriptive census only: no gate, no verdict, no prereg, no trial booking",
        ],
    }


# -------------------------------------------------------------- E83 / E84

def _single_print_cell(rows, eras=ERAS, event_dates=None):
    """E83: one era cell re-read with its single most influential swap removed.

    Removing transition i from a cell of n alphas moves the mean to
    ``(n*m - a_i)/(n-1)``, so the biggest collapse is always the transition
    farthest from the mean. A cell that keeps less than half its magnitude
    without one transition is quoting one swap, not a period.
    """
    out = {}
    for name, _lo, _hi in eras:
        sub = [r for r in rows
               if r.get("era") == name
               and isinstance(r.get("churn_alpha_bp"), (int, float))]
        if not sub:
            continue
        vals = [r["churn_alpha_bp"] for r in sub]
        n = len(sub)
        tot = sum(vals)
        m = tot / n
        face = {"transitions": n, "mean_bp": round(m, 1),
                "median_bp": round(sorted(vals)[n // 2], 1),
                "single_swap_removable": n >= 2}
        if n >= 2:
            best = None
            for r, a in zip(sub, vals):
                new = (tot - a) / (n - 1)
                if best is None or abs(new) < abs(best["mean_without_bp"]):
                    best = {"removed_window": [r["date"], r["next"]],
                            "removed_alpha_bp": round(a, 1),
                            "removed_swapped": sorted(set(r.get("entrant_names") or ())
                                                      | set(r.get("exit_names") or ())),
                            "mean_without_bp": round(new, 1)}
            share = (abs(best["mean_without_bp"]) / abs(m)) if m else None
            best["magnitude_remaining_pct"] = (round(100.0 * share, 1)
                                               if share is not None else None)
            best["single_print"] = bool(share is not None and share < 0.5)
            best["sign_flip"] = bool(m * best["mean_without_bp"] < 0)
            if event_dates is not None:
                d0, d1 = best["removed_window"]
                best["removed_carries_a_print"] = bool(
                    _transition_hits(d0, d1, best["removed_swapped"], event_dates))
            face["most_influential_removal"] = best
        out[name] = face
    return out


def _single_print_gap(me_rows, mid_rows, eras=ERAS, event_dates=None):
    """E83: the me-vs-mid churn gap re-read with one transition removed.

    The two books rebalance on different dates (month-end vs mid-month), so
    there is no matched transition to drop -- the date sets are disjoint by
    construction. The gap is therefore perturbed the only way it can be: remove
    the single most influential transition from ONE side and leave the other
    intact. Both sides are tried and the larger collapse is reported together
    with the side it came from.
    """
    out = {}
    for name, _lo, _hi in eras:
        a_rows = [r for r in me_rows
                  if r.get("era") == name
                  and isinstance(r.get("churn_alpha_bp"), (int, float))]
        b_rows = [r for r in mid_rows
                  if r.get("era") == name
                  and isinstance(r.get("churn_alpha_bp"), (int, float))]
        if not a_rows or not b_rows:
            continue
        a_vals = [r["churn_alpha_bp"] for r in a_rows]
        b_vals = [r["churn_alpha_bp"] for r in b_rows]
        ma = sum(a_vals) / len(a_vals)
        mb = sum(b_vals) / len(b_vals)
        gap = mb - ma
        face = {"transitions_me": len(a_vals), "transitions_mid": len(b_vals),
                "gap_bp": round(gap, 1),
                "single_swap_removable": len(a_vals) >= 2 or len(b_vals) >= 2}
        best = None
        if len(a_vals) >= 2:
            for r, a in zip(a_rows, a_vals):
                new = mb - (sum(a_vals) - a) / (len(a_vals) - 1)
                cand = {"removed_side": "me", "removed_window": [r["date"], r["next"]],
                        "removed_alpha_bp": round(a, 1),
                        "removed_swapped": sorted(set(r.get("entrant_names") or ())
                                                  | set(r.get("exit_names") or ())),
                        "gap_without_bp": round(new, 1)}
                if best is None or abs(new) < abs(best["gap_without_bp"]):
                    best = cand
        if len(b_vals) >= 2:
            for r, b in zip(b_rows, b_vals):
                new = (sum(b_vals) - b) / (len(b_vals) - 1) - ma
                cand = {"removed_side": "mid", "removed_window": [r["date"], r["next"]],
                        "removed_alpha_bp": round(b, 1),
                        "removed_swapped": sorted(set(r.get("entrant_names") or ())
                                                  | set(r.get("exit_names") or ())),
                        "gap_without_bp": round(new, 1)}
                if abs(new) < abs(best["gap_without_bp"]):
                    best = cand
        if best is not None:
            share = (abs(best["gap_without_bp"]) / abs(gap)) if gap else None
            best["magnitude_remaining_pct"] = (round(100.0 * share, 1)
                                               if share is not None else None)
            best["single_print"] = bool(share is not None and share < 0.5)
            best["sign_flip"] = bool(gap * best["gap_without_bp"] < 0)
            if event_dates is not None:
                d0, d1 = best["removed_window"]
                best["removed_carries_a_print"] = bool(
                    _transition_hits(d0, d1, best["removed_swapped"], event_dates))
            face["most_influential_removal"] = best
        out[name] = face
    return out


def _mode_universe_diff(reports, modes=("neutralise_int", "neutralise")):
    """E84: which names one screen repairs and the other leaves alone."""
    touched = {}
    for mode in modes:
        touched[mode] = {r["name"]: r for r in reports[mode]["names"]
                         if r.get("action") != "kept-gapped-only"}
    small, big = touched[modes[0]], touched[modes[1]]
    extra = sorted(set(big) - set(small))
    return {
        "modes": list(modes),
        "names_touched": {m: len(touched[m]) for m in modes},
        "names_events": {m: reports[m]["events_neutralised"] for m in modes},
        "names_only_in_%s" % modes[1]: len(extra),
        "extra_names": extra,
        "extra_prints": [
            {"name": n, "events": big[n]["events"],
             "prints": [{"date": p.get("date"), "ret_pct": p.get("ret_pct"),
                         "ratio": p.get("ratio"),
                         "nearest_int": p.get("nearest_int"),
                         "resid_pct": p.get("resid_pct")}
                        for p in big[n].get("prints", ())]}
            for n in extra],
        "note": "the conservative arm repairs a strict subset: every name and every "
                "print it touches is also touched by the full arm",
    }


def _mode_row_diff(rows_a, rows_b):
    """E84: exact transition-by-transition comparison of two screen modes."""
    a = {r["date"]: r.get("churn_alpha_bp") for r in rows_a}
    b = {r["date"]: r.get("churn_alpha_bp") for r in rows_b}
    dates = sorted(set(a) & set(b))
    diffs = []
    for d in dates:
        x, y = a[d], b[d]
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            if x != y:
                diffs.append({"date": d, "a_bp": x, "b_bp": y})
        elif x is not y:
            diffs.append({"date": d, "a_bp": x, "b_bp": y})
    return {
        "transitions_compared": len(dates),
        "transitions_differing": len(diffs),
        "date_set_mismatch": len(set(a) ^ set(b)),
        "differing_rows": diffs[:20],
        "bit_identical": not diffs and not (set(a) ^ set(b)),
    }


def _extra_name_relevance(churn_row_sets, extra_names, event_dates):
    """E84: did any transition ever swap one of the names only the wider arm fixes?"""
    extra = set(extra_names)
    ever_swapped = set()
    windows_with_print = 0
    windows_with_swap = 0
    for rows in churn_row_sets:
        for r in rows:
            swapped = set(r.get("entrant_names") or ()) | set(r.get("exit_names") or ())
            if not swapped & extra:
                continue
            windows_with_swap += 1
            ever_swapped |= swapped & extra
            if _transition_hits(r["date"], r["next"], sorted(swapped & extra),
                                event_dates):
                windows_with_print += 1
    return {"extra_names": len(extra),
            "extra_names_ever_swapped": len(ever_swapped),
            "extra_names_ever_swapped_list": sorted(ever_swapped),
            "windows_swapping_an_extra_name": windows_with_swap,
            "windows_where_an_extra_name_carried_a_print": windows_with_print}


def run_singleprint(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                    modes=("neutralise_int", "neutralise", "drop"), mid_day=15,
                    eras=ERAS):
    """E83 + E84: is a published churn cell one swap wide, and is the second arm wasted?

    E82 found the newest-era amplification of the mid-month churn gap is a
    single transition (mid15 2024-01-15 sz159925). E83 turns that from an
    anecdote into a screen over every published churn cell: each book, each
    screen mode, each era, re-read with its single most influential transition
    removed, flagged when less than half the magnitude survives. E84 audits
    ``neutralise_int`` against ``neutralise`` -- the two arms returned identical
    churn rows in E80/E82, and a silently duplicate arm is the shape of an
    accounting error. Both questions are answered from ONE burn, because they
    need the same four universes; the universe-level half of E84 is hermetic and
    costs nothing.

    Drop mode is flagged separately everywhere: it removes names, so a dropped
    name changes the book's composition rather than repairing a bar, and its
    cells are not comparable to the neutralise arms.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    event_dates = _event_dates(raw, cal_full)

    universes = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode,
                                                       cal=cal_full)
        reports[mode] = report
        universes[mode] = repaired

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(outdir, start=start, pick_n=pick_n,
                                    exclude=exclude, mid_day=mid_day,
                                    raw=univ, full_churn=True)

    book_labels = ["me", "mid%d" % mid_day]
    cells, gaps = {}, {}
    for book in book_labels:
        cells[book] = {}
        for label in universes:
            cells[book][label] = _single_print_cell(
                faces[label]["books"][book]["churn_rows"], eras, event_dates)
    for label in universes:
        gaps[label] = _single_print_gap(
            faces[label]["books"]["me"]["churn_rows"],
            faces[label]["books"]["mid%d" % mid_day]["churn_rows"], eras,
            event_dates)

    n_cells = sum(len(era_map) for book in cells.values()
                  for era_map in book.values())
    n_gaps = sum(len(v) for v in gaps.values())
    flagged = []
    for book in book_labels:
        for label in universes:
            for era, face in cells[book][label].items():
                rm = face.get("most_influential_removal")
                if rm and rm.get("single_print"):
                    flagged.append({
                        "face": "churn_alpha_bp_mean", "book": book,
                        "universe": label, "era": era,
                        "mean_bp": face["mean_bp"],
                        "without_one_swap_bp": rm["mean_without_bp"],
                        "magnitude_remaining_pct": rm["magnitude_remaining_pct"],
                        "sign_flip": rm["sign_flip"],
                        "removed_window": rm["removed_window"],
                        "removed_carries_a_print": rm.get("removed_carries_a_print"),
                    })
    for label in universes:
        for era, face in gaps[label].items():
            rm = face.get("most_influential_removal")
            if rm and rm.get("single_print"):
                flagged.append({
                    "face": "churn_alpha_gap_bp", "book": "mid%d-me" % mid_day,
                    "universe": label, "era": era,
                    "mean_bp": face["gap_bp"],
                    "without_one_swap_bp": rm["gap_without_bp"],
                    "magnitude_remaining_pct": rm["magnitude_remaining_pct"],
                    "sign_flip": rm["sign_flip"],
                    "removed_side": rm.get("removed_side"),
                    "removed_window": rm["removed_window"],
                    "removed_carries_a_print": rm.get("removed_carries_a_print"),
                })

    # E84: the two neutralise arms, universe half (exact) and cell half (exact)
    universe_diff = _mode_universe_diff(reports)
    row_diffs = {book: _mode_row_diff(
        faces["neutralise_int"]["books"][book]["churn_rows"],
        faces["neutralise"]["books"][book]["churn_rows"]) for book in book_labels}
    all_rows = [faces[label]["books"][b]["churn_rows"]
                for label in universes for b in book_labels]
    relevance = _extra_name_relevance(all_rows,
                                      universe_diff["extra_names"], event_dates)
    era_cell_diffs = {}
    for book in book_labels:
        for era in cells[book]["neutralise_int"]:
            a = cells[book]["neutralise_int"][era].get("mean_bp")
            b = cells[book]["neutralise"].get(era, {}).get("mean_bp")
            if a != b:
                era_cell_diffs["%s:%s" % (book, era)] = {"int_bp": a, "all_bp": b}

    identical = all(d["bit_identical"] for d in row_diffs.values())
    modeeq = {
        "study": "e84_screen_mode_equivalence",
        "evidence_cutoff": cutoff,
        "question": "neutralise_int and neutralise produced identical churn cells in "
                    "E80/E82 -- is the second arm a duplicate burn?",
        "universe_half": universe_diff,
        "churn_row_half": row_diffs,
        "era_cell_diffs": era_cell_diffs,
        "relevance_to_this_book": relevance,
        "verdict": ("identical_on_this_face" if identical else
                    "differs_somewhere"),
        "reading": [
            "the conservative arm touches a strict subset of the names the full arm "
            "repairs, so the universes are NOT the same object",
            "the churn cells are identical here because a repaired bar can only move a "
            "cell through a name the book actually swapped inside that window",
            "so the right statement is 'duplicate for THIS consumer at THIS cutoff', "
            "not 'the modes are the same screen' -- any face that prices per-name "
            "returns over the whole universe (book returns, breadth) must still run the "
            "full arm",
        ],
        "honest": [
            "a zero row difference can also mean both arms failed to repair anything; "
            "the touched-name counts above are the control against that",
            "drop mode is not part of this comparison: it removes names and changes "
            "composition, so it can never be a duplicate of a bar-repair arm",
        ],
    }

    bond = {
        "study": "e83_single_print_screen",
        "evidence_cutoff": cutoff,
        "spec": {"start": start, "pick_n": pick_n,
                 "exclude_prefixes": list(exclude), "modes": list(modes),
                 "mid_month_day": mid_day,
                 "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
                 "books": book_labels,
                 "screen": "each era cell of every book/universe pair, re-read with its "
                           "single most influential transition removed "
                           "(mean_without = (n*m - a_i)/(n-1), pick the smallest "
                           "|mean_without|)",
                 "flag_rule": "single_print when less than 50% of the cell's magnitude "
                              "survives the removal of one transition",
                 "universe_members": len(raw),
                 "events_indexed": len(event_dates),
                 "runs": len(universes)},
        "screen_reports": reports,
        "cells": cells,
        "gaps": gaps,
        "flagged": flagged,
        "flagged_count": len(flagged),
        "cells_examined": n_cells + n_gaps,
        "results": {
            "cells_examined": n_cells + n_gaps,
            "cell_breakdown": {"book_era_cells": n_cells, "gap_era_cells": n_gaps},
            "flagged": len(flagged),
            "flagged_unscreened": len([f for f in flagged
                                       if f["universe"] == "unscreened"]),
            "flagged_neutralise": len([f for f in flagged
                                       if f["universe"].startswith("neutralise")]),
            "flagged_drop": len([f for f in flagged if f["universe"] == "drop"]),
            "flagged_with_a_print": len([f for f in flagged
                                         if f["removed_carries_a_print"]]),
        },
        "mode_equivalence_ref": "MODEEQ-%s.json" % cutoff.replace("-", ""),
        "honest": [
            "the screen removes the single most influential transition; it does not "
            "test whether a second removal matters too, so 'not single print' only "
            "means the cell survives one swap",
            "an era cell with two transitions cannot survive any removal by "
            "arithmetic -- its magnitude_remaining_pct is 0 by construction, so read "
            "the transitions count before the flag",
            "removal is unweighted: transition alphas are an equal-weight mean over "
            "swapped names, so a period with few transitions can be dominated by one "
            "wide window",
            "drop mode is flagged separately and cannot be compared to the neutralise "
            "arms cell-for-cell",
            "descriptive census only: no gate, no verdict, no prereg, no trial booking",
        ],
    }
    return bond, modeeq


def _median_sorted(s):
    """Median of an already-sorted list (mean of the two middles when even)."""
    n = len(s)
    if not n:
        return None
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return 0.5 * (s[mid - 1] + s[mid])


def _robust_stats(vals, trim_pct=10.0):
    """Mean, median and symmetric trimmed mean of one cell's own values.

    Every churn cell in E80/E82/E83 is a MEAN over per-transition numbers, and
    those numbers are heavy-tailed by construction (one swap can own a window).
    A mean that survives as a median is a statement about the typical
    transition; a mean that collapses is a statement about a few.
    """
    clean = [float(v) for v in vals if isinstance(v, (int, float))]
    n = len(clean)
    if not n:
        return {"n": 0, "mean_bp": None, "median_bp": None, "trim10_bp": None,
                "trim_dropped": 0, "median_keep_pct_of_mean": None,
                "trim10_keep_pct_of_mean": None}
    s = sorted(clean)
    k = int(n * trim_pct / 100.0)
    core = s[k:n - k] if n - 2 * k > 0 else s
    mean = sum(clean) / n
    med = _median_sorted(s)
    trim = sum(core) / len(core)

    def keep(x):
        if mean == 0:
            return None
        return round(100.0 * x / mean, 1)

    return {"n": n, "mean_bp": round(mean, 1), "median_bp": round(med, 1),
            "trim10_bp": round(trim, 1),
            "trim_dropped": (2 * k) if core is not s else 0,
            "median_keep_pct_of_mean": keep(med),
            "trim10_keep_pct_of_mean": keep(trim)}


def _concentration(vals, k=3):
    """How much of a cell's signed total the k largest |values| carry."""
    clean = [float(v) for v in vals if isinstance(v, (int, float))]
    if not clean:
        return None
    order = sorted(range(len(clean)), key=lambda i: -abs(clean[i]))[:k]
    top = sum(clean[i] for i in order)
    tot = sum(clean)
    return {"k": len(order), "top_sum_bp": round(top, 1),
            "total_sum_bp": round(tot, 1),
            "top_share_of_total_pct": (round(100.0 * top / tot, 1)
                                       if tot else None)}


def run_robustchurn(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                    modes=("neutralise_int", "neutralise", "drop"), mid_day=15,
                    eras=ERAS):
    """E85: put a robust estimator beside every published churn cell's mean.

    E83 showed one transition can own a cell; that is a magnitude statement
    about the MEAN. This leg asks the complementary question on the same burn:
    does the cell's centre of mass move? Cells are (book, universe|mode, era)
    and each carries mean / median / 10% trimmed mean plus the share of the
    signed total carried by the three largest transitions. No published face is
    rewritten and no predictor is claimed.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    event_dates = _event_dates(raw, cal_full)

    universes = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        universes[mode] = repaired

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(outdir, start=start, pick_n=pick_n,
                                    exclude=exclude, mid_day=mid_day,
                                    raw=univ, full_churn=True)

    books = ["me", "mid%d" % mid_day]
    cells, delta_cells = [], []
    for book in books:
        base_rows = faces["unscreened"]["books"][book]["churn_rows"]
        for label in universes:
            rows = (base_rows if label == "unscreened"
                    else faces[label]["books"][book]["churn_rows"])
            for name, _lo, _hi in eras:
                sub = [r["churn_alpha_bp"] for r in rows if r.get("era") == name]
                st = _robust_stats(sub)
                if not st["n"]:
                    continue
                cells.append({"book": book, "universe": label, "era": name,
                              "face": "churn_alpha_bp", **st,
                              "concentration_top3": _concentration(sub, 3)})
        for mode in modes:
            rows, _agg = _churn_join(base_rows,
                                     faces[mode]["books"][book]["churn_rows"],
                                     event_dates, eras)
            for name, _lo, _hi in eras:
                sub = [r["delta_bp"] for r in rows if r["era"] == name]
                st = _robust_stats(sub)
                if not st["n"]:
                    continue
                delta_cells.append({"book": book, "mode": mode, "era": name,
                                    "face": "delta_bp", **st,
                                    "concentration_top3": _concentration(sub, 3)})

    def _tally(rows):
        live = [c for c in rows if c["median_keep_pct_of_mean"] is not None]
        return {
            "cells": len(live),
            "median_keeps_under_half_pct": len(
                [c for c in live if abs(c["median_keep_pct_of_mean"]) < 50.0]),
            "trim10_keeps_under_half_pct": len(
                [c for c in live
                 if c["trim10_keep_pct_of_mean"] is not None
                 and abs(c["trim10_keep_pct_of_mean"]) < 50.0]),
            "median_flips_sign": len(
                [c for c in live
                 if (c["median_bp"] or 0.0) * (c["mean_bp"] or 0.0) < 0]),
            "top3_over_half_of_total_pct": len(
                [c for c in live
                 if c["concentration_top3"]
                 and c["concentration_top3"]["top_share_of_total_pct"] is not None
                 and abs(c["concentration_top3"]["top_share_of_total_pct"]) > 50.0]),
        }

    return {
        "study": "e85_robust_churn_estimators",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "mid_month_day": mid_day,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": books,
            "estimators": ["mean", "median", "trimmed_mean_10pct"],
            "concentration": "sum of the 3 largest |value| transitions over the "
                             "cell signed total; >50% means three transitions "
                             "carry the cell",
            "universe_members": len(raw),
            "events_indexed": len(event_dates),
            "descriptive_only": "no prereg, no judgement, zero ledger booking",
        },
        "cells": cells,
        "delta_cells": delta_cells,
        "summary": {"levels": _tally(cells), "deltas": _tally(delta_cells)},
        "screen_reports": reports,
    }


# -------------------------------------------------------------- E91

def _top_transitions(rows, k=3):
    """The k largest |churn_alpha_bp| transitions of one cell, by name and date.

    E87 showed the two oldest eras have no centre of mass (top-3 carry 108-149%
    of the signed total). A share is not auditable, so this leg prints the
    window, the swapped names and the two side means that produced the number;
    the newest-era cells ride along as the control.
    """
    live = [r for r in (rows or []) if isinstance(r.get("churn_alpha_bp"), (int, float))]
    if not live:
        return []
    tot = sum(r["churn_alpha_bp"] for r in live)
    order = sorted(range(len(live)), key=lambda i: -abs(live[i]["churn_alpha_bp"]))[:k]
    out = []
    for i in order:
        r = live[i]
        ent, ext = r.get("entrant_fwd_pct"), r.get("exit_fwd_pct")
        side = None
        if isinstance(ent, (int, float)) and isinstance(ext, (int, float)):
            side = "entrants" if ent > ext else "exits"
        out.append({
            "date": r.get("date"), "next": r.get("next"),
            "churn_alpha_bp": r.get("churn_alpha_bp"),
            "share_of_signed_total_pct": (round(100.0 * r["churn_alpha_bp"] / tot, 1)
                                          if tot else None),
            "entrants": r.get("entrants"), "exits": r.get("exits"),
            "entrant_fwd_pct": ent, "exit_fwd_pct": ext,
            "carried_by": side,
            "entrant_names": (r.get("entrant_names") or [])[:10],
            "exit_names": (r.get("exit_names") or [])[:10],
        })
    return out


def run_topnames(outdir, start="2013-01-01", pick_n=9999, exclude=("sh511",),
                 modes=("neutralise_int", "neutralise", "drop"), mid_day=15,
                 eras=ERAS, top_k=3):
    """E91: make every concentrated churn cell auditable by name and date.

    Each (book, universe|mode, era) cell publishes its top-k transitions with
    the decision window, the swapped tickers, both side means and which side
    carried the sign, beside the plain cell mean. Nothing is re-estimated: rows
    are the same ``full_churn`` burn E82/E85/E86/E87 read.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]

    universes = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        universes[mode] = repaired

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(outdir, start=start, pick_n=pick_n,
                                    exclude=exclude, mid_day=mid_day,
                                    raw=univ, full_churn=True)

    books = ["me", "mid%d" % mid_day]
    cells = []
    for book in books:
        for label in universes:
            rows = faces[label]["books"][book]["churn_rows"]
            for name, _lo, _hi in eras:
                sub = [r for r in rows if r.get("era") == name
                       and isinstance(r.get("churn_alpha_bp"), (int, float))]
                if not sub:
                    continue
                vals = [r["churn_alpha_bp"] for r in sub]
                mean = sum(vals) / len(vals)
                top = _top_transitions(sub, top_k)
                top_sum = sum(t["churn_alpha_bp"] for t in top)
                cells.append({
                    "book": book, "universe": label, "era": name,
                    "transitions": len(sub),
                    "mean_bp": round(mean, 1),
                    "top_k": top,
                    "top_k_share_of_signed_total_pct":
                        (round(100.0 * top_sum / sum(vals), 1) if sum(vals) else None),
                    "top1_is_more_than_half": (abs(top[0]["churn_alpha_bp"])
                                               > abs(mean) * len(sub) * 0.5
                                               if top else None),
                })

    def _tally(rows):
        shar = [c["top_k_share_of_signed_total_pct"] for c in rows
                if c["top_k_share_of_signed_total_pct"] is not None]
        return {
            "cells": len(rows),
            "cells_with_top3_over_half_pct": len([s for s in shar if abs(s) > 50.0]),
            "cells_named": len([c for c in rows if c["top_k"]]),
        }

    return {
        "study": "e91_top_churn_transition_names",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "mid_month_day": mid_day, "top_k": top_k,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": books,
            "names_truncated_to": 10,
            "descriptive_only": "no prereg, no judgement, zero ledger booking",
            "universe_members": len(raw),
        },
        "cells": cells,
        "summary": _tally(cells),
        "screen_reports": reports,
    }


# -------------------------------------------------------------- E86

def _loo_means(vals):
    """Every leave-one-out mean of one cell: ``(n*m - a_i)/(n-1)``.

    E83 reports only ``argmin |mean_without|``; E86 asks what the WHOLE
    removal distribution looks like, so each cell's answer is the spread of
    all n leave-one-out re-reads, not its worst member.
    """
    clean = [float(v) for v in vals if isinstance(v, (int, float))]
    n = len(clean)
    if n < 2:
        return []
    tot = sum(clean)
    return [(tot - a) / (n - 1) for a in clean]


def _breakdown_k(vals, target_frac=0.5):
    """How many transitions must be removed before |mean| falls to target_frac.

    Greedy removal of the transition farthest from the current mean (the same
    "most influential" rule E83 applies once, iterated). k is the count of
    removals, ``share_of_transitions_pct`` its size relative to the cell, and
    ``path_bp`` records the mean after each removal so a reader can see whether
    the collapse is stepwise or one cliff.
    """
    clean = [float(v) for v in vals if isinstance(v, (int, float))]
    n = len(clean)
    if n < 2:
        return {"k": None, "n": n, "share_of_transitions_pct": None,
                "mean_after_bp": None, "path_bp": []}
    m0 = sum(clean) / n
    rest = list(clean)
    k = 0
    path = []
    while len(rest) > 1:
        cur = sum(rest) / len(rest)
        idx = max(range(len(rest)), key=lambda i: abs(rest[i] - cur))
        rest.pop(idx)
        k += 1
        cur = sum(rest) / len(rest)
        path.append(round(cur, 1))
        if abs(cur) <= abs(m0) * target_frac:
            return {"k": k, "n": n,
                    "share_of_transitions_pct": round(100.0 * k / n, 1),
                    "mean_after_bp": round(cur, 1), "path_bp": path}
    return {"k": None, "n": n, "share_of_transitions_pct": None,
            "mean_after_bp": round(rest[0], 1), "path_bp": path}


def _loo_stats(vals):
    """E86: the leave-one-out distribution of one cell plus its breakdown k."""
    clean = [float(v) for v in vals if isinstance(v, (int, float))]
    n = len(clean)
    if n < 2:
        return {"n": n, "loo_available": False, "mean_bp": (round(clean[0], 1)
                                                            if clean else None)}
    m = sum(clean) / n
    s = sorted(_loo_means(clean))

    def q(p):
        i = min(len(s) - 1, max(0, int(round(p * (len(s) - 1)))))
        return round(s[i], 1)

    half = abs(m) * 0.5
    kill = len([x for x in s if abs(x) < half])
    flip = len([x for x in s if x * m < 0])
    return {
        "n": n, "loo_available": True, "mean_bp": round(m, 1),
        "loo_min_bp": round(s[0], 1), "loo_p10_bp": q(0.10),
        "loo_median_bp": q(0.50), "loo_p90_bp": q(0.90),
        "loo_max_bp": round(s[-1], 1),
        "loo_kills_half_count": kill,
        "loo_kills_half_pct": round(100.0 * kill / n, 1),
        "loo_flips_sign_count": flip,
        "loo_flips_sign_pct": round(100.0 * flip / n, 1),
        "breakdown": _breakdown_k(clean),
    }


def run_loodist(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                modes=("neutralise_int", "neutralise", "drop"), mid_day=15,
                eras=ERAS):
    """E86: how wide is a churn cell -- every removal, and the breakdown count.

    E83 asked "does removing ONE transition kill the cell". This leg answers the
    size question that leaves open: over all n removals, how many kill it, how
    wide is the leave-one-out spread, and how many removals (k, greedily) are
    needed before the magnitude halves. A cell that dies on 1 of 27 removals is
    a different object from a cell that dies on 20 of 27, though E83's flag is
    identical for both.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    event_dates = _event_dates(raw, cal_full)

    universes = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        universes[mode] = repaired

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(outdir, start=start, pick_n=pick_n,
                                    exclude=exclude, mid_day=mid_day,
                                    raw=univ, full_churn=True)

    books = ["me", "mid%d" % mid_day]
    cells, gap_cells = [], []
    for book in books:
        base_rows = faces["unscreened"]["books"][book]["churn_rows"]
        for label in universes:
            rows = (base_rows if label == "unscreened"
                    else faces[label]["books"][book]["churn_rows"])
            for name, _lo, _hi in eras:
                sub = [r["churn_alpha_bp"] for r in rows if r.get("era") == name]
                st = _loo_stats(sub)
                if not st["n"]:
                    continue
                cells.append({"book": book, "universe": label, "era": name,
                              "face": "churn_alpha_bp", **st})

    mid_book = "mid%d" % mid_day
    me_rows = faces["unscreened"]["books"]["me"]["churn_rows"]
    mid_rows = faces["unscreened"]["books"][mid_book]["churn_rows"]
    for name, _lo, _hi in eras:
        a = [r["churn_alpha_bp"] for r in me_rows if r.get("era") == name]
        b = [r["churn_alpha_bp"] for r in mid_rows if r.get("era") == name]
        a = [v for v in a if isinstance(v, (int, float))]
        b = [v for v in b if isinstance(v, (int, float))]
        if not a or not b:
            continue
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        gap = mb - ma
        me_loo = [mb - x for x in _loo_means(a)]
        mid_loo = [x - ma for x in _loo_means(b)]
        both = sorted(round(x, 1) for x in me_loo + mid_loo)
        half = abs(gap) * 0.5
        gap_cells.append({
            "book": "%s-me" % mid_book, "universe": "unscreened", "era": name,
            "face": "churn_alpha_gap_bp",
            "n_me": len(a), "n_mid": len(b), "gap_bp": round(gap, 1),
            "loo_both_min_bp": both[0] if both else None,
            "loo_both_median_bp": (both[len(both) // 2] if both else None),
            "loo_both_max_bp": both[-1] if both else None,
            "loo_both_kills_half_count": len([x for x in both if abs(x) < half]),
            "loo_both_flips_sign_count": len([x for x in both if x * gap < 0]),
            "loo_draws": len(both),
        })

    live = [c for c in cells if c.get("loo_available")]
    ks = [c["breakdown"]["k"] for c in live if c["breakdown"]["k"] is not None]
    shares = [c["breakdown"]["share_of_transitions_pct"] for c in live
              if c["breakdown"]["share_of_transitions_pct"] is not None]
    return {
        "study": "e86_loo_distribution",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "mid_month_day": mid_day,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": books,
            "loo": "all n leave-one-out re-reads of each cell, (n*m - a_i)/(n-1)",
            "breakdown": "greedy removal of the transition farthest from the "
                         "current mean, repeated until |mean| <= 50% of the "
                         "original |mean|",
            "descriptive_only": "no prereg, no judgement, zero ledger booking",
        },
        "cells": cells,
        "gap_cells": gap_cells,
        "summary": {
            "level_cells": len(cells),
            "level_cells_with_loo": len(live),
            "cells_dying_on_one_removal": len(
                [c for c in live if c["loo_kills_half_count"] >= 1]),
            "cells_where_one_removal_is_under_10pct_of_removals": len(
                [c for c in live if c["loo_kills_half_pct"] < 10.0]),
            "cells_where_majority_of_removals_kill": len(
                [c for c in live if c["loo_kills_half_pct"] > 50.0]),
            "breakdown_k_median": (sorted(ks)[len(ks) // 2] if ks else None),
            "breakdown_share_pct_median": (sorted(shares)[len(shares) // 2]
                                           if shares else None),
            "gap_cells": len(gap_cells),
        },
        "screen_reports": reports,
    }


# -------------------------------------------------------------- E89

def _sd(vals):
    """Sample standard deviation (ddof=1); None for fewer than two points."""
    import math

    n = len(vals)
    if n < 2:
        return None
    m = sum(vals) / n
    return math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1))


def _jackknife_mean(vals):
    """Closed-form jackknife standard error of one cell mean.

    For the mean the jackknife reduces to the textbook standard error
    ``sqrt(sum (x_i - m)^2 / (n*(n-1)))``, so a cell's sampling noise is priced
    from the alphas already in memory -- no resampling, no second burn.
    """
    import math

    clean = [float(v) for v in vals if isinstance(v, (int, float))]
    n = len(clean)
    if n < 2:
        return {"n": n, "mean_bp": (round(clean[0], 1) if clean else None),
                "jk_se_bp": None, "jk_lo90_bp": None, "jk_hi90_bp": None,
                "jk_available": False}
    m = sum(clean) / n
    ss = sum((x - m) ** 2 for x in clean)
    se = math.sqrt(ss / (n * (n - 1)))
    return {"n": n, "mean_bp": round(m, 1), "jk_se_bp": round(se, 2),
            "jk_lo90_bp": round(m - 1.6449 * se, 1),
            "jk_hi90_bp": round(m + 1.6449 * se, 1),
            "jk_available": True}


def _boot_mean_ci(vals, draws=2000, seed=20261022):
    """Seeded percentile bootstrap of one cell mean (reproducible by seed).

    A fixed seed plus a stable draw order makes the face bit-reproducible; the
    point estimate stays the plain mean, so the interval is an ADDED column and
    never a replacement for a published number.
    """
    import math
    import random

    clean = [float(v) for v in vals if isinstance(v, (int, float))]
    n = len(clean)
    if n < 2:
        return {"boot_available": False, "draws": 0, "boot_p05_bp": None,
                "boot_p95_bp": None, "boot_ci_straddles_zero": None,
                "boot_signflip_pct": None, "boot_se_bp": None}
    rng = random.Random(seed)
    means = []
    for _ in range(draws):
        means.append(sum(clean[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    m = sum(clean) / n

    def q(p):
        i = min(len(means) - 1, max(0, int(round(p * (len(means) - 1)))))
        return round(means[i], 1)

    lo, hi = q(0.05), q(0.95)
    cross = len(means) if m == 0 else len([x for x in means if x * m < 0])
    return {"boot_available": True, "draws": draws, "seed": seed,
            "boot_p05_bp": lo, "boot_p95_bp": hi,
            "boot_ci_straddles_zero": bool(lo <= 0.0 <= hi),
            "boot_signflip_pct": round(100.0 * cross / len(means), 1),
            "boot_se_bp": round(_sd(means), 2)}


def _gap_interval(a, b, draws=2000, seed=20261022):
    """Interval for ``mean(b) - mean(a)`` with the two books resampled apart.

    The books are separate transition populations, so their standard errors add
    in quadrature; the bootstrap draws each side independently from the same
    seed, keeping the whole face reproducible.
    """
    import math
    import random

    ca = [float(v) for v in a if isinstance(v, (int, float))]
    cb = [float(v) for v in b if isinstance(v, (int, float))]
    na, nb = len(ca), len(cb)
    if na < 2 or nb < 2:
        return {"n_me": na, "n_mid": nb, "gap_bp": None,
                "gap_available": False, "jk_available": False,
                "jk_se_bp": None, "jk_lo90_bp": None,
                "jk_hi90_bp": None, "boot_p05_bp": None, "boot_p95_bp": None,
                "boot_ci_straddles_zero": None, "boot_signflip_pct": None}
    ma, mb = sum(ca) / na, sum(cb) / nb
    gap = mb - ma
    sea, seb = _sd(ca) / math.sqrt(na), _sd(cb) / math.sqrt(nb)
    se = math.sqrt(sea * sea + seb * seb)
    rng = random.Random(seed)
    diffs = []
    for _ in range(draws):
        sa = sum(ca[rng.randrange(na)] for _ in range(na)) / na
        sb = sum(cb[rng.randrange(nb)] for _ in range(nb)) / nb
        diffs.append(sb - sa)
    diffs.sort()

    def q(p):
        i = min(len(diffs) - 1, max(0, int(round(p * (len(diffs) - 1)))))
        return round(diffs[i], 1)

    lo, hi = q(0.05), q(0.95)
    cross = len(diffs) if gap == 0 else len([x for x in diffs if x * gap < 0])
    return {"n_me": na, "n_mid": nb, "gap_bp": round(gap, 1),
            "gap_available": True, "jk_available": True,
            "jk_se_bp": round(se, 2),
            "jk_lo90_bp": round(gap - 1.6449 * se, 1),
            "jk_hi90_bp": round(gap + 1.6449 * se, 1),
            "boot_p05_bp": lo, "boot_p95_bp": hi,
            "boot_ci_straddles_zero": bool(lo <= 0.0 <= hi),
            "boot_signflip_pct": round(100.0 * cross / len(diffs), 1),
            "interval_clears_zero": bool(
                (gap - 1.6449 * se) * (gap + 1.6449 * se) > 0)}


def run_churnse(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                modes=("neutralise_int", "neutralise", "drop"), mid_day=15,
                eras=ERAS, draws=2000, seed=20261022):
    """E89: a sampling interval beside every churn cell and churn gap.

    Every published churn number is a point estimate over 25-29 transitions, so
    a reader cannot separate "+318.8bp" from zero. This leg adds, on the same
    burn, a closed-form jackknife standard error and a seeded percentile
    bootstrap (fixed seed recorded in the spec) beside each mean, plus the share
    of resamples whose sign differs from the point estimate. The mean column is
    untouched: the interval is an extra face, never a revision.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    event_dates = _event_dates(raw, cal_full)

    universes = {"unscreened": raw}
    reports = {}
    for mode in modes:
        repaired, report = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = report
        universes[mode] = repaired

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(outdir, start=start, pick_n=pick_n,
                                    exclude=exclude, mid_day=mid_day,
                                    raw=univ, full_churn=True)

    books = ["me", "mid%d" % mid_day]
    cells, delta_cells = [], []
    for book in books:
        base_rows = faces["unscreened"]["books"][book]["churn_rows"]
        for label in universes:
            rows = (base_rows if label == "unscreened"
                    else faces[label]["books"][book]["churn_rows"])
            for name, _lo, _hi in eras:
                sub = [r["churn_alpha_bp"] for r in rows if r.get("era") == name]
                jk = _jackknife_mean(sub)
                if not jk["n"]:
                    continue
                bt = _boot_mean_ci(sub, draws=draws, seed=seed)
                cells.append({"book": book, "universe": label, "era": name,
                              "face": "churn_alpha_bp", **jk, **bt,
                              "interval_clears_zero": (
                                  None if not jk["jk_available"] or not jk["mean_bp"]
                                  else bool(jk["jk_lo90_bp"] * jk["jk_hi90_bp"] > 0))})
        for mode in modes:
            rows, _agg = _churn_join(base_rows,
                                     faces[mode]["books"][book]["churn_rows"],
                                     event_dates, eras)
            for name, _lo, _hi in eras:
                sub = [r["delta_bp"] for r in rows if r["era"] == name]
                jk = _jackknife_mean(sub)
                if not jk["n"]:
                    continue
                bt = _boot_mean_ci(sub, draws=draws, seed=seed)
                delta_cells.append({"book": book, "mode": mode, "era": name,
                                    "face": "delta_bp", **jk, **bt,
                                    "interval_clears_zero": (
                                        None if not jk["jk_available"]
                                        or not jk["mean_bp"]
                                        else bool(jk["jk_lo90_bp"] * jk["jk_hi90_bp"] > 0))})

    mid_book = "mid%d" % mid_day
    me_rows = faces["unscreened"]["books"]["me"]["churn_rows"]
    mid_rows = faces["unscreened"]["books"][mid_book]["churn_rows"]
    gap_cells = []
    for name, _lo, _hi in eras:
        a = [r["churn_alpha_bp"] for r in me_rows if r.get("era") == name]
        b = [r["churn_alpha_bp"] for r in mid_rows if r.get("era") == name]
        g = _gap_interval(a, b, draws=draws, seed=seed)
        if not g["gap_available"]:
            continue
        gap_cells.append({"book": "%s-me" % mid_book, "universe": "unscreened",
                          "era": name, "face": "churn_alpha_gap_bp", **g})

    def _tally(rows):
        live = [c for c in rows if c.get("jk_available")]
        ses = [c["jk_se_bp"] for c in live if c["jk_se_bp"] is not None]
        return {
            "cells": len(rows),
            "cells_with_interval": len(live),
            "jk_interval_clears_zero": len(
                [c for c in live if c["interval_clears_zero"]]),
            "jk_interval_straddles_zero": len(
                [c for c in live if c["interval_clears_zero"] is False]),
            "boot_interval_clears_zero": len(
                [c for c in live if c["boot_ci_straddles_zero"] is False]),
            "boot_interval_straddles_zero": len(
                [c for c in live if c["boot_ci_straddles_zero"] is True]),
            "jk_se_bp_median": (sorted(ses)[len(ses) // 2] if ses else None),
            "mean_exceeds_own_se": len(
                [c for c in live
                 if c["jk_se_bp"] and (c.get("mean_bp") or c.get("gap_bp"))
                 and abs(c.get("mean_bp") or c.get("gap_bp")) > c["jk_se_bp"]]),
            "signflip_pct_median": (sorted(
                [c["boot_signflip_pct"] for c in live
                 if c["boot_signflip_pct"] is not None])[
                len([c for c in live if c["boot_signflip_pct"] is not None]) // 2]
                if live else None),
        }

    return {
        "study": "e89_churn_sampling_intervals",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "modes": list(modes), "mid_month_day": mid_day,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": books,
            "jackknife": "closed-form SE of a mean, "
                         "sqrt(sum (x_i-mean)^2 / (n*(n-1))); 90% band = "
                         "mean +/- 1.6449*SE",
            "bootstrap": "percentile bootstrap of the mean, %d draws, fixed "
                         "seed %d (reproducible by seed, no panel read)"
                         % (draws, seed),
            "gap_interval": "mid-minus-me, books resampled independently, "
                            "SEs added in quadrature; the two books decide on "
                            "different calendar dates (30 me vs 29 mid15 in "
                            "2021_2023) so nothing pairs date-to-date, but they "
                            "hold the same names over the same era, which makes "
                            "the true difference error SMALLER than this "
                            "quadrature band -- the gap band is conservative",
            "interval_meaning": "sampling noise of the transition sample only: "
                                "cells are monthly decisions on overlapping "
                                "holdings, not iid prints, so no significance "
                                "claim is made and no cell is called positive or "
                                "negative on the strength of its band",
            "descriptive_only": "no prereg, no judgement, zero ledger booking",
        },
        "cells": cells,
        "delta_cells": delta_cells,
        "gap_cells": gap_cells,
        "summary": {"levels": _tally(cells), "deltas": _tally(delta_cells),
                    "gaps": _tally(gap_cells)},
        "screen_reports": reports,
    }


# ------------------------------------------------ E92 gap-tolerant split screen

def _gap_print_census(raw, cal_full, limits=(1, 2, 5)):
    """E92: every gapped print the fixed adjacency rule leaves unrepaired.

    ``panel_screen`` screens a print only when it sits on the next session. E91
    found the 12:1 split that owns a published era gap sitting one *missing bar*
    away from its own previous close, i.e. inside that blind spot. This census
    lists the gapped prints per gap limit (in sessions) and keeps the integer
    share ratios separate from the rest, because only an integer ratio is
    evidence of a corporate action rather than a resumption misprint.
    """
    import panel_screen

    events = []
    for s in sorted(raw):
        pair = raw[s]
        closes = pair[0] if isinstance(pair, tuple) else pair
        for e in panel_screen.split_events(closes, cal=cal_full):
            if e["adjacent"]:
                continue
            im = e.get("implied") or {}
            events.append({
                "name": s, "date": e["date"], "prev_date": e["prev_date"],
                "gap_sessions": e["gap_sessions"],
                "ret_pct": round(e["ret_pct"], 2),
                "ratio": round(im.get("ratio", e["factor"]), 4),
                "nearest_int": im.get("nearest_int"),
                "resid_pct": (round(im["resid_pct"], 3) if im else None),
                "integer_like": bool(im.get("integer_like")),
                "era": _era_of(e["date"]),
            })

    census = {}
    for lim in limits:
        eligible = [e for e in events
                    if e["integer_like"] and e["gap_sessions"] <= lim]
        by_era = {}
        for name, _lo, _hi in ERAS:
            sub = [e for e in eligible if e["era"] == name]
            if sub:
                by_era[name] = len(sub)
        census["gap%d" % lim] = {
            "gap_limit_sessions": lim,
            "gapped_prints_total": len(events),
            "eligible_integer_prints": len(eligible),
            "eligible_names": len(set(e["name"] for e in eligible)),
            "eligible_by_era": by_era,
            "non_integer_gapped": len([e for e in events if not e["integer_like"]
                                       and e["gap_sessions"] <= lim]),
            "largest_eligible": sorted(eligible,
                                       key=lambda e: -abs(e["ret_pct"]))[:10],
        }
    return {"gapped_prints": len(events), "by_gap_limit": census,
            "events": events}


def run_gapsplit(outdir, start="2020-01-01", pick_n=9999, exclude=("sh511",),
                 limits=(1, 2, 5), mid_day=15, eras=ERAS):
    """E92: does the published churn gap survive a gap-tolerant split screen?

    E91 named the defect: sh510150's unadjusted 12:1 split lands behind a missing
    bar, so both screen arms leave it at +9424.4bp and it owns 2021_2023's churn
    gap. Here the screen is widened one session (then two, then five) and the
    churn gap is re-derived on the same burn, so the answer is measured rather
    than argued. The unscreened column is kept; no published face is rewritten.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= start]
    cutoff = cal[-1]
    event_dates = _event_dates(raw, cal_full)

    universes = {"unscreened": raw}
    reports = {}
    for lim in limits:
        label = "gap%d" % lim
        repaired, report = panel_screen.screen_universe(
            raw, mode="neutralise_gap", cal=cal_full, gap_limit=lim)
        reports[label] = report
        universes[label] = repaired

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(None, start=start, pick_n=pick_n,
                                    exclude=exclude,
                                    mid_day=mid_day, raw=univ,
                                    full_churn=True)

    data = {"study": "e92_gap_tolerant_split_screen",
            "evidence_cutoff": cutoff,
            "spec": {
                "start": start, "pick_n": pick_n,
                "exclude_prefixes": list(exclude),
                "gap_limits_sessions": list(limits), "mid_month_day": mid_day,
                "costs_run": [0.0, 1.0, 3.0],
                "screen_modes": ["unscreened", "neutralise_gap"],
                "why_costs": "the churn sleeve is a name-level mean over swapped "
                             "names and no cost multiplier can move it; the standard "
                             "triple is kept because run_midmonth publishes all three "
                             "arms and the era spread is read off the same burn",
                "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
                "books": ["me", "mid%d" % mid_day],
                "universe_members": len(raw),
            },
            "census": _gap_print_census(raw, cal_full, limits),
            "screen_reports": reports,
            "honest": [
                "the gap-tolerant branch repairs only integer-ratio prints inside "
                "the session limit, so a real resumption that happens to land on an "
                "integer ratio would be repaired too -- the ratio test is evidence, "
                "not proof",
                "a wider gap limit buys more repairs and more false positives "
                "together; the sweep is published so the reader can see what each "
                "session costs",
                "churn sleeve is an equal-weight mean over the swapped names, not a "
                "portfolio return",
                "screen reports count repairs, not book impact: a repaired print "
                "still enters the rank cache at its adjusted level",
                "descriptive census only: no gate, no verdict, no prereg, no trial "
                "count",
            ]}

    book_labels = ["me", "mid%d" % mid_day]
    gaps = {}
    for era in [n for n, _lo, _hi in eras]:
        row = {}
        for label in universes:
            me = faces[label]["eras"].get(era, {}).get("me", {})
            mid = faces[label]["eras"].get(era, {}).get("mid", {})
            a, b = me.get("churn_alpha_bp_mean"), mid.get("churn_alpha_bp_mean")
            row[label] = {
                "me_churn_alpha_bp": a, "mid_churn_alpha_bp": b,
                "churn_gap_bp": (round(b - a, 1)
                                 if a is not None and b is not None else None),
            }
        base_gap = (row.get("unscreened") or {}).get("churn_gap_bp")
        for label in universes:
            g = row[label].get("churn_gap_bp")
            row[label]["delta_vs_unscreened_bp"] = (
                round(g - base_gap, 1)
                if isinstance(g, (int, float))
                and isinstance(base_gap, (int, float)) else None)
        gaps[era] = row
    data["churn_gap_by_era"] = gaps

    joins = {}
    for book in book_labels:
        base_rows = faces["unscreened"]["books"][book]["churn_rows"]
        joins[book] = {}
        for lim in limits:
            label = "gap%d" % lim
            rows, agg = _churn_join(base_rows,
                                    faces[label]["books"][book]["churn_rows"],
                                    event_dates, eras)
            moved = [r for r in rows if r.get("hit")
                     and isinstance(r.get("delta_bp"), (int, float))
                     and abs(r["delta_bp"]) > 0.5]
            joins[book][label] = {
                "eras": agg,
                "transitions": len(rows),
                "transitions_moved": len(moved),
                "top_moved": _worst_transitions(rows, n=6),
            }
    data["joins"] = joins
    return data


# ------------------------------------------------------------------- plumbing

# (E111) a face's LEVEL is produced by panel_screen's repair code, so two faces
# are comparable only when that code is the same. E110 burned this lesson: a
# pre-E108 face joined against a post-E108 one and the difference was reported
# as a defect. The cutoff was stamped; the code version was not.
REPAIR_FACTOR_KEY = "repair_factor"


def _stamp_repair_factor(payload):
    """Put the repair-factor id on a face this module is about to write."""
    if isinstance(payload, dict) and not payload.get(REPAIR_FACTOR_KEY):
        try:
            import panel_screen
            payload[REPAIR_FACTOR_KEY] = panel_screen.repair_factor_id()
            payload["repair_factor_src"] = "+".join(panel_screen.REPAIR_FACTOR_SRC)
        except Exception as exc:      # a burn is never failed over its stamp
            payload["repair_factor_error"] = repr(exc)
    return payload


def write_json(outdir, name, payload):
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, name)
    payload = _stamp_repair_factor(payload)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return p


def selftest():
    ok = tot = 0
    def chk(cond, label):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % label)

    # risk profile on a known path: 1.0 -> 1.20 -> 0.90 -> 1.30
    curve = [("2020-01-02", 1.0), ("2020-02-03", 1.10), ("2020-02-28", 1.20),
             ("2020-03-31", 0.90), ("2020-04-30", 1.30)]
    prof = risk_profile(curve, 0.5)
    chk(prof["max_drawdown_pct"] == -25.0, "max dd 1.20 -> 0.90 is -25%")
    chk(prof["worst_month"]["month"] == "2020-03", "worst month is the -25% month")
    chk(prof["best_month"]["month"] == "2020-04", "best month is the +44% month")
    chk(prof["longest_underwater_sessions"] == 1, "one session underwater before the new high")
    chk(prof["negative_months"] == 1, "March is the only negative month on the mark set")

    # classification table
    cal = ["2026-09-%02d" % d for d in range(1, 22)]
    dead = [{"date": "2026-09-01", "close": 1.0, "volume": 0.0, "amount": 0.0},
            {"date": "2026-09-02", "close": 1.0, "volume": 0.0, "amount": 0.0}]
    chk(classify_stale("sh999999.csv", dead, cal, cal[-1])["class"] == "DEAD_LISTING",
        "zero-turnover tail reads dead")
    live = [{"date": "2026-09-%02d" % d, "close": 1.0, "volume": 1000.0, "amount": 2000.0}
            for d in (1, 2, 3, 4)]
    chk(classify_stale("sh512390.csv", live, cal, cal[-1])["class"] == "SOURCE_SIDE_GAP",
        "traded tail before the bulk date reads source-side gap")
    at_bulk = [{"date": "2026-09-%02d" % d, "close": 1.0, "volume": 1000.0, "amount": 2000.0}
               for d in (20, 21, 22)]
    chk(classify_stale("sh500000.csv", at_bulk, cal, cal[-1])["class"] == "REFRESH_FAILURE",
        "tail ending on the bulk date reads refresh failure")
    chk(classify_stale("510880_t73.csv", live, cal, cal[-1])["class"] == "PINNED_SLOT_COPY",
        "tagged filename reads pinned copy")

    # month-end collapse keeps the last mark of each month
    me = _month_ends([("2020-01-02", 1.0), ("2020-01-31", 2.0), ("2020-02-03", 3.0)])
    chk(me == [("2020-01-31", 2.0), ("2020-02-03", 3.0)], "month-end collapse")

    # pair leg: a ratio curve carries the spread's own drawdown, not the legs'
    lad = [("2020-01-02", 1.0), ("2020-02-03", 0.80), ("2020-03-31", 1.0)]
    wide = [("2020-01-02", 1.0), ("2020-02-03", 0.72), ("2020-03-31", 1.0)]
    lm = dict(lad)
    ratio = [(d, v / lm[d]) for d, v in wide if d in lm and lm[d] > 0]
    chk(risk_profile(lad, 0.25)["max_drawdown_pct"] == -20.0, "ladder leg dd -20%")
    chk(risk_profile(wide, 0.25)["max_drawdown_pct"] == -28.0, "wide leg dd -28%")
    chk(risk_profile(ratio, 0.25)["max_drawdown_pct"] == -10.0,
        "ratio curve dd is the spread (-10%), not either leg")

    # cash-leg scaling: None stays the zero-cash convention, x0 empties the series
    chk(_scale_cash(None, 2.0) is None, "no cash panel stays no cash panel")
    sc = _scale_cash({"series": {"2020-01-02": 0.001}}, 3.0)
    chk(abs(sc["series"]["2020-01-02"] - 0.003) < 1e-15, "multiplier scales daily returns")
    chk(_scale_cash({"series": {"2020-01-02": 0.001}}, 0.0)["series"] == {},
        "x0 empties the series so the engine reads 0.0")
    chk(_scale_cash({"series": {}}, 1.0)["series"] == {}, "empty series survives scaling")

    # cash attribution arithmetic on a synthetic table
    rows = {"x0": {"ann_return_pct": -0.43}, "x1": {"ann_return_pct": 0.12}}
    chk(round((rows["x1"]["ann_return_pct"] - rows["x0"]["ann_return_pct"]) * 100, 2) == 55.0,
        "attribution is the ann column difference in bp")

    # size tilt legs: month marks, the 2/5+3/5 identity, and the spread in bp
    mr = _month_rets([("2020-01-31", 1.0), ("2020-02-28", 1.1), ("2020-03-31", 1.21)])
    chk(len(mr) == 2 and abs(mr[0][1] - 0.10) < 1e-12 and mr[1][0] == "2020-03",
        "month returns come off month-end marks")
    chk(abs((0.4 * 0.01 + 0.6 * 0.03) - 0.022) < 1e-12,
        "equal-weight ladder month decomposes into 2/5 large + 3/5 small")
    chk(abs((0.03 - 0.01) * 1e4 - 200.0) < 1e-9,
        "tilt spread is the large-vs-small monthly gap in bp")
    mom = _moments([0.01, 0.03, 0.05])
    chk(abs(mom["mean"] - 0.03) < 1e-12 and abs(mom["sd"] - 0.02) < 1e-9,
        "sample moments use the n-1 denominator")
    mem_raw = {"shX": ({"2020-01-31": 1.0, "2020-02-28": 1.2, "2020-03-31": 0.9}, {})}
    mem = _member_monthly(["2020-01-31", "2020-02-28", "2020-03-31"], "shX", mem_raw)
    chk(abs(mem["2020-02"] - 0.2) < 1e-12 and abs(mem["2020-03"] + 0.25) < 1e-12,
        "member monthly returns read their own month-end closes")

    # rebalance-day shift: clamping, dedupe, and the mid-month pick
    chk(_shift_indices([0, 5, 9], -1, 10) == [0, 4, 8], "shift -1 clamps at index 0")
    chk(_shift_indices([8, 9], 1, 10) == [9], "shift +1 clamps and dedupes at the last bar")
    chk(_shift_indices([3], 0, 10) == [3], "zero shift is the identity")
    cal_mid = ["2020-01-02", "2020-01-15", "2020-01-31",
               "2020-02-03", "2020-02-14", "2020-02-28"]
    chk(_mid_month_indices(cal_mid, 15) == [1, 5],
        "mid-month picks the first session on/after the 15th, once per month")
    chk(_mid_month_indices(cal_mid, 1) == [0, 3],
        "mid-month day 1 reads as the first session of each month")
    chk(_shift_indices(_mid_month_indices(cal_mid, 15), -1, len(cal_mid)) == [0, 4],
        "shifting the mid-month set moves every decision one session earlier")

    # E42: era slicing, OLS recovery, and the additive spread identity
    chk(_in_era("2016-12", None, "2016-12-31") and not _in_era("2017-01", None, "2016-12-31"),
        "era upper bound is inclusive on its month")
    chk(_in_era("2017-01", "2017-01-01", "2020-12-31") and not _in_era("2021-01", "2017-01-01", "2020-12-31"),
        "era lower bound is inclusive and the next year is out")
    chk(_in_era("2024-03", "2024-01-01", None), "open-ended era has no upper bound")
    xs = [-0.02, -0.01, 0.0, 0.01, 0.02]
    ys = [0.02 + 2.0 * x for x in xs]
    b, a, r2 = _ols(ys, xs)
    chk(abs(b - 2.0) < 1e-12 and abs(a - 0.02) < 1e-12 and abs(r2 - 1.0) < 1e-12,
        "OLS recovers beta/alpha/R2 on an exact linear series")
    chk(_ols([0.1, 0.2], [0.1, 0.2]) == (None, None, None), "fewer than 3 points is undetermined")
    chk(_ols([0.1, 0.1, 0.1], [0.01, 0.02, 0.03]) == (None, None, None),
        "a flat y has no slope to estimate")
    raw = 95.0
    neutral, size_part = 120.0, -25.0
    chk(abs((neutral + size_part) - raw) < 1e-12,
        "additive identity: raw spread = size-neutral intercept + size component")

    # E43: four-member skin is a strict subset, and the tilt builder drops only the
    # months a leg cannot be priced on
    chk(set(TILT4_SMALL) < set(TILT_SMALL) and len(TILT4_SMALL) == 2,
        "four-member small leg is a two-name subset of the five-member skin")
    chk(abs((2 / 4.0) - 0.5) < 1e-12 and abs((2 / 4.0 + 2 / 4.0) - 1.0) < 1e-12,
        "four-member skin weights 0.5/0.5 so the identity still closes")
    f_mem = {"L1": {"m1": 0.01, "m2": 0.01}, "L2": {"m1": 0.01},
             "S1": {"m1": 0.03, "m2": 0.05}, "S2": {"m1": 0.03}}
    f_brk = {"L1": set(), "L2": set(), "S1": set(), "S2": {"m2"}}
    used, tilts, drops = _tilt_series(f_mem, f_brk, ["m1", "m2", "m3"],
                                      ("L1", "L2"), ("S1", "S2"))
    chk(used == ["m1", "m2"], "tilt builder keeps only months both legs can price")
    chk(abs(tilts["m1"] - 0.02) < 1e-12, "two-name legs average before the spread")
    chk(abs(tilts["m2"] - 0.04) < 1e-12,
        "a broken member drops out of the leg mean, it does not drop the month")
    chk(len(drops) == 1 and drops[0]["month"] == "m3"
        and "S1" in drops[0]["members_missing"],
        "an unpriced month is disclosed, never silently averaged")
    comp = _compose_counts(["sh510300", "sh510500", "sh512880"], TILT_LARGE, TILT_SMALL)
    chk(comp["n"] == 3 and comp["ladder_small_names"] == 1
        and comp["ladder_large_names"] == 1 and comp["other_weight_pct"] == round(100 / 3.0, 4),
        "composition counts split holdings into ladder small / ladder large / other")
    chk(_compose_counts([], TILT_LARGE, TILT_SMALL) == {"n": 0},
        "an empty book has no composition to report")

    # E44: every leave-one-out skin drops exactly one member and keeps both legs alive
    lg5, sm5 = _skin_sets(None)
    chk(lg5 == TILT_LARGE and sm5 == TILT_SMALL,
        "the full skin is the untouched five-member set")
    lg4, sm4 = _skin_sets("sh588000")
    chk(lg4 == TILT_LARGE and sm4 == TILT4_SMALL,
        "dropping STAR reproduces the E43 four-member skin exactly")
    lg1, sm1 = _skin_sets("sh510050")
    chk(len(lg1) == 1 and sm1 == TILT_SMALL,
        "dropping a large-cap leaves a one-name large leg, not an empty one")
    chk(all(_skin_sets(d)[0] and _skin_sets(d)[1] for d in (TILT_LARGE + TILT_SMALL)),
        "no single-member drop empties either size leg")

    # E44 burn-in: the gate is window-relative, and the arrival index is the
    # first bar whose trailing window is fully priced (a gap restarts the run)
    chk(_first_eligible_idx([None] * 10, 3) is None,
        "a series with no priced closes never becomes eligible")
    chk(_first_eligible_idx([1.0] * 300, 250) == 249,
        "a fully priced series clears the 250-bar gate on its 250th bar")
    gap = [1.0] * 249 + [None] + [1.0] * 250
    chk(_first_eligible_idx(gap, 250) == 499,
        "a single missing close restarts the burn-in inside the window")
    chk(_first_eligible_idx([None] * 100 + [1.0] * 250, 250) == 349,
        "eligibility is window-relative: the first 100 sessions are dead for everyone")
    # annual chaining off month-end marks
    chk(_annual_rets([("2020-12-31", 1.0), ("2021-12-31", 1.10),
                      ("2022-12-31", 0.99)]) == {"2021": 10.0, "2022": -10.0},
        "annual returns chain each year off the prior year-end mark")
    chk(_annual_rets([("2021-06-30", 2.0)]) == {}, 
        "a single year has no prior close to chain from")

    # E45 warm vs cold: dead-block counting, slice faces, spread arithmetic
    cur = [("2020-01-02", 1.0), ("2020-01-03", 1.1), ("2020-02-03", 1.2)]
    chk(_bars_before(cur, "2020-02-03") == 2, "bars before a date excludes the date itself")
    chk(_bars_before(cur, None) == 0, "an unknown first-invested date counts no dead bars")
    chk(_bars_before(cur, "2019-01-01") == 0, "a date before the curve counts nothing")
    chk(_curve_faces(cur[:2]) is None, "a slice under 3 bars has no annualised face")
    face = _curve_faces(cur)
    chk(face["bars"] == 3 and face["from"] == "2020-01-02" and face["ann_return_pct"] > 0,
        "a 3-bar slice reports from/to/bars/ann")
    chk(_curve_faces(cur)["ann_return_pct"] == _curve_faces(cur)["ann_return_pct"],
        "the face is deterministic on the same slice")
    chk(_spread_bp({"ann_return_pct": 1.0}, {"ann_return_pct": 2.5}) == 150.0,
        "spread is the wide-minus-ladder ann gap in bp")
    chk(_spread_bp(None, {"ann_return_pct": 2.5}) is None,
        "a missing leg has no spread")
    csh = {"series": {"2020-01-02": 0.001, "2020-01-03": 0.001, "2020-02-03": 0.001}}
    ccal = [d for d, _v in cur]
    chk(abs(_cash_accrual_pct(csh, ccal, "2020-02-03") - 0.2) < 1e-9,
        "cash accrual compounds the daily repo returns before the first invested bar")
    chk(_cash_accrual_pct(None, ccal, "2020-02-03") == 0.0,
        "no cash panel accrues nothing")
    chk(_cash_accrual_pct(csh, ccal, None) == 0.0,
        "a book with no first-invested bar accrues nothing")

    # E46 era splitting: contiguous halves that keep the whole slice
    spl = _split_curve([("d%d" % i, 1.0 + i) for i in range(10)], 2)
    chk([len(s) for s in spl] == [5, 5], "two parts of ten bars split five and five")
    chk(spl[0][0][0] == "d0" and spl[-1][-1][0] == "d9",
        "the split keeps the first and last bar of the slice")
    chk(_split_curve([("d%d" % i, 1.0) for i in range(3)], 2) == [],
        "a slice too short to split is refused, not half-split")

    # E58 cut roll-up: flip set, band stats and dead parts are read per cut
    fake = {"A": {"part_spreads_bp": [10.0, -20.0, 0.0], "part_band_bp": 30.0,
                  "sign_flips_inside_era": True, "widest_part": 1,
                  "parts": [{"part": 1, "from": "2020-01-01", "to": "2020-02-01"},
                            {"part": 2, "from": "2020-02-02", "to": "2020-03-01"}]},
            "B": {"part_spreads_bp": [5.0, 7.0], "part_band_bp": 2.0,
                  "sign_flips_inside_era": False, "widest_part": 2,
                  "parts": [{"part": 1, "from": "2020-01-01", "to": "2020-02-01"},
                            {"part": 2, "from": "2020-02-02", "to": "2020-03-01"}]}}
    cup = _cut_summary(fake)
    chk(cup["flip_count"] == 1 and cup["eras_flipping"] == ["A"],
        "cut summary names exactly the eras that flip")
    chk(cup["bands_bp"] == {"A": 30.0, "B": 2.0} and cup["band_widest_era"] == "A",
        "cut summary keeps the per-era band and the widest era")
    chk(cup["band_mean_bp"] == 16.0 and cup["band_median_bp"] == 16.0,
        "band mean and median agree on a two-era cut")
    chk(cup["zero_spread_parts_by_era"] == {"A": 1},
        "a part with spread exactly 0 is counted as a dead band slot")
    chk(_widest_window(fake["A"]) == "2020-01-01..2020-02-01",
        "the widest part is reported with the window of that cut")
    chk(_widest_window({"widest_part": 9, "parts": []}) is None,
        "a missing widest part reports no window instead of guessing one")

    # E44 churn sleeve: identical books swap nothing
    ccal = ["2020-01-%02d" % d for d in (2, 3, 6, 7)]
    cpx = {"a": [1.0, 1.0, 1.0, 1.0], "b": [1.0, 1.0, 1.0, 1.0]}
    same = [(1, ["a", "b"]), (3, ["a", "b"])]
    rows, agg = _churn_stats(ccal, cpx, same)
    chk(len(rows) == 1 and rows[0]["entrants"] == 0 and rows[0]["churn_alpha_bp"] is None,
        "identical consecutive books produce no churn and no churn alpha")
    chk(agg == {}, "a book that never swaps contributes no era aggregate")

    # one-in one-out with known forward returns: alpha == entrant minus exit
    swap = [(1, ["a"]), (3, ["b"])]
    cpx2 = {"a": [1.0, 1.0, 2.0, 1.1], "b": [1.0, 1.0, 2.0, 0.9]}
    rows2, agg2 = _churn_stats(ccal, cpx2, swap)
    chk(rows2[0]["entrants"] == 1 and rows2[0]["exits"] == 1,
        "a full swap reports one entrant and one exit")
    chk(abs(rows2[0]["churn_alpha_bp"] - (-2000.0)) < 1e-9,
        "churn alpha is entrant forward return minus exit forward return in bp "
        "(-10%% entrant vs +10%% exit -> -2000bp)")

    # E57: the other calendar's next book decides the bucket, and the "next"
    # decision is strictly after the one being classified
    dec = [(0, ["a"]), (5, ["a", "b"]), (9, ["b", "c"])]
    chk(_next_decision_idx(dec, 0) == 1, "next decision skips a same-session twin")
    chk(_next_decision_idx(dec, 5) == 2 and _next_decision_idx(dec, 9) is None,
        "next decision is strictly after the bar index")
    bk = _classify_entrants(["a", "b", "c", "d"], next_hold=["a", "b"], drop_next=["b"])
    chk(bk["other_drops_next"] == ["b"], "a name the other book sheds is chase")
    chk(bk["other_still_holds"] == ["a"], "a name the other book keeps is being early")
    chk(bk["disjoint"] == ["c", "d"], "names in neither book are a different slice")
    chk(_classify_entrants(["a"], None, None)["disjoint"] == ["a"],
        "a missing other book buckets everything as disjoint, not as a silent pass")

    # E59 sweep: the offset is measured to the NEXT month-end decision, and a
    # missing arm reports None rather than a silent zero gap
    scal = ["2020-01-%02d" % d for d in range(1, 11)]
    chk(_calendar_offsets(scal, [3, 6], [4, 7])["mean_sessions_to_month_end"] == 1.0,
        "a decision one session before month-end has offset 1")
    chk(_calendar_offsets(scal, [3], [])["mean_sessions_to_month_end"] is None,
        "no month-end decision leaves the offset unknown, not zero")
    sbook = {"me": {"arms": {"x1": {"full_window_ann_pct": 5.0,
                                    "eras": {"A": {"ann_return_pct": 4.0}}}}},
             "mid10": {"offset": {"mean_sessions_to_month_end": 6.0},
                       "arms": {"x1": {"full_window_ann_pct": 4.0,
                                       "turnover_per_year": 0.6,
                                       "eras": {"A": {"ann_return_pct": 3.5}}}}}}
    sg = _sweep_gaps(sbook, "x1", eras=(("A", "a", "b"),))
    chk(sg["mid10"]["full_window_gap_bp"] == -100.0,
        "sweep gap is the off-cycle minus month-end ann in bp")
    chk(sg["mid10"]["eras"]["A"]["gap_bp"] == -50.0,
        "sweep era gap carries the same sign convention")
    chk(_sweep_gaps(sbook, "x3", eras=(("A", "a", "b"),))["mid10"]["full_window_gap_bp"] is None,
        "a cost level with no arm reports no gap instead of a zero")

    # E63 cost face: the shift is the fee signature of a sweep day, and a
    # missing arm reports None instead of a silent zero shift
    cg = {"x0": {"mid10": {"full_window_gap_bp": -60.0, "turnover_per_year": 0.58,
                           "eras": {"A": {"gap_bp": -70.0}}}},
          "x3": {"mid10": {"full_window_gap_bp": -68.0, "turnover_per_year": 0.58,
                           "eras": {"A": {"gap_bp": -66.0}}}}}
    face = _cost_face(cg, "x0", "x3", eras=(("A", "a", "b"),))
    chk(face["mid10"]["full_window_shift_bp"] == -8.0,
        "cost shift is x3 minus x0 on the same sweep day")
    chk(face["mid10"]["eras"]["A"]["shift_bp"] == 4.0,
        "era shift is signed per era, not folded into the full window")
    chk(face["mid10"]["turnover_per_year"]["x0"] == 0.58,
        "the cost face carries turnover beside the gap it is pricing")
    cg_missing = {"x0": {"mid10": {"full_window_gap_bp": -60.0, "eras": {}}},
                  "x3": {"mid10": {"full_window_gap_bp": None, "eras": {}}}}
    chk(_cost_face(cg_missing, "x0", "x3", eras=(("A", "a", "b"),))
        ["mid10"]["full_window_shift_bp"] is None,
        "an unpriced cost arm leaves the shift unknown, not zero")

    # E65 delay ladder: a +k lag moves every decision k sessions later, and the
    # tail clamps into the last bar instead of inventing future sessions
    chk(_shift_indices([3, 6], 1, 10) == [4, 7],
        "a one-session lag moves each decision exactly one session later")
    chk(_shift_indices([8, 9], 3, 10) == [9],
        "a lag past the calendar end clamps to the last bar and dedupes")

    # era attribution follows the decision date, not the next date
    chk(_era_of("2023-12-29") == "2021_2023" and _era_of("2024-01-02") == "2024_now",
        "era boundaries key on the decision date")

    # E66 early ladder: the two sides of the boundary must never share a label,
    # and a negative shift stays inside the calendar
    chk(_early_label(3) == "me_m3" and _lag_label(3) == "me_lag3"
        and _early_label(3) != _lag_label(3),
        "early and late rows carry distinct labels at the same magnitude")
    chk(_lag_label(-1) == "me_lag-1" and _shift_indices([0, 5, 9], -1, 10) == [0, 4, 8],
        "an early lag is the negative shift and clamps at the first bar")

    # E69 weekly clash: the weekly grid is one decision per ISO week, and the
    # monthly-cadence reading snaps each month-end to the nearest weekly session
    _wk_cal = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05",
               "2024-01-08", "2024-01-09", "2024-01-10"]
    chk(_weekly_indices(_wk_cal) == [0, 5],
        "the weekly grid keeps one decision per ISO week")
    chk(_nearest_weekly_to_month_end([0, 5, 10], [3, 8]) == [5, 10]
        and _nearest_weekly_to_month_end([0, 5, 10], [4, 6]) == [5],
        "month-ends snap to the nearest weekly session, deduped")
    chk(_nearest_weekly_to_month_end([], [3]) == [] and
        _nearest_weekly_to_month_end([0], []) == [],
        "an empty grid returns no decisions instead of raising")

    # E70 cost face on the weekly clash: the same rows at two cost levels, read
    # out of ONE face, and a fee-only gap must move while a price-path gap does not
    _synth = {"gaps": {"x0": {"week": {"full_window_gap_bp": -40.0,
                                      "turnover_per_year": 0.70,
                                      "cost_per_year_bp": 0.0,
                                      "eras": {"2024_now": {"gap_bp": -50.0}}},
                              "week_near_me": {"full_window_gap_bp": -8.0,
                                               "turnover_per_year": 0.50,
                                               "cost_per_year_bp": 0.0,
                                               "eras": {"2024_now": {"gap_bp": -9.0}}}},
                       "x3": {"week": {"full_window_gap_bp": -55.0,
                                      "turnover_per_year": 0.70,
                                      "cost_per_year_bp": 30.0,
                                      "eras": {"2024_now": {"gap_bp": -50.0}}},
                              "week_near_me": {"full_window_gap_bp": -8.0,
                                               "turnover_per_year": 0.50,
                                               "cost_per_year_bp": 30.0,
                                               "eras": {"2024_now": {"gap_bp": -9.0}}}}},
              "books": {"week": {"decision_days": 349},
                        "week_near_me": {"decision_days": 82}}}
    _rows0 = _weekly_cal_rows(_synth, "x0")
    _rows3 = _weekly_cal_rows(_synth, "x3")
    chk(_rows0["week"]["decision_days"] == 349 and
        _rows3["week_near_me"]["cost_per_year_bp"] == 30.0 and
        _rows0["week"]["eras"]["2024_now"] == -50.0,
        "one cost level reads decision days, fee and era gaps off the same face")
    _cf = _cost_face(_synth["gaps"], "x0", "x3")
    chk(_cf["week"]["full_window_shift_bp"] == -15.0 and
        _cf["week_near_me"]["full_window_shift_bp"] == 0.0 and
        _cf["week"]["eras"]["2024_now"]["shift_bp"] == 0.0,
        "a fee-only gap moves with the multiplier while a price-path gap holds still")

    # E67 neighbourhood: the second-session arms keep their seeded names, and
    # the three-point bracket separates a point kick from a ramp
    import tempfile as _tf
    chk(_early_label(2) == "me_m2" and _lag_label(2) == "me_lag2"
        and _lag_label(-2) == "me_lag-2",
        "the two-session arms reuse the early/late label machinery")
    chk(_bracket_shape([-19.0, 0.0, -19.0]) == "spike"
        and _bracket_shape([-19.0, -30.0, -65.0]) == "ramp"
        and _bracket_shape([3.0, 1.0, -5.0]) == "ramp"
        and _bracket_shape([-19.0, 12.0, -19.0]) == "non_monotone"
        and _bracket_shape([-19.0, None, -19.0]) == "incomplete",
        "bracket shape reads spike/ramp/non-monotone/incomplete off three points")
    with _tf.TemporaryDirectory() as _td:
        _face, _path = _read_early_face(_td, "2026-10-20", "2013-01-01")
        chk(_face is None and _path.endswith("EARLYDELAY-20261020-s20130101.json"),
            "a missing early face reads as absent with the expected path")
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _td:
        _face, _path = _read_late_face(_td, "2026-10-20", "2013-01-01")
        chk(_face is None and _path.endswith("ENTRYDELAY-20261020-s20130101.json"),
            "a missing late face reads as absent with the expected path")

    # E71 name census: overlap splits into entrants/exits, pairing snaps to the
    # nearest session, churn counts the book's own drift, and a stale hold is
    # exactly the gap between two decisions
    _ov = _overlap_stats(["a", "b", "c"], ["b", "c", "d"])
    chk(_ov["common"] == 2 and _ov["entrants"] == 1 and _ov["exits"] == 1
        and _ov["share_of_base"] == 0.6667 and _ov["jaccard"] == 0.5,
        "overlap splits common names into directional entrants and exits")
    chk(_overlap_stats([], ["a"])["share_of_base"] is None
        and _overlap_stats([], [])["jaccard"] is None,
        "an empty held set reports None instead of dividing by zero")
    chk(_pair_to_grid([0, 5, 10], [1, 6, 11]) == {0: 1, 5: 6, 10: 11}
        and _pair_to_grid([4, 6], [5]) == {4: 5, 6: 5}
        and _pair_to_grid([0], []) == {},
        "each decision pairs to its nearest session and an empty grid pairs nothing")
    _ch = _name_churn_stats([["a", "b"], ["a", "b"], ["c"]])
    chk(_ch["steps"] == 2 and _ch["mean_names_kept_share"] == 0.5
        and _ch["mean_names_changed"] == 1.5 and _ch["max_names_changed"] == 3,
        "churn counts how far a book's own membership moves per decision")
    chk(_name_churn_stats([["a"]])["steps"] == 0,
        "a single decision has no churn step")
    _st = _stale_hold_stats([0, 5, 21], [["a", "b"], ["a", "c"], ["d"]])
    chk(_st["exits"] == 3 and _st["mean_sessions_held_after_exit"] == 12.33
        and _st["max_sessions_held_after_exit"] == 16,
        "a stale hold is the gap to the next decision, averaged over every exit")
    chk(_stale_hold_stats([0], [["a"]])["mean_sessions_held_after_exit"] is None,
        "a book with one decision reports no stale hold")
    _sm = _pair_summary([{"share_of_base": 1.0, "entrants": 0, "exits": 0,
                         "same_session": True},
                        {"share_of_base": 0.5, "entrants": 4, "exits": 2,
                         "same_session": False}])
    chk(_sm["n_pairs"] == 2 and _sm["same_session_pairs"] == 1
        and _sm["mean_share_of_base"] == 0.75 and _sm["mean_entrants"] == 2.0,
        "pair summary averages overlap and counts coincident sessions separately")
    chk(_membership_reading(0.99) == "same_names"
        and _membership_reading(0.60) == "diverging_names"
        and _membership_reading(None) == "insufficient",
        "the membership label reads same/diverging/insufficient off the overlap")
    chk(_tail_guard([100, 110, 12]) == [True, True, False]
        and _tail_guard([0, 40, 60, 80]) == [False, True, True, True]
        and _tail_guard([]) == [],
        "a mid-arrival stub bar and an empty cash bar are dropped, growth is kept")

    # E72 stale-exit pricing: the return is close-to-close, an unpriced end is
    # None (never a flat hold), and an event is charged at the equal weight of
    # the book that dropped the name late
    chk(abs(_cum_return([1.0, 1.2, 0.9], 0, 1) - 0.2) < 1e-12,
        "cum return reads the two closes it is pointed at")
    chk(abs(_cum_return([1.0, 1.2, 0.9], 1, 2) + 0.25) < 1e-12,
        "cum return carries a loss as a negative number")
    chk(_cum_return([1.0, None, 0.9], 0, 1) is None
        and _cum_return([0.0, 1.0], 0, 1) is None
        and _cum_return([1.0], 0, 3) is None
        and _cum_return(None, 0, 1) is None,
        "a missing bar, a zero base, an out-of-range index and no series are all None")
    _cal = ["2020-01-%02d" % d for d in range(1, 11)]
    _me_i, _me_b = [0, 5, 9], [["a", "b"], ["a", "c"], ["a"]]
    _wk_i = [0, 2, 4, 6, 8]
    _wk_b = [["a", "b"], ["a", "b"], ["a"], ["a"], ["a"]]
    _px = {s: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
           for s in ("a", "b", "c")}
    _px["b"] = [1.0, 1.0, 1.0, 1.0, 1.0, 0.9] + [0.9] * 4
    _ev, _sk = _stale_hold_events(
        _me_i, _me_b, _wk_i, _wk_b, lambda s, a, b: _cum_return(_px[s], a, b))
    chk(len(_ev) == 1 and _ev[0]["name"] == "b"
        and _ev[0]["extra_sessions"] == 3
        and abs(_ev[0]["weight_pct"] - 50.0) < 1e-9,
        "only the name the weekly book already sold is priced, at 1/n of the book")
    chk(abs(_ev[0]["bp_contrib"] + 500.0) < 1e-9,
        "a -10% tail on a half-weight name charges -500bp to the book")
    chk(_sk["never_in_weekly_book"] == 1,
        "a name the weekly book never holds is a coverage difference, not a tail")
    chk(_stale_hold_events(_me_i, _me_b, _wk_i, _wk_b,
                           lambda s, a, b: None)[1]["unpriced"] == 1,
        "an unpriced tail is disclosed, not charged as a flat hold")
    _ag = _stale_aggregate(_ev, _years_between("2020-01-01", "2020-12-31"))
    chk(_ag["events"] == 1 and abs(_ag["total_bp"] + 500.0) < 1e-9
        and abs(_ag["bp_per_year"] + 500.0) < 1.0
        and _ag["negative_share"] == 1.0 and _ag["mean_extra_sessions"] == 3.0,
        "the aggregate carries total bp, bp/yr, the negative share and the sessions")
    chk(_stale_aggregate([], 1.0)["total_bp"] == 0.0
        and _stale_aggregate([], 1.0)["bp_per_year"] is None,
        "no events reports zero bp and no rate instead of dividing by nothing")
    chk(_years_between("2020-01-01", "2020-01-01") is None
        and _years_between(None, "2020-01-01") is None,
        "a zero-length or malformed span has no year rate")

    # E74 relative stale tail: the same events charged against the wide book so
    # a market-wide move nets out and only a name effect can survive
    _px2 = {"a": [1.0] * 6, "b": [1.0] * 6}
    _wr = _wide_session_returns(_px2, ["a", "b"], 6)
    chk(len(_wr) == 6 and _wr[0] is None and abs(_wr[3]) < 1e-15,
        "the wide book return starts empty and averages flat names to zero")
    chk(_wide_session_returns({"a": [1.0, 1.2, None]}, ["a"], 3)[2] is None,
        "a session with no priced member reads None, not a flat zero")
    chk(abs(_compound_between([None, 0.1, 0.1], 0, 2) - 0.21) < 1e-12,
        "the wide book compounds its per-session returns over the span")
    chk(_compound_between([None, 0.1, None, 0.1], 0, 3) is None
        and _compound_between([None, 0.1], 1, 1) is None,
        "a gap inside the span and a zero-length span are both None")
    _ev2, _sk2 = _stale_hold_events(
        _me_i, _me_b, _wk_i, _wk_b,
        lambda s, a, b: _cum_return(_px[s], a, b),
        book_ret_fn=lambda a, b: -0.10)
    chk(len(_ev2) == 1 and abs(_ev2[0]["bp_contrib"] + 500.0) < 1e-9
        and abs(_ev2[0]["relative_bp_contrib"]) < 1e-9
        and abs(_ev2[0]["excess_return_pct"]) < 1e-9,
        "a tail that is exactly the book's move nets to zero relative bp")
    _ev3, _sk3 = _stale_hold_events(
        _me_i, _me_b, _wk_i, _wk_b,
        lambda s, a, b: _cum_return(_px[s], a, b),
        book_ret_fn=lambda a, b: None)
    chk(_sk3["unpriced_book"] == 1 and "relative_bp_contrib" not in _ev3[0],
        "an unpriceable reference span is disclosed beside the raw event")
    chk(_stale_aggregate(_ev2, 1.0, key="relative_bp_contrib",
                         ret_key="excess_return_pct")["events"] == 1
        and _stale_aggregate(_ev, 1.0, key="relative_bp_contrib")["events"] == 0,
        "the relative aggregate counts only events that carry a relative charge")
    chk(_relative_reading(-500.0, 0.0) == "collapsed"
        and _relative_reading(-100.0, -90.0) == "survives"
        and _relative_reading(-100.0, 120.0) == "partial"
        and _relative_reading(-3.0, 4.0) == "collapsed"
        and _relative_reading(None, 5.0) == "insufficient",
        "the collapse label uses the shrink share with a small-raw floor")
    chk(abs(_max_session_jump(_px["b"], 2, 5) - 0.10) < 1e-9
        and _max_session_jump([1.0, 10.4, 0.87], 0, 2) > ARTEFACT_JUMP,
        "a split prints as a jump past the daily-limit screen, a normal move does not")
    chk(_max_session_jump([1.0, None, 0.9], 0, 2) is not None
        and abs(_max_session_jump([1.0, None, 0.9], 0, 2) - 0.10) < 1e-9
        and _max_session_jump([1.0, 10.4, None, 0.87], 0, 3) > ARTEFACT_JUMP,
        "a missing bar does not hide the split behind it -- priced pairs are compared")
    chk(_max_session_jump([1.0, 1.0], 1, 1) is None
        and _max_session_jump([None, 1.0], 0, 1) is None,
        "a zero-length span and a single priced close leave the jump unjudged")

    # E75 panel-wide split audit: consecutive PRICED closes + integer-ratio fingerprint
    _pcal = ["2020-01-0%d" % i for i in range(1, 6)]
    _ppx = {"a": [10.414, None, 0.87, 0.88, 0.89],
            "b": [1.0, 1.01, 1.02, 1.03, 1.04]}
    _pbr = _breadth(_ppx, ["a", "b"], 5)
    chk(_pbr == [2, 1, 2, 2, 2],
        "breadth counts priced members per session and a missing bar is not a member")
    _pev = _split_events(_pcal, _ppx, ["a", "b"], _pbr)
    chk(len(_pev) == 1 and _pev[0]["name"] == "a"
        and _pev[0]["date"] == "2020-01-03" and _pev[0]["gap_sessions"] == 2
        and not _pev[0]["adjacent"],
        "a split behind a suspension bar is flagged once and marked gapped, not adjacent")
    chk(abs(_pev[0]["ret_pct"] + 91.65) < 0.5 and _pev[0]["direction"] == "down",
        "the flagged move carries its direction and size")
    chk(abs(_pev[0]["book_impact_bp"] - 4582.3) < 1.0,
        "one name in a two-name book charges |r|/n in bp")
    _rs = _split_ratio(-0.9167)
    chk(_rs["nearest_int"] == 12 and _rs["integer_like"],
        "a 12:1 split print recovers an integer ratio inside the 2% band")
    chk(not _split_ratio(-0.05)["integer_like"] and _split_ratio(-1.0) is None,
        "an ordinary move is not integer-like and a -100% print has no ratio")
    _ps = _split_summary(_pev, 1.0)
    chk(_ps["events"] == 1 and _ps["names"] == 1 and _ps["gapped"] == 1
        and abs(_ps["total_book_bp"] - _pev[0]["book_impact_bp"]) < 1e-9,
        "the split summary totals the book impacts and counts names and gaps")

    # E76 screen-regrade: the opt-in loader, the delta table, and era shortfall
    import panel_screen
    chk(panel_screen.selftest() == 0,
        "the opt-in screen module passes its own selftest")
    _cur = [("2020-01-02", 1.0), ("2020-01-31", 1.1), ("2020-02-28", 1.2)]
    chk(_era_rows(_cur, _cur, _cur,
                  (("short", "2020-01-01", "2020-01-31"),))["short"]["bars"] == 2,
        "era slicing keeps the bars inside the era")
    chk("skipped" in _era_rows(_cur, _cur, _cur,
                               (("empty", "2019-01-01", "2019-12-31"),))["empty"],
        "an era with no bars is skipped, not published as a zero")
    _faces = {"unscreened": {"ladder": {"2020-01-01": {"ann_pct": 10.0, "sharpe": 1.0}},
                             "eras": {"pre2017": {"spread_ann_bp": -40.0,
                                                  "ladder_ann_pct": 5.0,
                                                  "wide_ann_pct": 1.0,
                                                  "ratio_path": {"max_drawdown_pct": -12.0,
                                                                 "ann_pct": 1.0}}}},
              "neutralise": {"ladder": {"2020-01-01": {"ann_pct": 12.5, "sharpe": 1.2}},
                             "eras": {"pre2017": {"spread_ann_bp": 15.0,
                                                  "ladder_ann_pct": 6.0,
                                                  "wide_ann_pct": 7.5,
                                                  "ratio_path": {"max_drawdown_pct": -9.0,
                                                                 "ann_pct": 2.0}}}}}
    _d = _delta_rows("unscreened", _faces)
    _ann = [r for r in _d if r["face"] == "ladder@2020-01-01" and r["column"] == "ann_pct"][0]
    chk(_ann["unscreened"] == 10.0 and _ann["neutralise"] == 12.5
        and abs(_ann["delta_neutralise"] - 2.5) < 1e-12,
        "the delta row keeps the unscreened twin and reports screened-minus-unscreened")
    _sp = [r for r in _d if r["face"] == "era:pre2017" and r["column"] == "spread_ann_bp"][0]
    chk(_sp["unscreened"] == -40.0 and _sp["delta_neutralise"] == 55.0,
        "the era spread delta is the same arithmetic on the era column")
    chk(any(r["column"] == "ratio_max_drawdown_pct" for r in _d),
        "the ratio path is carried into the delta table, not just the levels")

    # E77 screened-wide: the headline extractor, the era flatten, the delta table
    _wf = {"universe_size": 100, "bars": 50, "schemes": {
        "ladder5": {"metrics": {"ann_return_pct": 5.0}},
        "top9999": {"metrics": {"ann_return_pct": 8.0, "ann_vol_pct": 17.0,
                                "sharpe": 0.5, "total_return_pct": 90.0},
                    "aux": {"turnover_per_year": 0.7, "cost_per_year_bp": 9.1},
                    "vs_ladder_bp_annualised": 265.9,
                    "vs_ladder": {"months": 106, "mean_bp": 20.5, "t": 1.29}}}}
    _wh = _wide_headline(_wf, 9999)
    chk(_wh["wide_ann_pct"] == 8.0 and _wh["ladder_ann_pct"] == 5.0
        and _wh["vs_ladder_bp_annualised"] == 265.9 and _wh["t"] == 1.29,
        "the wide headline reads the wide book and keeps the ladder twin beside it")
    chk(_wide_headline({}, 9999)["wide_ann_pct"] is None,
        "a face without the scheme yields None, not a crash")
    _er = _wide_era_headline({"a": {"wide_ann_pct": 7.0, "ladder_ann_pct": 5.0,
                                    "spread_ann_bp": 200.0,
                                    "ratio_path": {"ann_pct": 3.0,
                                                   "max_drawdown_pct": -9.0}},
                              "b": {"bars": 3, "skipped": "fewer than 2 bars"}})
    chk(_er["a"]["spread_ann_bp"] == 200.0 and _er["a"]["ratio_max_drawdown_pct"] == -9.0
        and "skipped" in _er["b"],
        "era flatten carries the spread and the ratio path and keeps a skipped era honest")
    _dfaces = {
        "unscreened": {"windows": {"2020-01-01": {"x1": {"wide_ann_pct": 8.0},
                                                  "x3": {"wide_ann_pct": 7.0}},
                                   "2018-01-01": {"x1": {"wide_ann_pct": 8.0},
                                                  "x3": {"wide_ann_pct": 7.5}}},
                       "eras": {"x1": {"now": {"spread_ann_bp": 100.0}},
                                "x3": {"now": {"spread_ann_bp": 90.0}}}},
        "neutralise": {"windows": {"2020-01-01": {"x1": {"wide_ann_pct": 11.0},
                                                  "x3": {"wide_ann_pct": 10.0}},
                                   "2018-01-01": {"x1": {"wide_ann_pct": 11.0},
                                                  "x3": {"wide_ann_pct": 10.5}}},
                       "eras": {"x1": {"now": {"spread_ann_bp": 400.0}},
                                "x3": {"now": {"spread_ann_bp": 380.0}}}}}
    _drows = _wide_delta_rows("unscreened", _dfaces, ["neutralise"],
                              ("2020-01-01", "2018-01-01"), (1.0, 3.0),
                              (("pre2017", None, "2016-12-31"), ("now", "2024-01-01", None)))
    _cell = [r for r in _drows if r["face"] == "wide@2020-01-01@x1"
             and r["column"] == "wide_ann_pct"][0]
    chk(_cell["unscreened"] == 8.0 and _cell["neutralise"] == 11.0
        and abs(_cell["delta_neutralise"] - 3.0) < 1e-12,
        "the window delta keeps the unscreened twin and reports screened-minus-unscreened")
    _ecell = [r for r in _drows if r["face"] == "era:now@x3"
              and r["column"] == "spread_ann_bp"][0]
    chk(_ecell["unscreened"] == 90.0 and _ecell["delta_neutralise"] == 290.0,
        "the era delta is the same arithmetic at the cost-x3 level")
    _missing = [r for r in _drows if r["face"] == "era:pre2017@x1"
                and r["column"] == "spread_ann_bp"]
    chk(_missing and _missing[0]["unscreened"] is None
        and _missing[0]["delta_neutralise"] is None,
        "an era the face does not publish yields None cells, not a fabricated zero")

    # E78 screened weekly residual: the residual table keeps both books and twins
    _kfaces = {
        "unscreened": {"calendar_rows": {"x1": {
            "week": {"full_window_gap_bp": -53.0, "turnover_per_year": 0.789,
                     "cost_per_year_bp": 10.0, "eras": {"2024_now": -71.0}},
            "week_near_me": {"full_window_gap_bp": -11.0, "turnover_per_year": 0.595,
                             "cost_per_year_bp": 7.8, "eras": {"2024_now": -15.0}}}}},
        "neutralise": {"calendar_rows": {"x1": {
            "week": {"full_window_gap_bp": -20.0, "turnover_per_year": 0.790,
                     "cost_per_year_bp": 10.1, "eras": {"2024_now": -30.0}},
            "week_near_me": {"full_window_gap_bp": 6.0, "turnover_per_year": 0.596,
                             "cost_per_year_bp": 7.9, "eras": {"2024_now": 4.0}}}}},
    }
    _wd = _week_delta_rows("unscreened", _kfaces, ("neutralise",), (1.0,),
                           ("week", "week_near_me"),
                           (("2024_now", "2024-01-01", "2026-12-31"),))
    _wres = [r for r in _wd if r["face"] == "week_near_me@x1"
             and r["column"] == "full_window_gap_bp"][0]
    chk(_wres["unscreened"] == -11.0 and _wres["neutralise"] == 6.0
        and _wres["delta_neutralise"] == 17.0,
        "the weekly residual row keeps the unscreened gap beside the screened one")
    _wera = [r for r in _wd if r["face"] == "era:week@2024_now@x1"]
    chk(_wera and _wera[0]["unscreened"] == -71.0
        and _wera[0]["delta_neutralise"] == 41.0,
        "era-level weekly gaps enter the same table with the same arithmetic")
    _wturn = [r for r in _wd if r["face"] == "week@x1"
              and r["column"] == "turnover_per_year"][0]
    chk(abs(_wturn["delta_neutralise"] - 0.001) < 1e-9,
        "the turnover column is carried so the fee control can be read beside it")
    _wmiss = _week_delta_rows("unscreened", {"unscreened": _kfaces["unscreened"],
                                             "drop": {"calendar_rows": {}}},
                              ("drop",), (1.0,), ("week",), ())
    chk(_wmiss and _wmiss[0]["drop"] is None and _wmiss[0]["delta_drop"] is None,
        "a mode that emitted no cell yields None instead of a zero delta")

    # E80 screened mid-month: the churn table keeps both books and twins
    _eras80 = (("2024_now", "2024-01-01", "2026-12-31"),)
    _mface = {"eras": {"2024_now": {
        "me": {"churn_alpha_bp_mean": 95.6, "negative_churn_share_pct": 42.9},
        "mid": {"churn_alpha_bp_mean": -123.7, "negative_churn_share_pct": 48.1},
        "gap_x0_bp": -87.0, "gap_x1_bp": -87.0, "gap_x3_bp": -89.0,
        "churn_alpha_gap_bp": -219.3}},
        "books": {"me": {"arms": {"x1": {"turnover_per_year": 0.594,
                                         "full_window_ann_pct": 5.0,
                                         "eras": {"2024_now": {"ann_return_pct": 4.0}}}}},
                  "mid15": {"arms": {"x1": {"turnover_per_year": 0.591,
                                            "full_window_ann_pct": 4.1,
                                            "eras": {"2024_now": {"ann_return_pct": 3.1}}}}}}}
    _sface = {"eras": {"2024_now": {
        "me": {"churn_alpha_bp_mean": 95.0, "negative_churn_share_pct": 43.0},
        "mid": {"churn_alpha_bp_mean": -100.0, "negative_churn_share_pct": 47.0},
        "gap_x0_bp": 10.0, "gap_x1_bp": 10.0, "gap_x3_bp": 8.0,
        "churn_alpha_gap_bp": -195.0}},
        "books": {"me": {"arms": {"x1": {"turnover_per_year": 0.596,
                                         "full_window_ann_pct": 5.1,
                                         "eras": {"2024_now": {"ann_return_pct": 4.2}}}}},
                  "mid15": {"arms": {"x1": {"turnover_per_year": 0.593,
                                            "full_window_ann_pct": 4.3,
                                            "eras": {"2024_now": {"ann_return_pct": 3.4}}}}}}}
    _mrows = _mid_delta_rows("unscreened", {"unscreened": _mface, "neutralise": _sface},
                             ("neutralise",), _eras80, (1.0,))
    _mgap = [r for r in _mrows if r["face"] == "gap:2024_now@x1"
             and r["column"] == "gap_bp"][0]
    chk(_mgap["unscreened"] == -87.0 and _mgap["neutralise"] == 10.0
        and _mgap["delta_neutralise"] == 97.0,
        "the mid-month gap row keeps the unscreened twin beside the screened one")
    _mchurn = [r for r in _mrows if r["face"] == "churngap:2024_now"
               and r["column"] == "churn_alpha_gap_bp"][0]
    chk(_mchurn["unscreened"] == -219.3 and _mchurn["delta_neutralise"] == 24.3,
        "the churn-alpha gap enters the same table with the same arithmetic")
    _mturn = [r for r in _mrows if r["face"] == "mid@x1"
              and r["column"] == "turnover_per_year"][0]
    chk(abs(_mturn["delta_neutralise"] - 0.002) < 1e-9,
        "the turnover control is carried so the fee channel can be read beside it")
    _mneg = [r for r in _mrows if r["face"] == "negchurn:mid@2024_now"][0]
    chk(_mneg["unscreened"] == 48.1 and _mneg["delta_neutralise"] == -1.1,
        "the negative-swap share travels with its own twin")
    _mmiss = _mid_delta_rows("unscreened", {"unscreened": _mface, "drop": {}},
                             ("drop",), _eras80, (1.0,))
    chk(all(r["drop"] is None and r["delta_drop"] is None for r in _mmiss),
        "a mode that emitted no cell yields None instead of a zero delta")
    chk(_dig(_mface, "eras", "2024_now", "me") is not None
        and _dig(_mface, "eras", "1999_missing", "me") is None,
        "_dig returns None the moment the path breaks")
    chk(_mid_flip_eras({"unscreened": _mface, "neutralise": _sface}, ("neutralise",),
                       _eras80, lambda f, e: _dig(f, "eras", e, "gap_x1_bp")) == ["2024_now"],
        "an era whose gap changes sign under the screen is named")
    chk(_mid_flip_eras({"unscreened": _mface, "neutralise": _mface}, ("neutralise",),
                       _eras80, lambda f, e: _dig(f, "eras", e, "gap_x1_bp")) == [],
        "a screen that leaves the gap alone flips nothing")

    # E82: the churn-gap join has to separate a repair effect from a composition one
    _ed = {"a": ["2020-02-03"], "b": ["2020-04-01"]}
    _h = _transition_hits("2020-01-31", "2020-02-28", ["a", "c"], _ed)
    chk(len(_h) == 1 and _h[0]["name"] == "a",
        "an event inside the priced window is a hit")
    chk(_transition_hits("2020-02-03", "2020-02-28", ["a"], _ed) == [],
        "an event on the decision day itself belongs to the previous window")
    chk(_transition_hits("2020-03-31", "2020-04-30", ["b"], _ed)[0]["name"] == "b",
        "a later event lands in its own window")
    _brows = [{"date": "2020-01-31", "next": "2020-02-28", "era": "x",
               "entrant_names": ["a"], "exit_names": ["z"], "churn_alpha_bp": 100.0},
              {"date": "2020-02-28", "next": "2020-03-31", "era": "x",
               "entrant_names": ["c"], "exit_names": ["z"], "churn_alpha_bp": 100.0}]
    _mrows82 = [{"date": "2020-01-31", "churn_alpha_bp": -10.0},
                {"date": "2020-02-28", "churn_alpha_bp": 100.0}]
    _jrows, _jagg = _churn_join(_brows, _mrows82, _ed, (("x", "2020-01", "2020-03"),))
    chk([r["hit"] for r in _jrows] == [True, False],
        "only the transition holding the event is tagged")
    chk(_jrows[0]["delta_bp"] == -110.0 and _jrows[1]["delta_bp"] == 0.0,
        "the delta is measured transition-by-transition against its own twin")
    chk(_jagg["x"]["transitions"] == 2 and _jagg["x"]["hit_transitions"] == 1
        and _jagg["x"]["delta_mean_hit_bp"] == -110.0
        and _jagg["x"]["delta_mean_clean_bp"] == 0.0,
        "hit and clean columns are averaged separately")
    chk(_jagg["x"]["hit_share_of_delta_pct"] == 100.0,
        "all of the movement can be attributed to the repaired transitions")
    _jrows2, _jagg2 = _churn_join(_brows, [{"date": "2020-01-31", "churn_alpha_bp": 100.0},
                                          {"date": "2020-02-28", "churn_alpha_bp": 100.0}],
                                  _ed, (("x", "2020-01", "2020-03"),))
    chk(_jagg2["x"]["delta_mean_all_bp"] == 0.0
        and _jagg2["x"]["hit_share_of_delta_pct"] is None,
        "a flat join yields no attribution instead of a zero share")
    chk(_churn_join(_brows, [], _ed, (("x", "2020-01", "2020-03"),))[1] == {},
        "a mode with no rows produces no era cells")

    # E83: a cell is one swap wide when one removal halves its magnitude
    _eras83 = (("x", "2020-01", "2020-12"),)
    _crow = lambda d, a: {"date": d, "next": d, "era": "x", "churn_alpha_bp": a,
                          "entrant_names": ["a"], "exit_names": ["z"]}
    _one_wide = [ _crow("2020-01-31", 1000.0), _crow("2020-02-28", 100.0),
                  _crow("2020-03-31", 90.0), _crow("2020-04-30", 110.0) ]
    _c83 = _single_print_cell(_one_wide, _eras83)["x"]
    chk(_c83["mean_bp"] == 325.0
        and _c83["most_influential_removal"]["removed_alpha_bp"] == 1000.0
        and _c83["most_influential_removal"]["single_print"] is True,
        "a cell whose mean sits on one transition is flagged single print")
    _flat = [ _crow("2020-01-31", 100.0), _crow("2020-02-28", 100.0),
              _crow("2020-03-31", 100.0), _crow("2020-04-30", 100.0) ]
    _c83b = _single_print_cell(_flat, _eras83)["x"]
    chk(_c83b["most_influential_removal"]["magnitude_remaining_pct"] == 100.0
        and _c83b["most_influential_removal"]["single_print"] is False,
        "a flat cell loses nothing to the removal and is not flagged")
    _c83c = _single_print_cell([_crow("2020-01-31", 100.0)], _eras83)["x"]
    chk(_c83c["single_swap_removable"] is False
        and "most_influential_removal" not in _c83c,
        "a one-transition cell is not removable and says so")
    _crown = [{"date": "2020-01-31", "next": "2020-02-28", "era": "x",
               "churn_alpha_bp": 300.0, "entrant_names": ["p"], "exit_names": ["z"]},
              {"date": "2020-02-28", "next": "2020-03-31", "era": "x",
               "churn_alpha_bp": 10.0, "entrant_names": ["q"], "exit_names": ["z"]},
              {"date": "2020-03-31", "next": "2020-04-30", "era": "x",
               "churn_alpha_bp": 10.0, "entrant_names": ["r"], "exit_names": ["z"]}]
    _c83d = _single_print_cell(_crown, _eras83, {"p": ["2020-02-10"]})["x"]
    chk(_c83d["most_influential_removal"]["removed_carries_a_print"] is True,
        "the removed transition is tagged when its swapped name carries a print")
    chk(_single_print_cell(_crown, _eras83, {"q": ["2020-02-10"]})["x"]
        ["most_influential_removal"]["removed_carries_a_print"] is False,
        "a print on an unremoved transition does not leak into the flag")
    chk(_single_print_cell([], _eras83) == {},
        "no rows means no cell")
    _grow = lambda d, a: {"date": d, "next": d, "era": "x", "churn_alpha_bp": a,
                          "entrant_names": ["m"], "exit_names": ["z"]}
    _g_me = [_grow("2020-01-31", 0.0), _grow("2020-02-28", 0.0),
             _grow("2020-03-31", 0.0), _grow("2020-04-30", 0.0)]
    _g_mid = [_grow("2020-02-10", 100.0), _grow("2020-03-10", 100.0),
              _grow("2020-04-10", 100.0), _grow("2020-05-10", -1900.0)]
    _g83 = _single_print_gap(_g_me, _g_mid, _eras83)["x"]
    chk(_g83["gap_bp"] == -400.0
        and _g83["most_influential_removal"]["gap_without_bp"] == 100.0
        and _g83["most_influential_removal"]["single_print"] is True,
        "a gap owned by one transition on one side is flagged with the surviving gap")
    chk(_g83["most_influential_removal"]["removed_side"] == "mid"
        and _g83["most_influential_removal"]["removed_window"][0] == "2020-05-10",
        "the gap screen names WHICH book the owning transition came from")
    _g83b = _single_print_gap(_g_me, _g_me, _eras83)["x"]
    chk(_g83b["gap_bp"] == 0.0 and _g83b["most_influential_removal"]["single_print"] is False,
        "a zero gap is never a single print, whatever the removal does")
    chk("most_influential_removal" not in _single_print_gap(
        _g_me[:1], _g_me[:1], _eras83)["x"],
        "two single-transition books have nothing removable")
    chk(_single_print_gap(_g_me, [], _eras83) == {},
        "a book with no rows in the era yields no gap cell")

    # E84: two screen modes are only duplicates if the universes agree
    _rep = lambda mode, names: {"mode": mode, "events_neutralised": len(names),
                                "names": names}
    _ru = {"neutralise_int": _rep("neutralise_int",
                                  [{"name": "a", "action": "neutralise", "events": 1,
                                    "prints": [{"date": "2020-02-10", "return_pct": -50.0,
                                                "ratio": 2.0, "resid_pct": 0.0}]}]),
           "neutralise": _rep("neutralise",
                              [{"name": "a", "action": "neutralise", "events": 1,
                                "prints": [{"date": "2020-02-10", "return_pct": -50.0,
                                            "ratio": 2.0, "resid_pct": 0.0}]},
                               {"name": "b", "action": "neutralise", "events": 1,
                                "prints": [{"date": "2020-03-02", "return_pct": -41.0,
                                            "ratio": 1.69, "resid_pct": 15.0}]}])}
    _md = _mode_universe_diff(_ru)
    chk(_md["names_touched"] == {"neutralise_int": 1, "neutralise": 2}
        and _md["names_only_in_neutralise"] == 1
        and _md["extra_names"] == ["b"],
        "the conservative arm is a strict subset and the extra name is named")
    _r1 = [{"date": "2020-01-31", "churn_alpha_bp": 100.0},
           {"date": "2020-02-28", "churn_alpha_bp": None}]
    _r2 = [{"date": "2020-01-31", "churn_alpha_bp": 100.0},
           {"date": "2020-02-28", "churn_alpha_bp": None}]
    chk(_mode_row_diff(_r1, _r2)["bit_identical"] is True,
        "matching rows including matching Nones are bit identical")
    chk(_mode_row_diff(_r1, [_r2[0], {"date": "2020-02-28", "churn_alpha_bp": 0.0}])
        ["transitions_differing"] == 1,
        "a None versus a zero is a real difference, not a gap")
    chk(_mode_row_diff(_r1, _r1[:1])["date_set_mismatch"] == 1,
        "a missing transition is reported as a date-set mismatch")
    _rel = _extra_name_relevance([_crown], ["q"], {"q": ["2020-03-15"]})
    chk(_rel["extra_names_ever_swapped"] == 1
        and _rel["windows_where_an_extra_name_carried_a_print"] == 1,
        "an extra name that was swapped inside a print window is counted")
    chk(_extra_name_relevance([_crown], ["zz"], {})["windows_swapping_an_extra_name"] == 0,
        "a name the book never swaps contributes nothing")

    # E85 robust estimators: a pure mean cell must show its tail, not hide it
    _flat = _robust_stats([5.0] * 20)
    chk(_flat["mean_bp"] == 5.0 and _flat["median_bp"] == 5.0
        and _flat["trim10_bp"] == 5.0 and _flat["trim_dropped"] == 4,
        "a constant cell reads identical under mean/median/trim and drops 2 per tail")
    _tail = _robust_stats([1.0] * 18 + [-100.0, 1000.0])
    chk(_tail["mean_bp"] == 45.9 and _tail["median_bp"] == 1.0,
        "one huge positive and one huge negative leave the mean near the outlier "
        "scale while the median stays on the body")
    chk(abs(_tail["median_keep_pct_of_mean"] - 2.2) < 0.05,
        "the keep-percentage is the ratio of the two, not a re-rounding of bp")
    chk(_robust_stats([-3.0, -1.0, -2.0])["median_bp"] == -2.0,
        "median of an even-length negative cell averages the two middles")
    chk(_robust_stats([])["n"] == 0 and _robust_stats([None, "x"])["mean_bp"] is None,
        "an empty or non-numeric cell reports n=0 rather than a fabricated zero")
    _conc = _concentration([1.0, 1.0, 1.0, 1.0, 96.0], 3)
    chk(_conc["top_sum_bp"] == 98.0 and abs(_conc["top_share_of_total_pct"] - 98.0) < 0.05,
        "the top-3 share of a single-outlier cell is printed as a percentage")
    chk(_concentration([5.0, -5.0], 3)["top_share_of_total_pct"] is None,
        "a cell whose signed total is zero reports no share instead of dividing by zero")

    # E86 leave-one-out distribution: all n removals, not one argmin
    _loo = _loo_means([10.0, 20.0, 30.0])
    chk(len(_loo) == 3, "a cell of n transitions has exactly n leave-one-out means")
    chk(abs(_loo[0] - 25.0) < 1e-12 and abs(_loo[2] - 15.0) < 1e-12,
        "removing a low value raises the mean and vice versa")
    chk(abs(sum(_loo) / 3.0 - 20.0) < 1e-12,
        "the LOO means average back to the cell mean (each value is dropped once)")
    chk(_loo_means([4.0]) == [], "a single-transition cell has no removal to price")
    _st = _loo_stats([10.0, 20.0, 30.0])
    chk(_st["loo_kills_half_count"] == 0 and _st["loo_flips_sign_count"] == 0,
        "a tight positive cell survives every single removal")
    _st1 = _loo_stats([100.0, 1.0, 1.0])
    chk(_st1["loo_kills_half_count"] == 1 and _st1["loo_kills_half_pct"] == 33.3,
        "in a one-outlier cell exactly one removal (the outlier) halves the mean")
    _bd = _breakdown_k([100.0, 1.0, 1.0])
    chk(_bd["k"] == 1 and _bd["mean_after_bp"] == 1.0,
        "breakdown k is the greedy removal count and the rest mean")
    _bd3 = _breakdown_k([10.0, 10.0, -10.0, -10.0])
    chk(_bd3["k"] is None,
        "a cell whose mean is already 0 never falls under half of 0 -- honest None")
    chk(_breakdown_k([7.0])["k"] is None,
        "a one-transition cell has no breakdown count")
    _bdp = _breakdown_k([50.0, 4.0, 3.0, 2.0, 1.0])
    chk(_bdp["k"] == 1 and _bdp["path_bp"][0] == 2.5,
        "the greedy path prints the mean after each removal, not just the endpoint")

    # E89 sampling intervals: an added band, never a revised mean
    _jkf = _jackknife_mean([5.0] * 20)
    chk(_jkf["mean_bp"] == 5.0 and _jkf["jk_se_bp"] == 0.0
        and _jkf["jk_lo90_bp"] == 5.0 and _jkf["jk_hi90_bp"] == 5.0,
        "a constant cell carries zero sampling noise and a degenerate band")
    _jk = _jackknife_mean([10.0, 20.0, 30.0])
    chk(abs(_jk["jk_se_bp"] - 5.7735) < 0.005,
        "jackknife SE of the mean is sqrt(sum sq dev / (n*(n-1)))")
    chk(abs(_jk["jk_se_bp"] - round(_sd([10.0, 20.0, 30.0]) / (3 ** 0.5), 2)) < 1e-9,
        "the closed form equals sd/sqrt(n) -- the textbook standard error")
    chk(_jackknife_mean([4.0])["jk_available"] is False
        and _jackknife_mean([4.0])["mean_bp"] == 4.0,
        "a one-transition cell keeps its point estimate but reports no interval")
    _b1 = _boot_mean_ci([10.0, 20.0, 30.0], draws=200, seed=7)
    _b2 = _boot_mean_ci([10.0, 20.0, 30.0], draws=200, seed=7)
    chk(_b1 == _b2 and _b1["draws"] == 200 and _b1["seed"] == 7,
        "the bootstrap face is bit-reproducible from its recorded seed")
    chk(_b1["boot_p05_bp"] <= 20.0 <= _b1["boot_p95_bp"],
        "a tight positive cell keeps its point estimate inside the band")
    _bz = _boot_mean_ci([-40.0, 30.0, 10.0, 0.0], draws=200, seed=7)
    chk(_bz["boot_ci_straddles_zero"] is True,
        "a sign-mixed cell has a band that crosses zero")
    chk(_boot_mean_ci([-100.0] * 12 + [100.0] * 12,
                      draws=200, seed=7)["boot_signflip_pct"] == 100.0,
        "a cell whose mean is exactly zero reports every resample as a sign flip")
    _g0 = _gap_interval([10.0, 20.0, 30.0], [10.0, 20.0, 30.0], draws=200, seed=7)
    chk(_g0["gap_bp"] == 0.0 and _g0["jk_se_bp"] > 0
        and _g0["interval_clears_zero"] is False,
        "two samples of the same cell give a zero gap whose band still crosses "
        "zero -- the difference of two draws is not itself exactly zero")
    _g1 = _gap_interval([1.0, 2.0, 3.0], [101.0, 102.0, 103.0], draws=200, seed=7)
    chk(abs(_g1["gap_bp"] - 100.0) < 1e-9 and _g1["interval_clears_zero"] is True,
        "a gap equal to a pure level shift clears zero")
    chk(_gap_interval([4.0], [1.0, 2.0], draws=50, seed=7)["gap_available"] is False,
        "a gap needs two transitions on each side")

    # E91 top-transition names: a share becomes auditable by date and ticker
    _tr = [{"date": "2021-05-17", "next": "2021-06-15", "era": "2021_2023",
            "churn_alpha_bp": -900.0, "entrants": 3, "exits": 4,
            "entrant_fwd_pct": -8.0, "exit_fwd_pct": 1.0,
            "entrant_names": ["sz159925"], "exit_names": ["sh510300"]},
           {"date": "2021-06-15", "next": "2021-07-15", "era": "2021_2023",
            "churn_alpha_bp": 60.0, "entrants": 2, "exits": 2,
            "entrant_fwd_pct": 2.0, "exit_fwd_pct": 1.4,
            "entrant_names": ["sh512100"], "exit_names": ["sh510500"]},
           {"date": "2021-07-15", "next": "2021-08-16", "era": "2021_2023",
            "churn_alpha_bp": -40.0, "entrants": 1, "exits": 1,
            "entrant_fwd_pct": 0.5, "exit_fwd_pct": 0.9,
            "entrant_names": ["sh512880"], "exit_names": ["sh511010"]}]
    _top = _top_transitions(_tr, 3)
    chk(len(_top) == 3 and _top[0]["churn_alpha_bp"] == -900.0,
        "the top transition is the largest magnitude, printed first")
    chk(_top[0]["date"] == "2021-05-17" and _top[0]["next"] == "2021-06-15",
        "each top transition carries its decision window, not a bare share")
    chk(_top[0]["entrant_names"] == ["sz159925"], "the swapped names ride with the row")
    chk(_top[0]["carried_by"] == "exits",
        "the sign is attributed to the weaker side (exits beat entrants here)")
    chk(_top[1]["carried_by"] == "entrants", "a rising window is carried by entrants")
    chk(abs(_top[0]["share_of_signed_total_pct"] - 102.3) < 0.2,
        "the share is computed against the cell signed total, so it can exceed 100%")
    chk(_top_transitions([{"churn_alpha_bp": None}], 3) == [],
        "a cell with no numeric alpha publishes no names instead of a fake row")
    chk(_top_transitions([], 3) == [], "an empty cell has no top transitions")

    # (E92) the gap census counts only integer-ratio gapped prints inside the limit
    _gcal = ["2021-05-27", "2021-05-28", "2021-05-31", "2021-06-01",
             "2021-06-02", "2021-06-03", "2021-06-04", "2021-06-05",
             "2021-06-07"]
    _graw = {
        "sh510150": ({"2021-05-27": 10.414, "2021-05-31": 0.8678}, {}),  # 12:1, gap 1
        "sh510300": ({"2021-06-01": 10.0, "2021-06-02": 3.0}, {}),       # 3.33, adj
        "sh510500": ({"2021-06-02": 10.0, "2021-06-07": 1.0}, {}),       # 10:1, gap 3
        "sh512880": ({"2021-06-03": 10.0, "2021-06-05": 3.0}, {}),       # 3.33, gap 1
    }
    _gc = _gap_print_census(_graw, _gcal, limits=(1, 2, 5))
    _c1, _c2, _c5 = (_gc["by_gap_limit"]["gap%d" % n] for n in (1, 2, 5))
    chk(_gc["gapped_prints"] == 3,
        "only gapped prints enter the census (the adjacent one is screened already)")
    chk(_c1["eligible_integer_prints"] == 1 and _c1["eligible_names"] == 1,
        "gap_limit=1 catches the 12:1 split one missing bar away")
    chk(_c2["eligible_integer_prints"] == 1,
        "gap_limit=2 adds nothing when the only other gapped print is 3 sessions out")
    chk(_c5["eligible_integer_prints"] == 2,
        "gap_limit=5 reaches the 10:1 print across a longer suspension")
    chk(_c1["non_integer_gapped"] == 1 and _c5["non_integer_gapped"] == 1,
        "the non-integer gapped print is counted as left alone, never repaired")
    chk(_c1["eligible_by_era"] == {"2021_2023": 1},
        "eligibility is tagged with the era of the print date")

    # (E93) era-spread gap-arm table: every row keeps both twins and the
    # gap-arm deltas are computed against each of them independently.
    _faces = {
        "unscreened": {"eras": {"A": {"spread_ann_bp": 100.0},
                                "B": {"spread_ann_bp": -50.0},
                                "C": {"bars": 12}}},
        "neutralise": {"eras": {"A": {"spread_ann_bp": 90.0},
                                "B": {"spread_ann_bp": -40.0},
                                "C": {"spread_ann_bp": 10.0}}},
        "neutralise_gap@1": {"eras": {"A": {"spread_ann_bp": 95.0},
                                      "B": {"spread_ann_bp": 5.0},
                                      "C": {"spread_ann_bp": None}}},
        "neutralise_gap@5": {"eras": {"A": {"spread_ann_bp": 99.0},
                                      "B": {"spread_ann_bp": -48.0},
                                      "C": {"spread_ann_bp": None}}},
    }
    _rows = _screengapera_rows(_faces)
    chk(len(_rows) == 2, "spread rows skip eras with no published spread")
    _a = _rows[0]
    chk(_a["delta_vs_unscreened_neutralise_gap@1"] == -5.0,
        "gap arm delta is read against the unscreened twin")
    chk(_a["delta_vs_adjacent_only_neutralise_gap@1"] == 5.0,
        "the same cell's delta against the adjacent-only twin is independent")
    chk(_a["adjacent_only_spread_ann_bp"] == 90.0,
        "the adjacent-only arm is carried on every row, never nested")
    chk(_rows[1]["delta_vs_adjacent_only_neutralise_gap@5"] == -8.0,
        "a sign-carrying delta keeps its sign against the adjacent arm")

    # (E81 screentilt) the tilt delta table must report a zero arm as zero and a
    # repaired arm cell-by-cell, with the beta column carried independently.
    _tf = {"unscreened": {"eras": {"A": {"tilt_annualised_bp": 100.0,
                                         "beta_ladder_on_tilt": 0.500,
                                         "alpha_monthly_bp": 5.0,
                                         "r_squared": 0.250},
                                   "B": {"bars": 12}}},
           "neutralise_int": {"eras": {"A": {"tilt_annualised_bp": 100.0,
                                             "beta_ladder_on_tilt": 0.500,
                                             "alpha_monthly_bp": 5.0,
                                             "r_squared": 0.250}}},
           "neutralise": {"eras": {"A": {"tilt_annualised_bp": 140.0,
                                         "beta_ladder_on_tilt": 0.620,
                                         "alpha_monthly_bp": 5.0,
                                         "r_squared": 0.310}}}}
    _tr = _tiltdelta_rows(_tf)
    chk(len(_tr) == 8, "two eras x four columns: a skipped era still publishes rows")
    chk(all(r["delta_neutralise_int"] in (None, 0) for r in _tr),
        "an arm that repairs nothing publishes a zero delta on every cell")
    chk([r["delta_neutralise"] for r in _tr if r["column"] == "tilt_annualised_bp"
         and r["era"] == "A"] == [40.0],
        "the repaired arm moves the tilt level by the measured amount")
    chk([r["delta_neutralise"] for r in _tr if r["column"] == "beta_ladder_on_tilt"
         and r["era"] == "A"] == [0.12],
        "the beta column is carried on its own row, not folded into the tilt row")
    chk(all(r["delta_neutralise"] is None for r in _tr if r["era"] == "B"),
        "a skipped era has no delta instead of a fabricated one")

    # E81 calcost screen twin: an identical arm moves nothing, a shifted arm does.
    # The activity leg is mandatory -- two identical arms would otherwise pass as
    # "the screen changes nothing" without the delta table ever being read.
    def _calcost_arm(spread, ladder_ann):
        return {"calendars": {"cost_x1": {"me": {
            "rebalances": 12,
            "ladder5": {"ann_return_pct": ladder_ann, "max_drawdown_pct": -10.0,
                        "turnover_per_year": 0.5, "cost_per_year_bp": 13.0},
            "wide_top9999": {"ann_return_pct": 9.0, "max_drawdown_pct": -12.0,
                             "turnover_per_year": 0.6, "cost_per_year_bp": 15.0},
            "vs_ladder_spread_bp": spread}}}}

    _cf = {"unscreened": _calcost_arm(100.0, 8.0),
           "neutralise_int": _calcost_arm(100.0, 8.0),
           "neutralise": _calcost_arm(90.0, 8.5)}
    _cr = _calcost_delta_rows(_cf)
    chk(len(_cr) == 9, "nine cells: one spread plus four columns on two schemes")
    chk(all(r["delta_neutralise_int"] in (None, 0) for r in _cr),
        "an arm that repairs nothing publishes a zero delta on every cell")
    chk(any(r["delta_neutralise"] for r in _cr) and
        [r["delta_neutralise"] for r in _cr if r["column"] == "vs_ladder_spread_bp"] == [-10.0],
        "a repaired arm does move the spread cell, so the zero row is a real read")
    chk([r["delta_neutralise"] for r in _cr
         if r["column"] == "ann_return_pct" and r["scheme"] == "ladder5"] == [0.5],
        "per-scheme columns are compared within the same scheme, not across")

    # E81 leg 2 (spread face): the same three properties -- identical arm moves
    # nothing, a shifted arm moves the right cell, and the skip cell stays None
    # rather than being priced as zero.
    def _spread_face(neutral):
        def row(v):
            return {c: v for c in SPREAD_COLUMNS}
        return {"eras": {"2021_2023": row(neutral), "2024_now": row(None),
                         "full": row(neutral)}}

    _sf = {"unscreened": _spread_face(300.0),
           "neutralise_int": _spread_face(300.0),
           "neutralise": _spread_face(420.0)}
    _sr = _spread_delta_rows("unscreened", _sf,
                             ("neutralise_int", "neutralise"),
                             (("2021_2023", "2021-01-01", "2023-12-31"),
                              ("2024_now", "2024-01-01", None)))
    chk(len(_sr) == 15, "fifteen cells: five columns on three eras")
    _sn = [r for r in _sr if r["column"] == "size_neutral_ann_bp"]
    chk(all(r["delta_neutralise_int"] in (None, 0) for r in _sn),
        "a screen arm that repairs nothing publishes a zero delta on the spread face")
    chk([r["delta_neutralise"] for r in _sn
         if r["era"] == "2021_2023"] == [120.0],
        "a repaired arm moves the size-neutral cell by its own amount")
    chk([r["delta_neutralise"] for r in _sn if r["era"] == "2024_now"] == [None],
        "an era with no data stays None on both sides, never priced as zero")
    chk([r["delta_neutralise_int"] for r in _sn if r["era"] == "2021_2023"] == [0.0]
        and [r["delta_neutralise"] for r in _sn if r["era"] == "2021_2023"] == [120.0],
        "each arm keeps its own delta column, so a later arm cannot overwrite an earlier one")
    chk(all(r["delta_neutralise_int"] in (None, 0) for r in _sr),
        "the zero arm stays zero on every column, not just the one being read")

    # E81 leg 3 (robustness face): the cell grid needs the same three properties
    # -- a repairing arm that moves nothing stays zero, each arm keeps its own
    # delta column, and an unmeasured cell stays None on both sides.
    def _rob_face(neutral):
        def cell(v):
            return {"era": {"2021_2023": {c: v for c in SPREAD_COLUMNS},
                            "2024_now": {c: None for c in SPREAD_COLUMNS}}}
        return {"cells": {"cost_x1|me": cell(neutral), "cost_x3|mid15": cell(neutral)}}

    _rf = {"unscreened": _rob_face(200.0),
           "neutralise_int": _rob_face(200.0),
           "neutralise": _rob_face(260.0)}
    _rr = _robdelta_rows("unscreened", _rf, ("neutralise_int", "neutralise"),
                         (("2021_2023", "2021-01-01", "2023-12-31"),
                          ("2024_now", "2024-01-01", None)))
    chk(len(_rr) == 30, "thirty cells: five columns on two eras on two cells")
    _rn = [r for r in _rr if r["column"] == "size_neutral_ann_bp"]
    chk(all(r["delta_neutralise_int"] in (None, 0) for r in _rn),
        "the non-repairing arm publishes a zero delta on every robustness cell")
    chk([r["delta_neutralise"] for r in _rn if r["era"] == "2021_2023"] == [60.0, 60.0],
        "the repairing arm moves both calendar x fee cells by its own amount")
    chk([r["delta_neutralise_int"] for r in _rn if r["era"] == "2021_2023"] == [0.0, 0.0],
        "each arm keeps its own delta column on the robustness face too")
    chk([r["delta_neutralise"] for r in _rn if r["era"] == "2024_now"] == [None, None],
        "an unmeasured robustness cell stays None rather than being priced as zero")

    # E95 leg: the newest-era cell must be measurable on an explicit month list
    # (so the stability grid and the published face agree by construction), the
    # grid must actually shorten the window, and the verdict must be a pure
    # function of the two spreads it compares.
    _fake = {"tilt": {"2024-%02d" % m: 0.01 * m for m in range(1, 13)},
             "lad_m": {"2024-%02d" % m: 0.005 * m for m in range(1, 13)}}
    _full = _tilt_stats(_fake, sorted(_fake["tilt"]))
    chk(_full["months"] == 12
        and _full["tilt_annualised_bp"] == round(0.065 * 12 * 1e4, 1),
        "the tilt cell is the same arithmetic on an explicit month list")
    _half = _tilt_stats(_fake, sorted(_fake["tilt"])[:6])
    chk(_half["months"] == 6 and _half["to"] == "2024-06"
        and _half["tilt_annualised_bp"] != _full["tilt_annualised_bp"],
        "truncating the window really moves the cell, so the grid is not a no-op")
    chk(_tilt_stats(_fake, ["2024-01", "2024-02"])["skipped"],
        "a window too short to regress is skipped, never priced as a number")
    chk(_stability_verdict(40.0, 50.0) == "inside_end_choice_span"
        and _stability_verdict(60.0, 50.0) == "beyond_end_choice_span"
        and _stability_verdict(None, 50.0) is None,
        "the stability verdict is pure and stays None when either spread is unmeasured")

    # E98: the same grid on every era. Four things have to hold before an era
    # span can be quoted: the reader sees BOTH face schemas (a flat-only reader
    # reports "nothing published" for the whole screened family), an era the
    # panel does not reach is skipped rather than measured on borrowed months,
    # the grid really moves the cell (otherwise "the span is small" is the
    # arithmetic of a no-op), and the span is scaled by the era's own movement.
    import tempfile
    _tmpd = tempfile.mkdtemp(prefix="e98")
    try:
        with open(os.path.join(_tmpd, "TILT-ERA-20260101.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"evidence_cutoff": "2026-01-01",
                       "eras": {"2021_2023": {"months": 36,
                                              "tilt_annualised_bp": 100.0}}}, fh)
        with open(os.path.join(_tmpd, "TILT-ERA-20260102.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"evidence_cutoff": "2026-01-02",
                       "faces": {"unscreened": {"eras": {
                           "2021_2023": {"months": 36, "tilt_annualised_bp": 140.0}}},
                           "neutralise_int": {"eras": {
                               "2021_2023": {"months": 36,
                                             "tilt_annualised_bp": 145.0}}}}}, fh)
        _pr = _published_era_readings(_tmpd, "2021_2023")
        _pr_absent = _published_era_readings(_tmpd, "2024_now")
    finally:
        for _n in os.listdir(_tmpd):
            os.remove(os.path.join(_tmpd, _n))
        os.rmdir(_tmpd)
    chk(len(_pr) == 3 and {p["arm"] for p in _pr} == {None, "unscreened",
                                                      "neutralise_int"},
        "both face schemas are read: a flat eras block and one per screening arm")
    chk(_pr_absent == [],
        "an era with no published reading comes back empty, never guessed")

    # hermetic core: 24 months of a tilting ladder, two eras that both reach
    _hc = {"months": ["2021-%02d" % m for m in range(1, 13)]
                    + ["2022-%02d" % m for m in range(1, 13)],
           "tilt": {}, "lad_m": {}, "dropped": {}}
    for _i, _m in enumerate(_hc["months"]):
        _hc["tilt"][_m] = 0.001 * (_i + 1)
        _hc["lad_m"][_m] = 0.002 * (_i + 1)
    _toy_eras = (("A", "2021-01-01", "2021-12-31"), ("B", "2022-01-01", None))
    _rows98 = [_endchoice_era_row(_hc, _e, 6, "") for _e in _toy_eras]
    _a, _b = _rows98
    chk(_a["span_bp"] is not None and _a["span_bp"] > 0,
        "the end grid actually moves the cell -- a zero span would be a no-op sweep")
    chk(_a["months_dropped_max"] == 5 and _a["monthly_sd_bp"],
        "each truncated run states how much of its era it threw away, and the era's "
        "own monthly movement comes with it")
    chk(_endchoice_era_row(_hc, ("C", "2030-01-01", None), 6, "").get("skipped")
        and _endchoice_era_row(_hc, ("C", "2030-01-01", None), 6, "")["span_bp"] is None,
        "an era the panel does not reach is skipped, never measured on borrowed months")

    # E99: the arm must be the key, and every row must carry every arm
    _fake_faces = {
        "unscreened": {"eras": {"E1": {"me": {"churn_alpha_bp_mean": 10.0,
                                              "x1_ann_pct": 1.0}}}},
        "neutralise_gap1": {"eras": {"E1": {"me": {"churn_alpha_bp_mean": 40.0,
                                                    "x1_ann_pct": 2.0}}}},
    }
    _rows = _level_rows(_fake_faces, [("E1", "2020-01", "2020-12"),
                                      ("E2", "2021-01", "2021-12")],
                        ["unscreened", "neutralise_gap1"], books=("me",))
    _r0 = _rows[0]
    chk(_r0["arms"]["unscreened"]["churn_alpha_bp_mean"] == 10.0
        and _r0["arms"]["neutralise_gap1"]["churn_alpha_bp_mean"] == 40.0,
        "two arms on one (era, book) cell keep their own level -- no arm overwrites another")
    chk(_r0["arms"]["neutralise_gap1"]["delta_vs_unscreened_bp"] == 30.0
        and _r0["arms"]["unscreened"]["delta_vs_unscreened_bp"] == 0.0,
        "the screened level carries its distance from the untreated one")
    chk(_rows[1]["arms"]["unscreened"]["churn_alpha_bp_mean"] is None,
        "an era the burn never populated reads null, not a borrowed number")
    chk(_level_coverage(_rows, ["unscreened", "neutralise_gap1"])["missing_arm_keys"] == []
        and _level_coverage(_rows, ["unscreened", "neutralise_gap1"])["cells"] == 4,
        "every (era, book) row carries every arm key, populated or not")
    _flip_faces = [{"era": "E1", "book": "me", "arms": {
        "unscreened": {"churn_alpha_bp_mean": -5.0},
        "neutralise_gap1": {"churn_alpha_bp_mean": 5.0}}}]
    chk(_level_sign_flips(_rows, ["unscreened", "neutralise_gap1"]) == []
        and _level_sign_flips(_flip_faces, ["unscreened", "neutralise_gap1"]) == ["E1/me"],
        "a level that changes sign across arms is reported, a same-sign pair is not")

    # E101: the end grid must truncate, never re-stamp, and the arm delta
    # verdict must be readable off its two spans alone
    _cal = ["2020-%02d-%02d" % (m, d) for m, d in
            ((1, 31), (2, 28), (3, 31), (4, 30), (5, 29))]
    _dec = [(0, ["a"]), (2, ["b"]), (4, ["c"])]
    chk(_truncate_decisions(_dec, _cal, "2020-03-31") == [(0, ["a"]), (2, ["b"])],
        "a grid end drops the decisions after it and keeps the ones inside it")
    chk(_truncate_decisions(_dec, _cal, "2020-03-30") == [(0, ["a"])]
        and _truncate_decisions(_dec, _cal, "2020-03-31") == [(0, ["a"]), (2, ["b"])],
        "the end is read on the session date, not on the decision ordinal")
    _grid = _era_end_grid(_dec, _cal, ("E1", "2020-01-01", "2020-04-30"), 12)
    chk(_grid == ["2020-01-31", "2020-03-31"],
        "the era grid is taken inside its own window and keeps session order")
    chk(_era_end_grid(_dec, _cal, ("E1", "2020-01-01", "2020-04-30"), 1)
        == ["2020-03-31"],
        "a 1-end grid is the last session inside the era, not the first")
    chk(_endgrid_span([1.0, None, 4.0]) == 3.0 and _endgrid_span([2.0]) is None,
        "a span needs two numbers and ignores a null cell")
    chk(_min_span([None, -40.0, 12.0]) == -40.0 and _min_span([None]) is None,
        "the smaller level span is the smaller of the populated ones")
    chk(_arm_delta_verdict(40.0, 800.0) == (0.05, "delta_stable_levels_fragile"),
        "a delta that spans 5% of its levels survives the grid")
    chk(_arm_delta_verdict(515.0, 1184.1)[1] == "delta_moves_with_the_end",
        "a delta that spans 43% of its levels moves with the end")
    chk(_arm_delta_verdict(0.0, 0.0)[1] == "levels_fixed_across_ends"
        and _arm_delta_verdict(30.0, 0.0)[1] == "delta_moves_while_levels_hold",
        "a frozen level pair is named, not divided by zero")
    chk(_arm_delta_verdict(None, 500.0) == (None, None)
        and _arm_delta_verdict(20.0, None) == (None, None),
        "an unmeasured span yields no verdict instead of a default one")

    # E102: a zero-delta series is a step only when exactly one end moves
    _zp = _grid_zero_profile([0.0, 0.0, 0.0, -745.9])
    chk(_zp["zero_ends"] == 3 and _zp["step_signature"],
        "three zero ends and one move read as a one-transition step")
    _zp = _grid_zero_profile([0.0, 12.0, 0.0, -745.9])
    chk(_zp["zero_ends"] == 2 and not _zp["step_signature"],
        "two non-zero ends are a movement, not a step")
    chk(_grid_zero_profile([0.049, 0.0])["zero_ends"] == 2
        and _grid_zero_profile([-0.049])["ends"] == 1,
        "the zero rule is the published 0.05bp precision, on both signs")
    chk(_grid_zero_profile([None, 0.0])["ends"] == 1
        and not _grid_zero_profile([])["step_signature"],
        "a null cell is not an end and an empty grid is not a step")
    _caches = {"unscreened": {"prices": {"a": [1.0, 2.0], "b": [3.0, 4.0]}},
               "repair": {"prices": {"a": [1.0, 2.5], "b": [3.0, 4.0]}}}
    chk(_arm_price_edits(_caches, "repair")["symbols_with_changed_prices"] == 1,
        "an arm that edits one print is one edit, not one fewer name")
    chk(_arm_price_edits(_caches, "unscreened")["symbols_with_changed_prices"] == 0,
        "the base arm edits nothing against itself")

    # E103: a ladder that does not move is not a ladder of measurements
    _lg = _limit_groups({1: "a", 2: "a", 3: "b", 4: "b", 5: "b"})
    chk(_lg["distinct_objects"] == 2 and _lg["growth_limits"] == [1, 3],
        "five limits over two edit faces read as two objects, moving at 1 and 3")
    chk(_lg["saturates_at"] == 3,
        "the saturation point is the first limit of the last face, not the last "
        "limit walked")
    _lg = _limit_groups({1: "a", 2: "b", 3: "c"})
    chk(_lg["distinct_objects"] == 3 and _lg["growth_limits"] == [1, 2, 3],
        "a ladder that moves at every limit keeps every limit as a growth point")
    _lg = _limit_groups({})
    chk(_lg["distinct_objects"] == 0 and _lg["growth_limits"] == []
        and _lg["saturates_at"] is None,
        "an empty ladder names no saturation point instead of defaulting to 0")
    _raw = {"a": ({"2020-01-02": 1.0, "2020-01-03": 2.0}, {}),
            "b": ({"2020-01-02": 5.0, "2020-01-03": 6.0}, {})}
    _univ = {"a": ({"2020-01-02": 1.0, "2020-01-03": 1.0}, {}),
             "b": ({"2020-01-02": 5.0, "2020-01-03": 6.0}, {})}
    chk(_arm_edit_face(_raw, _univ) == ["a|2020-01-03"],
        "an edit face is the changed bars, not the touched names")
    chk(_arm_edit_face(_raw, _raw) == [],
        "an arm identical to the base has an empty edit face")
    _rep = {"names": [{"name": "a", "action": "neutralise",
                       "prints": [{"date": "2020-01-03"}]},
                      {"name": "b", "action": "kept-gapped-only",
                       "prints": [{"date": "2020-01-09"}]}]}
    chk(_print_set(_rep) == [("a", "2020-01-03")],
        "a print is only a repair when the arm repaired it, not when it was left "
        "gapped")

    # E100: an arm delta must split into pieces that ADD UP to it
    _g = {"2020-01-31": {"churn_alpha_bp": 10.0}, "2020-02-28": {"churn_alpha_bp": -30.0}}
    _u = {"2020-01-31": {"churn_alpha_bp": 10.0}, "2020-02-28": {"churn_alpha_bp": 10.0},
          "2020-03-31": {"churn_alpha_bp": -10.0}}
    _pc, _pm = _arm_delta_contrib(_g, _u)
    chk(_pm["level_gap_bp"] == -10.0 and _pm["level_unscreened_bp"] == 3.3,
        "the two arm levels are each their own equal-weight mean")
    chk(abs(_pm["residual_bp"]) < 1e-9,
        "the pieces sum to the delta exactly when both arms keep their own n")
    chk(_pm["common_transitions"] == 2 and _pm["unscreened_only_transitions"] == 1
        and _pm["gap_only_transitions"] == 0,
        "a date that exists in only one arm is counted as one-sided, not dropped")
    _g2 = {"2020-01-31": {"churn_alpha_bp": 10.0}}
    _u2 = {"2020-01-31": {"churn_alpha_bp": 10.0}}
    _pc2, _pm2 = _arm_delta_contrib(_g2, _u2)
    chk(_pm2["delta_bp"] == 0.0 and _pm2["residual_bp"] == 0.0
        and _pc2[0]["contrib_bp"] == 0.0,
        "two arms that agree on every transition produce a zero delta and zero pieces")
    _mk = lambda rows, share, sides=("both",): {"delta_bp": 100.0,
                                               "top_share_of_delta_pct": share,
                                               "top": [{"side": s} for s in sides]}
    chk(_arm_split_verdict(_mk([], 60.0)) == "delta_is_one_window",
        "one window carrying 60% of the delta is one window")
    chk(_arm_split_verdict(_mk([], 30.0)) == "delta_is_a_few_windows",
        "three windows carrying 30% is a few windows, not a broad move")
    chk(_arm_split_verdict(_mk([], 60.0, ("both", "gap_only")))
        == "delta_is_a_transition_that_exists_in_one_arm",
        "a one-sided date among the largest pieces outranks the share test")
    chk(_arm_split_verdict({"delta_bp": None, "top": []}) == "no_delta",
        "an unmeasurable cell reads no_delta instead of broad")

    # E104: an UNCHANGED holding can carry the split that E100's swap lists miss
    _gp = {"A": [1.0, 1.05, 1.10], "B": [1.0, 0.11, 0.11], "C": [1.0, 2.0, 2.0]}
    _up = {"A": [1.0, 1.05, 1.10], "B": [1.0, 1.05, 1.05], "C": [1.0, 1.00, 1.00]}
    _hs = _held_read_split(_gp, _up, {"A", "B", "C"}, {"A", "B", "C"}, 0, 1, top_k=2)
    chk(_hs["persistent_names"] == 3,
        "only names held at BOTH ends of the window are read")
    chk(abs(_hs["residual_bp"]) < 1e-9,
        "the per-name pieces add up to the window delta exactly")
    chk(_hs["top"][0]["name"] in ("B", "C"),
        "the biggest contributor is a name whose read differs between the arms")
    _hs2 = _held_read_split(_gp, _gp, {"A", "B"}, {"A", "B"}, 0, 1)
    chk(_hs2["delta_bp"] == 0.0 and not _hs2["top"][0]["read_gap_pct"],
        "two arms reading the same prices produce a zero split, not a tiny one")
    _hs3 = _held_read_split(_gp, _up, {"A", "B"}, {"C"}, 0, 1)
    chk(_hs3["persistent_names"] == 0 and _hs3["delta_bp"] is None,
        "a window that swaps everything has no unchanged holding to read")
    # E105: a level is a mean, so the largest single-name read must travel with it
    _hs4 = _held_read_split({"A": [1.0, 1.10], "B": [1.0, 1.00]},
                            {"A": [1.0, 1.10], "B": [1.0, 1.00]}, {"A", "B"},
                            {"A", "B"}, 0, 1)
    chk(_hs4["max_abs_read"]["share_of_window_mean_pct"] == 200.0,
        "a single name reading twice the window mean is published as 200% of it")
    _hs5 = _held_read_split({"A": [1.0, 1.10], "B": [1.0, 9.0]},
                            {"A": [1.0, 1.10], "B": [1.0, 9.0]}, {"A", "B"},
                            {"A", "B"}, 0, 1)
    chk(_hs5["max_abs_read"]["share_of_window_mean_pct"] is not None
        and _hs5["max_abs_read"]["share_eligible"] is True,
        "a big read against a big mean still prints its share")
    _hs6 = _held_read_split({"A": [1.0, 1.006], "B": [1.0, 1.007]},
                            {"A": [1.0, 1.006], "B": [1.0, 1.007]}, {"A", "B"},
                            {"A", "B"}, 0, 1)
    chk(_hs6["max_abs_read"]["share_of_window_mean_pct"] is not None
        and _hs6["max_abs_read"]["share_of_window_mean_pct"] <= 300.0,
        "a flat window's share stays a share, not a four-digit ratio")
    _hs7 = _held_read_split({"A": [1.0, 1.002], "B": [1.0, 0.998]},
                            {"A": [1.0, 1.002], "B": [1.0, 0.998]}, {"A", "B"},
                            {"A", "B"}, 0, 1)
    chk(_hs7["max_abs_read"]["share_eligible"] is False
        and _hs7["max_abs_read"]["share_of_window_mean_pct"] is None,
        "a mean inside the floor publishes no share and says why")
    chk(_held_split_verdict({"persistent_reads": 0}) == "no_unchanged_holdings",
        "a cell with no persistent reads says so instead of reading as no split")
    chk(_held_split_verdict({"persistent_reads": 5, "delta_mean_bp": 0.0})
        == "no_split_inside_unchanged_holdings",
        "zero delta on a measured cell is a finding, not a missing measurement")
    # E104b: the repair is not automatically the plausible side of a print
    _hs8 = _held_read_split({"A": [1.0, 3.0]}, {"A": [1.0, 1.2]}, {"A"}, {"A"}, 0, 1)
    chk(_hs8["reads_beyond_100pct"]["gap"] == 1
        and _hs8["reads_beyond_100pct"]["unscreened"] == 0,
        "a repaired read past +100% is counted against the repaired arm alone")
    _hrow = {"persistent_reads": 5, "delta_mean_bp": 7.0,
             "windows": [{"delta_bp": -7.0}, {"delta_bp": 0.0}, {"delta_bp": 0.0}]}
    chk(_held_split_verdict(_hrow) == "delta_is_one_window"
        and _hrow["top_share_of_delta_pct"] == 100.0,
        "one window carrying the whole split reads as one window")

    # E111: a face's producing code is part of its identity, not a footnote
    _g1 = _repair_factor_guard([("a", {"repair_factor": "abc123456789"}),
                                ("b", {"repair_factor": "abc123456789"})])
    chk(_g1["verdict"] == "uniform", "two faces stamped by one factor are comparable")
    _g2 = _repair_factor_guard([("a", {"repair_factor": "abc123456789"}), ("b", {})])
    chk(_g2["verdict"] == "version_unknown" and _g2["unstamped"] == ["b"],
        "an unstamped face reads as UNKNOWN, never as agreeing")
    _g3 = _repair_factor_guard([("a", {"repair_factor": "aaaaaaaaaaaa"}),
                                ("b", {"repair_factor": "bbbbbbbbbbbb"})])
    chk(_g3["verdict"] == "mixed_repair_factors",
        "two code versions are two experiments, published as mixed rather than MISMATCH")
    _g4 = _repair_factor_guard([("a", None), ("b", {"repair_factor": "aaaaaaaaaaaa"})])
    chk(_g4["verdict"] == "version_unknown" and _g4["unstamped"] == ["a"],
        "a missing face is unstamped, so the join is refused before anything is read")

    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


# -------------------------------------------------------------- E88

def _cell_index(rows, keys):
    out = {}
    for r in rows or []:
        k = tuple(r.get(x) for x in keys)
        if k not in out:
            out[k] = r
    return out


def _mean_control(a_rows, b_rows, keys):
    """Join two faces cell by cell and count bit-identical ``mean_bp``.

    A face built by a different leg is comparable only when its means were
    read off the same per-transition rows; anything else is a re-derived burn
    and would reintroduce the r1135/r1142 two-burn pit.
    """
    ia, ib = _cell_index(a_rows, keys), _cell_index(b_rows, keys)
    shared = [k for k in ia if k in ib]
    bad = [{"keys": list(k), "a": ia[k].get("mean_bp"),
            "b": ib[k].get("mean_bp")}
           for k in shared if ia[k].get("mean_bp") != ib[k].get("mean_bp")]
    return {"shared_cells": len(shared), "matched": len(shared) - len(bad),
            "mismatched": len(bad),
            "only_in_a": len([k for k in ia if k not in ib]),
            "only_in_b": len([k for k in ib if k not in ia]),
            "mismatch_rows": bad}


def _repair_factor_guard(labeled):
    """(E111) -> verdict over the repair-factor stamps of the faces being joined.

    ``labeled`` is ``[(name, face)]``. A face with no stamp is UNKNOWN, never
    equal: the honest reading of a pre-stamp face is that its producing code is
    not recorded, so a join against it can neither agree nor disagree. Faces
    stamped with different ids are two different experiments; the difference
    between them is a version, not a defect.
    """
    tags = {n: ((f or {}).get(REPAIR_FACTOR_KEY) or None) for n, f in labeled}
    missing = sorted(n for n, t in tags.items() if not t)
    distinct = sorted({t for t in tags.values() if t})
    if missing:
        verdict = "version_unknown"
    elif len(distinct) > 1:
        verdict = "mixed_repair_factors"
    else:
        verdict = "uniform"
    return {
        "verdict": verdict, "stamps": tags,
        "unstamped": missing, "distinct": distinct,
        "rule": "an unstamped face is UNKNOWN, never agreeing; only faces "
                "carrying the same repair_factor may be compared cell by cell",
        "how_to_clear": "re-burn the unstamped (or old-factor) twin on the current "
                        "panel; back-stamping a face is impossible, because the code "
                        "that burned it is what the stamp would be claiming",
    }


def run_burncontrol(outdir=None, dirpath=None):
    """E88: prove the interval and robust faces sit on the published burn."""
    import glob as _glob

    d = dirpath or os.path.join(ROOT, "results", "e44_midmonth")

    def _newest(pat):
        hits = sorted(_glob.glob(os.path.join(d, pat)))
        return hits[-1] if hits else None

    se_p, rob_p, s13_p = (_newest("CHURNSE-2*.json"),
                          _newest("CHURNROBUST-2*.json"),
                          _newest("CHURNROBUST-2*-s2013.json"))

    def _load(p):
        if not p:
            return None
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)

    se, rob, s13 = _load(se_p), _load(rob_p), _load(s13_p)
    missing = [n for n, v in (("churnse", se), ("churnrobust", rob),
                              ("churnrobust_s2013", s13)) if v is None]
    if missing:
        return {"study": "e88_churnrobust_burn_control",
                "status": "awaiting_faces", "missing": missing,
                "controls": {}}

    ck = ("book", "universe", "era")
    dk = ("book", "mode", "era")
    controls = {}
    if se and rob:
        controls["se_vs_robust_2020"] = {
            "levels": _mean_control(se.get("cells"), rob.get("cells"), ck),
            "deltas": _mean_control(se.get("delta_cells"),
                                    rob.get("delta_cells"), dk)}
    if se and s13:
        controls["se_vs_robust_2013_shared_eras"] = {
            "levels": _mean_control(se.get("cells"), s13.get("cells"), ck),
            "deltas": _mean_control(se.get("delta_cells"),
                                    s13.get("delta_cells"), dk)}
    bad = sum(v["mismatched"] for c in controls.values() for v in c.values())
    shared = sum(v["shared_cells"] for c in controls.values() for v in c.values())
    # E110: this control recomputes nothing -- it joins faces already on disk. A twin
    # burned at an older cutoff (or before a repair-factor change) cannot agree no
    # matter which arm the current leg runs in, so name that condition instead of
    # reporting a bare MISMATCH as if the burn were wrong.
    cutoffs = {n: (f.get("evidence_cutoff") if f else None)
               for n, f in (("churnse", se), ("churnrobust", rob),
                            ("churnrobust_s2013", s13))}
    stale_twins = [n for n, c in cutoffs.items() if c != cutoffs["churnse"]]
    # E111: the cutoff guard catches one of the two axes. A face burned by other
    # repair code is a different experiment, so it can neither agree (as the old
    # "identical" status would claim for two unstamped faces) nor disagree.
    factors = _repair_factor_guard([("churnse", se), ("churnrobust", rob),
                                    ("churnrobust_s2013", s13)])
    if factors["verdict"] != "uniform":
        status = factors["verdict"]
    elif bad == 0:
        status = "identical_on_this_face"
    elif stale_twins:
        status = "mismatch_across_cutoffs"
    else:
        status = "MISMATCH"
    return {
        "study": "e88_churnrobust_burn_control",
        "evidence_cutoff": se.get("evidence_cutoff"),
        "status": status,
        "cutoffs": cutoffs,
        "stale_twins": stale_twins,
        "repair_factor": factors,
        "confound": ("a twin whose cutoff differs from the interval face mixes panel "
                     "arrival (and any factor change since it was burned) with the "
                     "burn; re-derive the twin at the current cutoff before reading "
                     "the control as a burn verdict") if stale_twins else None,
        "spec": {
            "faces": [os.path.relpath(p, ROOT) for p in (se_p, rob_p, s13_p)],
            "control": "join every cell on (book, universe|mode, era) and compare "
                       "mean_bp by exact equality; a re-derived burn shows up here",
            "note": "the 2013-start control only covers the eras both faces carry "
                    "(era cells are era-local, so the shared eras must agree "
                    "bit-for-bit or the earlier start changed the burn)",
        },
        "controls": controls,
        "summary": {"shared_cells": shared, "mismatched": bad},
    }


# ------------------------------------------- leg: churn LEVELs named by arm (E99)

LEVEL_BOOKS = ("me", "mid")


def _arm_level_cell(face, era, book):
    """One published churn LEVEL cell, read off a face by (era, book)."""
    row = ((face or {}).get("eras") or {}).get(era) or {}
    cell = row.get(book) or {}
    return {"churn_alpha_bp_mean": cell.get("churn_alpha_bp_mean"),
            "x1_ann_pct": cell.get("x1_ann_pct"),
            "negative_churn_share_pct": cell.get("negative_churn_share_pct")}


def _level_rows(faces, eras, arms, books=LEVEL_BOOKS):
    """(era, book) rows carrying one cell per arm, with the arm as the key.

    The arm is the dictionary key, never a column name: E96 found both
    published LEVEL faces carried no arm at all, and a row of bare levels
    cannot be labelled after the fact. ``delta_vs_unscreened_bp`` sits beside
    every arm so a screened level can never be read as the untreated one.
    """
    rows = []
    for era in [e[0] for e in eras]:
        for book in books:
            cells = {arm: _arm_level_cell((faces or {}).get(arm), era, book)
                     for arm in arms}
            base = (cells.get("unscreened") or {}).get("churn_alpha_bp_mean")
            for arm in arms:
                v = cells[arm].get("churn_alpha_bp_mean")
                cells[arm]["delta_vs_unscreened_bp"] = (
                    round(v - base, 1)
                    if isinstance(v, (int, float)) and isinstance(base, (int, float))
                    else None)
            rows.append({"era": era, "book": book, "arms": cells})
    return rows


def _level_sign_flips(rows, arms):
    """(era, book) cells whose LEVEL changes sign across arms."""
    out = []
    for r in rows:
        vals = [c.get("churn_alpha_bp_mean") for a, c in r["arms"].items()
                if a in arms and isinstance(c.get("churn_alpha_bp_mean"), (int, float))]
        if len(vals) >= 2 and min(vals) < 0 < max(vals):
            out.append("%s/%s" % (r["era"], r["book"]))
    return sorted(out)


def _level_coverage(rows, arms):
    """Structural check: every row must carry every arm key."""
    missing = []
    for r in rows:
        for arm in arms:
            if arm not in r["arms"]:
                missing.append("%s/%s/%s" % (r["era"], r["book"], arm))
    return {"rows": len(rows), "arms": len(arms),
            "cells": len(rows) * len(arms), "missing_arm_keys": missing}


def _published_level_control(outdir, faces,
                             published="MID-20261020-s20180101.json"):
    """Join the already-published start-2018 LEVEL face against the unscreened arm."""
    path = os.path.join(outdir or os.path.join(ROOT, "results", "e44_midmonth"),
                        published)
    if not os.path.isfile(path):
        return {"file": published, "status": "absent"}
    try:
        with open(path, encoding="utf-8") as fh:
            pub = json.load(fh)
    except (OSError, ValueError):
        return {"file": published, "status": "unreadable"}
    joined, diffs = 0, []
    for era, row in (pub.get("eras") or {}).items():
        for book in LEVEL_BOOKS:
            mine = _arm_level_cell(faces.get("unscreened"), era, book)
            theirs = (row.get(book) or {}).get("churn_alpha_bp_mean")
            a, b = mine.get("churn_alpha_bp_mean"), theirs
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                joined += 1
                diffs.append(abs(a - b))
    return {"file": published, "status": "compared",
            "published_cutoff": pub.get("evidence_cutoff"),
            "cells_joined": joined,
            "max_abs_diff_bp": round(max(diffs), 1) if diffs else None,
            "identical": bool(diffs) and max(diffs) == 0.0,
            "note": "the published twin was burned on an earlier cutoff, so a "
                    "non-zero drift is a re-derivation through new data, not a "
                    "producing-code difference"}


def run_midlevels(outdir, start="2018-01-01", pick_n=9999, exclude=("sh511",),
                  gap_limits=(1, 5), mid_day=15, costs=(0.0, 1.0, 3.0), eras=ERAS):
    """E99: the start-2018 churn LEVELs, each carrying the arm that produced it.

    E96 could not label MID-20261020-s20180101.json at all: its 2017_2020 era
    has no arm twin on the 2020-start sibling, so every arm stopped at 0.854
    coverage. The fix is not an inference but a burn -- one universe per arm,
    the same calendars, the same rank cache, and the arm written into the spec
    from the loop that built the universes rather than typed afterwards.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]

    universes = {"unscreened": raw}
    universes["neutralise_int"], reports = (
        panel_screen.screen_universe(raw, mode="neutralise_int", cal=cal_full))
    reports = {"neutralise_int": reports}
    for k in gap_limits:
        label = "neutralise_gap%d" % int(k)
        universes[label], reports[label] = panel_screen.screen_universe(
            raw, mode="neutralise_gap", cal=cal_full, gap_limit=int(k))
    arms = list(universes)  # the arm list IS the producing loop

    faces = {}
    for label, univ in universes.items():
        faces[label] = run_midmonth(outdir, start=start, pick_n=pick_n,
                                    exclude=exclude, mid_day=mid_day,
                                    costs=costs, raw=univ)

    rows = _level_rows(faces, eras, arms)
    populated = sorted({r["era"] for r in rows
                        if any(isinstance(c.get("churn_alpha_bp_mean"), (int, float))
                               for c in r["arms"].values())})
    era_gaps = {}
    for era in [e[0] for e in eras]:
        era_gaps[era] = {arm: (faces[arm]["eras"].get(era) or {}).get("gap_x1_bp")
                         for arm in arms}
    newest = eras[-1][0]
    return {
        "study": "e99_midmonth_levels_by_arm",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "mid_month_day": mid_day, "cost_mult_list": list(costs),
            "cost_bp_per_side": base.COST_BP_SIDE,
            "arms": arms,
            "arm_source": "spec.arms is list(universes) from the producing loop; "
                          "'unscreened' is the untouched e27 loader, the gap arms "
                          "are panel_screen.screen_universe(mode=neutralise_gap, "
                          "gap_limit=k), all on one panel calendar",
            "gap_limits": [int(k) for k in gap_limits],
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": "me = month-end decisions; mid = first session on/after the "
                     "%dth; both on one calendar, one universe per arm" % mid_day,
            "level_cell": "eras[era][book].churn_alpha_bp_mean (the LEVEL E96 "
                          "found unlabelled)",
        },
        "screen_reports": reports,
        "levels": rows,
        "era_gaps_x1_bp": era_gaps,
        "answers": {
            "arms": arms,
            "populated_eras": populated,
            "coverage": _level_coverage(rows, arms),
            "level_sign_flips_across_arms": _level_sign_flips(rows, arms),
            "newest_era_level_bp": {
                book: {arm: ((faces[arm]["eras"].get(newest) or {})
                             .get(book, {}).get("churn_alpha_bp_mean"))
                       for arm in arms} for book in LEVEL_BOOKS},
            "published_control": _published_level_control(outdir, faces),
        },
        "honest": [
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
            "the arm is a universe repair, not a different strategy: every arm "
            "keeps the same calendars, rank cache and fee ladder",
            "coverage: a cell is emitted for every (era, book, arm) triple, so an "
            "era the burn could not populate shows up as null, never as a missing key",
            "a level that moves across arms is not a level the repair created; it "
            "is a level the untreated panel was carrying on a repaired print",
        ],
    }


# ------------------------------------ E101: is the arm DELTA end-stable?

def _truncate_decisions(decisions, cal, end):
    """Every decision whose session is on or before ``end``.

    A re-burned window cannot see the forward leg of its own final decision,
    and that is exactly what happens here: ``_churn_stats`` needs a following
    decision and skips the last one, so truncating the list is a window
    truncation, not a re-stamp of a full-window reading.
    """
    return [(i, holds) for i, holds in decisions if cal[i] <= end]


def _era_end_grid(decisions, cal, era, ends):
    """The last ``ends`` decision sessions of one era, ascending."""
    name = era[0]
    idxs = [i for i, _ in decisions if _era_of(cal[i], (era,)) == name]
    return [cal[i] for i in idxs[-int(ends):]]


def _next_decision_session(decisions, cal, end):
    """The first decision session strictly after ``end`` (None if there is none).

    Pricing a grid cell through the NEXT decision is what keeps the cell's
    meaning constant: an era's own last transition needs a following decision
    to have a forward leg at all, so a hard truncation at the end date silently
    drops it. The published control caught exactly that -- the 2017_2020 me
    delta read 0.0bp under a hard cut against the published -745.9bp, and the
    whole 745.9 sits in the transition the cut had thrown away.
    """
    for i, _holds in decisions:
        if cal[i] > end:
            return cal[i]
    return None


def _endgrid_span(vals):
    v = [x for x in vals if isinstance(x, (int, float))]
    return round(max(v) - min(v), 1) if len(v) >= 2 else None


def _min_span(vals):
    v = [x for x in vals if isinstance(x, (int, float))]
    return min(v) if v else None


def _arm_delta_verdict(delta_span, level_span):
    """One (era, book) cell: does the DELTA survive an end grid the levels do not?

    Returns (delta_over_level_span, verdict). The rule is mechanical: a delta
    whose grid span is at most a quarter of the smaller of its two level spans
    is reading through a movement that moves both arms together.
    """
    if delta_span is None or level_span is None:
        return None, None
    if level_span == 0.0:
        return None, ("levels_fixed_across_ends" if delta_span == 0.0
                      else "delta_moves_while_levels_hold")
    return round(delta_span / level_span, 2), (
        "delta_stable_levels_fragile" if delta_span <= 0.25 * level_span
        else "delta_moves_with_the_end")


def _arm_price_edits(caches, arm, base="unscreened"):
    """How many symbols an arm actually edits, not how many it keeps.

    The screens repair prints rather than drop tickers, so two arms can hold
    the same name set and still be different objects. A delta identity alone
    cannot tell "the repair does not bind on this panel" from "this arm is the
    base universe under another name"; the edit count can.
    """
    base_p = caches[base]["prices"]
    p = caches[arm]["prices"]
    changed = [s for s in sorted(p) if base_p.get(s) != p[s]]
    return {"symbols_with_changed_prices": len(changed),
            "first_three": changed[:3]}


def _grid_zero_profile(deltas):
    """Zero ends and the step signature of one delta series across a grid.

    Kept as a pure function so the selftest can pin the rule the E102 leg
    publishes: an end reads zero at the precision the E99 deltas are quoted
    at (|delta| < 0.05bp), and a series is a one-transition step when exactly
    one end of the grid is non-zero -- the era's own last end.
    """
    kv = [x for x in deltas if isinstance(x, (int, float))]
    zeros = [x for x in kv if abs(x) < 0.05]
    non_zero = [x for x in kv if abs(x) >= 0.05]
    return {"ends": len(kv), "zero_ends": len(zeros),
            "non_zero_ends": len(non_zero),
            "non_zero_delta_bp": [round(x, 1) for x in non_zero],
            "step_signature": bool(kv) and len(zeros) == len(kv) - 1
                              and len(non_zero) == 1}


def _read_published_levels(outdir, published):
    path = os.path.join(outdir or os.path.join(ROOT, "results", "e44_midmonth"),
                        published)
    if not os.path.isfile(path):
        return None, {"file": published, "status": "absent"}
    try:
        with open(path, encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        return None, {"file": published, "status": "unreadable"}
    index = {}
    for row in face.get("levels") or []:
        index[(row.get("era"), row.get("book"))] = row.get("arms") or {}
    return index, {"file": published, "status": "read",
                   "published_cutoff": face.get("evidence_cutoff"),
                   "rows": len(face.get("levels") or [])}


def run_gaparm_endgrid(outdir, start="2018-01-01", pick_n=9999, exclude=("sh511",),
                       gap_limit=1, ends=12, mid_day=15, eras=ERAS,
                       published="MID-20261026-s20180101-armed.json"):
    """E101: put the E99 arm delta under the E98 end grid.

    E99 published the gap arm's effect as a difference of LEVELs (-745.9bp on
    the 2017_2020 me level, -1098.3bp on 2021_2023), and E98 showed the tilt
    LEVEL is end-fragile on every era the panel reaches. A difference of two
    fragile numbers is not automatically fragile: if both arms move together
    the delta survives while neither level may be quoted. So the grid is run on
    BOTH arms and every end prints the two levels beside their delta.

    Cost note: the decision sets are causal (book at bar i uses bars <= i), so
    each arm's books are built ONCE on the full window and each grid end only
    truncates the decision list. No e27.simulate call is needed -- the cell is
    the churn level, which is a name-level read, not a portfolio return.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]

    gap_label = "neutralise_gap%d" % int(gap_limit)
    universes = {"unscreened": raw}
    universes[gap_label], reports = panel_screen.screen_universe(
        raw, mode="neutralise_gap", cal=cal_full, gap_limit=int(gap_limit))
    arms = ["unscreened", gap_label]

    calendars = [("me", sorted(set(base.month_end_indices(cal)))),
                 ("mid", _mid_month_indices(cal, mid_day))]

    caches = {}
    for label in arms:
        univ = universes[label]
        all_syms = sorted(set(base.LADDER) | set(univ))
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = univ.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms if s in univ]
        rank_cache = {}
        decisions = {}
        for cname, idxs in calendars:
            decisions[cname] = _decision_sets(cal, prices, amounts, universe,
                                              pick_n, idxs, rank_cache)
        caches[label] = {"prices": prices, "decisions": decisions,
                         "universe_members": len(universe)}

    agg_cache = {}

    def agg_for(arm, book, end):
        decs = caches[arm]["decisions"][book]
        nxt = _next_decision_session(decs, cal, end)
        window_end = nxt or cal[-1]
        key = (arm, book, window_end)
        if key not in agg_cache:
            dec = _truncate_decisions(decs, cal, window_end)
            _rows, agg = _churn_stats(cal, caches[arm]["prices"], dec, eras)
            agg_cache[key] = agg
        return agg_cache[key]

    pub_index, pub_meta = _read_published_levels(outdir, published)

    era_rows, control = [], {}
    for era in eras:
        name, lo, hi = era
        grid = _era_end_grid(caches["unscreened"]["decisions"]["me"], cal, era, ends)
        row = {"era": name, "era_from": lo, "era_to": hi, "grid_ends": len(grid)}
        if len(grid) < 3:
            row.update({"skipped": "fewer than 3 decision ends fall inside this era",
                        "end_choice_series": [], "delta_span_bp": {},
                        "level_span_bp": {}, "verdict": {}, "delta_over_level_span": {}})
            era_rows.append(row)
            continue
        series = []
        for end in grid:
            books = {}
            for book in LEVEL_BOOKS:
                per_arm, priced = {}, {}
                for a in arms:
                    nxt = _next_decision_session(caches[a]["decisions"][book], cal, end)
                    priced[a] = nxt or cal[-1]
                    per_arm[a] = ((agg_for(a, book, end).get(name) or {})
                                  .get("churn_alpha_bp_mean"))
                delta = (round(per_arm[gap_label] - per_arm["unscreened"], 1)
                         if per_arm["unscreened"] is not None
                         and per_arm[gap_label] is not None else None)
                books[book] = {"levels_bp": per_arm, "delta_bp": delta,
                               "priced_through": priced}
            series.append({"window_end": end, "books": books})

        level_span = {book: {a: _endgrid_span([s["books"][book]["levels_bp"][a]
                                               for s in series]) for a in arms}
                      for book in LEVEL_BOOKS}
        delta_span = {book: _endgrid_span([s["books"][book]["delta_bp"] for s in series])
                      for book in LEVEL_BOOKS}
        ratio, verdict = {}, {}
        for book in LEVEL_BOOKS:
            ds = delta_span[book]
            ls = _min_span(level_span[book].values())
            ratio[book], verdict[book] = _arm_delta_verdict(ds, ls)
        row.update({"end_choice_series": series,
                    "level_span_bp": level_span,
                    "delta_span_bp": delta_span,
                    "delta_over_level_span": ratio,
                    "verdict": verdict,
                    "latest_end": {"window_end": grid[-1],
                                   "books": series[-1]["books"]}})
        era_rows.append(row)
        # the published (full-window) delta against this grid's own latest end
        legs = {}
        for book in LEVEL_BOOKS:
            theirs = ((pub_index or {}).get((name, book)) or {}).get(gap_label) or {}
            mine = series[-1]["books"][book]["delta_bp"]
            t = theirs.get("delta_vs_unscreened_bp")
            legs[book] = {"published_delta_bp": t, "latest_end_delta_bp": mine,
                          "abs_diff_bp": (round(abs(t - mine), 1)
                                          if isinstance(t, (int, float))
                                          and isinstance(mine, (int, float)) else None)}
        control[name] = legs

    measured = [r for r in era_rows if r.get("delta_span_bp")]
    stable = {book: [r["era"] for r in measured
                     if (r["verdict"] or {}).get(book) == "delta_stable_levels_fragile"]
              for book in LEVEL_BOOKS}
    fragile = {book: [r["era"] for r in measured
                      if (r["verdict"] or {}).get(book) == "delta_moves_with_the_end"]
               for book in LEVEL_BOOKS}
    return {
        "study": "e101_gaparm_delta_under_end_grid",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "mid_month_day": mid_day, "arms": arms, "gap_limit": int(gap_limit),
            "grid": "the last %d month-end decision sessions of each era; the same "
                    "end is applied to both arms and both books" % int(ends),
            "cell": "eras[era][book].churn_alpha_bp_mean, the E99 LEVEL",
            "delta": "gap arm level minus unscreened level on the SAME end",
            "verdict_rule": "delta_stable_levels_fragile when the delta span is "
                            "<= 25% of the smaller level span in that era",
            "universe_members": {a: caches[a]["universe_members"] for a in arms},
        },
        "screen_report": reports,
        "eras": era_rows,
        "published_control": {"meta": pub_meta, "cells": control},
        "answers": {
            "measured_eras": [r["era"] for r in measured],
            "skipped_eras": [r["era"] for r in era_rows if r.get("skipped")],
            "delta_stable_eras": stable,
            "delta_moves_eras": fragile,
            "delta_span_bp": {r["era"]: r["delta_span_bp"] for r in measured},
            "level_span_bp": {r["era"]: r["level_span_bp"] for r in measured},
            "reads_as": (
                "the arm delta holds across the end grid on every measured era while "
                "at least one of its two levels does not, so the repair is a measurement "
                "even where the level it moves is not quotable"
                if measured and all(stable[b] == [r["era"] for r in measured]
                                    for b in LEVEL_BOOKS) else
                "at least one (era, book) delta moves with the end grid, so the arm "
                "effect must be cited per end the way its levels are"
                if measured else None),
        },
        "honest": [
            "descriptive census only: no gate, no verdict on the strategy, no prereg, "
            "no trial count, no ledger booking",
            "both arms share the panel calendar, the rank cache and the fee ladder; the "
            "arm is a universe repair, not a different strategy",
            "the grid moves the evaluation end only, so a delta that survives it is "
            "end-stable on THIS panel and says nothing about panel arrival effects",
            "a truncated window loses the forward leg of its own last decision, so every "
            "grid end is priced through the next decision of the same book: the "
            "published control reproduces the full-window delta exactly there, which "
            "is the proof that the cut is a cut of the evaluation end only",
            "the churn level is a name-level mean over swapped pairs, not a portfolio "
            "return: the delta moves a reading, not money",
        ],
    }


FAMILY_ARMS = ("unscreened", "neutralise_int", "neutralise_gap1",
               "neutralise_gap2", "neutralise_gap5")


def run_gaparm_family_endgrid(outdir, start="2018-01-01", pick_n=9999,
                              exclude=("sh511",), ends=12, mid_day=15,
                              eras=ERAS,
                              published="MID-20261026-s20180101-armed.json"):
    """E102: the whole five-arm family under the same end grid.

    E101 put ONE repair arm (neutralise_gap1) under the grid and found its
    delta on 2017_2020 is a one-transition step: 11 of 12 ends read exactly
    0.0bp and the twelfth is the era's own last end. E99 published FIVE arms
    and gap1/gap2/gap5 read the same delta to 0.1bp there, so a family read as
    five measurements may in fact be five names for one transition. This leg
    runs the identical grid on all five arms and prints, per arm and book, how
    many ends read exactly zero beside the delta span: a step leaves (ends-1)
    zeros and puts its whole span in the last end, an effect spreads movement
    across the grid.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]

    universes = {"unscreened": raw}
    reports = {}
    for label, mode, kw in (("neutralise_int", "neutralise_int", {}),
                            ("neutralise_gap1", "neutralise_gap", {"gap_limit": 1}),
                            ("neutralise_gap2", "neutralise_gap", {"gap_limit": 2}),
                            ("neutralise_gap5", "neutralise_gap", {"gap_limit": 5})):
        universes[label], reports[label] = panel_screen.screen_universe(
            raw, mode=mode, cal=cal_full, **kw)
    arms = list(FAMILY_ARMS)

    calendars = [("me", sorted(set(base.month_end_indices(cal)))),
                 ("mid", _mid_month_indices(cal, mid_day))]

    caches = {}
    for label in arms:
        univ = universes[label]
        all_syms = sorted(set(base.LADDER) | set(univ))
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = univ.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms if s in univ]
        rank_cache = {}
        decisions = {}
        for cname, idxs in calendars:
            decisions[cname] = _decision_sets(cal, prices, amounts, universe,
                                              pick_n, idxs, rank_cache)
        caches[label] = {"prices": prices, "decisions": decisions,
                         "universe_members": len(universe)}

    agg_cache = {}

    def agg_for(arm, book, end):
        decs = caches[arm]["decisions"][book]
        nxt = _next_decision_session(decs, cal, end)
        window_end = nxt or cal[-1]
        key = (arm, book, window_end)
        if key not in agg_cache:
            dec = _truncate_decisions(decs, cal, window_end)
            _rows, agg = _churn_stats(cal, caches[arm]["prices"], dec, eras)
            agg_cache[key] = agg
        return agg_cache[key]

    pub_index, pub_meta = _read_published_levels(outdir, published)

    era_rows = []
    for era in eras:
        name, lo, hi = era
        grid = _era_end_grid(caches["unscreened"]["decisions"]["me"], cal, era, ends)
        row = {"era": name, "era_from": lo, "era_to": hi, "grid_ends": len(grid)}
        if len(grid) < 3:
            row.update({"skipped": "fewer than 3 decision ends fall inside this era"})
            era_rows.append(row)
            continue
        series = []
        for end in grid:
            books = {}
            for book in LEVEL_BOOKS:
                per_arm, priced = {}, {}
                for a in arms:
                    nxt = _next_decision_session(caches[a]["decisions"][book], cal, end)
                    priced[a] = nxt or cal[-1]
                    per_arm[a] = ((agg_for(a, book, end).get(name) or {})
                                  .get("churn_alpha_bp_mean"))
                delta = {a: (round(per_arm[a] - per_arm["unscreened"], 1)
                             if per_arm[a] is not None
                             and per_arm["unscreened"] is not None else None)
                         for a in arms if a != "unscreened"}
                books[book] = {"levels_bp": per_arm, "delta_bp": delta,
                               "priced_through": priced}
            series.append({"window_end": end, "books": books})

        # per (book, arm): zero-delta ends, delta span, and the level spans it sits on
        per_arm_cell = {}
        for book in LEVEL_BOOKS:
            cell = {}
            for a in arms:
                if a == "unscreened":
                    continue
                dser = [s["books"][book]["delta_bp"][a] for s in series]
                zp = _grid_zero_profile(dser)
                zeros = [s["window_end"] for s, x in zip(series, dser)
                         if isinstance(x, (int, float)) and abs(x) < 0.05]
                lvl_a = [s["books"][book]["levels_bp"][a] for s in series]
                lvl_u = [s["books"][book]["levels_bp"]["unscreened"] for s in series]
                dspan = _endgrid_span(dser)
                lspan = _min_span([_endgrid_span(lvl_a), _endgrid_span(lvl_u)])
                ratio, verdict = _arm_delta_verdict(dspan, lspan)
                cell[a] = {"ends": zp["ends"], "zero_ends": zp["zero_ends"],
                           "zero_end_dates": zeros,
                           "non_zero_ends": zp["non_zero_ends"],
                           "non_zero_delta_bp": zp["non_zero_delta_bp"],
                           "delta_span_bp": dspan,
                           "level_span_bp": {"arm": _endgrid_span(lvl_a),
                                             "unscreened": _endgrid_span(lvl_u)},
                           "delta_over_level_span": ratio,
                           "verdict": verdict,
                           "step_signature": zp["step_signature"]}
            per_arm_cell[book] = cell

        # is the screen family one reading or several, on this era and book?
        family = {}
        for book in LEVEL_BOOKS:
            latest = {a: series[-1]["books"][book]["delta_bp"][a]
                      for a in arms if a != "unscreened"}
            scr = [x for x in latest.values() if isinstance(x, (int, float))]
            distinct = sorted({round(x, 1) for x in scr})
            family[book] = {
                "latest_end_delta_bp": latest,
                "distinct_screen_deltas": len(distinct),
                "distinct_values_bp": distinct,
                "screen_max_minus_min_bp": (round(max(scr) - min(scr), 1)
                                            if len(scr) >= 2 else None),
                "reads_as": ("one_reading_many_names" if len(distinct) == 1
                             else "distinct_repairs"),
            }

        control = {}
        for book in LEVEL_BOOKS:
            for a in arms:
                if a == "unscreened":
                    continue
                theirs = ((pub_index or {}).get((name, book)) or {}).get(a) or {}
                t = theirs.get("delta_vs_unscreened_bp")
                mine = series[-1]["books"][book]["delta_bp"][a]
                control.setdefault(book, {})[a] = {
                    "published_delta_bp": t, "latest_end_delta_bp": mine,
                    "abs_diff_bp": (round(abs(t - mine), 1)
                                    if isinstance(t, (int, float))
                                    and isinstance(mine, (int, float)) else None)}

        row.update({"end_choice_series": series,
                    "per_arm": per_arm_cell,
                    "family": family,
                    "published_control": control})
        era_rows.append(row)

    measured = [r for r in era_rows if r.get("per_arm")]
    zero_ends = {r["era"]: {b: {a: "%d/%d" % (c["zero_ends"], c["ends"])
                                for a, c in (r["per_arm"][b] or {}).items()}
                            for b in LEVEL_BOOKS} for r in measured}
    delta_span = {r["era"]: {b: {a: c["delta_span_bp"]
                                 for a, c in (r["per_arm"][b] or {}).items()}
                             for b in LEVEL_BOOKS} for r in measured}
    steps = {r["era"]: {b: sorted(a for a, c in (r["per_arm"][b] or {}).items()
                                  if c["step_signature"])
                        for b in LEVEL_BOOKS} for r in measured}
    identity = {r["era"]: r["family"] for r in measured}

    # control must reproduce the published delta on the grid's own latest end
    ctrl_diff = []
    for r in measured:
        for book, per_arm in (r.get("published_control") or {}).items():
            for a, legs in per_arm.items():
                if legs["abs_diff_bp"] is not None and legs["abs_diff_bp"] > 0.05:
                    ctrl_diff.append({"era": r["era"], "book": book, "arm": a,
                                      "abs_diff_bp": legs["abs_diff_bp"]})

    one_reading = [ (r["era"], b) for r in measured for b in LEVEL_BOOKS
                    if (r["family"].get(b) or {}).get("reads_as")
                    == "one_reading_many_names" ]
    any_step = any(steps[r["era"]][b] for r in measured for b in LEVEL_BOOKS)

    return {
        "study": "e102_gaparm_family_endgrid",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "mid_month_day": mid_day, "arms": arms,
            "grid": "the last %d month-end decision sessions of each era; the same "
                    "end is applied to all five arms and both books" % int(ends),
            "cell": "eras[era][book].churn_alpha_bp_mean (the E99 LEVEL)",
            "delta": "screen arm level minus unscreened level on the SAME end",
            "zero_rule": "an end reads zero when |delta| < 0.05bp, the precision the "
                         "published E99 deltas are quoted at",
            "step_rule": "step_signature when exactly one end of the grid is non-zero "
                         "and it is the era's own last end",
            "universe_members": {a: caches[a]["universe_members"] for a in arms},
        },
        "screen_report": reports,
        "eras": era_rows,
        "published_control": {"meta": pub_meta, "mismatches": ctrl_diff},
        "answers": {
            "measured_eras": [r["era"] for r in measured],
            "skipped_eras": [r["era"] for r in era_rows if r.get("skipped")],
            "zero_ends": zero_ends,
            "delta_span_bp": delta_span,
            "step_arms": steps,
            "arm_price_edits": {a: _arm_price_edits(caches, a)
                                for a in arms if a != "unscreened"},
            "family_identity": identity,
            "control_reproduces_published": not ctrl_diff,
            "reads_as": (
                "the five published arms are %d distinct end-grid measurements and "
                "%d era-book cells in which four screen arms quote one identical "
                "delta: the family is a measurement of one transition under several "
                "names wherever the identity cells are the movers"
                % (len(arms), len(one_reading))
                if one_reading else
                "every era-book cell separates the screen arms, so the published "
                "family reads as %d independent measurements" % len(arms)
                if measured else None),
        },
        "honest": [
            "descriptive census only: no gate, no verdict on the strategy, no prereg, "
            "no trial count, no ledger booking",
            "all five arms share the panel calendar, the rank cache and the fee ladder; "
            "the arms are universe repairs, not different strategies",
            "a zero-delta end is not a zero effect: the grid truncates the evaluation "
            "end and every end is priced through the next decision of the same book, so "
            "a transition sitting after the era's own last end can still be counted",
            "identical deltas across gap1/gap2/gap5 mean the gap limit does not bind on "
            "this panel; it does not mean the three screens are the same object",
            "the churn level is a name-level mean over swapped pairs, not a portfolio "
            "return: the deltas move a reading, not money",
        ],
    }


def _print_set(report):
    """The (name, date) pairs an arm actually repaired, from a screen report.

    ``events_neutralised`` counts repaired prints; the ladder needs the prints
    themselves, because the question "does limit L add anything to limit L-1" is
    answered by which print appeared, not by how many.
    """
    out = []
    for row in (report or {}).get("names") or []:
        if row.get("action") == "kept-gapped-only":
            continue
        for p in row.get("prints") or []:
            out.append((row.get("name"), p.get("date")))
    return sorted(out)


def _arm_edit_face(raw, univ):
    """Every bar an arm rewrites, as ``symbol|date`` cells.

    A repair multiplies the closes on and after the print, so one repaired print
    shows up as hundreds of changed cells. Print count and cell count are two
    different measurements: publishing only one of them reads as either a single
    print or a rewritten panel.
    """
    cells = []
    for s in sorted(univ):
        c0 = raw[s][0]
        c1 = univ[s][0]
        if c1 is c0:
            continue
        for d, v in c1.items():
            if c0.get(d) != v:
                cells.append("%s|%s" % (s, d))
    return cells


def _limit_groups(signatures):
    """Group gap limits by identical edit face, and say where the ladder moves.

    ``signatures`` maps limit -> hashable edit signature. Two limits with the same
    signature rewrite exactly the same cells, so they are one object under two
    names, not two measurements -- which is the whole E103 question. ``growth_limits``
    is every limit whose signature differs from the limit below it (the first limit
    is always a growth point, since it is measured against nothing).
    """
    order = sorted(signatures)
    groups, seen = [], {}
    for lim in order:
        sig = signatures[lim]
        if sig not in seen:
            seen[sig] = {"signature": sig, "limits": []}
            groups.append(seen[sig])
        seen[sig]["limits"].append(lim)
    growth = []
    prev = None
    for lim in order:
        if prev is None or signatures[lim] != signatures[prev]:
            growth.append(lim)
        prev = lim
    return {"groups": groups,
            "distinct_objects": len(groups),
            "growth_limits": growth,
            "saturates_at": (groups[-1]["limits"][0] if groups else None)}


def run_gap_limit_ladder(outdir, start="2018-01-01", pick_n=9999,
                         exclude=("sh511",), max_limit=20, mid_day=15,
                         eras=ERAS, max_cell_arms=8,
                         published="MID-20261026-s20180101-armed.json"):
    """E103: at which gap limit does the screen actually start to bind?

    E102 found gap1/gap2/gap5 publish one identical delta on every era-book cell
    while gap1 and gap5 differ on exactly one of 1,271 names, so the published gap
    limit is an assumption rather than an identified parameter: on this panel the
    three columns may be three names for one object and cannot corroborate each
    other. This leg walks ``gap_limit`` 1..max_limit and publishes the frontier --
    how many symbols, prints and bars each limit rewrites, the binding print named
    by date, and the panel's own gapped-print spectrum -- then measures the
    published cells on one representative per DISTINCT edit face. Two limits with
    an identical edit face are one object by construction, so no burn is needed to
    say their cells agree; only a limit that changes the face can change a cell.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]

    # the panel's own gap spectrum: why a ladder may saturate immediately
    spectrum, max_gap = {}, 0
    for s in sorted(raw):
        for e in panel_screen.split_events(raw[s][0], cal=cal_full):
            if e["adjacent"]:
                continue
            g = e["gap_sessions"]
            max_gap = max(max_gap, g)
            key = str(g) if g <= max_limit else "gt%d" % max_limit
            ent = spectrum.setdefault(key, {"gapped_prints": 0,
                                            "integer_like": 0, "prints": []})
            ent["gapped_prints"] += 1
            if (e.get("implied") or {}).get("integer_like"):
                ent["integer_like"] += 1
                ent["prints"].append("%s@%s" % (s, e["date"]))

    # the ladder: one screen per limit, retained only on a new edit face
    rows, signatures, reps, rep_reports = [], {}, {}, {}
    prev_prints = None
    for lim in range(1, int(max_limit) + 1):
        univ, rep = panel_screen.screen_universe(
            raw, mode="neutralise_gap", cal=cal_full, gap_limit=lim)
        cells = _arm_edit_face(raw, univ)
        sig = hashlib.sha1("\n".join(cells).encode()).hexdigest()[:12]
        prints = _print_set(rep)
        new_prints = ([p for p in prints if p not in set(prev_prints or [])]
                      if prev_prints is not None else list(prints))
        symbols = sorted({c.split("|")[0] for c in cells})
        rows.append({"limit": lim,
                     "symbols_rewritten": len(symbols),
                     "prints_repaired": rep.get("events_neutralised"),
                     "gapped_eligible": rep.get("gapped_eligible"),
                     "bars_rewritten": len(cells),
                     "new_symbols_vs_previous": len(
                         {p[0] for p in new_prints} - set(
                             p[0] for p in (prev_prints or []))),
                     "new_prints": [{"name": p[0], "date": p[1]}
                                    for p in new_prints],
                     "edit_signature": sig})
        signatures[lim] = sig
        if sig not in reps:
            reps[sig] = {"limit": lim, "universe": univ}
            rep_reports[lim] = rep.get("mode")
        prev_prints = prints

    ladder = _limit_groups(signatures)
    growth = ladder["growth_limits"]
    first_growth = growth[1] if len(growth) > 1 else None
    binding_prints = []
    for r in rows:
        if r["limit"] == first_growth:
            binding_prints = r["new_prints"]

    # cells: one representative per distinct face, plus the unscreened base
    arm_limits = [g["limits"][0] for g in ladder["groups"]]
    measured_limits = arm_limits[:int(max_cell_arms)]
    unmeasured = [lim for lim in arm_limits if lim not in measured_limits]
    all_syms = sorted({s for s in raw})
    calendars = [("me", sorted(set(base.month_end_indices(cal)))),
                 ("mid", _mid_month_indices(cal, mid_day))]

    caches = {}
    for lim, univ in [("unscreened", raw)] + [
            (reps[sig]["limit"], reps[sig]["universe"]) for sig in reps
            if reps[sig]["limit"] in measured_limits]:
        all_syms_a = sorted(set(base.LADDER) | set(univ))
        prices, amounts = {}, {}
        for s in all_syms_a:
            c, a = univ.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms_a if s in univ]
        rank_cache = {}
        decisions = {}
        for cname, idxs in calendars:
            decisions[cname] = _decision_sets(cal, prices, amounts, universe,
                                              pick_n, idxs, rank_cache)
        caches[lim] = {"prices": prices, "decisions": decisions,
                       "universe_members": len(universe)}

    def level_at(arm, book, era_row):
        name, _lo, _hi = era_row
        decs = caches[arm]["decisions"][book]
        grid = _era_end_grid(decs, cal, era_row, 1)
        if not grid:
            return None
        nxt = _next_decision_session(decs, cal, grid[-1])
        window_end = nxt or cal[-1]
        _rows, agg = _churn_stats(cal, caches[arm]["prices"],
                                  _truncate_decisions(decs, cal, window_end), eras)
        return (agg.get(name) or {}).get("churn_alpha_bp_mean")

    pub_index, pub_meta = _read_published_levels(outdir, published)

    cells = []
    ctrl_diff = []
    for era_row in eras:
        for book in LEVEL_BOOKS:
            base_level = level_at("unscreened", book, era_row)
            per_arm = {}
            for lim in measured_limits:
                lvl = level_at(lim, book, era_row)
                per_arm["neutralise_gap%d" % lim] = {
                    "level_bp": lvl,
                    "delta_vs_unscreened_bp": (
                        round(lvl - base_level, 1)
                        if isinstance(lvl, (int, float))
                        and isinstance(base_level, (int, float)) else None)}
            first = per_arm.get("neutralise_gap%d" % measured_limits[0], {}) \
                if measured_limits else {}
            d0 = first.get("delta_vs_unscreened_bp")
            for label, v in per_arm.items():
                d = v["delta_vs_unscreened_bp"]
                v["moves_vs_gap%d_bp"] = (
                    round(abs(d - d0), 1)
                    if isinstance(d, (int, float)) and isinstance(d0, (int, float))
                    else None)
                theirs = ((pub_index or {}).get((era_row[0], book)) or {}) \
                    .get(label) or {}
                t = theirs.get("delta_vs_unscreened_bp")
                v["published_delta_bp"] = t
                v["abs_diff_vs_published_bp"] = (
                    round(abs(t - d), 1)
                    if isinstance(t, (int, float)) and isinstance(d, (int, float))
                    else None)
                if v["abs_diff_vs_published_bp"] is not None \
                        and v["abs_diff_vs_published_bp"] > 0.05:
                    ctrl_diff.append({"era": era_row[0], "book": book,
                                      "arm": label,
                                      "abs_diff_bp": v["abs_diff_vs_published_bp"]})
            moved = [label for label, v in per_arm.items()
                     if isinstance(v.get("moves_vs_gap%d_bp"
                                         % measured_limits[0]), (int, float))
                     and v["moves_vs_gap%d_bp" % measured_limits[0]] >= 0.05] \
                if measured_limits else []
            cells.append({"era": era_row[0], "book": book,
                          "unscreened_level_bp": base_level,
                          "arms": per_arm, "arms_that_move_a_cell": moved})

    first_mover = None
    for lim in measured_limits[1:]:
        label = "neutralise_gap%d" % lim
        moved_any = [c for c in cells
                     if label in (c.get("arms_that_move_a_cell") or [])]
        if moved_any:
            first_mover = {"limit": lim, "cells": len(moved_any),
                           "examples": [{"era": c["era"], "book": c["book"],
                                         "moves_bp": (c["arms"] or {})
                                         .get(label, {}).get(
                                             "moves_vs_gap%d_bp" % measured_limits[0])}
                                        for c in moved_any[:4]]}
            break

    empty_limits = [r["limit"] for r in rows
                    if r["limit"] not in growth and not r["new_prints"]]
    return {
        "study": "e103_gap_limit_ladder",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "mid_month_day": mid_day, "gap_limits_walked": [1, int(max_limit)],
            "cell": "eras[era][book].churn_alpha_bp_mean (the E99 LEVEL)",
            "cell_arms": "the unscreened base plus one representative per distinct "
                         "edit face; limits inside one face are one object and are "
                         "not re-burned",
            "move_rule": "an arm moves a cell when its delta against unscreened "
                         "differs from the gap1 delta by at least 0.05bp, the "
                         "precision the published deltas are quoted at",
            "measured_limits": measured_limits,
            "unmeasured_limits": unmeasured,
        },
        "gap_spectrum": {"max_gap_sessions": max_gap,
                         "by_gap_sessions": spectrum},
        "ladder": rows,
        "edit_face_groups": ladder,
        "cells": cells,
        "published_control": {"meta": pub_meta, "mismatches": ctrl_diff},
        "answers": {
            "distinct_objects_in_ladder": ladder["distinct_objects"],
            "growth_limits": growth,
            "first_limit_that_adds_a_print": first_growth,
            "binding_prints": binding_prints,
            "limits_that_add_nothing": empty_limits,
            "gap_ceiling_sessions": (ladder["saturates_at"]
                                     if ladder["distinct_objects"] > 1 else None),
            "first_limit_that_moves_a_published_cell": (
                first_mover["limit"] if first_mover else None),
            "first_mover_detail": first_mover,
            "control_reproduces_published": not ctrl_diff,
            "verdict": ("identified" if first_mover else "not_identified"),
            "reads_as": (
                "no limit in 1..%d moves a published cell: every published gap "
                "column is one object under several names and none of them "
                "corroborates another (the ladder's only real step is limit %s, "
                "which rewrites %s bar(s) and still moves nothing)"
                % (int(max_limit), first_growth,
                   next((r["bars_rewritten"] for r in rows
                         if r["limit"] == first_growth), None))
                if not first_mover else
                "the gap limit binds at %d: the first limit whose repair moves a "
                "published cell is %d, so a published column above that limit is "
                "not interchangeable with a column below it"
                % (first_mover["limit"], first_mover["limit"])),
        },
        "honest": [
            "descriptive census only: no gate, no verdict on the strategy, no "
            "prereg, no trial count, no ledger booking",
            "an identical edit face is a proof of an identical repair object, so "
            "limits inside one face are never counted as independent measurements",
            "the ladder publishes the frontier, not a chosen limit: no limit is "
            "recommended and gap1 stays the published control",
            "the gap spectrum is this panel's own: an integer-like gapped print "
            "beyond the saturation gap does not exist here, so the ladder's "
            "flatness is a property of the data, not of the walk",
            "the churn level is a name-level mean over swapped pairs, not a "
            "portfolio return: the deltas move a reading, not money",
        ],
    }


# -------------------------------------------------------------- E100

def _arm_delta_contrib(gap_map, unscr_map):
    """Exact additive split of one LEVEL delta into per-transition pieces.

    A level is an equal-weight mean over THAT arm's own transitions, so with
    unequal counts every row has to be divided by its own arm's n or the pieces
    do not add up to the delta. One-sided transitions (a decision date that
    exists in only one arm) are kept as rows of their own instead of being
    dropped by a join, and the residual (delta minus the sum of the pieces) is
    returned rather than assumed to be zero -- a partial join must not be able
    to pass as a decomposition.

    ``*_map`` maps decision date -> a churn row carrying churn_alpha_bp, already
    filtered to one era and to numeric alphas.
    """
    ng, nu = len(gap_map), len(unscr_map)
    rows = []
    for d in sorted(set(gap_map) & set(unscr_map)):
        g, u = gap_map[d], unscr_map[d]
        rows.append({"date": d, "side": "both",
                     "gap_bp": g.get("churn_alpha_bp"),
                     "unscreened_bp": u.get("churn_alpha_bp"),
                     "contrib_bp": (g["churn_alpha_bp"] / ng
                                    - u["churn_alpha_bp"] / nu) if ng and nu else None})
    for d in sorted(set(gap_map) - set(unscr_map)):
        rows.append({"date": d, "side": "gap_only",
                     "gap_bp": gap_map[d].get("churn_alpha_bp"),
                     "unscreened_bp": None,
                     "contrib_bp": gap_map[d]["churn_alpha_bp"] / ng if ng else None})
    for d in sorted(set(unscr_map) - set(gap_map)):
        rows.append({"date": d, "side": "unscreened_only",
                     "gap_bp": None,
                     "unscreened_bp": unscr_map[d].get("churn_alpha_bp"),
                     "contrib_bp": (-unscr_map[d]["churn_alpha_bp"] / nu) if nu else None})
    rows = [r for r in rows if isinstance(r.get("contrib_bp"), (int, float))]

    level_gap = (sum(r["churn_alpha_bp"] for r in gap_map.values()) / ng) if ng else None
    level_unscr = (sum(r["churn_alpha_bp"] for r in unscr_map.values()) / nu) if nu else None
    total = sum(r["contrib_bp"] for r in rows)
    delta = (level_gap - level_unscr
             if level_gap is not None and level_unscr is not None else None)
    meta = {
        "gap_n": ng, "unscreened_n": nu,
        "level_gap_bp": None if level_gap is None else round(level_gap, 1),
        "level_unscreened_bp": None if level_unscr is None else round(level_unscr, 1),
        "delta_bp": None if delta is None else round(delta, 1),
        "sum_contrib_bp": round(total, 1),
        "residual_bp": None if delta is None else round(delta - total, 6),
        "gap_only_transitions": len(set(gap_map) - set(unscr_map)),
        "unscreened_only_transitions": len(set(unscr_map) - set(gap_map)),
        "common_transitions": len(set(gap_map) & set(unscr_map)),
    }
    return rows, meta


def _arm_split_verdict(row, top_k=3):
    """Three-way reading of a level-delta split: one window, a few, or composition.

    ``delta_is_a_transition_that_exists_in_one_arm`` is checked first: if any of
    the largest pieces comes from a date present in only one arm, the delta is a
    decision-schedule difference and the shared windows cannot corroborate it.
    """
    d = row.get("delta_bp")
    if not isinstance(d, (int, float)) or d == 0:
        return "no_delta"
    top = (row.get("top") or [])[:top_k]
    if any(t.get("side") != "both" for t in top):
        return "delta_is_a_transition_that_exists_in_one_arm"
    share = row.get("top_share_of_delta_pct")
    if not isinstance(share, (int, float)):
        return "delta_unattributable"
    if abs(share) >= 50.0:
        return "delta_is_one_window"
    if abs(share) >= 25.0:
        return "delta_is_a_few_windows"
    return "delta_is_broad"


def _fwd_pct(prices, sym, i0, i1):
    """Forward percent return of one name over one decision window, or None."""
    s = prices.get(sym)
    if not s or i0 is None or i1 is None:
        return None
    p0, p1 = s[i0], s[i1]
    if p0 is None or p1 is None or p0 <= 0:
        return None
    return 100.0 * (p1 / p0 - 1.0)


def _window_drivers(grows, urows, gprices, uprices, g_i0, g_i1, u_i0, u_i1,
                    limit=3):
    """The swapped names whose forward read moves the most between the two arms.

    Naming a window is not enough: if the two arms hold the same names there, the
    delta can only come from the PRICE each arm reads for them. The drivers are
    exactly those names, with both reads and the gap between them, so a split
    artefact is visible as a name-level number instead of a level difference.
    """
    seen, out = set(), []
    for names in (grows.get("entrant_names") or [], grows.get("exit_names") or [],
                  urows.get("entrant_names") or [], urows.get("exit_names") or []):
        for nm in names:
            if nm in seen:
                continue
            seen.add(nm)
            g = _fwd_pct(gprices, nm, g_i0, g_i1)
            u = _fwd_pct(uprices, nm, u_i0, u_i1)
            if g is None or u is None:
                continue
            out.append({"name": nm,
                        "gap_fwd_pct": round(g, 2),
                        "unscreened_fwd_pct": round(u, 2),
                        "read_gap_pct": round(g - u, 2)})
    out.sort(key=lambda r: -abs(r["read_gap_pct"]))
    return out[:limit]


_SHARE_MEAN_FLOOR_PCT = 0.5


def _held_read_split(gprices, uprices, hold_prev, hold_cur, i0, i1, top_k=3):
    """The price-read split of a window's UNCHANGED holdings (E104).

    E100 could only see names that entered or exited: a ticker the book kept
    through the window contributes no swap, so a split inside it never reaches
    the churn sleeve -- yet the book still holds it and still earns its read.
    This leg reads exactly those names, same dates and same membership, under
    both arms' prices.
    """
    names = sorted(set(hold_prev) & set(hold_cur))
    rows = []
    for nm in names:
        g = _fwd_pct(gprices, nm, i0, i1)
        u = _fwd_pct(uprices, nm, i0, i1)
        if g is None or u is None:
            continue
        rows.append({"name": nm, "gap_fwd_pct": g, "unscreened_fwd_pct": u,
                     "read_gap_pct": g - u})
    n = len(rows)
    if not n:
        return {"persistent_names": 0, "gap_mean_pct": None,
                "unscreened_mean_pct": None, "delta_bp": None, "top": [],
                "residual_bp": None, "max_abs_read": None}
    gm = sum(r["gap_fwd_pct"] for r in rows) / n
    um = sum(r["unscreened_fwd_pct"] for r in rows) / n
    pieces = [{"name": r["name"],
               "contrib_bp": 100.0 * r["read_gap_pct"] / n,
               "gap_fwd_pct": round(r["gap_fwd_pct"], 2),
               "unscreened_fwd_pct": round(r["unscreened_fwd_pct"], 2),
               "read_gap_pct": round(r["read_gap_pct"], 2)} for r in rows]
    delta_bp = 100.0 * (gm - um)
    pieces.sort(key=lambda r: -abs(r["contrib_bp"]))
    biggest = max(rows, key=lambda r: abs(r["unscreened_fwd_pct"]))
    return {"persistent_names": n,
            "gap_mean_pct": round(gm, 4), "unscreened_mean_pct": round(um, 4),
            "delta_bp": round(delta_bp, 4),
            "top": pieces[:top_k],
            "residual_bp": round(delta_bp - sum(p["contrib_bp"] for p in pieces), 9),
            # an ETF does not double in a month: a read past +/-100% is a print
            # artefact, and E104 showed the REPAIRED arm can be the broken one,
            # so both arms are counted separately instead of assuming the fix
            "reads_beyond_100pct": {
                "gap": sum(1 for r in rows if abs(r["gap_fwd_pct"]) > 100.0),
                "unscreened": sum(1 for r in rows
                                  if abs(r["unscreened_fwd_pct"]) > 100.0),
                "names_gap": [r["name"] for r in rows
                              if abs(r["gap_fwd_pct"]) > 100.0][:5],
                "names_unscreened": [r["name"] for r in rows
                                     if abs(r["unscreened_fwd_pct"]) > 100.0][:5]},
            "max_abs_read": {
                "name": biggest["name"],
                "unscreened_fwd_pct": round(biggest["unscreened_fwd_pct"], 2),
                "gap_fwd_pct": round(biggest["gap_fwd_pct"], 2),
                # a level is a mean, so one name can carry it -- but only say so
                # where the mean is far enough from zero for the share to mean
                # anything (a 2% read against a 0.05% mean is not "4000%" of it)
                "share_of_window_mean_pct": (round(100.0 * biggest["unscreened_fwd_pct"] / um, 1)
                                             if abs(um) >= _SHARE_MEAN_FLOOR_PCT else None),
                "share_eligible": abs(um) >= _SHARE_MEAN_FLOOR_PCT,
                "window_mean_pct": round(um, 4)}}


def _held_split_verdict(row, top_k=3):
    """Is the unchanged-holding split none, one window, a few, or broad?"""
    if not row.get("persistent_reads"):
        return "no_unchanged_holdings"
    d = row.get("delta_mean_bp")
    if not isinstance(d, (int, float)) or abs(d) < 1e-9:
        return "no_split_inside_unchanged_holdings"
    windows = row.get("windows") or []
    total = sum(abs(w["delta_bp"]) for w in windows
                if isinstance(w.get("delta_bp"), (int, float)))
    if not total:
        return "delta_unattributable"
    top = sorted([w for w in windows if isinstance(w.get("delta_bp"), (int, float))],
                 key=lambda w: -abs(w["delta_bp"]))[:top_k]
    share = 100.0 * sum(abs(w["delta_bp"]) for w in top) / total
    row["top_share_of_delta_pct"] = round(share, 1)
    if share >= 50.0:
        return "delta_is_one_window"
    if share >= 25.0:
        return "delta_is_a_few_windows"
    return "delta_is_broad"


_REPAIRSTEP_MIN_STEP = 0.005        # rep/raw moving less than 0.5% is not a step
_REPAIRSTEP_CANCEL_TOL_PCT = 2.0    # a print is "removed" if the session reads under this
_REPAIRSTEP_PRINT_PCT = 100.0       # same family as the E104 reads_beyond_100pct line


def _ratio_walk(rprices, uprices, nm, cal, i0, i1):
    """(ratio, raw_ret_pct, rep_ret_pct) per session in [i0, i1] on priced pairs.

    Reads the arm-vs-raw level ratio over consecutive PRICED closes, so a
    suspended bar does not turn a moving ratio into a step.
    """
    rc = (rprices.get(nm) or [None] * len(cal))
    uc = (uprices.get(nm) or [None] * len(cal))
    out, prev = [], None
    for i in range(max(0, i0), min(len(cal), i1 + 1)):
        r, u = rc[i], uc[i]
        if not r or not u:
            continue
        ratio = r / u
        rec = {"date": cal[i], "ratio": ratio, "step": None,
               "raw_ret_pct": None, "rep_ret_pct": None}
        if prev:
            rec["step"] = ratio / prev["ratio"]
            rec["raw_ret_pct"] = 100.0 * (u / prev["u"] - 1.0)
            rec["rep_ret_pct"] = 100.0 * (r / prev["r"] - 1.0)
        rec["r"], rec["u"] = r, u
        out.append(rec)
        prev = rec
    return out


def run_repairstep(outdir, start="2018-01-01", exclude=("sh511",), gap_limit=1,
                   published="HELDSPLIT-20261026-s2018.json"):
    """E106: does the repaired arm step AT the print, and in which direction?

    E104 flagged %d reads past +/-100%% inside unchanged holdings and left one
    witness unexplained: sh510580 reads +1464%% in the repaired arm where the
    raw series reads +295%%. A forward-adjustment repair must (a) put its step
    on the session that carries the print and (b) cancel it, leaving a sane
    one-session read. This leg tests both properties for every flagged window
    and publishes, beside the face's own read, the read the same step would give
    with the reciprocal factor -- so "the fix is the broken side" is a number,
    not an opinion.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]
    idx = {d: i for i, d in enumerate(cal)}

    gap_label = "neutralise_gap%d" % int(gap_limit)
    repaired, reports = panel_screen.screen_universe(
        raw, mode="neutralise_gap", cal=cal_full, gap_limit=int(gap_limit))

    def price_axis(univ):
        out = {}
        for s in set(univ) | set(raw):
            c = univ.get(s, ({}, {}))[0]
            out[s] = [c.get(d) for d in cal]
        return out

    rp, up = price_axis(repaired), price_axis(raw)

    face = os.path.join(outdir, published)
    with open(face, "r", encoding="utf-8") as fh:
        held = json.load(fh)
    flagged = []
    for cell in held["cells"]:
        rb = cell.get("reads_beyond_100pct") or {}
        nxt = {w["date"]: w.get("next") for w in (cell.get("windows") or [])}
        for w in rb.get("windows") or []:
            for nm in sorted(set(w.get("names_gap") or [])
                             | set(w.get("names_unscreened") or [])):
                flagged.append({"era": cell["era"], "book": cell["book"],
                                "name": nm, "date": w["date"],
                                "next": nxt.get(w["date"]),
                                "flagged_by": ("gap" if nm in (w.get("names_gap") or [])
                                               else "unscreened")})
    seen, windows = set(), []
    for f in flagged:
        k = (f["name"], f["date"], f["next"])
        if k in seen or f["next"] is None:
            continue
        seen.add(k)
        windows.append(f)

    rows, asserts = [], {"steps_tested": 0, "ratio_product_mismatch": 0}
    for w in windows:
        nm, d0, d1 = w["name"], w["date"], w["next"]
        i0, i1 = idx.get(d0), idx.get(d1)
        row = dict(w)
        if i0 is None or i1 is None:
            row["verdict"] = "no_calendar_endpoint"
            rows.append(row)
            continue
        walk = [x for x in _ratio_walk(rp, up, nm, cal, i0 - 1, i1)]
        inside = [x for x in walk if x["step"] is not None and x["date"] > d0]
        first = next((x for x in walk if x["date"] == d0), None)
        last = next((x for x in walk if x["date"] == d1), None)
        if not first or not last:
            row["verdict"] = "missing_bars_at_window_ends"
            rows.append(row)
            continue
        raw_read = 100.0 * (last["u"] / first["u"] - 1.0)
        arm_read = 100.0 * (last["r"] / first["r"] - 1.0)
        total = last["ratio"] / first["ratio"]
        prod = 1.0
        for x in inside:
            prod *= x["step"]
        if abs(prod / total - 1.0) > 1e-6:
            asserts["ratio_product_mismatch"] += 1
        asserts["steps_tested"] += len(inside)

        steps = [x for x in inside if abs(x["step"] - 1.0) > _REPAIRSTEP_MIN_STEP]
        largest = max(steps, key=lambda x: abs(x["step"] - 1.0)) if steps else None
        if not steps:
            verdict = ("arm_untouched_raw_print" if abs(total - 1.0) < 1e-9
                       else "no_step_but_reads_differ")
        else:
            cancels = [x for x in steps
                       if abs(x.get("rep_ret_pct") or 0.0) <= _REPAIRSTEP_CANCEL_TOL_PCT
                       and abs(x.get("raw_ret_pct") or 0.0)
                       > _REPAIRSTEP_PRINT_PCT - 1e-9]
            amplifies = [x for x in steps
                         if (x.get("raw_ret_pct") is not None
                             and abs(x["raw_ret_pct"]) > _REPAIRSTEP_PRINT_PCT - 1e-9
                             and abs(x.get("rep_ret_pct") or 0.0)
                             > abs(x["raw_ret_pct"]))]
            unprinted = [x for x in steps
                         if (x.get("raw_ret_pct") or 0.0) is not None
                         and abs(x.get("raw_ret_pct") or 0.0)
                         <= _REPAIRSTEP_PRINT_PCT - 1e-9]
            if amplifies:
                verdict = "step_amplifies_print"
            elif cancels:
                verdict = "step_cancels_print"
            elif unprinted:
                verdict = "step_without_a_print"
            else:
                verdict = "step_partially_cancels"
        row.update({
            "raw_read_pct": round(raw_read, 2),
            "arm_read_pct": round(arm_read, 2),
            "ratio_at_window_start": round(first["ratio"], 6),
            "ratio_at_window_end": round(last["ratio"], 6),
            "largest_step": ({"date": largest["date"],
                              "factor": round(largest["step"], 6),
                              "raw_ret_pct": round(largest.get("raw_ret_pct") or 0.0, 2),
                              "rep_ret_pct": round(largest.get("rep_ret_pct") or 0.0, 2),
                              "raw_ret_cancelled_by_the_step": (
                                  abs(largest.get("rep_ret_pct") or 0.0)
                                  <= _REPAIRSTEP_CANCEL_TOL_PCT)}
                             if largest else None),
            "steps_inside_window": len(steps),
            "verdict": verdict,
        })
        if largest and verdict in ("step_amplifies_print", "step_without_a_print"):
            # the same print with the reciprocal (cancelling) factor: the step
            # factor IS the amplification, so dividing the raw read by it once
            # gives what the arm would have read had the factor been applied the
            # other way. Publishing it keeps "the fix is the broken side" a number.
            row["reciprocal_factor_read_pct"] = round(
                (1.0 + raw_read / 100.0) / largest["step"] * 100.0 - 100.0, 2)
        rows.append(row)

    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    fabricating = [r for r in rows
                   if r["verdict"] in ("step_amplifies_print", "step_without_a_print")]
    worst = max(fabricating, key=lambda r: abs(r["arm_read_pct"])) if fabricating else None
    return {
        "study": "e106_repair_step_consistency",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "exclude_prefixes": list(exclude),
            "arm": gap_label, "gap_limit": int(gap_limit),
            "population": ("every name the E104 face flagged as reading past "
                           "+/-100%% inside an unchanged holding, deduplicated "
                           "by (name, window) -- the witness list, not a screen"),
            "step": ("a session where rep/raw moves more than %g; the step "
                     "factor, the raw one-session read there and the repaired "
                     "one-session read are published together"
                     % _REPAIRSTEP_MIN_STEP),
            "consistency_tests": {
                "placed_at_a_print": "|raw one-session read| > 100% on the step session",
                "cancels_the_print": ("|repaired one-session read| <= %g%% on that "
                                      "session" % _REPAIRSTEP_CANCEL_TOL_PCT),
                "amplifies_the_print": ("|repaired read| > |raw read| on that session "
                                        "= the factor was applied the wrong way"),
            },
            "reciprocal_factor_read": ("(1+arm_read)/step - 1 = the read the same "
                                       "step gives with the reciprocal factor"),
        },
        "screen_reports": reports,
        "windows": rows,
        "answers": {
            "flagged_windows": len(rows),
            "verdict_tally": tally,
            "steps_tested": asserts["steps_tested"],
            "ratio_product_mismatch": asserts["ratio_product_mismatch"],
            "fabricating_windows": len(fabricating),
            "worst": ({k: worst[k] for k in
                       ("name", "era", "book", "date", "next", "verdict",
                        "raw_read_pct", "arm_read_pct", "largest_step",
                        "reciprocal_factor_read_pct")} if worst else None),
            "reading": (("none of the %d flagged reads is fabricated by a wrong-side "
                         "step: every step sits on a print and cancels it or leaves "
                         "an unrepaired raw print" % len(rows))
                        if not fabricating else
                        ("%d of %d flagged reads are fabricated by the repair itself: "
                         "the step sits on the print but multiplies instead of "
                         "dividing, so the arm reads worse than the raw series"
                         % (len(fabricating), len(rows)))),
        },
        "honest": [
            "descriptive census only: no gate, no verdict on the strategy, no "
            "prereg, no trial count, no ledger booking",
            "a step is judged against the panel's own one-session reads, not "
            "against a vendor corporate-action file; a real 1:N conversion and a "
            "misprint look identical here, and the step test says nothing about "
            "which of the two a name is",
            "plan_screen's repair semantics belong to panel_screen.neutralise; this "
            "leg publishes the defect but does not change any screened arm",
            "reciprocal_factor_read is arithmetic on the published step, not a "
            "re-burn: the arms' other bars are untouched",
        ],
    }


def run_heldsplit(outdir, start="2018-01-01", pick_n=9999, exclude=("sh511",),
                  gap_limit=1, mid_day=15, eras=ERAS, top_k=3):
    """E104: is a split print visible inside an UNCHANGED holding, and how big.

    E100 closed the gap arm as a price-read story but had to say that "a split
    inside an unchanged holding would be invisible here even though it still
    moves the book's curve". This leg measures that blind spot directly: for
    every transition, take the names the repair arm held at BOTH ends (they
    enter no swap list), read them forward under each arm's prices, and publish
    the mean read, the per-name contributors and the largest single-name read.

    The same per-window read answers E105: every era-book level whose
    transitions are few is a mean over few names, so it is published beside the
    largest single-name read and that name's share of the window mean.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]

    gap_label = "neutralise_gap%d" % int(gap_limit)
    universes = {"unscreened": raw}
    universes[gap_label], reports = panel_screen.screen_universe(
        raw, mode="neutralise_gap", cal=cal_full, gap_limit=int(gap_limit))
    arms = ["unscreened", gap_label]

    calendars = [("me", sorted(set(base.month_end_indices(cal)))),
                 ("mid", _mid_month_indices(cal, mid_day))]

    caches = {}
    for label in arms:
        univ = universes[label]
        all_syms = sorted(set(base.LADDER) | set(univ))
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = univ.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms if s in univ]
        rank_cache = {}
        decisions = {}
        for cname, idxs in calendars:
            decisions[cname] = _decision_sets(cal, prices, amounts, universe,
                                              pick_n, idxs, rank_cache)
        caches[label] = {"prices": prices, "decisions": decisions,
                         "universe_members": len(universe)}

    def arm_holdings(label, book, era_row):
        decs = caches[label]["decisions"][book]
        grid = _era_end_grid(decs, cal, era_row, 1)
        if not grid:
            return None
        nxt = _next_decision_session(decs, cal, grid[-1])
        window_end = nxt or cal[-1]
        dec = _truncate_decisions(decs, cal, window_end)
        return {"hold": {cal[i]: (i, set(h)) for i, h in dec},
                "window_end": window_end, "prices": caches[label]["prices"]}

    cells = []
    for era_row in eras:
        for book in LEVEL_BOOKS:
            a = arm_holdings("unscreened", book, era_row)
            b = arm_holdings(gap_label, book, era_row)
            row = {"era": era_row[0], "book": book, "arm": gap_label,
                   "window_end": (b or {}).get("window_end") or (a or {}).get("window_end")}
            if not a or not b:
                row.update({"skipped": "no decision ends for this era/book",
                            "persistent_reads": 0, "verdict": "no_unchanged_holdings"})
                cells.append(row)
                continue
            dates = sorted(set(a["hold"]) & set(b["hold"]))
            windows = []
            for d, nd in zip(dates, dates[1:]):
                if _era_of(d, eras) != era_row[0]:
                    continue
                i0 = a["hold"][d][0]
                i1 = a["hold"][nd][0]
                split = _held_read_split(b["prices"], a["prices"],
                                         b["hold"][d][1], b["hold"][nd][1],
                                         i0, i1, top_k=top_k)
                if not split["persistent_names"]:
                    continue
                split.update({"date": d, "next": nd})
                windows.append(split)

            if not windows:
                row.update({"persistent_reads": 0, "windows": [],
                            "verdict": "no_unchanged_holdings"})
                cells.append(row)
                continue
            deltas = [w["delta_bp"] for w in windows]
            nonzero = [w for w in windows if abs(w["delta_bp"]) > 1e-9]
            reads = sum(w["persistent_names"] for w in windows)
            biggest = max((w["max_abs_read"] for w in windows),
                          key=lambda r: abs(r["unscreened_fwd_pct"]))
            movers = sorted(windows, key=lambda w: -abs(w["delta_bp"]))[:top_k]
            beyond = {
                "gap": sum(w["reads_beyond_100pct"]["gap"] for w in windows),
                "unscreened": sum(w["reads_beyond_100pct"]["unscreened"]
                                  for w in windows),
                "windows": [{"date": w["date"],
                             **w["reads_beyond_100pct"]}
                            for w in windows
                            if w["reads_beyond_100pct"]["gap"]
                            or w["reads_beyond_100pct"]["unscreened"]][:6],
            }
            row.update({
                "persistent_reads": reads,
                "windows": [{"date": w["date"], "next": w["next"],
                             "persistent_names": w["persistent_names"],
                             "gap_mean_pct": w["gap_mean_pct"],
                             "unscreened_mean_pct": w["unscreened_mean_pct"],
                             "delta_bp": w["delta_bp"],
                             "residual_bp": w["residual_bp"],
                             "top": w["top"],
                             "max_abs_read": w["max_abs_read"]}
                            for w in windows],
                "transitions": len(windows),
                "reads_beyond_100pct": beyond,
                "windows_with_a_split_pct": round(100.0 * len(nonzero) / len(windows), 1),
                "delta_mean_bp": round(sum(deltas) / len(deltas), 2),
                "delta_max_abs_bp": round(max(deltas, key=abs), 2),
                "largest_single_name_read": dict(biggest, date=next(
                    w["date"] for w in windows if w["max_abs_read"] is biggest)),
                "top": movers,
            })
            row["verdict"] = _held_split_verdict(row, top_k=top_k)
            cells.append(row)

    measured = [c for c in cells if isinstance(c.get("delta_mean_bp"), (int, float))]
    with_split = [c for c in measured if abs(c["delta_mean_bp"]) > 1e-9]
    verdict_tally = {}
    for c in measured:
        verdict_tally[c.get("verdict")] = verdict_tally.get(c.get("verdict"), 0) + 1
    largest = sorted(({"era": c["era"], "book": c["book"],
                       **c["largest_single_name_read"]} for c in measured),
                     key=lambda r: -abs(r["unscreened_fwd_pct"]))[:8]
    return {
        "study": "e104_held_name_split_exposure",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "mid_month_day": mid_day, "arms": arms, "gap_limit": int(gap_limit),
            "top_k": top_k,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": list(LEVEL_BOOKS),
            "populations": "names held by the repair arm at BOTH ends of the window "
                           "(no swap, so E100's entrant/exit lists cannot see them)",
            "cell": "mean over the era's windows of 100*(mean_gap_read - "
                    "mean_unscreened_read) in bp, on the same names and dates",
            "additivity": "each name contributes 100*(g_u - u_u)/n, so the pieces sum "
                          "to the window delta; residual published, never assumed 0",
            "e105_column": "largest_single_name_read = the name with the biggest "
                           "absolute read in the window, with its share of that "
                           "window's mean -- a level over few transitions is a mean "
                           "over few names and must be published with it",
        },
        "screen_reports": reports,
        "cells": cells,
        "answers": {
            "cells_measured": len(measured),
            "cells_with_a_split": len(with_split),
            "verdict_tally": verdict_tally,
            "largest_unchanged_holding_splits": [
                {"era": c["era"], "book": c["book"],
                 "delta_mean_bp": c["delta_mean_bp"],
                 "delta_max_abs_bp": c["delta_max_abs_bp"],
                 "windows_with_a_split_pct": c["windows_with_a_split_pct"],
                 "verdict": c["verdict"],
                 "largest_window": (c["top"][0] if c["top"] else None)}
                for c in sorted(with_split, key=lambda c: -abs(c["delta_mean_bp"]))[:6]],
            "largest_single_name_reads": largest,
            "implausible_reads": {
                "gap_total": sum(c["reads_beyond_100pct"]["gap"] for c in measured),
                "unscreened_total": sum(c["reads_beyond_100pct"]["unscreened"]
                                        for c in measured),
                "cells": [{"era": c["era"], "book": c["book"],
                           "gap": c["reads_beyond_100pct"]["gap"],
                           "unscreened": c["reads_beyond_100pct"]["unscreened"],
                           "windows": c["reads_beyond_100pct"]["windows"]}
                          for c in measured
                          if c["reads_beyond_100pct"]["gap"]
                          or c["reads_beyond_100pct"]["unscreened"]],
                "reading": "a read past +/-100% in one window is a print artefact, "
                           "not a return; both arms are counted because the repair "
                           "is not automatically the plausible side",
            },
            "reading": ("no split print reaches an unchanged holding on this panel: "
                        "every window's persistent names read identically in both "
                        "arms" if not with_split else
                        "a split print does sit inside unchanged holdings on %d of %d "
                        "cells; the largest is %s/%s at %s"
                        % (len(with_split), len(measured),
                           max(with_split, key=lambda c: abs(c["delta_mean_bp"]))["era"],
                           max(with_split, key=lambda c: abs(c["delta_mean_bp"]))["book"],
                           round(max(with_split,
                                     key=lambda c: abs(c["delta_mean_bp"]))["delta_mean_bp"], 1))),
        },
        "honest": [
            "descriptive census only: no gate, no verdict on the strategy, no "
            "prereg, no trial count, no ledger booking",
            "the population is the REPAIR arm's persistent names; where the two arms "
            "hold different names the unscreened arm's own persistent set is not "
            "measured here (that is E100's swap face, not this one)",
            "an equal-weight mean of name-level reads is not a portfolio return",
            "a split read is inferred from the shape of the read plus the repair's own "
            "report, not proven against a vendor corporate-action file",
        ],
    }


def run_gaparm_topnames(outdir, start="2018-01-01", pick_n=9999, exclude=("sh511",),
                        gap_limit=1, mid_day=15, eras=ERAS, top_k=3,
                        published="MID-20261026-s20180101-armed.json"):
    """E100: name the transitions that carry the gap arm's two large LEVEL moves.

    E99 published the arm as a difference of levels (-745.9bp on 2017_2020 me,
    -1098.3bp on 2021_2023 me); E101 and E103 then showed the DELTA survives the
    end grid and the limit ladder while the levels themselves do not. A delta
    nobody can name is still unauditable, so this leg splits each cell's delta
    additively over the transitions (E91's full_churn rows) and publishes the
    window, the swapped tickers, and the names each arm actually held there.

    The level is recomputed with E103's own recipe -- the era's last decision
    end priced through the next decision of the same book -- so the split sums
    to the published number rather than to a nearby one.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    raw = e27.load_universe()
    if exclude:
        raw = {s: v for s, v in raw.items() if not s.startswith(tuple(exclude))}
    cal_full = base.load_panel()[0]
    cutoff = cal_full[-1]
    cal = [d for d in cal_full if d >= start]

    gap_label = "neutralise_gap%d" % int(gap_limit)
    universes = {"unscreened": raw}
    universes[gap_label], reports = panel_screen.screen_universe(
        raw, mode="neutralise_gap", cal=cal_full, gap_limit=int(gap_limit))
    arms = ["unscreened", gap_label]

    calendars = [("me", sorted(set(base.month_end_indices(cal)))),
                 ("mid", _mid_month_indices(cal, mid_day))]

    caches = {}
    for label in arms:
        univ = universes[label]
        all_syms = sorted(set(base.LADDER) | set(univ))
        prices, amounts = {}, {}
        for s in all_syms:
            c, a = univ.get(s, ({}, {}))
            prices[s] = [c.get(d) for d in cal]
            amounts[s] = [a.get(d) for d in cal]
        universe = [s for s in all_syms if s in univ]
        rank_cache = {}
        decisions = {}
        for cname, idxs in calendars:
            decisions[cname] = _decision_sets(cal, prices, amounts, universe,
                                              pick_n, idxs, rank_cache)
        caches[label] = {"prices": prices, "decisions": decisions,
                         "universe_members": len(universe)}

    def era_arm(arm, book, era_row):
        """One arm's churn rows for one era, on the level's own decision list."""
        name = era_row[0]
        decs = caches[arm]["decisions"][book]
        grid = _era_end_grid(decs, cal, era_row, 1)
        if not grid:
            return None
        nxt = _next_decision_session(decs, cal, grid[-1])
        window_end = nxt or cal[-1]
        dec = _truncate_decisions(decs, cal, window_end)
        rows, agg = _churn_stats(cal, caches[arm]["prices"], dec, eras,
                                 with_names=True)
        live = {r["date"]: r for r in rows
                if r.get("era") == name
                and isinstance(r.get("churn_alpha_bp"), (int, float))}
        hold = {cal[i]: (i, set(h)) for i, h in dec}
        return {"window_end": window_end, "rows": live, "hold": hold,
                "prices": caches[arm]["prices"],
                "level_bp": (agg.get(name) or {}).get("churn_alpha_bp_mean"),
                "negative_share_pct": (agg.get(name) or {}).get("negative_churn_share_pct")}

    pub_index, pub_meta = _read_published_levels(outdir, published)

    cells, ctrl_diff, carrier_counts = [], [], {}
    driver_counts = {}
    same_book_windows = 0
    for era_row in eras:
        for book in LEVEL_BOOKS:
            a = era_arm("unscreened", book, era_row)
            b = era_arm(gap_label, book, era_row)
            row = {"era": era_row[0], "book": book, "arm": gap_label,
                   "window_end": (b or {}).get("window_end") or (a or {}).get("window_end")}
            if not a or not b or not a["rows"] or not b["rows"]:
                row["skipped"] = "no measurable churn cell for both arms in this era"
                row["levels_bp"] = {"unscreened": (a or {}).get("level_bp"),
                                    gap_label: (b or {}).get("level_bp")}
                row["delta_bp"] = None
                row["verdict"] = "no_delta"
                cells.append(row)
                continue
            pieces, meta = _arm_delta_contrib(b["rows"], a["rows"])
            top = sorted(pieces, key=lambda r: -abs(r["contrib_bp"]))[:top_k]
            named = []
            for r in top:
                gset = (b["hold"].get(r["date"]) or (None, set()))[1]
                uset = (a["hold"].get(r["date"]) or (None, set()))[1]
                grows = b["rows"].get(r["date"]) or {}
                urows = a["rows"].get(r["date"]) or {}
                g_i0 = (b["hold"].get(r["date"]) or (None,))[0]
                g_i1 = (b["hold"].get(grows.get("next") or "") or (None,))[0]
                u_i0 = (a["hold"].get(r["date"]) or (None,))[0]
                u_i1 = (a["hold"].get(urows.get("next") or "") or (None,))[0]
                entry = {
                    "date": r["date"],
                    "next": grows.get("next") or urows.get("next"),
                    "side": r["side"],
                    "contrib_bp": round(r["contrib_bp"], 1),
                    "gap_bp": r["gap_bp"], "unscreened_bp": r["unscreened_bp"],
                    "alpha_change_bp": (round(r["gap_bp"] - r["unscreened_bp"], 1)
                                        if isinstance(r["gap_bp"], (int, float))
                                        and isinstance(r["unscreened_bp"], (int, float))
                                        else None),
                    "held_only_in_gap": sorted(gset - uset)[:10],
                    "held_only_in_unscreened": sorted(uset - gset)[:10],
                    "members_gap": len(gset), "members_unscreened": len(uset),
                    "entrant_names_gap": (grows.get("entrant_names") or [])[:8],
                    "exit_names_gap": (grows.get("exit_names") or [])[:8],
                    "drivers": _window_drivers(
                        grows, urows, b["prices"], a["prices"],
                        g_i0, g_i1, u_i0, u_i1) if r["side"] == "both" else [],
                }
                named.append(entry)
                for nm in (entry["held_only_in_gap"]
                           + entry["held_only_in_unscreened"]):
                    carrier_counts[nm] = carrier_counts.get(nm, 0) + 1
                for d in entry["drivers"]:
                    driver_counts[d["name"]] = driver_counts.get(d["name"], 0) + 1
                if entry["drivers"] and not (entry["held_only_in_gap"]
                                             or entry["held_only_in_unscreened"]):
                    same_book_windows += 1
            delta = meta["delta_bp"]
            top_sum = sum(n["contrib_bp"] for n in named)
            row.update({
                "transitions": {"unscreened": meta["unscreened_n"],
                                gap_label: meta["gap_n"]},
                "levels_bp": {"unscreened": meta["level_unscreened_bp"],
                              gap_label: meta["level_gap_bp"]},
                "delta_bp": delta,
                "neg_share_pct": {"unscreened": a["negative_share_pct"],
                                  gap_label: b["negative_share_pct"]},
                "contrib_pieces": len(pieces),
                "sum_top_contrib_bp": round(top_sum, 1),
                "top_share_of_delta_pct": (round(100.0 * top_sum / delta, 1)
                                           if delta else None),
                "residual_bp": meta["residual_bp"],
                "one_sided_transitions": {"gap_only": meta["gap_only_transitions"],
                                          "unscreened_only":
                                              meta["unscreened_only_transitions"]},
                "top": named,
            })
            row["verdict"] = _arm_split_verdict(row, top_k=top_k)
            theirs = ((pub_index or {}).get((era_row[0], book)) or {}).get(gap_label) or {}
            t = theirs.get("delta_vs_unscreened_bp")
            row["published_delta_bp"] = t
            row["abs_diff_vs_published_bp"] = (
                round(abs(t - delta), 1)
                if isinstance(t, (int, float)) and isinstance(delta, (int, float))
                else None)
            if row["abs_diff_vs_published_bp"] is not None \
                    and row["abs_diff_vs_published_bp"] > 0.05:
                ctrl_diff.append({"era": era_row[0], "book": book,
                                  "abs_diff_bp": row["abs_diff_vs_published_bp"]})
            cells.append(row)

    measured = [c for c in cells if isinstance(c.get("delta_bp"), (int, float))]
    movers = sorted(measured, key=lambda c: -abs(c["delta_bp"]))
    large = [c for c in movers if abs(c["delta_bp"]) >= 50.0]
    carriers = sorted(carrier_counts.items(), key=lambda kv: -kv[1])
    drivers = sorted(driver_counts.items(), key=lambda kv: -kv[1])
    verdict_tally = {}
    for c in measured:
        verdict_tally[c["verdict"]] = verdict_tally.get(c["verdict"], 0) + 1

    return {
        "study": "e100_gaparm_transition_names",
        "evidence_cutoff": cutoff,
        "spec": {
            "start": start, "pick_n": pick_n, "exclude_prefixes": list(exclude),
            "mid_month_day": mid_day, "arms": arms, "gap_limit": int(gap_limit),
            "top_k": top_k,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in eras],
            "books": list(LEVEL_BOOKS),
            "cell": "eras[era][book].churn_alpha_bp_mean (the E99 LEVEL), recomputed "
                    "with E103's recipe: the era's last decision end priced through "
                    "the next decision of the same book",
            "split": "level_arm = equal-weight mean over THAT arm's own transitions, "
                     "so each shared transition contributes a_gap/n_gap - "
                     "a_unscreened/n_unscreened; one-sided dates contribute their own "
                     "term; residual = delta - sum(pieces) is published, never assumed 0",
            "name_rule": "the names published per window are the holdings that appear "
                         "in one arm and not the other at that decision plus the "
                         "engine's own entrant/exit lists (truncated to 10/8)",
            "move_rule": "a cell is LARGE when |delta| >= 50bp, the threshold the two "
                         "published moves (745.9 / 1098.3) are read at",
        },
        "screen_reports": reports,
        "cells": cells,
        "answers": {
            "moves_named": [{"era": c["era"], "book": c["book"],
                             "delta_bp": c["delta_bp"], "verdict": c["verdict"],
                             "top_share_of_delta_pct": c["top_share_of_delta_pct"],
                             "largest_window": (c["top"][0] if c["top"] else None)}
                            for c in large],
            "large_moves": len(large),
            "verdict_tally": verdict_tally,
            "top_carrier_names": [{"name": n, "windows": k} for n, k in carriers[:10]],
            "distinct_names_in_top_windows": len(carriers),
            "price_read_driver_names": [{"name": n, "windows": k}
                                        for n, k in drivers[:10]],
            "distinct_price_driver_names": len(drivers),
            "top_windows_with_identical_holdings": same_book_windows,
            "reading": ("the two arms hold the same names at every top window that "
                        "carries a large move, so the delta is a PRICE-READ "
                        "difference, not a composition difference"
                        if same_book_windows and not carriers else
                        "the top windows change composition as well as reads; read "
                        "held_only_in_gap / held_only_in_unscreened per window"),
            "control_reproduces_published": not ctrl_diff,
            "control_mismatches": ctrl_diff,
            "reads_as": (
                "no level delta of 50bp or more exists between these arms on this "
                "panel, so there is nothing to name"
                if not large else
                "the %d largest arm deltas are split into named windows: %s"
                % (len(large),
                   "; ".join("%s/%s %.1fbp -> %s (%s, top-%d share %s%%)"
                             % (c["era"], c["book"], c["delta_bp"], c["verdict"],
                                (c["top"][0]["date"] if c["top"] else "n/a"),
                                len(c["top"]),
                                c["top_share_of_delta_pct"])
                             for c in large))),
        },
        "honest": [
            "descriptive census only: no gate, no verdict on the strategy, no "
            "prereg, no trial count, no ledger booking",
            "an equal-weight mean of name-level reads is not a portfolio return: the "
            "split moves a reading, not money",
            "the split is exact for THIS panel at THIS cutoff; a refreshed panel can "
            "add or lose a decision date and move the one-sided terms, which is why "
            "they are published separately from the shared ones",
            "naming a window names the swap that carried the reading; it does not "
            "claim the repair caused the forward returns inside it",
        ],
    }


def main(argv):
    ap = argparse.ArgumentParser(description="E39 panel census (descriptive, offline)")
    ap.add_argument("mode", nargs="?", default="all",
                    choices=["stale", "mtime", "ladder", "month", "pair", "cashdrag",
                             "tilt", "rebalday", "era", "spreadsize", "tiltera",
                             "calcost", "e42", "e43", "tilt4", "widecomp", "neutralrob",
                             "e44", "burnin", "knife", "skinloo", "e45", "warmspread",
                             "e46", "livespan", "cutcurve", "midmonth", "chase",
                             "midsweep", "entrydelay", "earlydelay", "neighborhood",
                             "weeklyclash", "weeknames", "stalehold", "staletail",
                             "panelsplit", "screenreg", "screencalc", "screenspread",
                             "screenrob", "screentilt", "screenwide", "screenweek",
                             "midscreen", "churngap", "singleprint", "robustchurn",
                             "loodist", "churnse", "burncontrol", "topnames",
                             "gapsplit", "screengapera", "tiltstable",
                             "endchoice",
                             "midlevels", "gaparmendgrid", "gaparmfamily",
                             "gaplimit", "gaptop3", "heldsplit", "repairstep",
                             "all", "selftest"])
    ap.add_argument("--month", default=None, help="YYYY-MM for the month attribution leg")
    ap.add_argument("--cost", type=float, default=1.0, help="cost multiple (e46 livespan leg)")
    ap.add_argument("--parts", type=int, default=2, help="chunks per era (e46 livespan leg)")
    ap.add_argument("--start", default="2020-01-01", help="window start (midmonth leg)")
    ap.add_argument("--costs", default="",
                    help="comma-separated cost multiples (midsweep leg, e.g. 0,3)")
    ap.add_argument("--lags", default="1,3,5,10",
                    help="comma-separated decision lags in sessions (entrydelay leg)")
    ap.add_argument("--neighbors", default="2",
                    help="comma-separated new magnitudes in sessions (neighborhood leg)")
    ap.add_argument("--gaps", default="1,2,5",
                    help="comma-separated gap limits in sessions (gapsplit leg)")
    ap.add_argument("--max-limit", type=int, default=20,
                    help="top of the gap_limit ladder (gaplimit leg)")
    args = ap.parse_args(argv)

    if args.mode == "selftest":
        return selftest()
    if args.mode in ("stale", "all"):
        f = run_stale(os.path.join(ROOT, "results", "e39_stale_two"))
        p = write_json(os.path.join(ROOT, "results", "e39_stale_two"),
                       "CENSUS-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "stale", "file": os.path.relpath(p, ROOT),
                          "stale_panels": f["stale_panels"],
                          "classes": {r["file"]: r["class"] for r in f["findings"]}},
                         ensure_ascii=False))
    if args.mode in ("mtime", "all"):
        f, pockets = run_mtime(None)
        outdir = os.path.join(ROOT, "results", "e39_panel_mtime")
        p = write_json(outdir, "CENSUS-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        with open(os.path.join(outdir, "data_face.csv"), "w", encoding="utf-8", newline="\n") as fh:
            w = csv.DictWriter(fh, fieldnames=["file", "mtime", "bytes", "rows", "last_bar",
                                               "rows_after_bulk_import"])
            w.writeheader()
            for row in pockets:
                w.writerow(row)
        print(json.dumps({"leg": "mtime", "file": os.path.relpath(p, ROOT),
                          "files_touched": f["refresh_wave"]["files_touched"],
                          "rows_carried": f["refresh_wave"]["rows_after_bulk_import_carried"],
                          "totals": f["totals"]}, ensure_ascii=False))
    if args.mode in ("ladder", "all"):
        f = run_ladder(None)
        outdir = os.path.join(ROOT, "results", "e39_ladder_risk")
        p = write_json(outdir, "LADDER-RISK-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "ladder", "file": os.path.relpath(p, ROOT),
                          "windows": {k: {"ann": v["ann_return_pct"],
                                          "maxdd": v["max_drawdown_pct"],
                                          "worst_month": v["worst_month"]}
                                      for k, v in f["windows"].items()}}, ensure_ascii=False))
    if args.mode == "pair":
        f = run_pair(None)
        outdir = os.path.join(ROOT, "results", "e40_pair_drawdown")
        p = write_json(outdir, "PAIR-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "pair", "file": os.path.relpath(p, ROOT),
                          "windows": {k: {"ann": {kk: vv["ann_return_pct"]
                                                  for kk, vv in v["profiles"].items()},
                                          "maxdd": {kk: vv["max_drawdown_pct"]
                                                    for kk, vv in v["profiles"].items()},
                                          "answers": v["answers"]}
                                      for k, v in f["windows"].items()}},
                         ensure_ascii=False))
        return 0
    if args.mode == "cashdrag":
        f = run_cashdrag(None)
        outdir = os.path.join(ROOT, "results", "e40_cashleg_drag")
        p = write_json(outdir, "CASHLeg-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "cashdrag", "file": os.path.relpath(p, ROOT),
                          "windows": {k: {"answers": v["answers"],
                                          "cash": v["cash_mechanism"],
                                          "ann": {n: {kk: r.get("ann_return_pct")
                                                      for kk, r in rows.items()}
                                                  for n, rows in v["schemes"].items()}}
                                      for k, v in f["windows"].items()}},
                         ensure_ascii=False))
        return 0
    if args.mode == "tilt":
        f = run_tilt(None)
        outdir = os.path.join(ROOT, "results", "e40_ladder_tilt")
        p = write_json(outdir, "TILT-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "tilt", "file": os.path.relpath(p, ROOT),
                          "windows": {k: {"tilt_annualised_bp": v["monthly"]["tilt_annualised_bp"],
                                          "tilt_sd_bp": v["monthly"]["tilt_sd_bp"],
                                          "beta": v["exposure_regression"]["beta_ladder_on_tilt"],
                                          "r2_pct": v["exposure_regression"]["tilt_explains_ladder_var_pct"],
                                          "worst_month": (v["worst_month_diagnostic"] or {}).get("month")}
                                      for k, v in f["windows"].items()}},
                         ensure_ascii=False))
        return 0
    if args.mode == "rebalday":
        f = run_rebalday(None)
        outdir = os.path.join(ROOT, "results", "e41_rebal_day")
        p = write_json(outdir, "SHIFT-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "rebalday", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"]}, ensure_ascii=False))
        return 0
    if args.mode == "era":
        f = run_era(None)
        outdir = os.path.join(ROOT, "results", "e41_spread_era")
        p = write_json(outdir, "ERA-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "era", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"],
                          "eras": {k: {"bars": v["bars"],
                                       "spread_bp": v.get("spread_ann_bp"),
                                       "ratio_dd": (v.get("ratio_path") or {}).get("max_drawdown_pct")}
                                   for k, v in f["eras"].items()}}, ensure_ascii=False))
        return 0
    if args.mode in ("spreadsize", "tiltera", "e42"):
        core = _monthly_core()
        if args.mode in ("spreadsize", "e42"):
            f = run_spreadsize(None, core=core)
            outdir = os.path.join(ROOT, "results", "e42_spread_size_neutral")
            p = write_json(outdir, "NEUTRAL-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
            print(json.dumps({"leg": "spreadsize", "file": os.path.relpath(p, ROOT),
                              "eras": {k: {"raw_bp": v.get("raw_spread_ann_bp"),
                                           "neutral_bp": v.get("size_neutral_ann_bp"),
                                           "size_bp": v.get("size_component_ann_bp"),
                                           "beta": v.get("beta_spread_on_tilt"),
                                           "r2_pct": v.get("tilt_explains_spread_var_pct")}
                                      for k, v in f["eras"].items()},
                              "answers": f["answers"]}, ensure_ascii=False))
        if args.mode in ("tiltera", "e42"):
            f = run_tilt_era(None, core=core)
            outdir = os.path.join(ROOT, "results", "e42_tilt_era")
            p = write_json(outdir, "TILT-ERA-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
            print(json.dumps({"leg": "tiltera", "file": os.path.relpath(p, ROOT),
                              "eras": {k: {"tilt_bp": v.get("tilt_annualised_bp"),
                                           "beta": v.get("beta_ladder_on_tilt"),
                                           "r2_pct": v.get("tilt_explains_ladder_var_pct")}
                                      for k, v in f["eras"].items()},
                              "answers": f["answers"]}, ensure_ascii=False))
        return 0
    if args.mode == "midlevels":
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        gaps = tuple(int(x) for x in args.gaps.split(",") if x.strip())
        f = run_midlevels(outdir, start=args.start, gap_limits=gaps)
        tag = f["spec"]["start"].replace("-", "")
        p = write_json(outdir, "MID-%s-s%s-armed.json"
                       % (f["evidence_cutoff"].replace("-", ""), tag), f)
        print(json.dumps({"leg": "midlevels", "file": os.path.relpath(p, ROOT),
                          "arms": f["answers"]["arms"],
                          "populated_eras": f["answers"]["populated_eras"],
                          "coverage": f["answers"]["coverage"],
                          "newest_era_level_bp": f["answers"]["newest_era_level_bp"],
                          "sign_flips": f["answers"]["level_sign_flips_across_arms"],
                          "published_control": f["answers"]["published_control"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "gaparmendgrid":
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        f = run_gaparm_endgrid(outdir, start=args.start)
        tag = f["spec"]["start"].replace("-", "")
        p = write_json(outdir, "GAPARM-ENDGRID-%s-s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), tag), f)
        print(json.dumps({"leg": "gaparmendgrid", "file": os.path.relpath(p, ROOT),
                          "arms": f["spec"]["arms"],
                          "measured_eras": f["answers"]["measured_eras"],
                          "delta_span_bp": f["answers"]["delta_span_bp"],
                          "level_span_bp": f["answers"]["level_span_bp"],
                          "stable": f["answers"]["delta_stable_eras"],
                          "moves": f["answers"]["delta_moves_eras"],
                          "control": f["published_control"]["meta"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "gaparmfamily":
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        f = run_gaparm_family_endgrid(outdir, start=args.start)
        tag = f["spec"]["start"].replace("-", "")
        p = write_json(outdir, "GAPARM-FAMILY-ENDGRID-%s-s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), tag), f)
        print(json.dumps({"leg": "gaparmfamily", "file": os.path.relpath(p, ROOT),
                          "arms": f["spec"]["arms"],
                          "measured_eras": f["answers"]["measured_eras"],
                          "zero_ends": f["answers"]["zero_ends"],
                          "step_arms": f["answers"]["step_arms"],
                          "family_identity": {e: {b: v.get("reads_as")
                                                  for b, v in (eid or {}).items()}
                                              for e, eid
                                              in f["answers"]["family_identity"].items()},
                          "control_reproduces_published":
                              f["answers"]["control_reproduces_published"],
                          "reads_as": f["answers"]["reads_as"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "gaplimit":
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        f = run_gap_limit_ladder(outdir, start=args.start, max_limit=args.max_limit)
        p = write_json(outdir, "GAPLIMIT-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "gaplimit", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"],
                          "ladder": [{"limit": r["limit"],
                                      "symbols": r["symbols_rewritten"],
                                      "prints": r["prints_repaired"],
                                      "bars": r["bars_rewritten"],
                                      "signature": r["edit_signature"]}
                                     for r in f["ladder"]],
                          "gap_spectrum": {k: {"gapped": v["gapped_prints"],
                                               "integer_like": v["integer_like"]}
                                           for k, v in
                                           f["gap_spectrum"]["by_gap_sessions"].items()},
                          "cells": [{"era": c["era"], "book": c["book"],
                                     "arms": {k: v["delta_vs_unscreened_bp"]
                                              for k, v in (c["arms"] or {}).items()}}
                                    for c in f["cells"]]},
                         ensure_ascii=False))
        return 0
    if args.mode == "repairstep":
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        f = run_repairstep(outdir, start=args.start)
        p = write_json(outdir, "REPAIRSTEP-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({
            "leg": "repairstep",
            "file": os.path.relpath(p, ROOT),
            "flagged_windows": f["answers"]["flagged_windows"],
            "tally": f["answers"]["verdict_tally"],
            "reading": f["answers"]["reading"],
            "worst": f["answers"]["worst"],
            "windows": [{"name": r["name"], "era": r["era"], "book": r["book"],
                         "date": r["date"], "next": r["next"],
                         "raw_read_pct": r.get("raw_read_pct"),
                         "arm_read_pct": r.get("arm_read_pct"),
                         "largest_step": r.get("largest_step"),
                         "verdict": r["verdict"]} for r in f["windows"]],
            "arithmetic": {"steps_tested": f["answers"]["steps_tested"],
                           "ratio_product_mismatch":
                               f["answers"]["ratio_product_mismatch"]},
        }, ensure_ascii=False, indent=1))
        return 0
    if args.mode == "heldsplit":
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        f = run_heldsplit(outdir, start=args.start)
        p = write_json(outdir, "HELDSPLIT-%s-s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""),
                          f["spec"]["start"][:4]), f)
        print(json.dumps({
            "leg": "heldsplit",
            "file": os.path.relpath(p, ROOT),
            "answers": {k: v for k, v in f["answers"].items()
                        if k != "largest_unchanged_holding_splits"},
            "splits": [{"era": s["era"], "book": s["book"],
                        "delta_mean_bp": s["delta_mean_bp"],
                        "max_window_bp": s["delta_max_abs_bp"],
                        "windows_with_split_pct": s["windows_with_a_split_pct"],
                        "verdict": s["verdict"],
                        "window": (s["largest_window"] or {}).get("date"),
                        "names": [t["name"] for t in
                                  (s["largest_window"] or {}).get("top", [])]}
                       for s in f["answers"]["largest_unchanged_holding_splits"]]},
            ensure_ascii=False))
        return 0
    if args.mode == "gaptop3":
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        f = run_gaparm_topnames(outdir, start=args.start)
        p = write_json(outdir, "GAPTOP3-%s-s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""),
                          f["spec"]["start"][:4]), f)
        print(json.dumps({
            "leg": "gaptop3",
            "file": os.path.relpath(p, ROOT),
            "answers": {k: v for k, v in f["answers"].items()
                        if k not in ("moves_named",)},
            "moves": [{"era": m["era"], "book": m["book"],
                       "delta_bp": m["delta_bp"], "verdict": m["verdict"],
                       "top_share": m["top_share_of_delta_pct"],
                       "windows": [{"date": w["date"], "contrib_bp": w["contrib_bp"],
                                    "side": w["side"],
                                    "only_gap": w["held_only_in_gap"][:5],
                                    "only_unscreened":
                                        w["held_only_in_unscreened"][:5]}
                                   for w in (m["largest_window"],) if w]}
                      for m in f["answers"]["moves_named"]]},
            ensure_ascii=False))
        return 0
    if args.mode == "tiltstable":
        outdir = os.path.join(ROOT, "results", "e42_tilt_era")
        f = run_tilt_stable(outdir)
        p = write_json(outdir, "NEWESTERA-STABILITY-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "tiltstable", "file": os.path.relpath(p, ROOT),
                          "cell_now_bp": f["cell_now"].get("tilt_annualised_bp"),
                          "end_choice": f["end_choice_answers"],
                          "stability": f["stability_answers"]}, ensure_ascii=False))
        return 0
    if args.mode == "endchoice":
        outdir = os.path.join(ROOT, "results", "e42_tilt_era")
        f = run_endchoice_all_eras(outdir)
        p = write_json(outdir, "ENDCHOICE-ALLERAS-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "endchoice", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"],
                          "spans": {r["era"]: r.get("span_bp") for r in f["eras"]},
                          "verdicts": f["answers"]["verdicts"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "calcost":
        f = run_calcost(None)
        outdir = os.path.join(ROOT, "results", "e42_calendar_cost")
        p = write_json(outdir, "COST-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "calcost", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"]}, ensure_ascii=False))
        return 0
    if args.mode == "screencalc":
        f = run_calcost_screenreg(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e42_calendar_cost")
        p = write_json(outdir, "COST-%s-screened.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "screencalc", "file": os.path.relpath(p, ROOT),
                          "band_by_cost": f["answers"]["band_by_cost"],
                          "band_widening_x1_to_x3_bp":
                              f["answers"]["band_widening_x1_to_x3_bp"],
                          "fee_channel_reading":
                              f["answers"]["fee_channel_reading"],
                          "widest_correction": f["answers"]["widest_correction"],
                          "delta_cells": f["answers"]["delta_cells"],
                          "non_zero_delta_cells":
                              f["answers"]["non_zero_delta_cells"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "screenspread":
        f = run_screenspread(None)
        outdir = os.path.join(ROOT, "results", "e42_spread_size_neutral")
        p = write_json(outdir, "NEUTRAL-%s-screened.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "screenspread", "file": os.path.relpath(p, ROOT),
                          "level_mean_over_eras_bp": f["answers"]["level_mean_over_eras_bp"],
                          "band_max_minus_min_bp": f["answers"]["band_max_minus_min_bp"],
                          "all_eras_positive": f["answers"]["all_eras_positive"],
                          "size_neutral_by_arm_era_bp":
                              f["answers"]["size_neutral_by_arm_era_bp"],
                          "sign_flips_vs_unscreened":
                              f["answers"]["sign_flips_vs_unscreened"],
                          "widest_correction": f["answers"]["widest_correction"],
                          "delta_cells": f["answers"]["delta_cells"],
                          "non_zero_delta_cells": f["answers"]["non_zero_delta_cells"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "screentilt":
        f = run_screentilt(None)
        outdir = os.path.join(ROOT, "results", "e42_tilt_era")
        p = write_json(outdir, "TILT-ERA-%s-screened.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "screentilt", "file": os.path.relpath(p, ROOT),
                          "tilt_by_arm_era_bp": f["answers"]["tilt_by_arm_era_bp"],
                          "tilt_range_by_arm_bp": f["answers"]["tilt_range_by_arm_bp"],
                          "beta_by_arm_era": f["answers"]["beta_by_arm_era"],
                          "sign_flips_vs_unscreened":
                              f["answers"]["sign_flips_vs_unscreened"],
                          "widest_correction": f["answers"]["widest_correction"],
                          "delta_cells": f["answers"]["delta_cells"],
                          "non_zero_delta_cells":
                              f["answers"]["non_zero_delta_cells"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "screenrob":
        f = run_screenrob(None)
        outdir = os.path.join(ROOT, "results", "e43_neutral_robust")
        p = write_json(outdir, "ROBUST-%s-screened.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "screenrob", "file": os.path.relpath(p, ROOT),
                          "all_positive": f["answers"]["all_positive"],
                          "range_bp": f["answers"]["range_bp"],
                          "sign_flips_vs_unscreened": f["answers"]["sign_flips_vs_unscreened"],
                          "widest_moves": f["answers"]["widest_moves"],
                          "newest_era_by_arm_cell_bp": f["answers"]["newest_era_by_arm_cell_bp"]},
                         ensure_ascii=False))
        return 0
    if args.mode in ("e43", "tilt4", "widecomp", "neutralrob"):
        core = _monthly_core()
        if args.mode in ("e43", "tilt4"):
            f = run_tilt4(None, core=core)
            outdir = os.path.join(ROOT, "results", "e43_tilt_4member")
            p = write_json(outdir, "HIST-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
            print(json.dumps({"leg": "tilt4", "file": os.path.relpath(p, ROOT),
                              "eras": {k: {"months": v.get("months"),
                                           "tilt_bp": v.get("tilt_annualised_bp"),
                                           "beta": v.get("beta_ladder_on_tilt"),
                                           "neutral_bp": v.get("spread_size_neutral_ann_bp")}
                                       for k, v in f["eras"].items()},
                              "answers": f["answers"]}, ensure_ascii=False))
        if args.mode in ("e43", "widecomp"):
            f = run_widecomp(None, core=core)
            outdir = os.path.join(ROOT, "results", "e43_wide_composition")
            p = write_json(outdir, "COMP-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
            print(json.dumps({"leg": "widecomp", "file": os.path.relpath(p, ROOT),
                              "composition_summary": f["composition_summary"],
                              "regressions": {k: {e: {kk: vv.get(kk) for kk in
                                                     ("months", "beta_on_tilt", "r_squared", "ann_bp")}
                                                 for e, vv in v.items()}
                                             for k, v in f["regressions"].items()},
                              "answers": f["answers"]}, ensure_ascii=False))
        if args.mode in ("e43", "neutralrob"):
            f = run_neutralrobust(None, core=core)
            outdir = os.path.join(ROOT, "results", "e43_neutral_robust")
            p = write_json(outdir, "ROBUST-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
            print(json.dumps({"leg": "neutralrob", "file": os.path.relpath(p, ROOT),
                              "answers": f["answers"]}, ensure_ascii=False))
        return 0
    if args.mode in ("e44", "burnin", "knife", "skinloo"):
        if args.mode in ("e44", "burnin"):
            f = run_burnin(None)
            outdir = os.path.join(ROOT, "results", "e44_burnin")
            p = write_json(outdir, "BURNIN-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
            print(json.dumps({"leg": "burnin", "file": os.path.relpath(p, ROOT),
                              "sessions_uninvested":
                                  f["answers"]["sessions_uninvested_by_start"],
                              "first_invested": f["answers"]["first_invested_bar_by_start"],
                              "spans": {k: {kk: (vv or {}).get("ann_return_pct")
                                            for kk, vv in v.items()}
                                        for k, v in f["era_spans_warm"].items()},
                              "answers": f["answers"]}, ensure_ascii=False))
        if args.mode == "knife":
            outdir = os.path.join(ROOT, "results", "e45_burnin_knife")
            os.makedirs(outdir, exist_ok=True)
            f = run_knife(outdir)
            p = write_json(outdir, "KNIFE-%s.json"
                           % f["evidence_cutoff"].replace("-", ""), f)
            print(json.dumps({"leg": "knife", "file": os.path.relpath(p, ROOT),
                              "answers": f["answers"]}, ensure_ascii=False))
        if args.mode in ("e44", "skinloo"):
            core = _monthly_core()
            f = run_skinloo(None, core=core)
            outdir = os.path.join(ROOT, "results", "e44_skin")
            p = write_json(outdir, "LOO-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
            print(json.dumps({"leg": "skinloo", "file": os.path.relpath(p, ROOT),
                              "skins": {k: {"skin": v["skin"],
                                            "neutral_2024_now_bp":
                                                v["eras"].get("2024_now", {}).get(
                                                    "spread_size_neutral_ann_bp"),
                                            "neutral_2021_2023_bp":
                                                v["eras"].get("2021_2023", {}).get(
                                                    "spread_size_neutral_ann_bp")}
                                        for k, v in f["skins"].items()},
                              "delta": f["delta_vs_full_skin_bp"],
                              "answers": f["answers"]}, ensure_ascii=False))
        return 0
    if args.mode in ("e45", "warmspread"):
        f = run_warmspread(None)
        outdir = os.path.join(ROOT, "results", "e45_warm_spread")
        p = write_json(outdir, "WARMSPREAD-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "warmspread", "file": os.path.relpath(p, ROOT),
                          "eras": {k: {"warm_bp": v["warm"]["spread_bp"],
                                       "cold_bp": v["cold"]["spread_bp"],
                                       "cold_dead_share_pct": v["cold"]["dead_block_share_pct"],
                                       "cold_cash_dead_pct":
                                           v["cold"]["cash_accrued_in_dead_block_pct"]}
                                   for k, v in f["eras"].items()},
                          "answers": f["answers"]}, ensure_ascii=False))
        return 0
    if args.mode in ("e46", "livespan"):
        f = run_livespan(None, parts=args.parts, cost_mult=args.cost)
        outdir = os.path.join(ROOT, "results", "e46_live_span")
        p = write_json(outdir, "LIVESPAN-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""),
                          "" if (args.cost == 1.0 and args.parts == 2)
                          else "-x%g-p%d" % (args.cost, args.parts)), f)
        print(json.dumps({"leg": "livespan", "file": os.path.relpath(p, ROOT),
                          "eras": {k: {"era_bp": v.get("era_spread_bp"),
                                       "parts_bp": v.get("part_spreads_bp"),
                                       "flip": v.get("sign_flips_inside_era")}
                                   for k, v in f["eras"].items()},
                          "answers": f["answers"]}, ensure_ascii=False))
        return 0
    if args.mode == "cutcurve":
        f = run_cutcurve(None)
        outdir = os.path.join(ROOT, "results", "e46_live_span")
        p = write_json(outdir, "CUTCURVE-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "cutcurve", "file": os.path.relpath(p, ROOT),
                          "cuts_swept": f["answers"]["cuts_swept"],
                          "series": f["answers"]["series_by_cost"],
                          "era_level_drift_bp": f["answers"]["era_level_drift_bp"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "midmonth":
        f = run_midmonth(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "MID-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""),
                          "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")), f)
        print(json.dumps({"leg": "midmonth", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"],
                          "eras": {k: {"me_x1_bp": v["me"]["x1_ann_pct"],
                                       "mid_x1_bp": v["mid"]["x1_ann_pct"],
                                       "gap_x1_bp": v.get("gap_x1_bp"),
                                       "me_churn_alpha_bp": v["me"]["churn_alpha_bp_mean"],
                                       "mid_churn_alpha_bp": v["mid"]["churn_alpha_bp_mean"]}
                                   for k, v in f["eras"].items()}},
                         ensure_ascii=False))
        return 0
    if args.mode == "chase":
        f = run_chase(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "CHASE-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "chase", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"],
                          "mid_buckets": {k: {b: v["buckets"][b]["fwd_pct_mean"]
                                              for b in CHASE_BUCKETS}
                                          for k, v in f["eras"]["mid15"].items()}},
                         ensure_ascii=False))
        return 0
    if args.mode == "midsweep":
        costs = (tuple(float(x) for x in args.costs.split(","))
                 if args.costs else (1.0,))
        f = run_midsweep(None, start=args.start, costs=costs)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        cost_tag = "" if costs == (1.0,) else "-c%s" % "_".join("%g" % c for c in costs)
        p = write_json(outdir, "MIDSWEEP-%s%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag, cost_tag), f)
        print(json.dumps({"leg": "midsweep", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"]}, ensure_ascii=False))
        return 0
    if args.mode == "entrydelay":
        costs = (tuple(float(x) for x in args.costs.split(","))
                 if args.costs else (1.0,))
        lags = tuple(int(x) for x in args.lags.split(",") if x.strip())
        f = run_entrydelay(None, start=args.start, lags=lags, costs=costs)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        cost_tag = "" if costs == (1.0,) else "-c%s" % "_".join("%g" % c for c in costs)
        p = write_json(outdir, "ENTRYDELAY-%s%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag, cost_tag), f)
        print(json.dumps({"leg": "entrydelay", "file": os.path.relpath(p, ROOT),
                          "delay_gap_bp": f["answers"]["delay_gap_bp"],
                          "newest_era_gap_bp": f["answers"]["newest_era_gap_bp"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "earlydelay":
        costs = (tuple(float(x) for x in args.costs.split(","))
                 if args.costs else (1.0,))
        early = tuple(int(x) for x in args.lags.split(",") if x.strip())
        f = run_earlydelay(None, start=args.start, early=early, costs=costs)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        cost_tag = "" if costs == (1.0,) else "-c%s" % "_".join("%g" % c for c in costs)
        p = write_json(outdir, "EARLYDELAY-%s%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag, cost_tag), f)
        print(json.dumps({"leg": "earlydelay", "file": os.path.relpath(p, ROOT),
                          "early_gap_bp": f["answers"]["early_gap_bp"],
                          "early_newest_era_gap_bp":
                              f["answers"]["early_newest_era_gap_bp"],
                          "late_rows_source": f["answers"]["late_rows_source"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "neighborhood":
        costs = (tuple(float(x) for x in args.costs.split(","))
                 if args.costs else (1.0,))
        f = run_neighborhood(None, start=args.start, costs=costs,
                             neighbors=tuple(int(x) for x in args.neighbors.split(",")
                                             if x.strip()))
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        cost_tag = "" if costs == (1.0,) else "-c%s" % "_".join("%g" % c for c in costs)
        p = write_json(outdir, "NEIGHBORHOOD-%s%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag, cost_tag), f)
        print(json.dumps({"leg": "neighborhood", "file": os.path.relpath(p, ROOT),
                          "neighbor_gap_bp": f["answers"]["neighbor_gap_bp"],
                          "brackets": {k: {"full_window_shape": v["full_window_shape"],
                                           "newest_era_shape": v["newest_era_shape"],
                                           "newest_era_bp": v["newest_era_bp"]}
                                       for k, v in f["answers"]["brackets"].items()}},
                         ensure_ascii=False))
        return 0
    if args.mode == "weeklyclash":
        costs = (tuple(float(x) for x in args.costs.split(","))
                 if args.costs else (1.0,))
        f = run_weeklyclash(None, start=args.start, costs=costs)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        cost_tag = "" if costs == (1.0,) else "-c%s" % "_".join("%g" % c for c in costs)
        p = write_json(outdir, "WEEKLYCLASH-%s%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag, cost_tag), f)
        print(json.dumps({"leg": "weeklyclash", "file": os.path.relpath(p, ROOT),
                          "calendar_rows": f["answers"]["calendar_rows"],
                          "turnover_ratio_vs_me": f["answers"]["turnover_ratio_vs_me"],
                          "week_overlap": f["answers"].get("week_overlap")},
                         ensure_ascii=False))
        return 0
    if args.mode == "weeknames":
        f = run_weeknames(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        p = write_json(outdir, "WEEKNAMES-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag), f)
        print(json.dumps({"leg": "weeknames", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"],
                          "pairs": {k: v["summary"] for k, v in f["pairs"].items()}},
                         ensure_ascii=False))
        return 0
    if args.mode == "stalehold":
        f = run_stalehold(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        p = write_json(outdir, "STALEHOLD-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag), f)
        print(json.dumps({"leg": "stalehold", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"],
                          "by_era": {k: {"events": v["events"],
                                         "total_bp": v["total_bp"],
                                         "bp_per_year": v["bp_per_year"]}
                                     for k, v in f["by_era"].items()},
                          "skipped": f["skipped"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "staletail":
        f = run_staletail(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        p = write_json(outdir, "STALETAIL-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag), f)
        print(json.dumps({"leg": "staletail", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"],
                          "by_era": {k: {"events": v["events"],
                                         "total_bp": v["total_bp"],
                                         "bp_per_year": v["bp_per_year"],
                                         "reading": v["reading"]}
                                     for k, v in f["by_era"].items()},
                          "skipped": f["skipped"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "panelsplit":
        f = run_panelsplit(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        start_tag = "" if args.start == "2020-01-01" else "-s%s" % args.start.replace("-", "")
        p = write_json(outdir, "PANELSPLIT-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), start_tag), f)
        print(json.dumps({"leg": "panelsplit", "file": os.path.relpath(p, ROOT),
                          "panel": f["panel"], "summary": f["summary"],
                          "by_era": {k: {"events": v["events"],
                                         "total_book_bp": v["total_book_bp"],
                                         "bp_per_year": v["bp_per_year"]}
                                     for k, v in f["by_era"].items()},
                          "top": [{"name": e["name"], "date": e["date"],
                                   "ret_pct": e["ret_pct"],
                                   "bp": e["book_impact_bp"],
                                   "ratio": (e.get("implied_ratio") or {}).get("ratio")}
                                  for e in f["top_events"][:5]]},
                         ensure_ascii=False))
        return 0
    if args.mode == "screenreg":
        f = run_screenreg(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "SCREENREG-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "screenreg", "file": os.path.relpath(p, ROOT),
                          "screen": {k: {"names_touched": v["names_touched"],
                                         "events": v["events_neutralised"],
                                         "integer_like": v["integer_like_events"]}
                                     for k, v in f["screen_reports"].items()},
                          "answers": f["answers"],
                          "moved_cells": [r for r in f["delta"]
                                          if any(r.get("delta_" + m) not in (None, 0)
                                                 for m in f["screen_reports"])][:12]},
                         ensure_ascii=False))
        return 0
    if args.mode == "screengapera":
        limits = tuple(int(x) for x in str(args.gaps).split(",") if x.strip())
        f = run_screengapera(None, start=args.start, gap_limits=limits)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "SCREENGAPERA-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "screengapera",
                          "file": os.path.relpath(p, ROOT),
                          "arms": f["spec"]["arms"],
                          "screen": {k: {"names_touched": v["names_touched"],
                                         "events": v["events_neutralised"],
                                         "gap_limit": v.get("gap_limit")}
                                     for k, v in f["screen_reports"].items()
                                     if k.startswith("neutralise_gap")},
                          "answers": {k: v for k, v in f["answers"].items()
                                      if k != "gap_limit_marginal"},
                          "era_rows": f["era_rows"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "screenwide":
        f = run_screenwide(None)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "SCREENWIDE-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "screenwide", "file": os.path.relpath(p, ROOT),
                          "screen": {k: {"names_touched": v["names_touched"],
                                         "events": v["events_neutralised"]}
                                     for k, v in f["screen_reports"].items()},
                          "answers": f["answers"],
                          "cost_shift": f["cost_shift"],
                          "moved_cells": [r for r in f["delta"]
                                          if any(r.get("delta_" + m) not in (None, 0)
                                                 for m in f["screen_reports"])][:10]},
                         ensure_ascii=False))
        return 0
    if args.mode == "screenweek":
        f = run_screenweek(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "WEEKCLASH-%s-screened.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "screenweek", "file": os.path.relpath(p, ROOT),
                          "screen": {k: {"names_touched": v["names_touched"],
                                         "events": v["events_neutralised"]}
                                     for k, v in f["screen_reports"].items()},
                          "residual_bp_by_cost": f["answers"]["residual_bp_by_cost"],
                          "residual_survival": f["answers"]["residual_survival"],
                          "newest_era_residual_bp":
                              f["answers"]["newest_era_residual_bp"],
                          "worst": f["answers"]["residual_worst_correction"],
                          "moved_cells": [r for r in f["delta"]
                                          if any(r.get("delta_" + m) not in (None, 0)
                                                 for m in f["screen_reports"])][:10]},
                         ensure_ascii=False))
        return 0
    if args.mode == "midscreen":
        f = run_midscreen(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "MIDSCREEN-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "midscreen", "file": os.path.relpath(p, ROOT),
                          "screen": {k: {"names_touched": v["names_touched"],
                                         "events": v["events_neutralised"]}
                                     for k, v in f["screen_reports"].items()},
                          "newest_era_gap_x1_bp":
                              f["results"]["newest_era_gap_x1_bp"],
                          "gap_survival": f["results"]["gap_survival"],
                          "churn_alpha_gap_bp":
                              f["results"]["newest_era_churn_alpha_gap_bp"],
                          "negative_churn_share":
                              f["results"]["newest_era_negative_churn_share_pct"],
                          "turnover_control":
                              f["results"]["turnover_per_year_control"],
                          "flip_eras": f["results"]["eras_whose_gap_changes_sign"],
                          "worst": f["results"]["worst_correction"],
                          "moved_cells": f["results"]["non_zero_delta_cells"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "churngap":
        f = run_churngap(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "CHURNGAP-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "churngap", "file": os.path.relpath(p, ROOT),
                          "events_indexed": f["spec"]["events_indexed"],
                          "results": f["results"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "singleprint":
        bond, modeeq = run_singleprint(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "SINGLEPRINT-%s.json"
                       % bond["evidence_cutoff"].replace("-", ""), bond)
        q = write_json(outdir, "MODEEQ-%s.json"
                       % modeeq["evidence_cutoff"].replace("-", ""), modeeq)
        print(json.dumps({"leg": "singleprint",
                          "file": os.path.relpath(p, ROOT),
                          "modeeq_file": os.path.relpath(q, ROOT),
                          "results": bond["results"],
                          "flagged": [{"book": f["book"], "universe": f["universe"],
                                       "era": f["era"], "face": f["face"],
                                       "mean_bp": f["mean_bp"],
                                       "remaining_pct": f["magnitude_remaining_pct"],
                                       "window": f["removed_window"]}
                                      for f in bond["flagged"]],
                          "modeeq": {"verdict": modeeq["verdict"],
                                     "touched": modeeq["universe_half"]["names_touched"],
                                     "extra_names": modeeq["universe_half"]
                                     ["names_only_in_neutralise"],
                                     "extra_ever_swapped": modeeq["relevance_to_this_book"]
                                     ["extra_names_ever_swapped"],
                                     "bit_identical": modeeq["verdict"]
                                     == "identical_on_this_face"}},
                         ensure_ascii=False))
        return 0
    if args.mode == "robustchurn":
        f = run_robustchurn(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        # r1135 pit: a variant burn must not overwrite the base face, so the
        # filename carries the window start whenever it is not the default.
        _sv = "" if args.start == "2020-01-01" else "-s%s" % args.start[:4]
        p = write_json(outdir, "CHURNROBUST-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), _sv), f)
        thin = [{"book": c["book"], "universe": c["universe"], "era": c["era"],
                 "mean_bp": c["mean_bp"], "median_bp": c["median_bp"],
                 "trim10_bp": c["trim10_bp"],
                 "median_keep_pct": c["median_keep_pct_of_mean"],
                 "top3_share_pct": (c["concentration_top3"] or {})
                 .get("top_share_of_total_pct")}
                for c in f["cells"]
                if c["median_keep_pct_of_mean"] is not None
                and abs(c["median_keep_pct_of_mean"]) < 50.0]
        print(json.dumps({"leg": "robustchurn", "file": os.path.relpath(p, ROOT),
                          "summary": f["summary"],
                          "thin_level_cells": thin,
                          "delta_rows": [{"book": c["book"], "mode": c["mode"],
                                          "era": c["era"],
                                          "mean_bp": c["mean_bp"],
                                          "median_bp": c["median_bp"],
                                          "trim10_bp": c["trim10_bp"],
                                          "median_keep_pct": c["median_keep_pct_of_mean"]}
                                         for c in f["delta_cells"]]},
                         ensure_ascii=False))
        return 0
    if args.mode == "loodist":
        f = run_loodist(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "LOODIST-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "loodist", "file": os.path.relpath(p, ROOT),
                          "summary": f["summary"],
                          "cells": [{"book": c["book"], "universe": c["universe"],
                                     "era": c["era"], "n": c["n"],
                                     "mean_bp": c["mean_bp"],
                                     "loo_min_bp": c.get("loo_min_bp"),
                                     "loo_median_bp": c.get("loo_median_bp"),
                                     "kills_half_pct": c.get("loo_kills_half_pct"),
                                     "breakdown_k": (c.get("breakdown") or {}).get("k"),
                                     "breakdown_share_pct":
                                         (c.get("breakdown") or {})
                                         .get("share_of_transitions_pct")}
                                    for c in f["cells"]],
                          "gap_cells": f["gap_cells"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "churnse":
        f = run_churnse(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "CHURNSE-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "churnse", "file": os.path.relpath(p, ROOT),
                          "summary": f["summary"],
                          "cells": [{"book": c["book"], "universe": c["universe"],
                                     "era": c["era"], "n": c["n"],
                                     "mean_bp": c["mean_bp"],
                                     "se_bp": c["jk_se_bp"],
                                     "jk90": [c["jk_lo90_bp"], c["jk_hi90_bp"]],
                                     "boot90": [c["boot_p05_bp"],
                                                c["boot_p95_bp"]],
                                     "clears_zero": c["interval_clears_zero"]}
                                    for c in f["cells"]],
                          "gap_cells": f["gap_cells"]},
                         ensure_ascii=False))
        return 0
    if args.mode == "gapsplit":
        lims = tuple(int(x) for x in args.gaps.split(",") if x.strip())
        f = run_gapsplit(None, start=args.start, limits=lims)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        _sv = "" if args.start == "2020-01-01" else "-s%s" % args.start[:4]
        p = write_json(outdir, "SCREENGAP-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), _sv), f)
        print(json.dumps({"leg": "gapsplit", "file": os.path.relpath(p, ROOT),
                          "census": {k: {"limit": v["gap_limit_sessions"],
                                         "gapped_total": v["gapped_prints_total"],
                                         "eligible": v["eligible_integer_prints"],
                                         "names": v["eligible_names"],
                                         "by_era": v["eligible_by_era"]}
                                     for k, v in
                                     f["census"]["by_gap_limit"].items()},
                          "churn_gap_by_era": f["churn_gap_by_era"],
                          "moved": {b: {k: v["transitions_moved"]
                                        for k, v in f["joins"][b].items()}
                                    for b in f["joins"]}},
                         ensure_ascii=False))
        return 0
    if args.mode == "topnames":
        f = run_topnames(None, start=args.start)
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        _sv = "" if args.start == "2020-01-01" else "-s%s" % args.start[:4]
        p = write_json(outdir, "CHURNTOP3-%s%s.json"
                       % (f["evidence_cutoff"].replace("-", ""), _sv), f)
        print(json.dumps({"leg": "topnames", "file": os.path.relpath(p, ROOT),
                          "summary": f["summary"],
                          "cells": [{"book": c["book"], "universe": c["universe"],
                                     "era": c["era"], "n": c["transitions"],
                                     "mean_bp": c["mean_bp"],
                                     "top3_share_pct":
                                         c["top_k_share_of_signed_total_pct"],
                                     "top1_over_half": c["top1_is_more_than_half"],
                                     "top": [{"date": t["date"],
                                              "bp": t["churn_alpha_bp"],
                                              "by": t["carried_by"],
                                              "in": t["entrant_names"][:3],
                                              "out": t["exit_names"][:3]}
                                             for t in c["top_k"]]}
                                    for c in f["cells"]]},
                         ensure_ascii=False))
        return 0
    if args.mode == "burncontrol":
        f = run_burncontrol()
        outdir = os.path.join(ROOT, "results", "e44_midmonth")
        p = write_json(outdir, "CHURNROBUST-CONTROL-%s.json"
                       % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "burncontrol", "file": os.path.relpath(p, ROOT),
                          "status": f["status"], "summary": f["summary"]},
                         ensure_ascii=False))
        return 0 if f["status"] != "MISMATCH" else 1
    if args.mode == "month":
        if not args.month:
            print("--month YYYY-MM required")
            return 2
        f = run_month(None, args.month)
        if not f:
            print("no calendar bars in %s" % args.month)
            return 2
        outdir = os.path.join(ROOT, "results", "e39_month_attribution")
        p = write_json(outdir, "MONTH-%s.json" % args.month, f)
        print(json.dumps({"leg": "month", "file": os.path.relpath(p, ROOT),
                          "equal_weight_pct": f["equal_weight_month_return_pct"],
                          "members": {k: v.get("month_return_pct") for k, v in f["members"].items()},
                          "anomalies": f["anomaly_flags"]}, ensure_ascii=False))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))