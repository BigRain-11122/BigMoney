"""E223 -- observation-rate ladder: does raising an anchor's frequency buy resolution?

E222 tested the turn-of-month overlay and rejected it, and its power block said the
question needs ~110 years because a calendar rule is observed once per month. That
left an obvious successor: a rule anchored more often (a weekly anchor gets 52
observations a year instead of 12). This face tests whether the extra observations
actually buy resolution, by running the SAME accounting on a ladder of anchors.

Frozen before reading any number:

  * arms: month_turn (first+last session of each month, 12/yr), week_h1, week_h2,
    week_h3 (first 1/2/3 sessions of each ISO week, 52/yr)
  * cost: one round trip (2 sides at COST_BASIS_V1 flat 13.041bp) per PERIOD --
    the anchor decides the period, so a weekly anchor pays weekly
  * excess per period = (held - toll) - all sessions of that period
  * split: first 60% of periods in-sample, rest out-of-sample, minimum OOS window
    24 months / 104 weeks (two years either way)
  * decision rule: ADOPT iff OOS periods >= floor AND OOS net excess/yr > 0 AND
    OOS t >= Bonferroni bar over the four arms AND still net at x2 costs;
    REJECT if the OOS window is long enough and any test fails; UNRESOLVED below.
  * resolution: MDE at 80% power (z=2.802) for the CURRENT test length, in bp/yr,
    because that -- not the observation count -- is what says whether the question
    can be settled. MDE_ann = z * sd_per_period * sqrt(per_year / T).

The ladder's payload is the comparison: an arm with 4.3x the observations resolves
a question better only if its per-period dispersion does not grow by the same
factor. Nothing here is re-tuned after the numbers are read.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402  (shared panel loader + statistics)

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "obs_rate")

# ---------------------------------------------------------------- frozen spec
COST_SIDE_BP = e222.COST_SIDE_BP           # 13.041 flat, per side
COST_X2_MULT = 2.0
SIDES_PER_PERIOD = 2                       # one round trip per anchor period
IS_FRAC = 0.60
ADOPT_T = 2.0
Z_80 = 2.802                               # 80% power, two-sided 5%
PRIMARY_SYMBOL = "sh510300"
BASKET = ["sh510300", "sh510050", "sh510500", "sh512100", "sh588000"]

# hold spec: ("first_last",) for the month anchor, ("first_n", n) for the weekly ones
ARMS = [
    {"name": "month_turn", "bucket": "month", "hold": ("first_last",),
     "periods_per_year": 12, "min_oos": 24},
    {"name": "week_h1", "bucket": "week", "hold": ("first_n", 1),
     "periods_per_year": 52, "min_oos": 104},
    {"name": "week_h2", "bucket": "week", "hold": ("first_n", 2),
     "periods_per_year": 52, "min_oos": 104},
    {"name": "week_h3", "bucket": "week", "hold": ("first_n", 3),
     "periods_per_year": 52, "min_oos": 104},
]


# ---------------------------------------------------------------- buckets
def week_buckets(calendar):
    """[(iso_year, iso_week), [session, ...]] in calendar order.

    ISO weeks are the anchor because a calendar week survives holidays: a week cut
    short by a holiday still has a first session, and the truncated hold is counted
    and published rather than silently equalised.
    """
    out, cur_key, cur = [], None, []
    for d in calendar:
        y, w = datetime.strptime(d, "%Y-%m-%d").isocalendar()[:2]
        key = (y, w)
        if key != cur_key:
            if cur:
                out.append((cur_key, cur))
            cur_key, cur = key, []
        cur.append(d)
    if cur:
        out.append((cur_key, cur))
    return out


def month_buckets(calendar):
    return e222.month_sessions(calendar)


def buckets_for(kind, calendar):
    return month_buckets(calendar) if kind == "month" else week_buckets(calendar)


def held_dates(days, hold):
    """Sessions actually held under a hold spec (never padded past the bucket)."""
    if hold[0] == "first_last":
        return [days[0]] + ([days[-1]] if len(days) > 1 else [])
    return days[:hold[1]]


def period_rows(buckets, ret_by_date, hold):
    """One row per anchor period: all sessions summed, plus the held sessions.

    An unpriced session makes the period unusable rather than contributing a zero,
    and a bucket shorter than the hold is flagged so the truncated count is visible
    (holiday weeks are common and they shrink the held exposure).
    """
    need = 2 if hold[0] == "first_last" else hold[1]
    rows = []
    for key, days in buckets:
        priced = [ret_by_date[d] for d in days if ret_by_date.get(d) is not None]
        all_bp = (1e4 * sum(priced)) if priced else None
        hv = [ret_by_date.get(d) for d in held_dates(days, hold)]
        if not hv or any(v is None for v in hv):
            held_bp = None
        else:
            held_bp = 1e4 * sum(hv)
        rows.append({
            "key": key,
            "n_sessions": len(days),
            "n_priced": len(priced),
            "all_bp": all_bp,
            "held_bp": held_bp,
            "short_bucket": len(days) < need,
            "held_sessions": len(hv),
        })
    return rows


def usable_rows(rows):
    return [r for r in rows if r["all_bp"] is not None and r["held_bp"] is not None]


def split_index(rows):
    return int(len(rows) * IS_FRAC)


# ---------------------------------------------------------------- statistics
def _mean(v):
    return e222._mean(v)


def _sd(v):
    return e222._sd(v)


def period_arm(rows, cost_side_bp, is_n, per_year):
    """Net overlay and excess-vs-always-in per period, split IS / OOS."""
    net, excess = [], []
    for r in rows:
        if r["all_bp"] is None or r["held_bp"] is None:
            continue
        n = r["held_bp"] - SIDES_PER_PERIOD * cost_side_bp
        net.append(n)
        excess.append(n - r["all_bp"])
    is_e, oos_e = excess[:is_n], excess[is_n:]
    sd_oos, m_oos = _sd(oos_e), _mean(oos_e)
    se_oos = (sd_oos / (len(oos_e) ** 0.5)) if (sd_oos is not None and oos_e) else None
    return {
        "periods": len(excess),
        "periods_per_year": per_year,
        "sides_per_period": SIDES_PER_PERIOD,
        "cost_side_bp": cost_side_bp,
        "cost_bp_per_period": SIDES_PER_PERIOD * cost_side_bp,
        "net_bp_per_period": _mean(net),
        "net_bp_per_year": (_mean(net) * per_year) if net else None,
        "excess_bp_per_period": _mean(excess),
        "excess_bp_per_year": (_mean(excess) * per_year) if excess else None,
        "excess_is_bp_per_period": _mean(is_e),
        "excess_oos_bp_per_period": m_oos,
        "excess_oos_bp_per_year": (m_oos * per_year) if m_oos is not None else None,
        "excess_sd_bp_per_period": sd_oos,
        "excess_oos_se_bp": se_oos,
        "excess_oos_t": (m_oos / se_oos) if (se_oos and m_oos is not None) else None,
        "oos_periods": len(oos_e),
        "sharpe_oos_ann": ((m_oos / sd_oos) * (per_year ** 0.5))
                          if (sd_oos and m_oos is not None) else None,
    }


def verdict(a, bar_t, a_x2, min_oos):
    """Frozen rule -- identical shape to E222, applied per PERIOD type."""
    if a["oos_periods"] < min_oos:
        return "UNRESOLVED", "oos_periods_%d_below_%d" % (a["oos_periods"], min_oos)
    if a["excess_oos_bp_per_year"] is None or a["excess_oos_t"] is None:
        return "UNRESOLVED", "oos_series_unusable"
    if a["excess_oos_bp_per_year"] <= 0:
        return "REJECT", "oos_net_excess_not_positive"
    if a["excess_oos_t"] < bar_t:
        return "REJECT", "oos_t_%.2f_below_bar_%.2f" % (a["excess_oos_t"], bar_t)
    if a_x2["excess_oos_bp_per_year"] is None or a_x2["excess_oos_bp_per_year"] <= 0:
        return "REJECT", "dies_at_x2_costs"
    return "ADOPT", "clears_rule"


def mde_block(a, per_year):
    """Minimum detectable annual excess at 80% power for the arm as it stands.

    MDE_ann = z * per_year * sd_per_period / sqrt(n_periods), which collapses to
    z * sd * sqrt(per_year / years) -- the honest cost of a calendar question is
    set by dispersion and horizon, not by the number of observations itself.
    """
    out = {"z_80pct_two_sided": Z_80, "periods_per_year": per_year,
           "oos_periods": a["oos_periods"], "mde_bp_per_period": None,
           "mde_bp_per_year": None, "periods_needed_for_observed": None,
           "years_needed_for_observed": None}
    sd, n = a["excess_sd_bp_per_period"], a["oos_periods"]
    if sd is None or not n or n < 2:
        return out
    se = sd / (n ** 0.5)
    out["mde_bp_per_period"] = Z_80 * se
    out["mde_bp_per_year"] = Z_80 * per_year * se
    m = a["excess_oos_bp_per_period"]
    if m:
        need = (Z_80 * sd / m) ** 2
        out["periods_needed_for_observed"] = need
        out["years_needed_for_observed"] = need / float(per_year)
    return out


# ---------------------------------------------------------------- run
def _arm_record(rows, spec, bar):
    is_n = split_index(rows)
    a = period_arm(rows, COST_SIDE_BP, is_n, spec["periods_per_year"])
    a_x2 = period_arm(rows, COST_SIDE_BP * COST_X2_MULT, is_n, spec["periods_per_year"])
    v, why = verdict(a, bar, a_x2, spec["min_oos"])
    return {
        "arm": a, "x2": a_x2, "verdict": v, "verdict_reason": why,
        "mde": mde_block(a, spec["periods_per_year"]),
        "short_buckets": sum(1 for r in rows if r["short_bucket"]),
        "held_sessions_total": sum(r["held_sessions"] for r in rows),
        "split": {"is_periods": is_n, "oos_periods": len(rows) - is_n,
                  "is_frac": IS_FRAC, "min_oos": spec["min_oos"]},
    }


def run(save=True, panel_dir=None):
    panel_dir = panel_dir or PANEL_DIR
    single = e222.load_closes(PRIMARY_SYMBOL, panel_dir)
    if not single:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = {s: e222.load_closes(s, panel_dir) for s in BASKET}
    basket = {k: v for k, v in basket.items() if v}

    bar = max(ADOPT_T, e222._z_two_sided(0.05 / len(ARMS)))
    payload = {}
    for label, series_map, symbol in (
            ("primary_single", {PRIMARY_SYMBOL: single}, PRIMARY_SYMBOL),
            ("basket_equal_weight", basket, "+".join(sorted(basket)))):
        calendar, rows = e222.daily_returns(series_map)
        if not calendar:
            continue
        ret_by_date = {r["date"]: r["ret"] for r in rows}
        per_arm = {}
        for spec in ARMS:
            buckets = buckets_for(spec["bucket"], calendar)
            prow = usable_rows(period_rows(buckets, ret_by_date, spec["hold"]))
            rec = _arm_record(prow, spec, bar)
            rec["buckets_total"] = len(buckets)
            per_arm[spec["name"]] = rec
        all_in_pp = {spec["name"]: _mean([r["all_bp"] for r in usable_rows(
            period_rows(buckets_for(spec["bucket"], calendar), ret_by_date, spec["hold"]))])
            for spec in ARMS}
        payload[label] = {
            "symbol": symbol,
            "sessions": len(calendar),
            "panel_start": calendar[0] if calendar else None,
            "panel_end": calendar[-1] if calendar else None,
            "always_in_bp_per_period": all_in_pp,
            "arms": per_arm,
        }

    prim = payload["primary_single"]
    ladder = _ladder(prim["arms"])
    face = {
        "study": "e223_obs_rate_ladder",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": prim["panel_end"],
        "spec": {
            "cost_side_bp": COST_SIDE_BP,
            "cost_basis": "rules.py COST_BASIS_V1 flat 13.041bp per side",
            "cost_x2_mult": COST_X2_MULT,
            "sides_per_period": SIDES_PER_PERIOD,
            "is_frac": IS_FRAC,
            "adopt_t_floor": ADOPT_T,
            "multiple_comparison_bar": bar,
            "z_80pct_two_sided": Z_80,
            "arms": [dict(name=s["name"], bucket=s["bucket"],
                          periods_per_year=s["periods_per_year"],
                          min_oos=s["min_oos"], hold=list(s["hold"]))
                     for s in ARMS],
            "primary_symbol": PRIMARY_SYMBOL,
            "basket": BASKET,
            "decision_rule": ("ADOPT iff OOS periods >= floor AND OOS net excess/yr > 0 "
                              "AND OOS t >= the 4-way Bonferroni bar AND still net at x2 "
                              "costs; REJECT if the OOS window is long enough and any "
                              "test fails; UNRESOLVED below the floor. Frozen before "
                              "reading."),
            "resolution_rule": ("the ladder's answer is the MDE at 80% power for each "
                                "arm's own test length, not the observation count"),
        },
        "ladder": ladder,
        "arms": payload,
        "honest": [
            "cash leg earns 0%: the weekly arms sit out 40-80% of sessions and give up "
            "the risk-free rate, which FAVOURS the overlays",
            "close-to-close fills with a per-side charge; no slippage, no open lag",
            "one ETF (today's listing set) for the primary arm: survivorship applies",
            "a truncated holiday week holds fewer sessions than the arm's nominal n; "
            "the count is published per arm as short_buckets rather than equalised",
            "the ladder reads the SAME panel and the same toll as E222, so the only "
            "thing that moves between rungs is the anchor and its period count",
            "no gate and no trial count consumed: the decision rule is the deliverable",
        ],
    }
    if save:
        os.makedirs(OUTDIR, exist_ok=True)
        stem = "OBSRATE-%s" % (face["evidence_cutoff"] or "unknown").replace("-", "")
        for name in (stem + ".json", "latest.json"):
            with open(os.path.join(OUTDIR, name), "w", encoding="utf-8") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
        print("face: %s" % os.path.join(OUTDIR, stem + ".json"))
    for row in ladder["rows"]:
        print("%-11s obs/yr=%2d periods=%4d excess=%8.2fbp/yr t=%6.2f MDE=%8.2fbp/yr -> %s" % (
            row["name"], row["periods_per_year"], row["periods"],
            row["excess_oos_bp_per_year"] or 0.0, row["excess_oos_t"] or 0.0,
            row["mde_bp_per_year"] or 0.0, row["verdict"]))
    print("verdict=%s | %s" % (ladder["verdict"], ladder["answer"][:160]))
    return face


def _ladder(per_arm):
    """The cross-arm comparison -- the actual deliverable of this face."""
    rows = []
    for spec in ARMS:
        rec = per_arm[spec["name"]]
        a, m = rec["arm"], rec["mde"]
        rows.append({
            "name": spec["name"],
            "bucket": spec["bucket"],
            "periods_per_year": spec["periods_per_year"],
            "periods": a["periods"],
            "oos_periods": a["oos_periods"],
            "time_in_market_pct": None,
            "net_bp_per_year": a["net_bp_per_year"],
            "excess_oos_bp_per_year": a["excess_oos_bp_per_year"],
            "excess_oos_t": a["excess_oos_t"],
            "excess_sd_bp_per_period": a["excess_sd_bp_per_period"],
            "mde_bp_per_year": m["mde_bp_per_year"],
            "periods_needed_for_observed": m["periods_needed_for_observed"],
            "verdict": rec["verdict"],
            "verdict_reason": rec["verdict_reason"],
            "short_buckets": rec["short_buckets"],
        })
    base = rows[0]
    for r in rows:
        if r["mde_bp_per_year"] and base["mde_bp_per_year"]:
            r["mde_ratio_vs_month"] = r["mde_bp_per_year"] / base["mde_bp_per_year"]
        else:
            r["mde_ratio_vs_month"] = None
    ok_mde = [r for r in rows if r["mde_bp_per_year"] is not None]
    answer_bits = []
    if len(ok_mde) >= 2:
        worst = max(ok_mde, key=lambda r: r["mde_bp_per_year"] or 0.0)
        best = min(ok_mde, key=lambda r: r["mde_bp_per_year"] or 0.0)
        obs_ratio = float(worst["periods_per_year"]) / float(base["periods_per_year"])
        answer_bits.append(
            "the %d-a-year arms carry %.1fx the observations of the %d-a-year anchor, "
            "yet their annual resolution spans %.2fx (tightest %s) to %.2fx (loosest %s) "
            "of the monthly anchor's -- so observing more often does not resolve a "
            "calendar question unless the per-period dispersion shrinks as fast as the "
            "frequency rises"
            % (worst["periods_per_year"], obs_ratio, base["periods_per_year"],
               (best["mde_bp_per_year"] / base["mde_bp_per_year"]), best["name"],
               (worst["mde_bp_per_year"] / base["mde_bp_per_year"]), worst["name"]))
    any_adopt = [r["name"] for r in rows if r["verdict"] == "ADOPT"]
    unres = [r["name"] for r in rows if r["verdict"] == "UNRESOLVED"]
    verdict = "ADOPT" if any_adopt else ("UNRESOLVED" if len(unres) == len(rows) else "REJECT")
    return {
        "rows": rows,
        "verdict": verdict,
        "adopted_arms": any_adopt,
        "unresolved_arms": unres,
        "obs_ratio_vs_month": (float(max(r["periods_per_year"] for r in rows))
                               / float(base["periods_per_year"])),
        "answer": " ".join(answer_bits) or "the ladder could not be measured",
    }


# ---------------------------------------------------------------- selftest
def _write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "open", "high", "low", "close", "volume", "amount"])
        for d, c in rows:
            w.writerow([d, c, c, c, c, 1000, 1000])


def _weekdays(n_weeks, per_week=5, start=(2020, 1, 6)):
    """Consecutive weekday calendar (no holidays) for `n_weeks` weeks."""
    out = []
    y, m, d = start
    from datetime import date, timedelta
    cur = date(y, m, d)
    for _ in range(n_weeks):
        for _ in range(per_week):
            out.append(cur.isoformat())
            cur += timedelta(days=1)
        cur += timedelta(days=2)      # skip the weekend
    return out


def _synthetic(cal, held_bp_cycle):
    """Closes whose per-session returns follow `held_bp_cycle` (callable day->bp)."""
    level, rows = 1.0, []
    for i, d in enumerate(cal):
        if i > 0:
            level *= (1.0 + held_bp_cycle(i, d) / 1e4)
        rows.append((d, level))
    return rows


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

    tmp = tempfile.mkdtemp(prefix="e223_")
    try:
        # --- 1) bucket shapes
        cal = _weekdays(30, 5)
        wb = week_buckets(cal)
        check("weekly bucketing splits the calendar with no session lost",
              len(wb) == 30 and sum(len(b[1]) for b in wb) == len(cal))
        check("a week keyed by ISO year+week, so a year boundary does not split a week",
              week_buckets(["2020-12-31", "2021-01-01"]) == [((2020, 53),
                                                              ["2020-12-31", "2021-01-01"])])
        check("a holiday week is shorter than the hold and says so",
              period_rows(week_buckets(["2024-01-01", "2024-01-02"]),
                          {"2024-01-01": 0.0, "2024-01-02": 0.01},
                          ("first_n", 3))[0]["short_bucket"] is True)

        # --- 2) hold semantics
        days = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
        check("first_last holds exactly the two ends", held_dates(days, ("first_last",))
              == ["2024-01-01", "2024-01-04"])
        check("first_n holds the first n sessions", held_dates(days, ("first_n", 2))
              == ["2024-01-01", "2024-01-02"])
        check("first_n never pads past the bucket", held_dates(days[:1], ("first_n", 3))
              == ["2024-01-01"])

        # --- 3) row arithmetic: unpriced sessions are holes, not zeros
        ret = {days[0]: 0.01, days[1]: 0.02, days[2]: 0.03, days[3]: 0.04}
        r = period_rows([("k", days)], ret, ("first_last",))[0]
        check("all_bp sums every priced session of the period",
              abs(r["all_bp"] - 1000.0) < 1e-6)
        check("held_bp sums only the held sessions",
              abs(r["held_bp"] - 500.0) < 1e-6)
        r_hole = period_rows([("k", days)], {days[0]: 0.01}, ("first_last",))[0]
        check("an unpriced held session makes the period unusable, never zero-filled",
              r_hole["held_bp"] is None and r_hole["all_bp"] is not None)

        # --- 4) arm arithmetic: one round trip per PERIOD, not per held session
        rows = period_rows([("k", days)], ret, ("first_n", 2))
        a = period_arm(rows, COST_SIDE_BP, 0, 52)
        check("the toll is exactly two sides per period",
              abs(a["cost_bp_per_period"] - 2 * COST_SIDE_BP) < 1e-9)
        check("net = held - toll", abs(a["net_bp_per_period"]
                                       - (300.0 - 2 * COST_SIDE_BP)) < 1e-6)
        check("excess = net - always-in (identity)",
              abs(a["excess_bp_per_period"] - ((300.0 - 2 * COST_SIDE_BP) - 1000.0)) < 1e-6)
        check("annualisation uses the arm's own period count, not 12",
              abs(a["net_bp_per_year"] - a["net_bp_per_period"] * 52) < 1e-6)

        # --- 5) a dispersion fixture, so REJECT/ADOPT are reachable
        cal2 = _weekdays(30, 5)
        held_ids = {1, 2, 6, 7, 11, 12, 16, 17, 21, 22, 26, 27}   # first two, alternating weeks
        rows_w = _synthetic(cal2, lambda i, d: (25.0 if i in held_ids else -20.0)
                            * (1.0 if i % 3 else -1.0))
        path = os.path.join(tmp, "p1")
        if not os.path.isdir(path):
            os.makedirs(path)
        _write_csv(os.path.join(path, "x.csv"), rows_w)
        calx, rws = e222.daily_returns({"x": e222.load_closes("x", path)})
        retx = {rw["date"]: rw["ret"] for rw in rws}
        prow = usable_rows(period_rows(week_buckets(calx), retx, ("first_n", 2)))
        aw = period_arm(prow, COST_SIDE_BP, split_index(prow), 52)
        check("a dispersed arm reports a real dispersion and a t or an explicit none",
              aw["excess_sd_bp_per_period"] is not None
              and (aw["excess_oos_t"] is not None or aw["excess_oos_se_bp"] is None))
        mblk = mde_block(aw, 52)
        check("MDE is priced in bp/yr at the arm's own frequency",
              mblk["mde_bp_per_year"] is not None
              and abs(mblk["mde_bp_per_year"]
                      - Z_80 * 52 * (aw["excess_sd_bp_per_period"]
                                     / (aw["oos_periods"] ** 0.5))) < 1e-6)

        # --- 6) the MDE comparison is the frequency, not the observation count
        fake_month = {"excess_sd_bp_per_period": 100.0, "oos_periods": 52,
                      "excess_oos_bp_per_period": 50.0}
        fake_week = {"excess_sd_bp_per_period": 100.0, "oos_periods": 52,
                     "excess_oos_bp_per_period": 50.0}
        mde_m = mde_block(fake_month, 12)["mde_bp_per_year"]
        mde_w = mde_block(fake_week, 52)["mde_bp_per_year"]
        check("equal dispersion and equal n: the higher-frequency arm needs MORE annual "
              "effect, so observations alone do not resolve anything",
              abs(mde_w / mde_m - (52.0 / 12.0)) < 1e-9)

        # --- 7) verdict branches, each reachable
        base = {"oos_periods": 200, "excess_oos_bp_per_year": 20.0,
                "excess_oos_t": 3.0, "excess_oos_bp_per_period": 1.0}
        x2ok = {"excess_oos_bp_per_year": 10.0}
        check("ADOPT path is reachable and needs the bar",
              verdict(base, 2.39, x2ok, 104)[0] == "ADOPT")
        check("a short out-of-sample window is UNRESOLVED, never ADOPT",
              verdict(dict(base, oos_periods=10), 2.39, x2ok, 104)[0] == "UNRESOLVED")
        check("a non-positive excess REJECTs with a named reason",
              verdict(dict(base, excess_oos_bp_per_year=-1.0), 2.39, x2ok, 104)
              == ("REJECT", "oos_net_excess_not_positive"))
        check("a t below the bar REJECTs with a named reason",
              verdict(dict(base, excess_oos_t=1.0), 2.39, x2ok, 104)[1].startswith("oos_t_"))
        check("dying at x2 costs REJECTs with a named reason",
              verdict(base, 2.39, {"excess_oos_bp_per_year": -2.0}, 104)
              == ("REJECT", "dies_at_x2_costs"))
        check("a zero-variance arm is unusable rather than t=infinity",
              verdict(dict(base, excess_oos_t=None), 2.39, x2ok, 104)
              == ("UNRESOLVED", "oos_series_unusable"))

        # --- 8) the ladder summary reports the tightest and loosest arm honestly
        def _fake(mde_yr, sd, periods, t):
            return {"arm": {"periods": periods, "oos_periods": periods,
                            "net_bp_per_year": 1.0, "excess_oos_bp_per_year": 2.0,
                            "excess_oos_t": t, "excess_sd_bp_per_period": sd},
                    "verdict": "REJECT", "verdict_reason": "fixture",
                    "short_buckets": 0,
                    "mde": {"mde_bp_per_year": mde_yr,
                            "periods_needed_for_observed": 5.0}}
        lad = _ladder({
            "month_turn": _fake(20.0, 30.0, 100, 0.5),
            "week_h1": _fake(60.0, 80.0, 400, 0.9),
            "week_h2": _fake(61.0, 81.0, 400, 0.8),
            "week_h3": _fake(62.0, 82.0, 400, 0.7),
        })
        check("the ladder names the tightest and loosest resolution",
              "month_turn" in lad["answer"] and "week_h3" in lad["answer"]
              and lad["verdict"] == "REJECT")

        # --- 9) determinism of the payload
        check("period_arm is deterministic",
              period_arm(prow, COST_SIDE_BP, split_index(prow), 52) == aw)

        # --- 10) the frozen spec is self-consistent
        check("every arm pays two sides and the bar is the 4-way Bonferroni value",
              SIDES_PER_PERIOD == 2 and len(ARMS) == 4
              and max(ADOPT_T, e222._z_two_sided(0.05 / len(ARMS)))
              > e222._z_two_sided(0.05 / 3))
        check("the weekly arms ask for two years of out-of-sample, not one month's worth",
              [s["min_oos"] for s in ARMS if s["bucket"] == "week"] == [104, 104, 104])
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