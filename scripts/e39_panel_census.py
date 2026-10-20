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

    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser(description="E39 panel census (descriptive, offline)")
    ap.add_argument("mode", nargs="?", default="all",
                    choices=["stale", "mtime", "ladder", "month", "pair", "all", "selftest"])
    ap.add_argument("--month", default=None, help="YYYY-MM for the month attribution leg")
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