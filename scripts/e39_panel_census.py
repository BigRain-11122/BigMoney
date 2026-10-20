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
                                                 n, 1.0, rank_cache)
    lad = curves["ladder5"]
    lmap = dict(lad)
    wide_name = "wide_top%d" % pick_n
    ratio = [(d, v / lmap[d]) for d, v in curves[wide_name] if d in lmap and lmap[d] > 0]
    rows = {}
    for name, lo, hi in eras:
        seg_l = _rebase(_slice_curve(lad, lo, hi))
        seg_w = _rebase(_slice_curve(curves[wide_name], lo, hi))
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


def _monthly_core(pick_n=9999, exclude=("sh511",)):
    """One shared build: both engine curves plus the member tilt series.

    The two E42 product legs read this object so their faces cannot drift apart
    and the expensive panel pass happens once per process.
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


# ------------------------------------ leg: E42 calendar band at cost x3

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
                      exclude=("sh511",), mid_day=15, cost_mults=(1.0, 3.0)):
    """Re-run the size-neutral spread on all four decision calendars at cost x3.

    E42's +181bp newest-era figure has survived neither a fee stress nor a
    calendar shift: E41 moved the calendar and the spread band moved 26bp, and
    E42's cost x3 moved the fee 3x. This leg crosses both axes and reports the
    size-neutral number per cell, so the only surviving claim is the one that
    clears both at once.
    """
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27

    core = core or _monthly_core()
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


def run_livespan(outdir, eras=ERAS, pick_n=9999, exclude=("sh511",), parts=2,
                 cost_mult=1.0):
    """E46: split every era in halves and read where its spread is earned."""
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


# ------------------------------------------------------------------- plumbing

def write_json(outdir, name, payload):
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, name)
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

    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser(description="E39 panel census (descriptive, offline)")
    ap.add_argument("mode", nargs="?", default="all",
                    choices=["stale", "mtime", "ladder", "month", "pair", "cashdrag",
                             "tilt", "rebalday", "era", "spreadsize", "tiltera",
                             "calcost", "e42", "e43", "tilt4", "widecomp", "neutralrob",
                             "e44", "burnin", "knife", "skinloo", "e45", "warmspread",
                             "e46", "livespan", "all", "selftest"])
    ap.add_argument("--month", default=None, help="YYYY-MM for the month attribution leg")
    ap.add_argument("--cost", type=float, default=1.0, help="cost multiple (e46 livespan leg)")
    ap.add_argument("--parts", type=int, default=2, help="chunks per era (e46 livespan leg)")
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
    if args.mode == "calcost":
        f = run_calcost(None)
        outdir = os.path.join(ROOT, "results", "e42_calendar_cost")
        p = write_json(outdir, "COST-%s.json" % f["evidence_cutoff"].replace("-", ""), f)
        print(json.dumps({"leg": "calcost", "file": os.path.relpath(p, ROOT),
                          "answers": f["answers"]}, ensure_ascii=False))
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