"""Bench cell: does the exchange repo curve pay for duration? (a cash leg, not a strategy)

The question (four-gate test (a): do we change what we do)
---------------------------------------------------------
Yesterday's rent audit closed the loop on the book: after the search rent it is worth about
the net repo rate (1.78%/yr), which means the marginal yuan is better spent making the CASH
leg better than making the book cleverer. So: on the SSE/SZSE repo curve we already have
(11 tenors, daily bars 2015-2026), does lending longer -- GC007 / GC028 / GC182 instead of
rolling GC001 -- actually pay, net of commission, after the days you cannot touch the money?

This is a cash-management question, not an alpha hunt: no leverage, no derivatives, no view.
It is also the only line in the book whose "edge" is collected by doing nothing.

Model (one cash bucket, no leverage)
------------------------------------
  * On each trading day, if the bucket is free, lend ALL of it at that day's close quote for
    tenor k. Maturity = the first trading day ON OR AFTER d + k calendar days; interest is paid
    on the ACTUAL calendar days held (that is why GC001 spikes on Thursdays -- a Friday lend
    spans three days). This convention is printed with the numbers.
  * Commission is the exchange's published schedule, charged on the principal, per lend.
  * Idle days (maturity landing between trading days) earn nothing. That cost is printed as
    utilisation, not hidden.
  * Compounding is on the bucket; there is no mark-to-market and no reinvestment risk by
    construction -- the rate is locked at lend time.

Criteria frozen before the run (all five must hold for GO):
  H1  pickup over the GC001 roll >= +0.30pp/yr net of commission (a cash leg has to be worth
      the operational step, not just nominally higher)
  H2  pickup positive in BOTH halves (2015-2020, 2021-2026) -- not one quarter-end episode
  H3  the tenor's worst calendar year is not worse than the GC001 roll's worst year
  H4  utilisation >= 60% of calendar days (a leg you cannot use is not a cash leg)
  H5  the pickup survives commission x2
Otherwise NO_EDGE (with the numbers kept -- 只增不改).

Known limits (disclosed, not hidden):
  * Quotes are the panel's close, not a guaranteed fill; the two longest tenors are thin
    (median volume printed) and are indicative until capacity is measured at our size.
  * No tax, no alternative cash venues (bank deposits, money-market funds) -- this cell asks
    only "is the repo curve behind us or against us".
  * The window includes 2015-2016 where short rates were structurally different; H2 exists
    precisely so a single regime cannot carry the verdict.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "bench_repo_ladder.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-REPO-LADDER.md")

REPO_DIR = os.path.join(bc.DATA, "repo_daily")

# tenor in calendar days -> file stem. The exchange's own terms are 1/3/4/7/14/28/91/182.
TENORS = [
    (1, "GC001"), (3, "GC003"), (4, "GC004"), (7, "GC007"),
    (14, "GC014"), (28, "GC028"), (91, "GC091"), (182, "GC182"),
    (1, "R-001"), (3, "R-003"), (7, "R-007"),
]
BASELINE = (1, "GC001")

# SSE published reverse-repo commission, as a fraction of the principal, by term.
FEES = {1: 0.00001, 2: 0.00002, 3: 0.00003, 4: 0.00004, 7: 0.00005,
        14: 0.00010, 28: 0.00020, 91: 0.00030, 182: 0.00030}

SPLIT = "2021-01-01"
H1_PICKUP_PP = 0.30
H3_TOL_PP = 0.05
H4_UTILISATION = 0.60


def _read(code):
    """Close quotes (annualised %) and the median daily volume for one tenor."""
    path = os.path.join(REPO_DIR, code + ".csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.dropna(subset=["close"]).sort_values("date")
    close = df.set_index("date")["close"].astype(float)
    vol = pd.to_numeric(df.get("volume"), errors="coerce").median()
    return {"close": close, "median_volume": float(vol) if pd.notna(vol) else None}


def _fee_for(tenor_days):
    return FEES.get(int(tenor_days), FEES[max(k for k in FEES if k <= int(tenor_days))])


def run_bucket(rate, tenor_days, calendar, fee=None):
    """Lend the whole bucket at `rate` for `tenor_days` whenever it is free.

    Returns the equity series (index = calendar days actually simulated) and the lend log.
    """
    if fee is None:
        fee = _fee_for(tenor_days)
    cal = list(calendar)
    cal_index = {d: i for i, d in enumerate(cal)}
    equity = [1.0] * len(cal)
    free_at = cal[0]
    lends = 0
    employed_days = 0
    missing_quotes = 0
    exhausted = False
    for i, d in enumerate(cal):
        equity[i] = equity[i - 1] if i else 1.0
        if exhausted or d < free_at:
            continue
        q = rate.get(d)
        if q is None or not np.isfinite(q):
            missing_quotes += 1
            continue
        # maturity: first trading day on or after d + tenor (calendar days)
        target = d + pd.Timedelta(days=int(tenor_days))
        j = cal_index.get(target)
        if j is None:
            later = [x for x in cal if x >= target]
            if not later:
                # the last lend would mature after the window: stop lending and keep the
                # balance carried. Breaking here used to leave the tail at the initial 1.0,
                # which read as "this tenor earned nothing" (a fake zero).
                exhausted = True
                continue
            maturity = later[0]
        else:
            maturity = target
        days = max(int((maturity - d).days), 1)
        equity[i] = equity[i] * (1.0 + float(q) / 100.0 * days / 365.0 - fee)
        employed_days += days
        lends += 1
        free_at = maturity
    eq = pd.Series(equity, index=cal)
    total_days = int((cal[-1] - cal[0]).days)
    idle = max(total_days - employed_days, 0)
    return eq, {"lends": lends, "employed_days": employed_days, "calendar_days": total_days,
                "idle_days": idle, "utilisation": round(employed_days / total_days, 4),
                "missing_quotes": missing_quotes}


def _cagr(eq):
    days = int((eq.index[-1] - eq.index[0]).days)
    if days <= 0 or eq.iloc[-1] <= 0:
        return None
    return round(float(eq.iloc[-1] ** (365.0 / days) - 1.0), 6)


def _year_returns(eq):
    out = {}
    for year, grp in eq.groupby(eq.index.year):
        if len(grp) < 2:
            continue
        days = int((grp.index[-1] - grp.index[0]).days)
        if days <= 0:
            continue
        out[str(year)] = round(float(grp.iloc[-1] / grp.iloc[0] - 1.0), 6)
    return out


def _pickup(series_a, series_b, start=None, end=None):
    """CAGR(a) - CAGR(b) in pp, optionally on a slice."""
    a, b = series_a, series_b
    if start is not None:
        a, b = a[a.index >= start], b[b.index >= start]
    if end is not None:
        a, b = a[a.index <= end], b[b.index <= end]
    if len(a) < 3 or len(b) < 3:
        return None
    ca, cb = _cagr(a), _cagr(b)
    if ca is None or cb is None:
        return None
    return round(100.0 * (ca - cb), 4)


def build(write=True):
    frames = {}
    for tenor, code in TENORS:
        got = _read(code)
        if got is not None and len(got["close"]) > 100:
            frames[code] = got
    if BASELINE[1] not in frames:
        payload = {"schema": "bench_repo_ladder/v1", "ts": bc_now(),
                   "verdict": "DATA-BLOCKED", "reason": "baseline %s missing" % BASELINE[1]}
        if write:
            bc.write_json(OUT_JSON, payload)
        return payload

    # the calendar is the baseline's own trading days: repo quotes only exist on trading days
    calendar = list(frames[BASELINE[1]]["close"].index)

    # control: rolling GC001 with and without commission
    base_eq, base_log = run_bucket(frames[BASELINE[1]]["close"], BASELINE[0], calendar)
    base_eq_free, _ = run_bucket(frames[BASELINE[1]]["close"], BASELINE[0], calendar, fee=0.0)

    arms = []
    for tenor, code in TENORS:
        row = {"code": code, "tenor_days": tenor, "fee": _fee_for(tenor)}
        if code not in frames:
            row.update({"status": "NO_DATA"})
            arms.append(row)
            continue
        close = frames[code]["close"]
        rate = close.to_dict()
        eq, log = run_bucket(rate, tenor, calendar)
        eq_free, _ = run_bucket(rate, tenor, calendar, fee=0.0)
        eq_double, _ = run_bucket(rate, tenor, calendar, fee=2.0 * _fee_for(tenor))
        cagr = _cagr(eq)
        years = _year_returns(eq)
        base_years = _year_returns(base_eq)
        worst = min(years.values()) if years else None
        base_worst = min(base_years.values()) if base_years else None
        row.update({
            "status": "OK",
            "bars": int(len(close)),
            "median_volume": frames[code]["median_volume"],
            "net_cagr": cagr,
            "gross_cagr_no_fee": _cagr(eq_free),
            "cagr_at_double_fee": _cagr(eq_double),
            "pickup_vs_gc001_pp": _pickup(eq, base_eq),
            "pickup_half1_pp": _pickup(eq, base_eq, end=SPLIT),
            "pickup_half2_pp": _pickup(eq, base_eq, start=SPLIT),
            "worst_year": worst,
            "gc001_worst_year": base_worst,
            "worst_year_vs_base_pp": (None if worst is None or base_worst is None
                                      else round(100.0 * (worst - base_worst), 4)),
            "utilisation": log["utilisation"],
            "idle_days_per_year": round(log["idle_days"] / max(log["calendar_days"] / 365.25, 1e-9), 1),
            "lends": log["lends"],
            "missing_quotes": log["missing_quotes"],
            "years": years,
        })
        arms.append(row)

    # ---- criteria, applied mechanically to the printed rows
    # regression guard: an arm that lent its whole balance cannot have earned exactly nothing.
    # (The first run of this cell reported 0.000% for every non-baseline tenor because the loop
    # broke out at the last lend and left the tail at the initial 1.0 -- a fake zero. It must
    # never pass silently again.)
    for a in arms:
        if a.get("status") == "OK" and a["lends"] > 10 and a["utilisation"] > 0.9:
            if a["net_cagr"] is None or a["net_cagr"] <= 0.0:
                a["status"] = "IMPLAUSIBLE_ZERO"
                a["verdict"] = "IMPLAUSIBLE_ZERO"
    base_row = next(a for a in arms if a["code"] == BASELINE[1] and a.get("status") == "OK")
    for a in arms:
        if a.get("status") != "OK":
            a["verdict"] = a.get("status") or "NO_DATA"
            continue
        checks = {
            "H1_pickup": a["pickup_vs_gc001_pp"] is not None and a["pickup_vs_gc001_pp"] >= H1_PICKUP_PP,
            "H2_both_halves": (a["pickup_half1_pp"] is not None and a["pickup_half2_pp"] is not None
                               and a["pickup_half1_pp"] > 0 and a["pickup_half2_pp"] > 0),
            "H3_worst_year": (a["worst_year_vs_base_pp"] is not None
                              and a["worst_year_vs_base_pp"] >= -H3_TOL_PP),
            "H4_utilisation": a["utilisation"] >= H4_UTILISATION,
            "H5_double_fee": (a["cagr_at_double_fee"] is not None and base_row["net_cagr"] is not None
                              and a["cagr_at_double_fee"] - base_row["net_cagr"] >= H1_PICKUP_PP / 100.0),
        }
        a["checks"] = checks
        if a["code"] == BASELINE[1] and a["tenor_days"] == BASELINE[0]:
            # the baseline is the ruler, not a candidate: its own pickup is zero by definition
            a["verdict"] = "BASELINE_REFERENCE"
        else:
            a["verdict"] = "GO" if all(checks.values()) else "NO_EDGE"

    # the headline verdict: the best-passing tenor, or NO_EDGE with the best pickup printed
    passing = [a for a in arms if a.get("verdict") == "GO"]
    ranked = sorted([a for a in arms if a.get("status") == "OK"],
                    key=lambda a: -(a["pickup_vs_gc001_pp"] or -9e9))
    best = ranked[0] if ranked else None
    if passing:
        top = max(passing, key=lambda a: a["pickup_vs_gc001_pp"])
        verdict = {a["code"]: a["verdict"] for a in arms}
        headline = "GO_%s" % top["code"]
    else:
        verdict = {a["code"]: a["verdict"] for a in arms}
        headline = "NO_EDGE"

    payload = {
        "schema": "bench_repo_ladder/v1",
        "ts": bc_now(),
        "cell": "repo_ladder",
        "question": "does lending longer on the exchange repo curve pay, net of commission "
                    "and idle days, versus rolling GC001?",
        "window": [str(calendar[0].date()), str(calendar[-1].date())],
        "calendar_days": int((calendar[-1] - calendar[0]).days),
        "baseline": {"code": BASELINE[1], "net_cagr": base_row["net_cagr"],
                     "gross_cagr_no_fee": _cagr(base_eq_free),
                     "fee_drag_pp": round(100.0 * (base_row["net_cagr"] - _cagr(base_eq_free)), 4),
                     "years": _year_returns(base_eq)},
        "curve_today": {a["code"]: round(float(frames[a["code"]]["close"].iloc[-1]), 3)
                        for a in arms if a.get("status") == "OK" and a["code"] in frames},
        "fees_used": {str(k): v for k, v in FEES.items()},
        "criteria": {"H1_pickup_pp": H1_PICKUP_PP, "H2_split": SPLIT,
                     "H3_worst_year_tol_pp": H3_TOL_PP,
                     "H4_utilisation": H4_UTILISATION, "H5_fee_multiplier": 2.0},
        "arms": arms,
        "best_by_pickup": None if not best else {
            "code": best["code"], "pickup_pp": best["pickup_vs_gc001_pp"],
            "verdict": best["verdict"]},
        "headline": headline,
        "verdict": verdict,
        "notes": ("Commission is the exchange schedule charged on principal per lend; interest is "
                  "paid on actual calendar days held; idle days between maturity and the next "
                  "trading day earn nothing. Volume is not converted to money -- the two longest "
                  "tenors are indicative until capacity is measured at our size."),
    }
    if write:
        bc.write_json(OUT_JSON, payload)
        write_md(payload)
    return payload


def bc_now():
    from datetime import datetime, timedelta, timezone
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def write_md(p):
    lines = []
    lines.append("# The repo curve as a cash leg -- does duration pay?\n")
    lines.append("Window %s -> %s (%d calendar days). Baseline: rolling %s at %.3f%% net." % (
        p["window"][0], p["window"][1], p["calendar_days"], BASELINE[1],
        100.0 * p["baseline"]["net_cagr"]))
    lines.append("")
    lines.append("| tenor | net CAGR | pickup vs GC001 | 1st half | 2nd half | worst year vs base | utilisation | idle d/yr | median volume | verdict |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for a in p["arms"]:
        if a.get("status") != "OK":
            lines.append("| %s | – | – | – | – | – | – | – | – | %s |" % (a["code"], a.get("verdict")))
            continue
        lines.append("| %s (%dd) | %.3f%% | %+.2fpp | %+.2f | %+.2f | %+.2f | %.1f%% | %.1f | %s | **%s** |" % (
            a["code"], a["tenor_days"], 100.0 * a["net_cagr"], a["pickup_vs_gc001_pp"],
            a["pickup_half1_pp"], a["pickup_half2_pp"],
            (a["worst_year_vs_base_pp"] if a["worst_year_vs_base_pp"] is not None else float("nan")),
            100.0 * a["utilisation"], a["idle_days_per_year"],
            (format(int(a["median_volume"]), ",") if a.get("median_volume") is not None else "n/a"),
            a["verdict"]))
    lines.append("")
    lines.append("**Headline: %s.**" % p["headline"])
    if p["best_by_pickup"]:
        lines.append("Best pickup is %s at %+.2fpp/yr (verdict %s)." % (
            p["best_by_pickup"]["code"], p["best_by_pickup"]["pickup_pp"],
            p["best_by_pickup"]["verdict"]))
    lines.append("")
    lines.append("Curve on the last bar: " + ", ".join(
        "%s %.3f%%" % (k, v) for k, v in sorted(p["curve_today"].items())))
    lines.append("")
    lines.append("Notes: " + p["notes"])
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    p = build(write=True)
    print(json.dumps({"headline": p.get("headline"),
                      "base": (p.get("baseline") or {}).get("net_cagr"),
                      "best": p.get("best_by_pickup")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
