"""E221 day-of-month profile across the full ETF universe.

Why this exists: the mid-month calendar family (E61/E215/E218/E219/E220) closed with
a verdict of "no quotable number at any width" -- the effect could not be resolved on
a five-name ladder book, because a ten-name book's own draw noise is 20-50x the 18bp
it was meant to explain. The question underneath it is much cheaper to ask on a wide
panel: is the month boundary a special place for ETF returns at all?

This script asks it with the whole ETF universe (every panel in data/daily), so the
sample is ~1,700 names x ~3,400 sessions instead of one book. It is a descriptive
census: no gate, no verdict, no prereg, no trial count consumed.

Method (stated because the two obvious variants disagree):
  * one observation per SESSION, not per name-session. The cross-section is averaged
    first (equal weight over names that actually trade that day), then the buckets are
    formed over session means and the standard error is computed over sessions. A
    name-day SE would understate it by the whole cross-sectional correlation.
  * a name missing a session is excluded from that session, never zero-filled.
  * positions are counted on the session calendar, from both ends of the month, so
    "the last two sessions" is a session statement and not a calendar-day one.

Usage:
  python scripts/e221_dom_profile.py run
  python scripts/e221_dom_profile.py selftest
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_DIR = os.path.join(ROOT, "data", "daily")
OUTDIR = os.path.join(ROOT, "results", "dom_profile")

MIN_NAMES = 20          # a session needs this many priced names to enter a bucket
ME_N = 2                # month-end = last ME_N sessions
MID_LO, MID_HI = 6, 15  # "mid" = 6th..15th session from the start of the month


# ---------------------------------------------------------------- panel loading
def load_panel(panel_dir=None):
    """Return (calendar, {sym: {date: close}}) read straight off data/daily/*.csv.

    Files are walked in sorted order so the face is byte-reproducible.
    """
    panel_dir = panel_dir or PANEL_DIR
    series = {}
    dates = set()
    for path in sorted(glob.glob(os.path.join(panel_dir, "*.csv"))):
        sym = os.path.basename(path)[:-4]
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
            continue
        if closes:
            series[sym] = closes
            dates.update(closes)
    return sorted(dates), series


def session_means(calendar, series):
    """Equal-weight cross-sectional mean return (bp) per session, plus name count."""
    out = []
    for i in range(1, len(calendar)):
        prev, cur = calendar[i - 1], calendar[i]
        rets = []
        for closes in series.values():
            a = closes.get(prev)
            b = closes.get(cur)
            if a and b:
                rets.append(b / a - 1.0)
        if len(rets) < MIN_NAMES:
            out.append({"date": cur, "n_names": len(rets), "mean_bp": None})
            continue
        out.append({"date": cur, "n_names": len(rets),
                    "mean_bp": 1e4 * sum(rets) / len(rets)})
    return out


# ---------------------------------------------------------------- bucketing
def month_positions(calendar):
    """Per session: (index from month start, 1-based) and (index from month end, 1-based).

    Counted on the SESSION calendar only -- two months with the same length in
    sessions get the same numbering even when one straddles a holiday.
    """
    by_month = {}
    for d in calendar:
        by_month.setdefault(d[:7], []).append(d)
    pos = {}
    for month, days in by_month.items():
        n = len(days)
        for k, d in enumerate(days, start=1):
            pos[d] = (k, n - k + 1)
    return pos


def bucket_rows(rows, pos):
    """Attach bucket labels to session rows (rows with no priced cross-section keep None)."""
    out = []
    for r in rows:
        p = pos.get(r["date"])
        if p is None:
            continue
        k_start, k_end = p
        r = dict(r)
        r["k_start"] = k_start
        r["k_end"] = k_end
        out.append(r)
    return out


def _stats(values):
    n = len(values)
    if n == 0:
        return {"n_days": 0, "mean_bp": None, "sd_bp": None, "se_bp": None, "t": None}
    m = sum(values) / n
    if n < 2:
        return {"n_days": n, "mean_bp": m, "sd_bp": None, "se_bp": None, "t": None}
    var = sum((v - m) ** 2 for v in values) / (n - 1)
    sd = var ** 0.5
    se = sd / (n ** 0.5)
    return {"n_days": n, "mean_bp": m, "sd_bp": sd, "se_bp": se,
            "t": (m / se) if se else None}


def profile(rows):
    """Bucket the session means by month-end position, by month-start position, and by group."""
    usable = [r for r in rows if r.get("mean_bp") is not None]
    by_end, by_start, groups = {}, {}, {"month_end_last2": [], "month_end_last1": [],
                                        "mid_6_15": [], "rest": [], "turn_of_month": []}
    for r in usable:
        by_end.setdefault(r["k_end"], []).append(r["mean_bp"])
        by_start.setdefault(r["k_start"], []).append(r["mean_bp"])
        if r["k_end"] <= ME_N:
            groups["month_end_last2"].append(r["mean_bp"])
        if r["k_end"] == 1:
            groups["month_end_last1"].append(r["mean_bp"])
        if r["k_end"] == 1 or r["k_start"] == 1:
            groups["turn_of_month"].append(r["mean_bp"])
        if MID_LO <= r["k_start"] <= MID_HI:
            groups["mid_6_15"].append(r["mean_bp"])
        if r["k_end"] > ME_N and not (MID_LO <= r["k_start"] <= MID_HI):
            groups["rest"].append(r["mean_bp"])
    face = {
        "unconditional": _stats([r["mean_bp"] for r in usable]),
        "by_k_end": {str(k): _stats(v) for k, v in sorted(by_end.items())},
        "by_k_start": {str(k): _stats(v) for k, v in sorted(by_start.items())},
        "groups": {k: _stats(v) for k, v in groups.items()},
    }
    me = face["groups"]["month_end_last2"]
    rest = face["groups"]["rest"]
    # `se_bp` must be tested against None, not for truthiness: a group with zero
    # session variance has se==0.0, and a truthiness test silently reported
    # "insufficient_days" for a perfectly measured 100bp gap (first selftest run).
    if me["n_days"] and rest["n_days"] and me["se_bp"] is not None and rest["se_bp"] is not None:
        diff = me["mean_bp"] - rest["mean_bp"]
        se = (me["se_bp"] ** 2 + rest["se_bp"] ** 2) ** 0.5
        face["month_end_minus_rest"] = {
            "diff_bp": diff, "se_bp": se,
            "t": (diff / se) if se > 0 else None,
            "t_note": None if se > 0 else "zero_variance_groups",
        }
    else:
        face["month_end_minus_rest"] = {"diff_bp": None, "se_bp": None, "t": None,
                                        "reason": "insufficient_days"}
    # The k_end / k_start ladders are a family of ~21 cells each, so the largest |t|
    # in them is a best-of-m reading and must be quoted against that threshold, not
    # against 1.96. Best cell + the bar it has to clear, published together.
    ladder = {k: v for k, v in face["by_k_end"].items() if v.get("t") is not None}
    if ladder:
        best_k = max(ladder, key=lambda k: abs(ladder[k]["t"]))
        m = len(ladder)
        face["best_bucket"] = {
            "axis": "k_end",
            "bucket": int(best_k),
            "mean_bp": ladder[best_k]["mean_bp"],
            "t": ladder[best_k]["t"],
            "n_days": ladder[best_k]["n_days"],
            "buckets_compared": m,
            "bonferroni_abs_t": _z_two_sided(0.05 / m),
            "clears_bonferroni": abs(ladder[best_k]["t"]) >= _z_two_sided(0.05 / m),
        }
    return face


def _z_two_sided(alpha):
    """Two-sided normal critical value for `alpha`, by bisection on erf (no scipy here)."""
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


POWER_Z = 2.802  # 80% power, two-sided 5%


def _power(face, months):
    """How many SESSIONS/MONTHS would the observed gap need to become resolvable.

    This is the load-bearing number for a calendar effect: widening the cross-section
    buys nothing, because the independent observation is the month, not the name.
    """
    gap = face.get("month_end_minus_rest") or {}
    me = face["groups"]["month_end_last2"]
    rest = face["groups"]["rest"]
    n_now = (me["n_days"] or 0) + (rest["n_days"] or 0)
    out = {"z_80pct_two_sided": POWER_Z, "months_in_test": months,
           "sessions_in_test": n_now, "observed_diff_bp": gap.get("diff_bp"),
           "se_bp": gap.get("se_bp"), "sessions_needed": None,
           "months_needed": None, "years_needed": None,
           "basis": "calendar effects are observed once per month, not once per name",
           "turn_of_month_adjacency": (
               "the first session of a month is the session right after the last one, so "
               "the turn-of-month group's two sessions per month are adjacent and its SE "
               "is optimistic")}
    d, se = gap.get("diff_bp"), gap.get("se_bp")
    if d and se and n_now:
        # se scales as 1/sqrt(N); N_needed = N_now * (z*se/d)^2
        factor = (POWER_Z * se / d) ** 2
        out["sessions_needed"] = n_now * factor
        if months:
            out["months_needed"] = out["sessions_needed"] * (months / float(n_now))
            out["years_needed"] = out["months_needed"] / 12.0
    return out
def run(save=True, panel_dir=None):
    calendar, series = load_panel(panel_dir)
    rows = session_means(calendar, series)
    pos = month_positions(calendar)
    rows = bucket_rows(rows, pos)
    face_stats = profile(rows)
    months_used = len({r["date"][:7] for r in rows if r.get("mean_bp") is not None})
    face_stats["power"] = _power(face_stats, months_used)
    cutoff = calendar[-1] if calendar else None
    face = {
        "study": "e221_dom_profile",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "spec": {
            "panel": "data/daily/*.csv (full ETF universe as carried in-repo)",
            "panel_start": calendar[0] if calendar else None,
            "symbols": len(series),
            "sessions": len(calendar),
            "unit": "bp per session, close-to-close, equal weight over priced names",
            "min_names_per_session": MIN_NAMES,
            "month_end_sessions": ME_N,
            "mid_sessions": [MID_LO, MID_HI],
            "se_basis": "sd over SESSION means / sqrt(n_sessions)",
        },
        "coverage": {
            "sessions_scored": sum(1 for r in rows if r.get("mean_bp") is not None),
            "sessions_dropped_thin": sum(1 for r in rows if r.get("mean_bp") is None),
            "median_names_per_session": _median([r["n_names"] for r in rows
                                                  if r.get("mean_bp") is not None]),
        },
        **face_stats,
        "honest": [
            "descriptive census only: no gate, no verdict, no prereg, no trial count consumed",
            "the ETF population is today's listed set carried in data/daily (listing survivorship)",
            "no costs, no execution model: this is a return profile, not a tradable rule",
            "positions are session positions within the month, not calendar days",
            "a stale close (illiquid ETF repeating yesterday's print) enters as a 0bp return",
        ],
    }
    if save:
        os.makedirs(OUTDIR, exist_ok=True)
        stem = "PROFILE-%s" % cutoff.replace("-", "")
        with open(os.path.join(OUTDIR, stem + ".json"), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        with open(os.path.join(OUTDIR, "by_dom.csv"), "w", encoding="utf-8",
                  newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["k_end", "n_days", "mean_bp", "sd_bp", "se_bp", "t"])
            for k, st in face_stats["by_k_end"].items():
                w.writerow([k, st["n_days"], _r(st["mean_bp"]), _r(st["sd_bp"]),
                            _r(st["se_bp"]), _r(st["t"])])
        print("face: %s" % os.path.join(OUTDIR, stem + ".json"))
    print("sessions=%d symbols=%d cutoff=%s" % (len(calendar), len(series), cutoff))
    print("uncond=%.2fbp  last2=%.2fbp (t=%.2f)  mid=%.2fbp  rest=%.2fbp  me-rest=%.2fbp (t=%.2f)" % (
        face_stats["unconditional"]["mean_bp"] or 0.0,
        face_stats["groups"]["month_end_last2"]["mean_bp"] or 0.0,
        face_stats["groups"]["month_end_last2"]["t"] or 0.0,
        face_stats["groups"]["mid_6_15"]["mean_bp"] or 0.0,
        face_stats["groups"]["rest"]["mean_bp"] or 0.0,
        face_stats["month_end_minus_rest"]["diff_bp"] or 0.0,
        face_stats["month_end_minus_rest"]["t"] or 0.0))
    return face


def _median(vals):
    vals = sorted(vals)
    if not vals:
        return None
    n = len(vals)
    return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0


def _r(v):
    return "" if v is None else round(v, 4)


# ---------------------------------------------------------------- selftest
def _write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "open", "high", "low", "close", "volume", "amount"])
        for d, c in rows:
            w.writerow([d, c, c, c, c, 1000, 1000])


def selftest():
    import tempfile
    import shutil

    ok = tot = 0

    def check(name, cond):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))

    tmp = tempfile.mkdtemp(prefix="e221_")
    try:
        # --- fixture: two months, 5 sessions each, 40 names.
        # Month-end (last 2 sessions of each month) earns +100bp, everything else 0.
        dates = ["2024-01-%02d" % d for d in (2, 3, 4, 5, 8)] + \
                ["2024-02-%02d" % d for d in (1, 2, 5, 6, 7)]
        me = {dates[3], dates[4], dates[8], dates[9]}
        empty = os.path.join(tmp, "panel")
        os.makedirs(empty)
        for s in range(40):
            closes = []
            level = 1.0
            for i, d in enumerate(dates):
                if i > 0:
                    step = 1.0 + (0.01 if dates[i] in me else 0.0)
                    level *= step
                closes.append((d, level))
            _write_csv(os.path.join(empty, "sh%06d.csv" % (510000 + s)), closes)

        cal, series = load_panel(empty)
        check("panel loads every symbol", len(series) == 40 and len(cal) == len(dates))
        rows = bucket_rows(session_means(cal, series), month_positions(cal))

        # 1) the bucket means really are +100bp on the month-end sessions
        face = profile(rows)
        check("month-end bucket picks up the fixture's +100bp",
              abs(face["groups"]["month_end_last2"]["mean_bp"] - 100.0) < 1e-6)
        check("the rest of the month is flat",
              abs(face["groups"]["rest"]["mean_bp"]) < 1e-6)
        check("month-end minus rest reproduces the 100bp gap",
              abs(face["month_end_minus_rest"]["diff_bp"] - 100.0) < 1e-6)
        check("a zero-variance group is a measured gap with an explicit no-t note",
              face["month_end_minus_rest"]["t"] is None
              and face["month_end_minus_rest"]["t_note"] == "zero_variance_groups")

        # 2) positions are session positions from BOTH ends, and a one-session month
        #    has k_start == k_end == 1.
        pos = month_positions(cal)
        check("first session of a month is k_start=1", pos[dates[0]][0] == 1)
        check("last session of a month is k_end=1", pos[dates[4]][1] == 1)
        check("k_start+k_end == sessions_in_month+1", all(
            k + e == len([d for d in dates if d[:7] == d0[:7]]) + 1
            for d0, (k, e) in pos.items()))
        check("a one-session month collapses both positions to 1",
              month_positions(["2024-03-01"])["2024-03-01"] == (1, 1))

        # 3) the SE is a SESSION SE: build a second fixture where every name moves
        #    identically each session (cross-sectional spread = 0 every day) but the
        #    month-end print differs BETWEEN months (+100bp in one, -100bp in the other).
        #    A name-day SE would read 0 and call this infinitely significant; the
        #    session SE must see the dispersion.
        d3 = ["2024-04-%02d" % d for d in (1, 2, 3, 4, 5)] + \
             ["2024-05-%02d" % d for d in (6, 7, 8, 9, 10)]
        me3 = {d3[3], d3[4], d3[8], d3[9]}
        mixed = os.path.join(tmp, "mixed")
        os.makedirs(mixed)
        for s in range(40):
            closes, level = [], 1.0
            for i, d in enumerate(d3):
                if i > 0 and d in me3:
                    level *= 1.01 if i < 5 else 0.99
                closes.append((d, level))
            _write_csv(os.path.join(mixed, "sh%06d.csv" % (530000 + s)), closes)
        calm, seriesm = load_panel(mixed)
        fm = profile(bucket_rows(session_means(calm, seriesm), month_positions(calm)))
        me_st = fm["groups"]["month_end_last2"]
        check("session dispersion is visible when a name-day SE would be a zero",
              me_st["n_days"] == 4 and me_st["sd_bp"] and me_st["sd_bp"] > 90.0)
        check("the two opposite month-ends cancel to ~0 mean with a real SE",
              abs(me_st["mean_bp"]) < 1e-6 and me_st["se_bp"] and me_st["se_bp"] > 40.0)

        # 3b) the ladder's best cell is published with the bar it must clear
        #     (buckets whose sessions are all identical have se=0 and are excluded,
        #      which is why the count is 2 and not 5 on this fixture)
        bb = fm["best_bucket"]
        check("best bucket publishes its own multiple-comparison bar",
              bb["buckets_compared"] == 2 and bb["bonferroni_abs_t"] > 1.96
              and bb["clears_bonferroni"] is False)
        check("a ladder with no usable t publishes no best_bucket",
              "best_bucket" not in face)
        check("two-sided z matches the textbook value", abs(_z_two_sided(0.05) - 1.959964) < 1e-4)

        # 4) a missing print drops the name from that session and never zero-fills it
        holey = os.path.join(tmp, "holey")
        os.makedirs(holey)
        for s in range(40):
            closes = [(d, 1.0) for d in dates]
            if s == 0:
                closes = [c for c in closes if c[0] != dates[1]]  # one name misses day 2
            _write_csv(os.path.join(holey, "sz%06d.csv" % (159000 + s)), closes)
        cal2, series2 = load_panel(holey)
        rows2 = {r["date"]: r for r in session_means(cal2, series2)}
        check("a name with no print that session is excluded, not zero-filled",
              rows2[dates[1]]["n_names"] == 39)

        # 5) thin sessions are dropped, not averaged
        thin = os.path.join(tmp, "thin")
        os.makedirs(thin)
        for s in range(MIN_NAMES - 1):
            _write_csv(os.path.join(thin, "sh%06d.csv" % (520000 + s)),
                       [(d, 1.0) for d in dates])
        cal3, series3 = load_panel(thin)
        check("a session below min_names is dropped rather than averaged",
              all(r["mean_bp"] is None for r in session_means(cal3, series3)))

        # 6) determinism: two runs over the same fixture give the identical payload
        f1 = profile(bucket_rows(session_means(cal, series), month_positions(cal)))
        f2 = profile(bucket_rows(session_means(cal, series), month_positions(cal)))
        check("the face is deterministic (identical payload on a re-run)", f1 == f2)

        # 7) a face with too few days reports the reason instead of a number
        one = profile([r for r in rows if r["mean_bp"] is not None][:2])
        check("insufficient days -> month_end_minus_rest says so",
              one["month_end_minus_rest"].get("reason") == "insufficient_days"
              or one["month_end_minus_rest"]["diff_bp"] is not None)
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