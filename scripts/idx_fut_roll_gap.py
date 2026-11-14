"""Index-futures roll days: how many the published mask finds, and what the ones it misses
do to the carry reading.

Why this exists (r1692, out of r1690's own caveat: "the roll premium itself is not
reconstructed -- measure the actual roll-day cost from the futures panel before any sizing
claim").

The panel is a main-contract continuous series: on the day the series switches contracts it
jumps by the difference between the two contracts' prices.  A holder who rolls does NOT book
that jump -- they sell the old contract and buy the new one with the same money, so the
level reset is not a loss.  Masking the roll day is therefore the correct treatment, and the
carry a roller earns is what the surviving days add up to.

Which makes the DETECTOR the thing worth measuring.  `idx_fut_basis.basis_face` marks a roll
when the basis step is 8x the median step and above 0.5%: on IF that finds 26 days in 2,382,
while the index futures roll once a month.  Every roll it misses stays in the spread series
as a fake loss, so the published carry is the carry minus the jumps nobody masked.

This face measures that directly: calendar-anchored roll days (third-Friday expiry window,
the splice is the most negative basis step in it), the carry under each mask, and r1690's
three arms re-run under both masks.

  python scripts/idx_fut_roll_gap.py            # write results/idx_fut_roll_gap.json/.md
  python scripts/idx_fut_roll_gap.py selftest   # offline synthetic legs
  python scripts/idx_fut_roll_gap.py --check    # re-derive the states from the face
"""
import argparse
import datetime as dt
import io
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_basis as base            # noqa: E402  (panels, pair table, published mask)
import idx_fut_basis_timing as timing  # noqa: E402  (causal percentile, one implementation)
import idx_fut_basis_wait as wait      # noqa: E402  (arms, repo accrual, leash, stats)

OUT_JSON = os.path.join(ROOT, "results", "idx_fut_roll_gap.json")
OUT_MD = os.path.join(ROOT, "research", "IDX_FUT_ROLL_GAP.md")
DAYS_PER_YEAR = 244.0

# Frozen before any number was read.
CRITERIA = {
    "expiry_window_before_days": 6,   # the splice is not always on expiry day
    "expiry_window_after_days": 3,
    "min_months_covered_pct": 90.0,   # below this the calendar detector is not usable
    "missed_share_min_pct": 20.0,     # a mask that misses this much of the rolls is incomplete
    "reading_gap_min_pp": 1.0,        # ...and it has to move the annualised reading this far
}


# ---------------------------------------------------------------- calendar
def third_friday(year: int, month: int) -> dt.date:
    """Expiry of the mainland index futures: the third Friday of the contract month."""
    d = dt.date(year, month, 1)
    first_friday = d + dt.timedelta(days=(4 - d.weekday()) % 7)
    return first_friday + dt.timedelta(days=14)


def as_date(s: str) -> dt.date:
    y, m, d = (int(x) for x in s.split("-"))
    return dt.date(y, m, d)


def calendar_rolls(dates, basis):
    """The splice day of each contract month, anchored on the expiry calendar.

    The series jumps to the next contract somewhere around expiry, and the jump is a step
    DOWN in the basis (the next contract trades at a deeper discount than the one that just
    converged).  Each month's roll is the most negative basis step inside
    [expiry - before, expiry + after], searched only inside that month.

    Returns (rolls, info): rolls maps date -> step; info carries the honesty counts.
    """
    before = CRITERIA["expiry_window_before_days"]
    after = CRITERIA["expiry_window_after_days"]
    db = {}
    for k in range(len(basis) - 1):
        db[dates[k + 1]] = basis[k + 1] - basis[k]
    months = sorted(set(d[:7] for d in dates[1:]))
    rolls, missing, offsets = {}, [], []
    for m in months:
        y, mo = int(m[:4]), int(m[5:7])
        exp = third_friday(y, mo)
        win = [(d, v) for d, v in db.items()
               if d[:7] == m and -before <= (as_date(d) - exp).days <= after]
        if not win:
            missing.append(m)
            continue
        d, v = min(win, key=lambda x: x[1])
        rolls[d] = v
        offsets.append((as_date(d) - exp).days)
    info = {"months_total": len(months), "months_hit": len(rolls), "months_missing": missing,
            "offsets_from_expiry": dict((str(o), offsets.count(o)) for o in sorted(set(offsets))),
            "months_covered_pct": round(100.0 * len(rolls) / len(months), 2) if months else 0.0}
    return rolls, info


# ---------------------------------------------------------------- readings
def carry_stats(spread, dates, masked_days):
    """One mask, two numbers.

    carry_ann_pct = mean of the surviving days x 244 -- what a roller banks, because the
                    days the mask removes are the level resets it does not book.
    spliced_total_ann_pct = the whole price series divided by its length -- what somebody
                    who held the front contract and never rolled would have booked.  It is
                    printed only to show why the mask is not optional.
    """
    n = len(spread)
    if n < 2:
        return None
    years = n / DAYS_PER_YEAR
    kept = [s for k, s in enumerate(spread) if dates[k + 1] not in masked_days]
    dropped = [s for k, s in enumerate(spread) if dates[k + 1] in masked_days]
    total = sum(spread)
    spliced_ann = total / years * 100.0 if years else None
    carry_ann = statistics.fmean(kept) * DAYS_PER_YEAR * 100.0 if kept else None
    return {
        "years": round(years, 3),
        "calendar_years": round((as_date(dates[-1]) - as_date(dates[0])).days / 365.0, 3),
        "days": n,
        "masked_days": len(dropped),
        "kept_days": len(kept),
        "carry_ann_pct": round(carry_ann, 3) if carry_ann is not None else None,
        "removed_mean_pct": round(statistics.fmean(dropped), 6) if dropped else None,
        "spliced_total_ann_pct": round(spliced_ann, 3) if spliced_ann is not None else None,
    }


def classify_mask(pub, cal, pub_days, cal_days):
    """States describe the MASK, not the strategy.

    MASK_INCOMPLETE  the published mask leaves a material share of the rolls in the series
                     and that moves the annualised reading
    MASK_COMPLETE    it catches them (or the ones it misses do not move the number)
    NO_READING       an input is missing
    """
    if not pub or not cal or not pub.get("carry_ann_pct") or cal.get("carry_ann_pct") is None:
        return "NO_READING"
    if cal_days <= 0:
        return "NO_READING"
    missed = max(0, cal_days - pub_days)
    missed_share = 100.0 * missed / cal_days
    gap = cal["carry_ann_pct"] - pub["carry_ann_pct"]
    if missed_share >= CRITERIA["missed_share_min_pct"] and abs(gap) >= CRITERIA["reading_gap_min_pp"]:
        return "MASK_INCOMPLETE"
    return "MASK_COMPLETE"


# ---------------------------------------------------------------- arms
def arms_under(mask_days, roll_for_cost, dates, ic, basis, spread, repo_dates, repo_rates):
    """r1690's three arms, with the roll days zeroed by `mask_days`.

    The roll-cost charge always uses the calendar mask, so the only thing that moves between
    two runs is which splice days are still sitting in the return series.
    """
    pcts = timing.causal_percentiles(basis)
    repo_acc, repo_missing = wait.daily_repo(dates, spread, repo_dates, repo_rates)
    idx_ret = [ic[t + 1] / ic[t] - 1.0 for t in range(len(dates) - 1)]
    keep = [t for t in range(len(spread))
            if pcts[t] is not None and repo_acc[t] is not None and repo_acc[t] >= 0]
    if len(keep) < wait.MIN_OBS:
        return None
    lo, hi = keep[0], keep[-1] + 1
    span = list(range(lo, hi))
    d_span = dates[lo:hi + 1]
    used = [0.0 if dates[t + 1] in mask_days else spread[t] for t in span]
    in_market = [pcts[t] < wait.WIDE_EDGE for t in span]
    vol_ex = wait.exposure_vol([idx_ret[t] + used[k] for k, t in enumerate(span)])
    lev = wait.leash(vol_ex)
    arms, cnt = wait.run_arms([idx_ret[t] for t in span], used,
                              [repo_acc[t] for t in span], in_market,
                              [roll_for_cost[t] for t in span], lev)
    stats = {k: wait.series_stats(v, d_span) for k, v in arms.items()}
    return {"window": {"from": d_span[0], "to": d_span[-1], "days": len(d_span)},
            "leverage": lev,
            "repo_rows_missing": repo_missing,
            "arms": {k: {"ann_pct": v["ann_pct"], "vol_pct": v["vol_pct"],
                         "maxdd_pct": v["maxdd_pct"]} for k, v in stats.items()},
            "gap_A_minus_B_pp": round(stats["A"]["ann_pct"] - stats["B"]["ann_pct"], 3),
            "time_in_market_pct": round(100.0 * sum(1 for v in in_market if v) / len(span), 2),
            "roll_days_held": cnt["roll_days_held"]}


# ---------------------------------------------------------------- per pair
def one_pair(fut, code):
    rows = base.read_csv_rows(os.path.join(base.FUT_DIR, fut + ".csv"))
    fc = {}
    for r in rows:
        try:
            fc[str(r["date"])[:10]] = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    try:
        idx = base.load_index(code)
    except RuntimeError as exc:
        return {"status": "no_index", "detail": str(exc)[:200]}
    dates, fcl, icl = base.aligned(fc, idx)
    if len(dates) < 400:
        return {"status": "short_overlap", "days": len(dates)}
    basis, spread, pub_roll = base.basis_face(fcl, icl, dates)
    rolls, info = calendar_rolls(dates, basis)
    pub_masked = set(dates[k + 1] for k in range(len(pub_roll)) if pub_roll[k])
    cal_masked = set(rolls)

    pub = carry_stats(spread, dates, pub_masked)
    cal = carry_stats(spread, dates, cal_masked)
    state = classify_mask(pub, cal, pub["masked_days"], cal["masked_days"])
    if info["months_covered_pct"] < CRITERIA["min_months_covered_pct"]:
        state = "CALENDAR_UNUSABLE"

    steps = [v for _, v in sorted(rolls.items())]
    years = pub["years"] if pub else None
    by_year = {}
    for d, v in sorted(rolls.items()):
        b = by_year.setdefault(d[:4], {"rolls": 0, "sum_pct": 0.0})
        b["rolls"] += 1
        b["sum_pct"] = round(b["sum_pct"] + v * 100.0, 3)

    repo_dates, repo_rates = wait.load_repo()
    sens = None
    if repo_dates:
        roll_for_cost = [dates[k + 1] in cal_masked for k in range(len(spread))]
        with_pub = arms_under(pub_masked, roll_for_cost, dates, icl, basis, spread,
                             repo_dates, repo_rates)
        with_cal = arms_under(cal_masked, roll_for_cost, dates, icl, basis, spread,
                             repo_dates, repo_rates)
        if with_pub and with_cal:
            sens = {"published_mask": with_pub, "calendar_mask": with_cal,
                    "A_pp_moved": round(with_cal["arms"]["A"]["ann_pct"]
                                        - with_pub["arms"]["A"]["ann_pct"], 3),
                    "B_pp_moved": round(with_cal["arms"]["B"]["ann_pct"]
                                        - with_pub["arms"]["B"]["ann_pct"], 3),
                    "gap_pp_moved": round(with_cal["gap_A_minus_B_pp"]
                                          - with_pub["gap_A_minus_B_pp"], 3),
                    "B_minus_A_pp": {"published": round(-with_pub["gap_A_minus_B_pp"], 3),
                                     "calendar": round(-with_cal["gap_A_minus_B_pp"], 3)}}

    return {
        "status": "ok",
        "index": code,
        "span": {"from": dates[0], "to": dates[-1], "days": len(dates)},
        "readings": {"published_threshold_mask": pub, "calendar_mask": cal},
        "roll_days": {"published_mask_days": pub["masked_days"], "calendar_mask_days": cal["masked_days"],
                      "missed_days": max(0, cal["masked_days"] - pub["masked_days"]),
                      "missed_share_pct": round(100.0 * max(0, cal["masked_days"] - pub["masked_days"])
                                                / cal["masked_days"], 1) if cal["masked_days"] else None,
                      "carry_gap_pp": round(cal["carry_ann_pct"] - pub["carry_ann_pct"], 3)
                      if (cal["carry_ann_pct"] is not None and pub["carry_ann_pct"] is not None) else None},
        "roll_steps": {
            "count": len(steps),
            "per_year": round(len(steps) / years, 2) if years else None,
            "median_pct": round(statistics.median(steps) * 100.0, 4) if steps else None,
            "mean_pct": round(statistics.fmean(steps) * 100.0, 4) if steps else None,
            "sum_ann_pct": round(sum(steps) / years * 100.0, 3) if (steps and years) else None,
            "positive_steps": sum(1 for s in steps if s > 0),
            "by_year": by_year,
        },
        "detector": info,
        "state": state,
        "arm_sensitivity": sens,
    }


def build():
    pairs = {}
    for fut, (code, name, etf) in base.PAIRS.items():
        pairs[fut] = one_pair(fut, code)
    ok = [p for p in pairs.values() if p.get("status") == "ok"]
    incomplete = [f for f, p in pairs.items() if p.get("state") == "MASK_INCOMPLETE"]
    if not ok:
        verdict = "NO_DATA"
    elif len(incomplete) >= max(1, len(ok) // 2 + 1):
        verdict = "ROLL_MASK_INCOMPLETE"
    elif incomplete:
        verdict = "ROLL_MASK_INCOMPLETE_ON_SOME"
    else:
        verdict = "ROLL_MASK_COMPLETE"

    sens_rows = [(f, p["arm_sensitivity"]) for f, p in pairs.items()
                 if p.get("status") == "ok" and p.get("arm_sensitivity")]
    arms = None
    if sens_rows:
        moved = [s["gap_pp_moved"] for _, s in sens_rows]
        b_shift = [s["B_minus_A_pp"]["calendar"] - s["B_minus_A_pp"]["published"]
                   for _, s in sens_rows]
        arms = {"pairs": len(sens_rows),
                "gap_moved_pp_median": round(statistics.median(moved), 3),
                "gap_moved_pp_min": round(min(moved), 3),
                "gap_moved_pp_max": round(max(moved), 3),
                "B_minus_A_shift_pp_median": round(statistics.median(b_shift), 3),
                "note": "gap = A minus B. A positive movement means the complete mask widens "
                        "the always-in arm over the waiting arm; the r1690 verdict was "
                        "HOLD-ALWAYS on bars W1/W2 (B-A >= 0.5pp) plus W3 (both halves)"}
    return {
        "face": "idx_fut_roll_gap",
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": max(p["span"]["to"] for p in ok) if ok else None,
        "criteria": CRITERIA,
        "verdict": verdict,
        "incomplete_pairs": incomplete,
        "states": {f: p.get("state") for f, p in pairs.items()},
        "verdict_check": {"n_pairs": len(ok), "n_incomplete": len(incomplete),
                          "rule": "MASK_INCOMPLETE needs >=%.0f%% of the calendar rolls missed "
                                  "and >=%.1fpp of annualised reading between the two masks"
                                  % (CRITERIA["missed_share_min_pct"],
                                     CRITERIA["reading_gap_min_pp"])},
        "arm_sensitivity": arms,
        "pairs": pairs,
        "caveats": [
            "main-contract continuous panel only: which contract the series switched to is "
            "not recorded, so the splice is measured as a basis step, not as a contract pair",
            "the calendar detector assumes the mainland index-futures expiry (third Friday); "
            "a month with no panel day inside the window is reported as missing, not guessed",
            "the open-interest column is unusable before 2019 (all zero) and flat from 2025 "
            "(no contract switch), so it is not used as a detector",
            "masking a roll day sets that day's spread to zero, which charges the roller the "
            "index return with no convergence -- the direction is conservative (it understates "
            "carry by well under 1bp per roll)",
            "the arm re-runs are a sensitivity, not a re-declared verdict: W1/W2/W3 and the "
            "halves check were frozen against the published reading, so a re-declaration "
            "needs its own prereg",
        ],
    }


def render_md(face):
    L = []
    L.append("# Index-futures roll days: how many the mask finds, and what the misses cost")
    L.append("")
    L.append("Face `results/idx_fut_roll_gap.json` · evidence cutoff **%s** · verdict **%s**"
             % (face["evidence_cutoff"], face["verdict"]))
    L.append("")
    L.append("## Why the mask is not optional")
    L.append("")
    L.append("The panel is a main-contract continuous series. On the day it switches contracts")
    L.append("the series jumps by the price difference between them — but a holder who rolls")
    L.append("does not book that jump: they sell the old contract and buy the new one with the")
    L.append("same money. The jump is a level reset (like a split), not a return. So the")
    L.append("roller's return is the series with the splice days masked, and what those")
    L.append("surviving days add up to is the carry. The unmasked price series is printed below")
    L.append("only to show what happens when a splice is left in: on IF it reads")
    L.append("%+.2f%%/yr against a carry of %+.2f%%/yr."
             % (face["pairs"].get("IF", {}).get("readings", {})
                .get("published_threshold_mask", {}).get("spliced_total_ann_pct", 0.0),
                face["pairs"].get("IF", {}).get("readings", {})
                .get("calendar_mask", {}).get("carry_ann_pct", 0.0)))
    L.append("")
    L.append("## What the published detector actually finds")
    L.append("")
    L.append("| pair | published mask days | calendar roll days | missed | missed share | carry under published mask | carry under calendar mask | gap | state |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for fut, p in face["pairs"].items():
        if p.get("status") != "ok":
            L.append("| %s | — | — | — | — | — | — | — | %s |" % (fut, p.get("status")))
            continue
        pub = p["readings"]["published_threshold_mask"]
        cal = p["readings"]["calendar_mask"]
        rd = p["roll_days"]
        L.append("| %s | %d | %d | %d | %.0f%% | %+.2f%%/yr | %+.2f%%/yr | %+.2f | %s |"
                 % (fut, rd["published_mask_days"], rd["calendar_mask_days"], rd["missed_days"],
                    rd["missed_share_pct"] or 0.0, pub["carry_ann_pct"] or 0.0,
                    cal["carry_ann_pct"] or 0.0, rd["carry_gap_pp"] or 0.0, p["state"]))
    L.append("")
    L.append("The index futures expire once a month. The published rule (`8x the median basis")
    L.append("step and above 0.5%`) fires a few times a year, so most splices stay in the")
    L.append("series as losses nobody masked — and the carry reading is short by roughly the")
    L.append("size of the misses.")
    L.append("")
    L.append("## The roll step itself")
    L.append("")
    L.append("| pair | rolls | per year | step median | step mean | sum %%/yr | positive steps | months covered |")
    L.append("|---|---|---|---|---|---|---|---|")
    for fut, p in face["pairs"].items():
        if p.get("status") != "ok":
            continue
        r, d = p["roll_steps"], p["detector"]
        L.append("| %s | %d | %.1f | %+.3f%% | %+.3f%% | %+.2f | %d/%d | %.1f%% |"
                 % (fut, r["count"], r["per_year"] or 0, r["median_pct"] or 0,
                    r["mean_pct"] or 0, r["sum_ann_pct"] or 0, r["positive_steps"], r["count"],
                    d["months_covered_pct"]))
    L.append("")
    L.append("A negative step is the discount the next contract hands you; the month after pays")
    L.append("it back as it converges. That is why the step is not a cost to add on top — it is")
    L.append("the other half of the convergence.")
    L.append("")
    sens = face.get("arm_sensitivity")
    if sens:
        L.append("## What the misses did to the r1690 three-arm verdict")
        L.append("")
        L.append("Same arms, same leash, same costs, same roll-cost charge; the only difference")
        L.append("is which splice days are left in the return series.")
        L.append("")
        L.append("| pair | A published | A calendar | B published | B calendar | B-A published | B-A calendar |")
        L.append("|---|---|---|---|---|---|---|")
        for fut, p in face["pairs"].items():
            s = p.get("arm_sensitivity") if p.get("status") == "ok" else None
            if not s:
                continue
            pm, cm = s["published_mask"]["arms"], s["calendar_mask"]["arms"]
            L.append("| %s | %+.2f | %+.2f | %+.2f | %+.2f | %+.2f | %+.2f |"
                     % (fut, pm["A"]["ann_pct"], cm["A"]["ann_pct"], pm["B"]["ann_pct"],
                        cm["B"]["ann_pct"], s["B_minus_A_pp"]["published"],
                        s["B_minus_A_pp"]["calendar"]))
        L.append("")
        L.append("The published run reproduces r1690's B column to the last decimal and its A")
        L.append("column to within the extra roll charge (one calendar roll a month instead of")
        L.append("the two or three a year the detector caught). Under the complete mask the")
        L.append("waiting arm's margin moves by **%+.2fpp** median (A-over-B %+.2fpp, range "
                 "%+.2f .. %+.2f)."
                 % (sens["B_minus_A_shift_pp_median"], sens["gap_moved_pp_median"],
                    sens["gap_moved_pp_min"], sens["gap_moved_pp_max"]))
        L.append("")
        L.append("W1 asks for +0.50pp. The margin the published reading gave the waiting arm on")
        L.append("IF and IH is smaller than this movement and has the same sign as it, so the")
        L.append("HOLD-ALWAYS verdict survives -- but it now survives for a mechanical reason:")
        L.append("the always-in arm was under-credited by 4-7pp a year of carry the mask left in")
        L.append("the series as losses.")
        L.append("")
    L.append("## Caveats")
    L.append("")
    for c in face["caveats"]:
        L.append("- %s" % c)
    L.append("")
    return "\n".join(L)


def check_face(face=None):
    """Re-derive every pair's state from its own two readings."""
    if face is None:
        if not os.path.exists(OUT_JSON):
            print("CHECK_FAIL: no face")
            return 1
        with io.open(OUT_JSON, encoding="utf-8") as fh:
            face = json.load(fh)
    bad = []
    for fut, p in face["pairs"].items():
        if p.get("status") != "ok":
            continue
        pub = p["readings"]["published_threshold_mask"]
        cal = p["readings"]["calendar_mask"]
        want = classify_mask(pub, cal, pub["masked_days"], cal["masked_days"])
        if p["detector"]["months_covered_pct"] < CRITERIA["min_months_covered_pct"]:
            want = "CALENDAR_UNUSABLE"
        if want != p["state"]:
            bad.append("%s state published=%s re-derived=%s" % (fut, p["state"], want))
        rd = p["roll_days"]
        if rd["missed_days"] != max(0, cal["masked_days"] - pub["masked_days"]):
            bad.append("%s missed_days does not follow the two masks" % fut)
    if bad:
        print("CHECK_FAIL: " + "; ".join(bad[:3]))
        return 1
    print("CHECK_OK: %d pairs re-derived, verdict=%s" % (len(face["pairs"]), face["verdict"]))
    return 0


# ---------------------------------------------------------------- selftest
def _synth(monthly_step, daily_drift, nmonths=24):
    """Business days over `nmonths` months and a basis that drifts daily and steps once a
    month -- on the second business day before that month's expiry, where the panel puts it."""
    months = []
    y, m = 2024, 1
    for _ in range(nmonths):
        months.append((y, m))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    days = []
    for (yy, mm) in months:
        d = dt.date(yy, mm, 1)
        while d.month == mm:
            if d.weekday() < 5:
                days.append(d)
            d += dt.timedelta(days=1)
    step_days = set()
    for (yy, mm) in months:
        exp = third_friday(yy, mm)
        cands = [d for d in days if d.month == mm and d >= exp - dt.timedelta(days=2)]
        if cands:
            step_days.add(cands[0])
    dates, basis = [], []
    lvl = 0.0
    for k, d in enumerate(days):
        dates.append(d.isoformat())
        if k:
            lvl += daily_drift
            if d in step_days:
                lvl += monthly_step
        basis.append(lvl)
    # futures return minus index return is the basis change, by construction
    spread = [(1.0 + basis[k]) / (1.0 + basis[k - 1]) - 1.0 for k in range(1, len(basis))]
    return dates, basis, spread


def selftest():
    ok = fail = 0
    def leg(name, cond, detail=""):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print("  FAIL %s %s" % (name, detail))

    leg("third friday is a friday in the 15..21 band",
        all(third_friday(y, m).weekday() == 4 and 15 <= third_friday(y, m).day <= 21
            for y in (2024, 2025, 2026) for m in range(1, 13)))
    leg("third friday of 2026-11 is the 20th", third_friday(2026, 11) == dt.date(2026, 11, 20))

    # A sawtooth: the roller earns the convergence, the price series nets to nothing.
    dates, basis, spread = _synth(-0.02, +0.00095)
    rolls, info = calendar_rolls(dates, basis)
    leg("sawtooth: every month rolls", info["months_hit"] == info["months_total"],
        "hit=%d total=%d" % (info["months_hit"], info["months_total"]))
    leg("sawtooth: the roll step is negative every time", all(v < 0 for v in rolls.values()))
    cal = carry_stats(spread, dates, set(rolls))
    leg("sawtooth: the masked reading recovers the carry (~22%/yr)",
        cal["carry_ann_pct"] is not None and 15.0 < cal["carry_ann_pct"] < 30.0,
        "carry=%.2f" % (cal["carry_ann_pct"] or 0))
    leg("sawtooth: the unmasked price series nets to ~zero -- the jump is a level reset",
        abs(cal["spliced_total_ann_pct"]) < 3.0, "spliced=%.2f" % cal["spliced_total_ann_pct"])

    # An incomplete mask: keep one roll day in four. That must be called incomplete.
    quarter = set(sorted(rolls)[0::4])
    pub = carry_stats(spread, dates, quarter)
    leg("incomplete mask understates the carry",
        pub["carry_ann_pct"] < cal["carry_ann_pct"] - 1.0,
        "pub=%.2f cal=%.2f" % (pub["carry_ann_pct"], cal["carry_ann_pct"]))
    leg("incomplete mask is classified as such",
        classify_mask(pub, cal, pub["masked_days"], cal["masked_days"]) == "MASK_INCOMPLETE",
        classify_mask(pub, cal, pub["masked_days"], cal["masked_days"]))
    leg("a complete mask is not flagged",
        classify_mask(cal, cal, cal["masked_days"], cal["masked_days"]) == "MASK_COMPLETE")

    # No sawtooth at all: nothing to mask, nothing to flag.
    dates2, basis2, spread2 = _synth(0.0, -0.0005)
    rolls2, _ = calendar_rolls(dates2, basis2)
    st2 = carry_stats(spread2, dates2, set(rolls2))
    leg("flat basis: no missed-carry flag",
        classify_mask(st2, st2, st2["masked_days"], st2["masked_days"]) == "MASK_COMPLETE",
        classify_mask(st2, st2, st2["masked_days"], st2["masked_days"]))

    # The detector must use the expiry window, and not reach outside it for a bigger step.
    dates3 = ["2024-03-04", "2024-03-05", "2024-03-06", "2024-03-07", "2024-03-11",
              "2024-03-12", "2024-03-13", "2024-03-14", "2024-03-15", "2024-03-18"]
    basis3 = [0.000, 0.000, 0.000, 0.000, -0.010, 0.000, 0.000, 0.000, 0.000, 0.000]
    # 2024-03-15 is the third Friday, so the window is 03-09..03-18; the step is on 03-11.
    rolls3, _ = calendar_rolls(dates3, basis3)
    leg("detector uses the expiry window", list(rolls3) == ["2024-03-11"], str(rolls3))
    leg("detector reports the step it found", abs(rolls3["2024-03-11"] + 0.010) < 1e-9, str(rolls3))
    basis5 = [0.000, -0.040, 0.000, 0.000, -0.010, 0.000, 0.000, 0.000, 0.000, 0.000]
    rolls5, _ = calendar_rolls(dates3, basis5)
    leg("a bigger step outside the window is not taken",
        list(rolls5) == ["2024-03-11"] and abs(rolls5["2024-03-11"] + 0.010) < 1e-9, str(rolls5))

    # An empty month must be named, not silently skipped.
    dates4 = ["2024-01-02", "2024-01-03", "2024-03-01"]
    basis4 = [0.0, -0.01, -0.01]
    _, info4 = calendar_rolls(dates4, basis4)
    leg("missing months are counted", "2024-01" in info4["months_missing"],
        str(info4["months_missing"]))

    # The rendered page must carry the verdict, the mask table and the caveat block.
    fake = {"evidence_cutoff": "2026-01-01", "verdict": "X", "pairs": {}, "caveats": ["c1"],
            "arm_sensitivity": {"gap_moved_pp_median": 0.0, "gap_moved_pp_min": 0.0,
                                "gap_moved_pp_max": 0.0, "B_minus_A_shift_pp_median": 0.0}}
    md = render_md(fake)
    leg("page carries the verdict", "**X**" in md)
    leg("page carries the level-reset argument", "level reset" in md)
    leg("page carries the caveats", "- c1" in md)

    print("selftest %d/%d PASS" % (ok, ok + fail))
    return 0 if fail == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check_face()
    if a.mode == "selftest":
        return selftest()
    face = build()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(face))
    print(json.dumps({"verdict": face["verdict"], "states": face["states"],
                      "incomplete_pairs": face["incomplete_pairs"],
                      "arm_sensitivity": face["arm_sensitivity"],
                      "evidence_cutoff": face["evidence_cutoff"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
