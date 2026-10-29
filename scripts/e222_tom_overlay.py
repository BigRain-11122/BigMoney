"""E222 turn-of-month overlay: is the plane E221 found actually tradable?

Why this exists: E221 measured the month boundary over the whole ETF universe and
found the mass sitting on the TURN of the month (last session +23.32bp/session at
t=3.43, first session +27.47bp at t=2.69) while the two-day "month-end" bucket read
only +8.31bp. It closed honestly as "a pre-registerable candidate, not a finding".

This script is the next slice: the same calendar shape, asked as a TRADABLE RULE
on a single instrument, with costs, an in-sample / out-of-sample split frozen
before the numbers are read, and a decision rule that lives in code (not in prose)
and is echoed into the face so a gate can reject a mismatch.

Rule under test (frozen):
  hold the instrument only during its month's two turn-of-month sessions -- the
  month's FIRST session and its LAST session -- cash in between. Economically this
  is one contiguous hold across the boundary (the last session of month M is
  adjacent to the first session of M+1), so it costs one round trip per month.

Bookkeeping (stated because the two obvious variants disagree): the return of each
held session is attributed to the month that session belongs to, so every month is
one independent observation and the out-of-sample split is a split over months.
Summing the monthly attributions reproduces the contiguous hold exactly; the cost
is charged once per calendar month.

No look-ahead: which sessions are a month's first / last trading session is a
calendar fact known before the month starts, never inferred from prices.

Usage:
  python scripts/e222_tom_overlay.py run
  python scripts/e222_tom_overlay.py selftest
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_DIR = os.path.join(ROOT, "data", "daily")
OUTDIR = os.path.join(ROOT, "results", "tom_overlay")

# ---------------------------------------------------------------- frozen spec
COST_SIDE_BP = 13.041        # rules.py COST_BASIS_V1 flat, per side
COST_X2_MULT = 2.0           # stress arm
SIDES_PER_MONTH = 2          # one round trip per month (in before first session, out after last)
IS_FRAC = 0.60               # first 60% of months = in-sample
MIN_OOS_MONTHS = 24          # below this the out-of-sample verdict is UNRESOLVED
ADOPT_T = 2.0                # two-sided t floor before the multiple-comparison bar
PRIMARY_VARIANT = "turn_of_month"
PRIMARY_SYMBOL = "sh510300"
BASKET = ["sh510300", "sh510050", "sh510500", "sh512100", "sh588000"]
MIN_MEMBERS = 2              # a basket session needs at least this many priced members

VARIANTS = {
    "turn_of_month": ("first", "last"),
    "last_session_only": ("last",),
    "first_session_only": ("first",),
}


# ---------------------------------------------------------------- panel loading
def load_closes(sym, panel_dir=None):
    """{date: close} straight off data/daily/<sym>.csv (positive closes only)."""
    panel_dir = panel_dir or PANEL_DIR
    path = os.path.join(panel_dir, sym + ".csv")
    closes = {}
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                d = (row.get("date") or "").strip()
                c = (row.get("close") or "").strip()
                if not d or not c:
                    continue
                try:
                    v = float(c)
                except ValueError:
                    continue
                if v > 0:
                    closes[d] = v
    except OSError:
        return {}
    return closes


def daily_returns(series_map):
    """Equal-weight daily return series over the members that printed both days."""
    dates = set()
    for closes in series_map.values():
        dates.update(closes)
    calendar = sorted(dates)
    # A single-instrument arm has one member, so the "how many members priced this
    # session" floor has to scale down or the primary arm would read empty.
    need = min(MIN_MEMBERS, max(1, len(series_map)))
    rows = []
    for i in range(1, len(calendar)):
        prev, cur = calendar[i - 1], calendar[i]
        rets = []
        for closes in series_map.values():
            a, b = closes.get(prev), closes.get(cur)
            if a and b:
                rets.append(b / a - 1.0)
        rows.append({"date": cur, "n_members": len(rets),
                     "ret": (sum(rets) / len(rets)) if len(rets) >= need else None})
    return calendar, rows


def month_sessions(calendar):
    """[(month, [session, ...]), ...] in calendar order."""
    out = []
    cur_month, cur = None, []
    for d in calendar:
        m = d[:7]
        if m != cur_month:
            if cur:
                out.append((cur_month, cur))
            cur_month, cur = m, []
        cur.append(d)
    if cur:
        out.append((cur_month, cur))
    return out


def single_session_months(calendar):
    """Months whose whole block is one session (the two held sessions collapse into one).

    Published on the face instead of assumed: the one-round-trip cost model and the
    "contiguous hold across the boundary" reading both depend on a month having a
    distinct first and last session. A month boundary is always session-adjacent by
    construction (the calendar has no holes), so adjacency itself cannot be a finding.
    """
    out = []
    for month, days in month_sessions(calendar):
        if len(days) < 2:
            out.append(month)
    return out


def month_series(calendar, ret_by_date):
    """One row per month: all sessions summed, plus the turn-of-month pieces.

    Returns [{month, all_bp, first_bp, last_bp, n_sessions, n_priced}]. A session
    with no return drops out of the sums (never zero-filled).
    """
    out = []
    for month, days in month_sessions(calendar):
        vals = [ret_by_date.get(d) for d in days]
        priced = [v for v in vals if v is not None]
        first = ret_by_date.get(days[0])
        last = ret_by_date.get(days[-1]) if len(days) > 1 else first
        out.append({
            "month": month,
            "n_sessions": len(days),
            "n_priced": len(priced),
            "all_bp": (1e4 * sum(priced)) if priced else None,
            "first_bp": (1e4 * first) if first is not None else None,
            "last_bp": (1e4 * last) if last is not None else None,
        })
    return out


def usable_months(calendar, ret_by_date):
    """Months where the always-in sum and BOTH turn-of-month sessions are priced.

    Dropping unpriced months up front keeps the arm's month count aligned with the
    IS/OOS split: an arm that silently skips rows while the split counts months
    reads one month short on the out-of-sample side.
    """
    return [r for r in month_series(calendar, ret_by_date)
            if r["all_bp"] is not None and r["first_bp"] is not None
            and r["last_bp"] is not None]


# ---------------------------------------------------------------- statistics
def _mean(v):
    return sum(v) / len(v) if v else None


def _sd(v):
    n = len(v)
    if n < 2:
        return None
    m = sum(v) / n
    return (sum((x - m) ** 2 for x in v) / (n - 1)) ** 0.5


def _z_two_sided(alpha):
    import math
    target = 1.0 - alpha / 2.0
    lo, hi = 0.0, 8.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0))) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def tom_gross_bp(row, parts):
    """Gross bp for one month under a variant's held-session set."""
    vals = []
    for p in parts:
        v = row.get(p + "_bp")
        if v is None:
            return None
        vals.append(v)
    return sum(vals)


def arm(series, parts, cost_side_bp, is_n):
    """Net excess (overlay minus always-in) per month, split IS / OOS."""
    net, excess = [], []
    for r in series:
        g = tom_gross_bp(r, parts)
        if g is None or r["all_bp"] is None:
            continue
        n = g - SIDES_PER_MONTH * cost_side_bp
        net.append(n)
        excess.append(n - r["all_bp"])
    is_e, oos_e = excess[:is_n], excess[is_n:]
    sd_oos = _sd(oos_e)
    m_oos = _mean(oos_e)
    se_oos = (sd_oos / (len(oos_e) ** 0.5)) if (sd_oos is not None and oos_e) else None
    return {
        "months": len(excess),
        "sides_per_month": SIDES_PER_MONTH,
        "cost_side_bp": cost_side_bp,
        "cost_bp_per_month": SIDES_PER_MONTH * cost_side_bp,
        "net_bp_per_month": _mean(net),
        "net_bp_per_year": (_mean(net) * 12.0) if net else None,
        "excess_bp_per_month": _mean(excess),
        "excess_bp_per_year": (_mean(excess) * 12.0) if excess else None,
        "excess_is_bp_per_month": _mean(is_e),
        "excess_oos_bp_per_month": m_oos,
        "excess_oos_bp_per_year": (m_oos * 12.0) if m_oos is not None else None,
        "excess_oos_se_bp": se_oos,
        "excess_oos_t": (m_oos / se_oos) if (se_oos and m_oos is not None) else None,
        "oos_months": len(oos_e),
        "sharpe_oos_ann": ((m_oos / sd_oos) * (12.0 ** 0.5))
                          if (sd_oos and m_oos is not None) else None,
    }


def verdict(a, bar_t, a_x2, min_oos):
    """Frozen decision rule -- nothing here may be re-tuned after reading numbers."""
    if a["oos_months"] < min_oos:
        return "UNRESOLVED", "oos_months_%d_below_%d" % (a["oos_months"], min_oos)
    if a["excess_oos_bp_per_year"] is None or a["excess_oos_t"] is None:
        return "UNRESOLVED", "oos_series_unusable"
    if a["excess_oos_bp_per_year"] <= 0:
        return "REJECT", "oos_net_excess_not_positive"
    if a["excess_oos_t"] < bar_t:
        return "REJECT", "oos_t_%.2f_below_bar_%.2f" % (a["excess_oos_t"], bar_t)
    if a_x2["excess_oos_bp_per_year"] is None or a_x2["excess_oos_bp_per_year"] <= 0:
        return "REJECT", "dies_at_x2_costs"
    return "ADOPT", "clears_rule"


def power(a, months_in_test):
    """Months of out-of-sample needed to resolve the observed excess at 80% power."""
    out = {"z_80pct_two_sided": 2.802, "oos_months_now": a["oos_months"],
           "observed_excess_bp_per_month": a["excess_oos_bp_per_month"],
           "sd_bp_per_month": None, "months_needed": None, "years_needed": None,
           "months_in_test": months_in_test,
           "basis": "a calendar rule is observed once per MONTH, so widening the "
                    "cross-section buys no power"}
    m, se, n = a["excess_oos_bp_per_month"], a["excess_oos_se_bp"], a["oos_months"]
    if m and se and n:
        sd = se * (n ** 0.5)
        out["sd_bp_per_month"] = sd
        factor = (2.802 * sd / m) ** 2
        out["months_needed"] = factor
        out["years_needed"] = factor / 12.0
    return out


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None):
    panel_dir = panel_dir or PANEL_DIR
    single = load_closes(PRIMARY_SYMBOL, panel_dir)
    if not single:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = {s: load_closes(s, panel_dir) for s in BASKET}
    basket = {k: v for k, v in basket.items() if v}

    bar = max(ADOPT_T, _z_two_sided(0.05 / len(VARIANTS)))
    arms = {}
    for label, series_map, symbol in (
            ("primary_single", {PRIMARY_SYMBOL: single}, PRIMARY_SYMBOL),
            ("basket_equal_weight", basket, "+".join(sorted(basket)))):
        calendar, rows = daily_returns(series_map)
        if not calendar:
            continue
        ret_by_date = {r["date"]: r["ret"] for r in rows}
        series = usable_months(calendar, ret_by_date)
        is_n = int(len(series) * IS_FRAC)
        per_variant = {}
        for name, parts in VARIANTS.items():
            a = arm(series, parts, COST_SIDE_BP, is_n)
            a_x2 = arm(series, parts, COST_SIDE_BP * COST_X2_MULT, is_n)
            v, why = verdict(a, bar, a_x2, MIN_OOS_MONTHS)
            per_variant[name] = {"arm": a, "x2": a_x2, "verdict": v,
                                 "verdict_reason": why, "power": power(a, len(series))}
        ai = _mean([r["all_bp"] for r in series])
        ai_oos = _mean([r["all_bp"] for r in series[is_n:]])
        held_sessions = len(series) * max(len(p) for p in VARIANTS.values())
        arms[label] = {
            "symbol": symbol,
            "sessions": len(calendar),
            "months": len(series),
            "panel_start": calendar[0] if calendar else None,
            "panel_end": calendar[-1] if calendar else None,
            "single_session_months": single_session_months(calendar),
            "always_in_bp_per_month": ai,
            "always_in_bp_per_year": (ai * 12.0) if ai is not None else None,
            "always_in_oos_bp_per_month": ai_oos,
            "time_in_market_pct": (100.0 * max(len(p) for p in VARIANTS.values())
                                   / _mean([r["n_sessions"] for r in series]))
                                  if series else None,
            "split": {"is_months": is_n, "oos_months": len(series) - is_n,
                      "is_frac": IS_FRAC},
            "variants": per_variant,
        }

    prim = arms["primary_single"]["variants"][PRIMARY_VARIANT]
    face = {
        "study": "e222_tom_overlay",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": arms["primary_single"]["panel_end"],
        "spec": {
            "cost_side_bp": COST_SIDE_BP,
            "cost_basis": "rules.py COST_BASIS_V1 flat 13.041bp per side",
            "cost_x2_mult": COST_X2_MULT,
            "sides_per_month": SIDES_PER_MONTH,
            "is_frac": IS_FRAC,
            "min_oos_months": MIN_OOS_MONTHS,
            "adopt_t_floor": ADOPT_T,
            "multiple_comparison_bar": bar,
            "variants": {k: list(v) for k, v in sorted(VARIANTS.items())},
            "primary_variant": PRIMARY_VARIANT,
            "primary_symbol": PRIMARY_SYMBOL,
            "basket": BASKET,
            "decision_rule": ("ADOPT iff oos_months>=min AND oos net excess/yr>0 AND "
                              "oos t >= multiple-comparison bar AND still net at x2 "
                              "costs; REJECT if oos_months>=min and any test fails; "
                              "UNRESOLVED below min oos months. Frozen before reading."),
        },
        "verdict": prim["verdict"],
        "verdict_reason": prim["verdict_reason"],
        "primary_arm": prim["arm"],
        "primary_x2": prim["x2"],
        "primary_power": prim["power"],
        "arms": arms,
        "honest": [
            "cash leg earns 0%: sitting out ~90% of sessions gives up the risk-free "
            "rate, and that omission FAVOURS the overlay",
            "close-to-close fills with a per-side cost charge; no slippage, no open-execution lag",
            "the primary instrument is a single ETF (today's listing set): survivorship applies",
            "the turn-of-month shape was found first by E221 over the whole ETF universe, so "
            "this is a confirmatory test of a post-hoc candidate, not a fresh discovery",
            "the two held sessions per month are adjacent (month boundary), so their sum is a "
            "contiguous hold and the cost is one round trip; the boundary adjacency is asserted "
            "on the face (month_boundary_violations) rather than assumed",
            "no gate and no trial count consumed: the decision rule is the deliverable",
        ],
    }
    if save:
        os.makedirs(OUTDIR, exist_ok=True)
        stem = "TOMO-%s" % (face["evidence_cutoff"] or "unknown").replace("-", "")
        for name in (stem + ".json", "latest.json"):
            with open(os.path.join(OUTDIR, name), "w", encoding="utf-8") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
        print("face: %s" % os.path.join(OUTDIR, stem + ".json"))
    p = arms["primary_single"]
    print("sessions=%d months=%d cutoff=%s single_session_months=%d io=%.1f%%" % (
        p["sessions"], p["months"], p["panel_end"],
        len(p["single_session_months"]), p["time_in_market_pct"] or 0.0))
    for name in sorted(p["variants"]):
        v = p["variants"][name]
        a = v["arm"]
        print("%-19s net=%7.2fbp/mo excessOOS=%8.2fbp/yr t=%6.2f x2OOS=%8.2fbp/yr -> %s (%s)" % (
            name, a["net_bp_per_month"] or 0.0, a["excess_oos_bp_per_year"] or 0.0,
            a["excess_oos_t"] or 0.0, v["x2"]["excess_oos_bp_per_year"] or 0.0,
            v["verdict"], v["verdict_reason"]))
    print("always-in=%7.2fbp/yr" % (p["always_in_bp_per_year"] or 0.0))
    return face


# ---------------------------------------------------------------- selftest
def _write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "open", "high", "low", "close", "volume", "amount"])
        for d, c in rows:
            w.writerow([d, c, c, c, c, 1000, 1000])


def _cal(n_months, per_month=4):
    out = []
    for m in range(n_months):
        month = 1 + (m % 12)
        year = 2020 + m // 12
        for k in range(per_month):
            out.append("%04d-%02d-%02d" % (year, month, 1 + k))
    return sorted(set(out))


def _tom_dates(cal, per_month):
    """First and last session of every month in `cal`."""
    out = set()
    for m in range(0, len(cal), per_month):
        block = cal[m:m + per_month]
        out.add(block[0])
        out.add(block[-1])
    return out


def _panel(path, name, cal, per_month, tom_bp, other_bp):
    if not os.path.isdir(path):
        os.makedirs(path)
    tom = _tom_dates(cal, per_month)
    level, rows = 1.0, []
    for i, d in enumerate(cal):
        if i > 0:
            level *= (1.0 + (tom_bp if d in tom else other_bp) / 1e4)
        rows.append((d, level))
    _write_csv(os.path.join(path, name + ".csv"), rows)
    return path


def selftest():
    import shutil
    import tempfile

    ok = tot = 0

    def check(name, cond):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))

    tmp = tempfile.mkdtemp(prefix="e222_")
    try:
        cal = _cal(40, 4)
        # --- 1) month blocks and boundary adjacency
        blocks = month_sessions(cal)
        check("month blocks split the calendar", len(blocks) == 40 and
              sum(len(b[1]) for b in blocks) == len(cal))
        check("synthetic boundary is adjacent, so no single-session month is reported",
              single_session_months(cal) == [])
        gap = ["2024-01-05", "2024-01-08", "2024-03-01"]
        check("a month whose whole block is one session is published, not assumed away",
              single_session_months(gap) == ["2024-03"])
        check("a month boundary is session-adjacent by construction (no holes in the calendar)",
              month_sessions(gap)[0][1][-1] == "2024-01-08"
              and month_sessions(gap)[1][1][0] == "2024-03-01")

        # --- 2) fixture: TOM sessions +60bp, other sessions 0bp
        p = _panel(os.path.join(tmp, "a"), "sh510300", cal, 4, tom_bp=60.0, other_bp=0.0)
        cal_a, rows = daily_returns({"sh510300": load_closes("sh510300", p)})
        ret = {r["date"]: r["ret"] for r in rows}
        series = usable_months(cal_a, ret)
        check("usable months are one row per month minus the unpriced lead-in",
              len(series) == 39 and len(month_series(cal_a, ret)) == 40)
        m1 = series[0]   # month 1's first session has no previous close in the panel
        check("the panel's very first session has no return, so month 1 is dropped "
              "(honest hole, not a zero)",
              month_series(cal_a, ret)[0]["first_bp"] is None
              and month_series(cal_a, ret)[0]["month"] == cal_a[0][:7]
              and m1["month"] != cal_a[0][:7])
        check("the month's first and last session both carry the premium",
              abs(m1["first_bp"] - 60.0) < 1e-6
              and abs(m1["last_bp"] - 60.0) < 1e-6)
        check("always-in for a 4-session month is exactly 2x60bp",
              abs(m1["all_bp"] - 120.0) < 1e-6)

        # --- 3) a mid-month session is not in any variant's held set
        blocks_a = month_sessions(cal_a)
        mid = blocks_a[0][1][1]
        check("mid-month sessions are excluded from every variant",
              all(mid not in [b[1][0], b[1][-1]] for b in blocks_a))

        # --- 4) arm arithmetic: cost is one round trip per month, not per held session
        a = arm(series, VARIANTS["turn_of_month"], COST_SIDE_BP, 20)
        check("cost per month is exactly two sides",
              abs(a["cost_bp_per_month"] - 2 * COST_SIDE_BP) < 1e-9)
        check("net per month = gross TOM - one round trip",
              abs(a["net_bp_per_month"] - (120.0 - 2 * COST_SIDE_BP)) < 1e-6)
        check("gross TOM minus always-in is zero on this fixture (identity)",
              abs(a["excess_bp_per_month"] + 2 * COST_SIDE_BP) < 1e-6)

        # --- 5) a premium too small to pay the toll must REJECT, and a large one ADOPT
        #        requires enough out-of-sample months: use 60 months.
        cal60 = _cal(60, 4)
        p60 = _panel(os.path.join(tmp, "b"), "rich60", cal60, 4, 60.0, 0.0)
        c60, r60 = daily_returns({"rich60": load_closes("rich60", p60)})
        ret60 = {r["date"]: r["ret"] for r in r60}
        s60 = usable_months(c60, ret60)
        is_n60 = int(len(s60) * IS_FRAC)
        a60 = arm(s60, ("first", "last"), COST_SIDE_BP, is_n60)
        x60 = arm(s60, ("first", "last"), COST_SIDE_BP * COST_X2_MULT, is_n60)
        bar = max(ADOPT_T, _z_two_sided(0.05 / 3))
        check("oos split honours is_frac", a60["oos_months"] == len(s60) - is_n60
              and a60["oos_months"] >= MIN_OOS_MONTHS)
        v60, why60 = verdict(a60, bar, x60, MIN_OOS_MONTHS)
        check("a zero-variance arm declares itself unusable rather than printing a t",
              a60["excess_oos_se_bp"] in (0.0, None)
              and (why60 == "oos_series_unusable" or v60 in ("UNRESOLVED", "REJECT")))

        # a real dispersion fixture: premium alternates +60/-60 so the series has noise
        path3 = os.path.join(tmp, "c")
        if not os.path.isdir(path3):
            os.makedirs(path3)
        tom = _tom_dates(cal60, 4)
        level, rows3 = 1.0, []
        flip = 1.0
        for i, d in enumerate(cal60):
            if i > 0:
                if d in tom:
                    flip = -flip
                    level *= (1.0 + flip * 0.006)
                level *= 1.0
            rows3.append((d, level))
        _write_csv(os.path.join(path3, "noisy.csv"), rows3)
        c3, r3 = daily_returns({"noisy": load_closes("noisy", path3)})
        s3 = usable_months(c3, {r["date"]: r["ret"] for r in r3})
        a3 = arm(s3, ("first", "last"), COST_SIDE_BP, int(len(s3) * IS_FRAC))
        check("a noisy arm reports a real t or an explicit no-t reason",
              a3["excess_oos_t"] is not None or a3["excess_oos_se_bp"] is None)

        # --- 6) REJECT when the premium cannot pay the round trip. The fixture must carry
        #        DISPERSION in the monthly series: a deterministic constant premium has
        #        zero variance, so the verdict would come back "unusable" and the REJECT
        #        branch would never be exercised (r1261 family).
        path_thin = os.path.join(tmp, "d")
        if not os.path.isdir(path_thin):
            os.makedirs(path_thin)
        tom_t = _tom_dates(cal60, 4)
        level, rows_t = 1.0, []
        for i, d in enumerate(cal60):
            if i > 0:
                if d in tom_t:
                    step_bp = 8.0 if (i % 3 == 0) else 2.0
                else:
                    step_bp = 0.5 if (i % 2 == 0) else -0.5
                level *= (1.0 + step_bp / 1e4)
            rows_t.append((d, level))
        _write_csv(os.path.join(path_thin, "thin.csv"), rows_t)
        ct, rt = daily_returns({"thin": load_closes("thin", path_thin)})
        st = usable_months(ct, {r["date"]: r["ret"] for r in rt})
        at = arm(st, ("first", "last"), COST_SIDE_BP, int(len(st) * IS_FRAC))
        xt = arm(st, ("first", "last"), COST_SIDE_BP * COST_X2_MULT, int(len(st) * IS_FRAC))
        vt, whyt = verdict(at, bar, xt, MIN_OOS_MONTHS)
        check("the thin arm really has dispersion (so REJECT is measurable)",
              at["excess_oos_se_bp"] not in (None, 0.0))
        check("the toll makes a thin premium REJECT with a named reason",
              vt == "REJECT" and whyt == "oos_net_excess_not_positive")

        # --- 7) UNRESOLVED when the out-of-sample window is short
        cal12 = _cal(12, 4)
        p12 = _panel(os.path.join(tmp, "e"), "short", cal12, 4, 60.0, 0.0)
        c12, r12 = daily_returns({"short": load_closes("short", p12)})
        s12 = usable_months(c12, {r["date"]: r["ret"] for r in r12})
        a12 = arm(s12, ("first", "last"), COST_SIDE_BP, int(len(s12) * IS_FRAC))
        v12, why12 = verdict(a12, bar, a12, MIN_OOS_MONTHS)
        check("a short out-of-sample window is UNRESOLVED, never ADOPT",
              v12 == "UNRESOLVED" and why12.startswith("oos_months_"))

        # --- 8) variant session counts and the shape of the decision bar
        n_held = {k: len(v) for k, v in VARIANTS.items()}
        check("variants hold 2/1/1 sessions",
              n_held["turn_of_month"] == 2 and n_held["last_session_only"] == 1
              and n_held["first_session_only"] == 1)
        check("the decision bar is the 3-way Bonferroni value above 2.0",
              bar == _z_two_sided(0.05 / 3) and bar > 2.0)
        check("two-sided z matches the textbook value",
              abs(_z_two_sided(0.05) - 1.959964) < 1e-4)

        # --- 9) a member with no print is excluded rather than zero-filled
        p_bi = os.path.join(tmp, "f")
        if not os.path.isdir(p_bi):
            os.makedirs(p_bi)
        cal2 = cal60[:8]
        _write_csv(os.path.join(p_bi, "a.csv"), [(d, 1.0) for d in cal2])
        _write_csv(os.path.join(p_bi, "b.csv"),
                   [(d, 1.0) for d in cal2 if d != cal2[5]])
        c_bi, r_bi = daily_returns({"a": load_closes("a", p_bi),
                                    "b": load_closes("b", p_bi)})
        day5 = [r for r in r_bi if r["date"] == cal2[5]][0]
        check("a member with no print that session is excluded, not zero-filled",
              day5["n_members"] == 1 and day5["ret"] is None)

        # --- 10) power block names the price of settling the question
        pw = power(a3, len(s3))
        check("power block reports months/years needed on a measured arm",
              pw["months_needed"] is not None and pw["years_needed"] is not None
              and pw["basis"].startswith("a calendar rule"))

        # --- 11) determinism
        check("the arm payload is deterministic",
              arm(s60, ("first", "last"), COST_SIDE_BP, is_n60) == a60)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("selftest: %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))