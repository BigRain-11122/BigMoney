"""A premium printed against a stale denominator moves exactly as fast as the price.

r2227. The CEO page says 159655 carries a +10.36% premium on 2026-11-27, up from
+7.32% the day before, and the reader is meant to act on that -- the premium
choice face even prices the swap at about 8,999 CNY. But that row's denominator
carries `nav_session = 2026-11-26`: the NAV behind the 11-27 premium is
yesterday's number. Nothing in the printed premium says so.

Where the denominator is stale, an exact identity holds. With P the price and
NAV the (unchanged) denominator,

    1 + premium_T     P_T / NAV          P_T
    -------------  =  -----------  =  ---------   =  1 + price change
    1 + premium_T-1   P_T-1 / NAV       P_T-1

So the whole 3.04pp "premium widening" on 159655 is the price move written a
second time. It carries no information about the premium at all. The true
premium is (1 + printed) / (1 + r) where r is that leg's own NAV return for the
day -- unknowable until the NAV lands.

This face answers three questions the premium book kept asking one round at a
time:

  1. Is a stale denominator rare or normal?   (per-leg history of nav_session)
  2. For a lagging leg, is waiting useless?   (same-day share over its history)
  3. How wrong is the printed premium?        (rebanded on that leg's NAV-return
                                               distribution; p10..p90 and worst)

Verdicts, one per lagging leg of the latest snapshot, keyed on that leg's own
same-day share over the snapshots this repo captured:
  DENOMINATOR_USUALLY_LANDS_SAME_DAY   -- >= 90%: a one-off, a later pass fixes it
  DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS -- 70-90%: on most days the field holds an
                                          intraday estimate; today it fell back to the
                                          previous official NAV and the row cannot say so
  DENOMINATOR_RARELY_LANDS_SAME_DAY    -- < 70%: this leg's number usually is not here yet
  UNMEASURED_NOT_ZERO                  -- too little history to judge; says so instead
                                          of printing a confident word

Output: results/etf_nav/lag_face.json + research/ETF_NAV_LAG_FACE.md.

Usage:
    python scripts/etf_nav_lag_face.py run
    python scripts/etf_nav_lag_face.py check
    python scripts/etf_nav_lag_face.py selftest
"""
import argparse
import csv
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
NAVH_DIR = os.path.join(ROOT, "data", "etf_premium", "nav_history")
CAL_PATH = os.path.join(ROOT, "data", "daily", "sh510300.csv")
OUT_JSON = os.path.join(ROOT, "results", "etf_nav", "lag_face.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_NAV_LAG_FACE.md")

SAME_DAY_LINE = 0.85          # history at or above this = the gap is a one-off
ESTIMATE_LINE = 0.70          # between the two = the field is usually an estimate
MIN_HISTORY = 3               # below this we refuse to judge a leg
REBAND_BAND = (0.10, 0.90)    # the band printed next to the rebanded premium


# ---------------------------------------------------------------- pure helpers
def lag_of(session, nav_session, index):
    """Trading-day distance between the snapshot and the NAV it used, or None."""
    if not session or not nav_session:
        return None
    a, b = index.get(session), index.get(nav_session)
    if a is None or b is None:
        return None
    return a - b


def nav_return_band(rets, band=REBAND_BAND):
    """p10/p90/worst of a NAV daily-return series.  None where not measurable."""
    if not rets:
        return {"n": 0, "p10": None, "p50": None, "p90": None, "worst": None}
    s = sorted(rets)
    n = len(s)
    lo = s[min(n - 1, max(0, int(band[0] * n)))]
    hi = s[min(n - 1, max(0, int(band[1] * n)))]
    return {"n": n, "p10": lo, "p50": statistics.median(s), "p90": hi,
            "worst": max(abs(min(s)), abs(max(s)))}


def reband(premium, band):
    """(1+true) = (1+printed)/(1+r): the printed premium's honest interval."""
    if premium is None or band.get("p90") is None:
        return None
    out = {}
    # a rising NAV pushes the true premium down, and vice versa
    out["lo_p10_p90"] = (1.0 + premium) / (1.0 + band["p90"]) - 1.0
    out["hi_p10_p90"] = (1.0 + premium) / (1.0 + band["p10"]) - 1.0
    w = band.get("worst")
    if w is not None:
        out["lo_worst"] = (1.0 + premium) / (1.0 + w) - 1.0
        out["hi_worst"] = (1.0 + premium) / (1.0 - w) - 1.0
    else:
        out["lo_worst"] = out["hi_worst"] = None
    return out


def classify(n_hist, same_day_share):
    """Four words.  The middle two are the useful ones -- and neither is 'unknown'.

    A leg whose own history lands same-day almost every time is a one-off: the
    collector ran before the publisher.  A leg at 70-90% is a different animal --
    on most days its number is an intraday estimate, and on the days it is not,
    the row silently keeps yesterday's official NAV.  Those two readings are not
    distinguishable from the row itself, which is why the band is printed.
    """
    if n_hist < MIN_HISTORY or same_day_share is None:
        return "UNMEASURED_NOT_ZERO"
    if same_day_share >= SAME_DAY_LINE:
        return "DENOMINATOR_USUALLY_LANDS_SAME_DAY"
    if same_day_share >= ESTIMATE_LINE:
        return "DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS"
    return "DENOMINATOR_RARELY_LANDS_SAME_DAY"


def price_move_is_the_whole_story(prev_row, cur_row, tol=1e-5):
    """The identity: with an unchanged denominator, premium moves as the price does.

    Returns (identity_holds, price_change, premium_ratio_minus_one).  Holds only
    when both rows printed against the SAME nav value, which is the lag case.

    tol is 1e-5, not machine epsilon: the test compares a ratio built from the
    printed premium, whose stored precision is about five significant digits, so
    a tighter line would fail on rounding rather than on a different premium.
    """
    if not prev_row or not cur_row:
        return None, None, None
    try:
        p0, p1 = float(prev_row["price"]), float(cur_row["price"])
        q0, q1 = float(prev_row["premium"]), float(cur_row["premium"])
    except (KeyError, TypeError, ValueError):
        return None, None, None
    if p0 <= 0 or (1.0 + q0) <= 0:
        return None, None, None
    price_chg = p1 / p0 - 1.0
    prem_ratio = (1.0 + q1) / (1.0 + q0) - 1.0
    return abs(prem_ratio - price_chg) <= max(tol, 1e-9), price_chg, prem_ratio


def verdict_for(legs):
    if not legs:
        return "EVERY_DENOMINATOR_IS_DATED_TODAY"
    words = {l["verdict"] for l in legs}
    if words == {"DENOMINATOR_USUALLY_LANDS_SAME_DAY"}:
        return "ONE_OFF_LAPSES_A_LATER_PASS_FIXES_THEM"
    if "DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS" in words:
        return "MOST_LAGGING_ROWS_ARE_ESTIMATES_WEARING_A_DATE"
    if "DENOMINATOR_RARELY_LANDS_SAME_DAY" in words:
        return "SOME_DENOMINATORS_RARELY_LAND_SAME_DAY"
    if "UNMEASURED_NOT_ZERO" in words:
        return "A_LAGGING_LEG_WITH_NO_HISTORY_TO_JUDGE_IT"
    return "LAGGING_LEGS_MIXED"


# ------------------------------------------------------------------- loaders
def load_calendar():
    days = []
    if os.path.exists(CAL_PATH):
        for line in open(CAL_PATH, encoding="utf-8").read().strip().splitlines()[1:]:
            days.append(line.split(",")[0])
    return days


def load_snaps(snap_dir):
    """[{session, rows: {code: {price, nav, premium, name, nav_session}}}]"""
    out = []
    for path in sorted(glob.glob(os.path.join(snap_dir, "*.csv"))):
        session = os.path.basename(path)[:10]
        rows = {}
        with open(path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                code = (r.get("code") or "").strip()
                if not code:
                    continue
                try:
                    price = float(r["price"])
                except (KeyError, TypeError, ValueError):
                    continue
                prem = None
                if r.get("premium_pct") not in (None, ""):
                    try:
                        prem = float(r["premium_pct"]) / 100.0
                    except ValueError:
                        prem = None
                rows[code] = {"name": r.get("name") or code, "price": price,
                              "nav": r.get("iopv"), "premium": prem,
                              "nav_session": (r.get("nav_session") or "").strip()}
        out.append({"session": session, "rows": rows})
    return out


def load_nav_returns(navh_dir):
    """{code: [daily return, ...]} from the official NAV history, last 120 rows."""
    out = {}
    for path in sorted(glob.glob(os.path.join(navh_dir, "*.csv"))):
        code = os.path.basename(path)[:-4]
        vals = []
        with open(path, encoding="utf-8") as fh:
            next(fh, None)
            for line in fh:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                try:
                    vals.append(float(parts[1]))
                except ValueError:
                    continue
        vals = vals[-121:]
        rets = [vals[i] / vals[i - 1] - 1.0 for i in range(1, len(vals)) if vals[i - 1] > 0]
        if rets:
            out[code] = rets[-120:]
    return out


# --------------------------------------------------------------------- build
def build(snaps, index, nav_rets):
    hist = {}          # code -> [lag, ...]
    lag_hist = {}
    n_rows = 0
    for snap in snaps:
        for code, row in snap["rows"].items():
            lag = lag_of(snap["session"], row.get("nav_session"), index)
            if lag is None:
                continue
            n_rows += 1
            lag_hist[lag] = lag_hist.get(lag, 0) + 1
            hist.setdefault(code, []).append(lag)

    latest = snaps[-1] if snaps else None
    prev = snaps[-2] if len(snaps) >= 2 else None
    legs = []
    if latest:
        for code, row in sorted(latest["rows"].items()):
            lag = lag_of(latest["session"], row.get("nav_session"), index)
            if lag is None or lag <= 0:
                continue
            mine = hist.get(code, [])
            same = None
            if mine:
                same = sum(1 for v in mine if v == 0) / float(len(mine))
            band = nav_return_band(nav_rets.get(code) or [])
            prem = row.get("premium")
            prev_row = None
            if prev and code in prev["rows"]:
                p = prev["rows"][code]
                prev_row = {"price": p["price"], "premium": p["premium"]}
            holds, price_chg, prem_ratio = price_move_is_the_whole_story(prev_row, row)
            legs.append({
                "code": code,
                "name": row["name"],
                "lag_trading_days": lag,
                "session": latest["session"],
                "nav_session": row.get("nav_session"),
                "premium_printed": prem,
                "nav_band": band,
                "premium_rebanded": reband(prem, band),
                "prev_premium_printed": (prev_row or {}).get("premium"),
                "price_change_since_prev_snapshot": price_chg,
                "premium_ratio_since_prev_snapshot": prem_ratio,
                "identity_price_is_the_whole_story": holds,
                "history_n": len(mine),
                "same_day_share": same,
                "verdict": classify(len(mine), same),
            })

    same_day = lag_hist.get(0, 0)
    face = {
        "generated": None,                       # stamped by run()
        "evidence_cutoff": latest["session"] if latest else None,
        "n_snapshots": len(snaps),
        "n_rows_with_a_dated_nav": n_rows,
        "lag_histogram": {str(k): v for k, v in sorted(lag_hist.items())},
        "same_day_share": (same_day / float(n_rows)) if n_rows else None,
        "latest": {
            "session": latest["session"] if latest else None,
            "n_legs": len(latest["rows"]) if latest else 0,
            "n_lagging": len(legs),
        },
        "legs": legs,
        "summary": _summary(legs),
        "verdict": verdict_for(legs),
        "statement": None,                       # filled by run()
        "thresholds": {"same_day_line": SAME_DAY_LINE, "estimate_line": ESTIMATE_LINE,
                       "min_history": MIN_HISTORY, "reband_band": list(REBAND_BAND)},
        "notes": [
            "premium_rebanded is (1+printed)/(1+r) over that leg's own official NAV daily "
            "returns; it is an interval for a number that has not been published yet, not a "
            "better estimate of it.",
            "identity_price_is_the_whole_story tests the exact relation "
            "(1+prem_T)/(1+prem_T-1) == P_T/P_T-1, which holds only while the denominator "
            "is unchanged; when it is true the printed premium change carries no premium "
            "information at all.",
            "same_day_share is over the snapshots this repo captured for that leg, not over "
            "the vendor's whole publication history; with a dozen snapshots the lines at "
            "85% and 70% describe the two groups that exist on the board, they are not a "
            "statistical test.",
        ],
    }
    face["statement"] = compose_statement(face)
    return face


def compose_statement(face):
    latest = face["latest"]
    cut = face["evidence_cutoff"]
    share = face["same_day_share"]
    if not latest["n_lagging"]:
        return ("Every denominator in the %s snapshot carries that session's own date "
                "(same-day share over history %.1f%%), so the figure behind that row "
                "belongs to the day it is printed on."
                % (cut, 100.0 * (share or 0.0)))
    s = face["summary"]
    bits = ["%d of %d legs in the %s snapshot are priced against a NAV that is not that "
            "session's (lag up to %d trading day(s)); over this repo's snapshot history "
            "only %.1f%% of rows are same-day."
            % (latest["n_lagging"], latest["n_legs"], cut, s["max_lag"],
               100.0 * (share or 0.0))]
    parts = []
    if s["n_usually"]:
        parts.append("%d are one-offs (their own history lands same-day on >= %d%% of "
                     "snapshots, so a later pass fixes them)"
                     % (s["n_usually"], 100 * SAME_DAY_LINE))
    if s["n_estimate"]:
        parts.append("%d sit at %d-%d%% -- on most days that field is an intraday "
                     "estimate, and today it fell back to yesterday's official NAV; the "
                     "row cannot tell you which one it is holding"
                     % (s["n_estimate"], 100 * ESTIMATE_LINE, 100 * SAME_DAY_LINE))
    if s["n_rarely"]:
        parts.append("%d rarely land same-day at all" % s["n_rarely"])
    if s["n_unmeasured"]:
        parts.append("%d have no history to judge them" % s["n_unmeasured"])
    if parts:
        bits.append("; ".join(parts) + ".")
    if s["n_identity_holds"]:
        bits.append("On %d of them the printed premium moved exactly as the price did "
                    "since the previous snapshot, which is what an unchanged denominator "
                    "forces -- those readings carry no premium information at all."
                    % s["n_identity_holds"])
    top = s["largest_premiums"]
    if top:
        shown = ", ".join("%s %s %.1f%%" % (t["code"], t["name"], 100 * t["premium_printed"])
                          for t in top)
        bits.append("Largest printed premiums among them: %s." % shown)
    return " ".join(bits)


def _summary(legs):
    def count(word):
        return sum(1 for l in legs if l["verdict"] == word)
    tops = sorted((l for l in legs if l["premium_printed"] is not None),
                  key=lambda l: -abs(l["premium_printed"]))[:5]
    return {
        "n_usually": count("DENOMINATOR_USUALLY_LANDS_SAME_DAY"),
        "n_estimate": count("DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS"),
        "n_rarely": count("DENOMINATOR_RARELY_LANDS_SAME_DAY"),
        "n_unmeasured": count("UNMEASURED_NOT_ZERO"),
        "n_identity_holds": sum(1 for l in legs
                                if l["identity_price_is_the_whole_story"] is True),
        "max_lag": max([l["lag_trading_days"] for l in legs] or [0]),
        "largest_premiums": [{"code": l["code"], "name": l["name"],
                              "premium_printed": l["premium_printed"],
                              "verdict": l["verdict"]} for l in tops],
    }


# ----------------------------------------------------------------------- io
def write_faces(face):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    lines = ["# ETF NAV lag face", "",
             "Generated %s · evidence cutoff %s" % (face["generated"], face["evidence_cutoff"]),
             "", "Verdict: `%s`" % face["verdict"], "", face["statement"] or "", "",
             "## Lag histogram over %d snapped rows" % face["n_rows_with_a_dated_nav"], "",
             "| lag (trading days) | rows |", "|---|---|"]
    for k, v in sorted(face["lag_histogram"].items(), key=lambda kv: int(kv[0])):
        lines.append("| %s | %d |" % (k, v))
    lines += ["", "## Lagging legs in the latest snapshot (%s)" % face["latest"]["session"], ""]
    if not face["legs"]:
        lines.append("None.")
    else:
        lines += ["| code | name | lag | nav_session | printed premium | rebanded p10..p90 | same-day | verdict |",
                  "|---|---|---|---|---|---|---|---|"]
        shown = sorted(face["legs"], key=lambda l: -abs(l["premium_printed"] or 0.0))[:15]
        for leg in shown:
            reb = leg["premium_rebanded"] or {}
            def pct(x):
                return "-" if x is None else "%.2f%%" % (100 * x)
            lines.append("| %s | %s | %d | %s | %s | %s..%s | %.0f%% of %d | `%s` |" % (
                leg["code"], leg["name"], leg["lag_trading_days"], leg["nav_session"],
                pct(leg["premium_printed"]), pct(reb.get("lo_p10_p90")),
                pct(reb.get("hi_p10_p90")), 100 * (leg["same_day_share"] or 0.0),
                leg["history_n"], leg["verdict"]))
        if len(face["legs"]) > len(shown):
            lines += ["", "Top 15 of %d lagging legs by |printed premium|; the full roster is "
                          "in `results/etf_nav/lag_face.json`." % len(face["legs"])]
    lines += ["", "## Notes", ""] + ["- " + n for n in face["notes"]] + [""]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


# --------------------------------------------------------------------- check
def run_check():
    if not os.path.exists(OUT_JSON):
        print("CHECK FAILED: face missing at %s" % OUT_JSON)
        return 3
    face = build(load_snaps(SNAP_DIR), index_of(load_calendar()), load_nav_returns(NAVH_DIR))
    on_disk = json.load(open(OUT_JSON, encoding="utf-8"))
    problems = []
    for key in ("evidence_cutoff", "n_snapshots", "n_rows_with_a_dated_nav",
                "lag_histogram", "verdict", "latest", "summary"):
        if on_disk.get(key) != face.get(key):
            problems.append(key)
    # the statement is derived from the same inputs; if inputs moved it is STALE
    if on_disk.get("statement") != face.get("statement"):
        problems.append("statement")
    if problems:
        print("STALE: %s drifted from its inputs (%s). Rerun `run`."
              % (os.path.basename(OUT_JSON), ", ".join(problems)))
        return 3
    print("CHECK OK: %s matches a fresh derive from the same inputs" % os.path.basename(OUT_JSON))
    return 0


def index_of(days):
    return {d: i for i, d in enumerate(days)}


# -------------------------------------------------------------------- selftest
def selftest():
    cal = ["2026-11-20", "2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26", "2026-11-27"]
    idx = index_of(cal)
    legs = 0
    fails = []

    def leg(name, ok, detail=""):
        nonlocal legs
        legs += 1
        if not ok:
            fails.append("%s %s" % (name, detail))

    # 1. lag arithmetic on a real calendar including a weekend gap
    leg("lag-1day", lag_of("2026-11-27", "2026-11-26", idx) == 1)
    leg("lag-weekend", lag_of("2026-11-23", "2026-11-20", idx) == 1)
    leg("lag-unknown-date", lag_of("2026-11-27", "2026-11-19", idx) is None)

    # 2. the identity: same denominator -> premium ratio equals the price ratio
    prev = {"price": 1.873, "premium": 0.07323}
    cur = {"price": 1.926, "premium": 0.1036}
    holds, chg, ratio = price_move_is_the_whole_story(prev, cur)
    leg("identity-holds", holds is True and abs(chg - ratio) < 1e-5, (chg, ratio))

    # 3. negative control: a real premium change must break the identity
    cur_bad = {"price": 1.926, "premium": 0.0732}
    holds_bad, _, _ = price_move_is_the_whole_story(prev, cur_bad)
    leg("identity-breaks-when-premium-really-changed", holds_bad is False)

    # 4. four-way classification, including the unmeasured leg
    leg("class-one-off", classify(9, 0.89) == "DENOMINATOR_USUALLY_LANDS_SAME_DAY")
    leg("class-estimate-band",
        classify(9, 0.78) == "DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS")
    leg("class-rarely", classify(60, 0.10) == "DENOMINATOR_RARELY_LANDS_SAME_DAY")
    leg("class-unmeasured", classify(1, 1.0) == "UNMEASURED_NOT_ZERO")
    leg("class-unmeasured-none", classify(9, None) == "UNMEASURED_NOT_ZERO")

    # 5. reband: a rising NAV pushes the true premium down, never up
    band = {"n": 60, "p10": -0.0119, "p50": -0.0023, "p90": 0.0117, "worst": 0.0458}
    rb = reband(0.1036, band)
    leg("reband-lo-below-printed", rb["lo_p10_p90"] < 0.1036)
    leg("reband-hi-above-printed", rb["hi_p10_p90"] > 0.1036)
    leg("reband-worst-wider", rb["hi_worst"] > rb["hi_p10_p90"])

    # 6. an empty return series must not become a zero-width interval
    rb_none = reband(0.05, nav_return_band([]))
    leg("reband-unmeasured-not-zero", rb_none is None)

    # 7. verdict words follow the leg set
    leg("verdict-all-dated", verdict_for([]) == "EVERY_DENOMINATOR_IS_DATED_TODAY")
    leg("verdict-one-off",
        verdict_for([{"verdict": "DENOMINATOR_USUALLY_LANDS_SAME_DAY"}]) ==
        "ONE_OFF_LAPSES_A_LATER_PASS_FIXES_THEM")
    leg("verdict-estimate-dominates",
        verdict_for([{"verdict": "DENOMINATOR_USUALLY_LANDS_SAME_DAY"},
                     {"verdict": "DENOMINATOR_IS_AN_ESTIMATE_ON_MOST_DAYS"}]) ==
        "MOST_LAGGING_ROWS_ARE_ESTIMATES_WEARING_A_DATE")

    # 8. end-to-end on a synthetic snapshot pair
    snaps = [
        {"session": "2026-11-26", "rows": {"X": {"name": "X", "price": 1.873, "nav": "1.7452",
                                                 "premium": 0.07323, "nav_session": "2026-11-26"}}},
        {"session": "2026-11-27", "rows": {"X": {"name": "X", "price": 1.926, "nav": "1.7452",
                                                 "premium": 0.1036, "nav_session": "2026-11-26"}}},
    ]
    face = build(snaps, idx, {"X": [0.004, -0.003, 0.012, -0.011]})
    leg("e2e-finds-one-lagging", face["latest"]["n_lagging"] == 1)
    leg("e2e-identity-flagged", face["legs"][0]["identity_price_is_the_whole_story"] is True)
    leg("e2e-statement-names-the-code", "X" in (face["statement"] or ""))
    leg("e2e-verdict-word", face["verdict"] == "A_LAGGING_LEG_WITH_NO_HISTORY_TO_JUDGE_IT",
        face["verdict"])

    # 9. a same-day pair must produce no lagging leg at all
    snaps_ok = [{"session": "2026-11-27", "rows": {"Y": {"name": "Y", "price": 2.0, "nav": "1.9",
                                                         "premium": 0.05, "nav_session": "2026-11-27"}}}]
    face_ok = build(snaps_ok, idx, {"Y": [0.001, -0.002]})
    leg("e2e-dated-face-is-quiet", face_ok["latest"]["n_lagging"] == 0 and
        face_ok["verdict"] == "EVERY_DENOMINATOR_IS_DATED_TODAY")

    # 10. a roster of ninety legs must still read like a sentence, not a dump
    many = {}
    for i in range(90):
        code = "T%03d" % i
        many[code] = {"name": "N%d" % i, "price": 1.0 + 0.001 * i, "nav": "1.0",
                      "premium": 0.01 * (i + 1), "nav_session": "2026-11-26"}
    face_many = build([{"session": "2026-11-27", "rows": many}], idx, {})
    leg("many-legs-summary-counts", face_many["summary"]["n_unmeasured"] == 90)
    leg("many-legs-statement-stays-readable", len(face_many["statement"]) < 1200,
        len(face_many["statement"]))
    leg("many-legs-top-five-only", len(face_many["summary"]["largest_premiums"]) == 5)

    # 11. negative control: a same-day leg must never be listed as lagging
    mixed = {"A": {"name": "A", "price": 1.0, "nav": "1.0", "premium": 0.01,
                   "nav_session": "2026-11-27"},
             "B": {"name": "B", "price": 1.0, "nav": "1.0", "premium": 0.02,
                   "nav_session": "2026-11-26"}}
    face_mixed = build([{"session": "2026-11-27", "rows": mixed}], idx, {})
    leg("negative-control-dated-leg-not-listed",
        [l["code"] for l in face_mixed["legs"]] == ["B"])

    for f in fails:
        print("FAIL " + f)
    print("%d legs, %d failed" % (legs, len(fails)))
    return 0 if not fails else 3


# ------------------------------------------------------------------------ run
def run():
    import datetime
    snaps = load_snaps(SNAP_DIR)
    if not snaps:
        print("STALE: no snapshots under %s" % SNAP_DIR)
        return 3
    face = build(snaps, index_of(load_calendar()), load_nav_returns(NAVH_DIR))
    face["generated"] = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    write_faces(face)
    print("verdict=%s cutoff=%s lagging=%d written %s"
          % (face["verdict"], face["evidence_cutoff"], face["latest"]["n_lagging"],
             os.path.relpath(OUT_JSON, ROOT)))
    print(face["statement"])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return run_check()
    if args.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
